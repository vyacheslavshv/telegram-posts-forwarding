import settings as stg
import re
import messages as msg

from tables import ClientUser, Transfer, StopWord ,  SummeryInfo , SystemInfo
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
from telethon.errors import FloodWaitError
from datetime import datetime, timedelta
from tortoise.transactions import in_transaction
from telethon.tl.custom import Button
from proxy import get_proxy

class ManageClient:

    def __init__(self, event):
        self.event = event
        self.chat_id = event.chat_id
        self.entities = event.message.entities

    async def message(self):
        await self.check_update()
        if await self.check_message():
            await self.forward_message()


    async def check_update(self):
        try:
            summary_db = await SummeryInfo.all()
        except Exception:
            return
        for sum_db in summary_db:
            try:
                if sum_db.last_update == datetime.today().date():
                    date = datetime.today() + timedelta(days=1)
                    sum_db.last_update = date
                    await sum_db.save()
                    me = await stg.client_user.get_me()
                    text = f' USER: {me.first_name}' + (f' {me.last_name}' if me.last_name else str())
                    summary_data = [text]
                    system_info_db = await SystemInfo.all()
                    for sysInf in system_info_db:
                        temp_str = ('\n1) ערוץ מקור: ' + str(sysInf.channel_from) + "\n" + '     פוסטים בערוץ מקור: ' + str(sysInf.from_daily_count) + "\n\n" + '2) ערוץ יעד: ' + str(sysInf.channel_to)
                                    + "\n" + '     הודעות שעברו לערוץ יעד: ' + str(sysInf.to_daily_count) + "\n\n" +  '3) קטגוריה: ' + str(sysInf.category) + "\n")

                        sysInf.from_daily_count = 0
                        sysInf.to_daily_count = 0
                        try:
                            await sysInf.save()
                        except Exception as e:
                            stg.logger.error(f"[check_update] Exception 1:{e}")
                            pass
                            
                        summary_data.append(temp_str)
                    try:
                        my_msg = ''
                        for val in summary_data:
                            my_msg = my_msg + str(val) + "\n"
                        await stg.client_user.send_message(sum_db.summary_channel, str(my_msg))
                    except Exception as e:
                        stg.logger.error(f"[check_update] Exception 2:{e}")
                else:
                    # date is in range
                    return 
            except Exception as e:
                stg.logger.error(f"[check_update] Exception 3:{e}")
                continue
        return


    async def check_message(self):

        try:
            if "MessageMediaUnsupported()" in str(self.event.message.media):
                stg.logger.info(f"[-] MessageMediaUnsupported,channel {self.chat_id} skipping it.")
                return False
        except Exception as e:
             stg.logger.info(f"[-] Cant see MessageMediaUnsupported")

        stop_words_db = await StopWord.all()
        for stop_word_db in stop_words_db:
            if stop_word_db.word in self.event.raw_text:
                stg.logger.info(f"[-] Banned word '{stop_word_db.word}' found, skipping it.")
                return False

        if self.event.message.entities:
            for entity in self.event.message.entities:
                if isinstance(entity, MessageEntityTextUrl):
                    stg.logger.info("[-] Entity url link found,.")
                    # return False

        # self.event.raw_text = re.sub(msg.regexp_tg_links, stg.OUR_LINK, self.event.raw_text)

        telegram_tags = re.findall(r"@\w+", self.event.text)
        if telegram_tags:
            for telegram_tag in telegram_tags:
                self.event.text = self.event.text.replace(telegram_tag, "")

        telegram_links = re.findall(r"(?:https?://)?t(?:elegram)?\.me/[^ ]+", self.event.text, flags=re.IGNORECASE)
        if telegram_links:
            for telegram_link in telegram_links:
                if telegram_link:
                    self.event.text = self.event.text.replace(telegram_link, "")

       
        new_text = self.event.text + stg.OUR_OUTRO
        self.event.text = new_text
        


        return True

    async def forward_message(self):
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all(). \
                prefetch_related('channel_to').prefetch_related('channel_from'):
            try:
                if transfer_db.channel_to.posts_left > 0:
                    async with in_transaction("default") as tconn:
                        posts_left = await tconn.execute_query_dict(
                            'SELECT posts_left FROM channel WHERE id = ?', [transfer_db.channel_to_id])
                        if posts_left[0]['posts_left'] > 0:
                            if transfer_db.channel_from.manual:
                                message = await stg.client_user.send_message(stg.problematic_channel,
                                                                             self.event.message)
                                stg.event_messages[message.id] = self.event.message
                                buttons = [[Button.inline('✅ Approve',
                                                          f'approve_post:{message.id}:{transfer_db.channel_to_id}'),
                                            Button.inline('❌ Reject', f'reject_post:{message.id}')]]
                                await stg.client_bot.send_message(
                                    stg.problematic_channel, 'Approve the post above?', buttons=buttons)
                            else:
                                await stg.client_user.send_message(transfer_db.channel_to_id, self.event.message)
                            await tconn.execute_query(
                                'UPDATE channel SET posts_left = posts_left - 1 WHERE id = ?',
                                [transfer_db.channel_to_id])
                    # transfer_db.channel_to.posts_left -= 1
                    # await transfer_db.channel_to.save()
                if stg.user_flood_wait:
                    stg.user_flood_wait = None
                if transfer_db.channel_to_id in stg.stopped_channels:
                    del stg.stopped_channels[transfer_db.channel_to_id]
            except FloodWaitError as e:
                stg.user_flood_wait = datetime.now() + timedelta(seconds=e.seconds)
            except Exception:
                stg.logger.exception('forward_message')
                stg.stopped_channels[transfer_db.channel_to_id] = \
                    (transfer_db.channel_to.title, transfer_db.channel_to.username)


class ClientEventHelper:
    def __init__(self, event):
        # print('Client:', event.stringify())
        stg.logger.info(event)
        self.manage = ManageClient(event)

    async def runner(self, func):
        try:
            await getattr(self.manage, func)()
        except Exception:
            stg.logger.exception('Client runner')


async def check_client_user_db():
    stg.client_user_db = await ClientUser.filter(id=1).first()
    if not stg.client_user_db:
        stg.client_user_db = ClientUser(id=1)
        await stg.client_user_db.save()


async def connect_user_tg():
    proxy = get_proxy('')
    stg.client_user = TelegramClient(
        'sessions/user', api_id=stg.TG_API_ID,
        api_hash=stg.TG_API_HASH, base_logger='telegram',proxy=proxy)
    await stg.client_user.connect()
