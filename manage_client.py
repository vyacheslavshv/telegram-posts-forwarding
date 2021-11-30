import settings as stg
import re

from tables import ClientUser, Transfer
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl


class ManageClient:

    def __init__(self, event):
        self.event = event
        self.chat_id = event.chat_id
        self.entities = event.message.entities

    async def message(self):
        if await self.check_message():
            await self.forward_message()

    async def check_message(self):
        # for word in stg.banned_words:
        #     if word in self.event.raw_text:
        #         stg.logger.info(f"[-] Banned word '{word}' found, skipping it.")
        #         return False
        #
        # private_chat_link = re.findall(r".*/joinchat/\w+", self.event.raw_text)
        # if private_chat_link:
        #     stg.logger.info("[-] Private join chat link found, skipping it.")
        #     return False

        # if self.event.message.entities:
        #     for entity in self.event.message.entities:
        #         if isinstance(entity, MessageEntityTextUrl):
        #             stg.logger.info("[-] Entity url link found, skipping it.")
        #             return False

        if not self.event.message.media:
            stg.logger.info("[-] There is no text or media, skipping it.")
            return False
        if self.event.raw_text:
            self.event.raw_text = None

        # telegram_tags = re.findall(r"@\w+", self.event.raw_text)
        # if telegram_tags:
        #     for telegram_tag in telegram_tags:
        #         self.event.raw_text = self.event.raw_text.replace(telegram_tag, stg.OUR_TAG)
        #
        # telegram_links = re.findall(r"h?t?t?p?s?:?/?/?[tT]\.[mM][eE]/\w+", self.event.raw_text)
        # if telegram_links:
        #     for telegram_link in telegram_links:
        #         if telegram_link:
        #             self.event.raw_text = self.event.raw_text.replace(telegram_link, stg.OUR_LINK)
        return True

    async def forward_message(self):
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all():
            await stg.client_user.send_message(transfer_db.channel_to_id, self.event.message)


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
