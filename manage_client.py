import settings as stg
import re

from tables import ClientUser, Transfer, StopWord , SummeryInfo , SystemInfo
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
from telethon.errors import FloodWaitError
from datetime import datetime, timedelta
from telethon.tl.custom import Button


class ManageClient:

    def __init__(self, event):
        self.event = event
        self.chat_id = event.chat_id
        self.entities = event.message.entities

    async def message(self):
        return
        # await self.check_update()
        # if await self.check_message():
        #     await self.forward_message()

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
        # stop_word_db = await StopWord.filter(word=self.event.raw_text).first()
        # if stop_word_db:
        #     stg.logger.info(f"[-] Banned word '{stop_word_db.word}' found, skipping it.")
        #     return False

        if not self.event.message.media:
            stg.logger.info("[-] There is no media, skipping it.")
            return False

        try:
            # Стикеры и аудио: ('application/x-tgsticker', 'audio/ogg')
            mime = self.event.message.media.document.mime_type
            if 'video' in mime:
                pass
            else:
                stg.logger.info("[-] There is message with file, skipping it.")
                return False
        except Exception:
            pass

        category_name = None
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all().\
                    prefetch_related('channel_to').prefetch_related('category'):
            category_name = transfer_db.category.name

        channel_to = None
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all().\
                    prefetch_related('channel_from').prefetch_related('channel_to'):
                channel_to = transfer_db.channel_to.title
        try:
            async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all().\
                    prefetch_related('channel_to').prefetch_related('channel_from'):
                try:
                    system_info_db = await SystemInfo.filter(channel_from=transfer_db.channel_from.title).first()
                    if system_info_db:
                        system_info_db.from_daily_count += 1 
                        await system_info_db.save()
                    else:
                        if channel_to:
                            system_info_db = SystemInfo(
                                channel_from = transfer_db.channel_from.title,
                                from_daily_count = 1,
                                channel_to = channel_to,
                                to_daily_count = 0,
                                category = category_name,
                            )
                            await system_info_db.save()
                except Exception as e:
                    stg.logger.info(f"[check_message] SystemInfo Exception: {e}")
        except Exception as e:
                stg.logger.info(f"[check_message] Transfer Exception: {e}")

        if self.event.raw_text:
            self.event.raw_text = None
        return True

    async def forward_message(self):
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all(). \
                prefetch_related('channel_to').prefetch_related('channel_from'):
            try:
                if transfer_db.channel_from.manual:
                    message = await stg.client_user.send_message(stg.problematic_channel, self.event.message)
                    stg.event_messages[message.id] = self.event.message
                    buttons = [[Button.inline('✅ Approve', f'approve_post:{message.id}:{transfer_db.channel_to_id}'),
                                Button.inline('❌ Reject', f'reject_post:{message.id}')]]
                    await stg.client_bot.send_message(
                        stg.problematic_channel, 'Approve the post above?', buttons=buttons)
                else:
                    await stg.client_user.send_message(transfer_db.channel_to_id, self.event.message)
                if stg.user_flood_wait:
                    stg.user_flood_wait = None
                if transfer_db.channel_to_id in stg.stopped_channels:
                    del stg.stopped_channels[transfer_db.channel_to_id]
            except FloodWaitError as e:
                stg.user_flood_wait = datetime.now() + timedelta(seconds=e.seconds)
                return
            except Exception:
                stg.logger.exception('forward_message')
                stg.stopped_channels[transfer_db.channel_to_id] = \
                    (transfer_db.channel_to.title, transfer_db.channel_to.username)
                return

            try:
                system_info_db = await SystemInfo.filter(channel_from=transfer_db.channel_from.title).first()
                if system_info_db:
                    system_info_db.to_daily_count += 1 
                    try:
                        await system_info_db.save()
                    except Exception as e:
                        stg.logger.error(f"[forward_message] system_info_db Exception : {e}") 
            except Exception as e:
                stg.logger.error(f"[forward_message] Transfer Exception : {e}")


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
    stg.client_user = TelegramClient(
        'sessions/user', api_id=stg.TG_API_ID,
        api_hash=stg.TG_API_HASH, base_logger='telegram')
    await stg.client_user.connect()
