import settings as stg
import re

from tables import ClientUser, Transfer, StopWord
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
from telethon.errors import FloodWaitError
from datetime import datetime, timedelta


class ManageClient:

    def __init__(self, event):
        self.event = event
        self.chat_id = event.chat_id
        self.entities = event.message.entities

    async def message(self):
        if await self.check_message():
            await self.forward_message()

    async def check_message(self):
        stop_words_db = await StopWord.all()
        for stop_word_db in stop_words_db:
            if stop_word_db.word in self.event.raw_text:
                stg.logger.info(f"[-] Banned word '{stop_word_db.word}' found, skipping it.")
                return False

        telegram_tags = re.findall(r"@\w+", self.event.text)
        if telegram_tags:
            for telegram_tag in telegram_tags:
                self.event.text = self.event.text.replace(telegram_tag, stg.OUR_TAG)

        telegram_links = re.findall(r"(?:https?://)?t(?:elegram)?\.me/[^ ]+", self.event.text, flags=re.IGNORECASE)
        if telegram_links:
            for telegram_link in telegram_links:
                if telegram_link:
                    self.event.text = self.event.text.replace(telegram_link, stg.OUR_LINK)
        return True

    async def forward_message(self):
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all(). \
                prefetch_related('channel_to'):
            try:
                await stg.client_user.send_message(transfer_db.channel_to_id, self.event.message)
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
    stg.client_user = TelegramClient(
        'sessions/user', api_id=stg.TG_API_ID,
        api_hash=stg.TG_API_HASH, base_logger='telegram')
    await stg.client_user.connect()
