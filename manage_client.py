import settings as stg
import re
import messages as msg

from tables import ClientUser, Transfer, StopWord
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
        stop_word_db = await StopWord.filter(word=self.event.raw_text).first()
        if stop_word_db:
            stg.logger.info(f"[-] Banned word '{stop_word_db.word}' found, skipping it.")
            return False

        if self.event.message.entities:
            for entity in self.event.message.entities:
                if isinstance(entity, MessageEntityTextUrl):
                    stg.logger.info("[-] Entity url link found, skipping it.")
                    return False

        self.event.raw_text = re.sub(msg.regexp_tg_links, stg.OUR_LINK, self.event.raw_text)
        return True

    async def forward_message(self):
        async for transfer_db in Transfer.filter(channel_from_id=self.chat_id, is_working=True).all():
            if transfer_db.transfers_left > 0:
                await stg.client_user.send_message(transfer_db.channel_to_id, self.event.message)

                transfer_db.transfers_left -= 1
                await transfer_db.save()


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
