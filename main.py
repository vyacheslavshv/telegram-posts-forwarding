import settings as stg
import asyncio
import database
import manage_client

from manage_bot import ManageBot
from manage_client import ManageClient
from telethon import events
from telethon import TelegramClient

from tables import ClientUser


client_bot = TelegramClient(
    'sessions/bot', int(stg.TG_API_ID), stg.TG_API_HASH, base_logger='telegram').start(bot_token=stg.TOKEN_BOT)
stg.client_bot = client_bot


@client_bot.on(events.NewMessage)
async def message(event):
    await BotEventHelper(event).runner('message')


@client_bot.on(events.ChatAction)
async def chat_action(event):
    BotEventHelper(event)


@client_bot.on(events.CallbackQuery)
async def callback(event):
    await BotEventHelper(event).runner('callback_query')


class BotEventHelper:

    def __init__(self, event):
        # print('Bot:', event.stringify())
        # stg.logger.info(event)
        self.manage = ManageBot(event)

    async def runner(self, func):
        try:
            await self.manage.init_()
            await getattr(self.manage, func)()
        except Exception:
            stg.logger.exception('Bot runner')


class ClientEventHelper:

    def __init__(self, event):
        # print('Client:', event.stringify())
        # stg.logger.info(event)
        self.manage = ManageClient(event)

    async def runner(self, func):
        try:
            # await self.manage.init_()
            await getattr(self.manage, func)()
        except Exception:
            stg.logger.exception('Client runner')


async def register_user_webhook():
    @stg.client_user.on(events.NewMessage(incoming=True))
    async def message(event):
        await ClientEventHelper(event).runner('message')

    try:
        await stg.client_user.run_until_disconnected()
    except Exception:
        stg.logger.exception('connect_tg;run_until_disconnected')


async def check_client_user_db():
    stg.client_user_db = await ClientUser.filter(id=1).first()
    if not stg.client_user_db:
        stg.client_user_db = ClientUser(id=1)
        await stg.client_user_db.save()


async def main():
    await database.init()
    await check_client_user_db()

    await manage_client.connect_user_tg()
    asyncio.create_task(register_user_webhook())

    await asyncio.gather(stg.client_bot.run_until_disconnected())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            exit()
        except Exception:
            stg.logger.exception('main')
