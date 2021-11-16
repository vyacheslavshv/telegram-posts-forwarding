import utils
import messages as msg
import re
import settings as stg
import buttons as btn

from tables import User, Category, Transfer, Channel

from telethon.errors import \
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError, PhoneCodeInvalidError
from telethon.utils import get_peer_id
from telethon.tl import types
from telethon.tl.custom import Button
from copy import deepcopy


class ManageBot:

    def __init__(self, event):
        self.event = event

        self.chat_db = None
        self.user_db = None

        self.chat_id = event.chat.id
        self.user_id = utils.get_user_id(event)

        try:
            self.text = self.event.text
        except AttributeError:
            self.text = None

    async def init_(self):
        # self.chat = await self.event.get_chat()
        # self.chat_db = self.session.query(tables.GroupTaskList).filter_by(group_id=self.chat.id).first()
        try:
            self.user = await self.event.get_sender()
        except AttributeError:
            self.user = await self.event.get_user()

        if self.user_id:
            await self.check_user()

    async def message(self):
        if self.event.message.is_private:
            await self.private_message()
            return

    async def callback_query(self):
        try:
            data = self.event.data.decode("utf-8").split(':')
            if len(data) > 1:
                await getattr(self, data[0])(*data[1:])
            else:
                await getattr(self, data[0])()
        except Exception:
            stg.logger.exception('callback_query')
        finally:
            await self.event.answer()

    async def private_message(self):
        if not (self.user_db.is_editor or self.user_db.is_admin):
            await self.respond(msg.only_for_administrators)
            return

        if self.user_db.is_admin:

            if self.text == '/login':
                await self.respond(msg.enter_phone_number)
                self.user_db.flow = 'phone_number_request'
                await self.user_db.save()
                return

            if self.user_db.flow:
                if self.text == '/cancel':

                    self.user_db.flow = None
                    await self.user_db.save()
                    await self.respond(msg.you_canceled_login)

                if self.user_db.flow == 'phone_number_request':

                    result = re.findall(r'^\+\d{5,17}$', self.text)
                    if not result:
                        await self.respond(msg.failed_number)
                        return

                    try:
                        sent_code = await stg.client_user.send_code_request(self.text)
                    except Exception:
                        stg.logger.exception('sent_code')
                        await self.reconnect_client_user()
                        await self.respond(msg.failed_number)
                        return

                    self.user_db.flow = 'sent_auth_code'
                    stg.client_user_db.phone_number_entered = self.text
                    stg.client_user_db.phone_code_hash = sent_code.phone_code_hash
                    await self.user_db.save()
                    await stg.client_user_db.save()

                    await self.respond(msg.enter_confirmation_code)
                    return

                elif self.user_db.flow == 'sent_auth_code':
                    try:
                        await stg.client_user.sign_in(
                            phone=stg.client_user_db.phone_number_entered, code=self.text[5:],
                            phone_code_hash=stg.client_user_db.phone_code_hash)
                        await self.you_logged_in()

                    except PhoneCodeExpiredError:
                        stg.logger.exception('')

                        self.user_db.flow = None
                        await self.user_db.save()
                        await self.reconnect_client_user()

                        await self.respond(msg.confirmation_code_has_expired)

                    except PhoneCodeInvalidError:
                        stg.logger.exception('')
                        await self.reconnect_client_user()
                        await self.respond(msg.phone_code_invalid)
                        return

                    except SessionPasswordNeededError:
                        stg.logger.exception('')
                        self.user_db.flow = '2FA needed'
                        await self.user_db.save()
                        await self.respond(msg.enter_two_factor_authentication)
                        return

                elif self.user_db.flow == '2FA needed':
                    try:
                        await stg.client_user.sign_in(password=self.event.text)
                        await self.you_logged_in()

                        self.user_db.flow = None
                        await self.user_db.save()

                    except PhoneCodeExpiredError:
                        stg.logger.exception('')

                        self.user_db.flow = None
                        await self.user_db.save()
                        await self.reconnect_client_user()

                        await self.respond(msg.confirmation_code_has_expired)

                    except PasswordHashInvalidError:
                        stg.logger.exception('')
                        await self.respond(msg.password_entered_is_invalid)
                        return

        if self.user_db.flow:
            if self.user_db.flow == 'add_category':

                if not self.text:
                    await self.respond('Error! Enter the category name in words:')
                    return

                await Category(name=self.text).save()
                await self.categories_by_topics(edit=False)
                return

            if 'edit_category' in self.user_db.flow:
                if not self.text:
                    await self.respond('Error! Enter a new category name in words:')
                    return

                category_id = int(self.user_db.flow.split(':')[1])

                category_db = await Category.filter(id=category_id).first()
                category_db.name = self.text
                await category_db.save()
                await self.categories_by_topics(edit=False)
                return

            if 'enter_channel_to' in self.user_db.flow:
                channel_ent = await self.get_channel_entity(data='insert_channel')
                if not channel_ent:
                    return

                channel_to_id = get_peer_id(channel_ent, add_mark=True)
                category_id = int(self.user_db.flow.split(':')[1])

                await self.insert_channel_db(channel_to_id, channel_ent.title, channel_ent.username)

                self.user_db.flow = f'enter_channel_from:{category_id}:{channel_to_id}'
                await self.user_db.save()

                await self.respond(msg.enter_link_from_channel, buttons=btn.cancel_channel_insertion)
                return

            if 'enter_channel_from' in self.user_db.flow:
                channel_ent = await self.get_channel_entity(data='insert_channel')
                if not channel_ent:
                    return

                flow_args = self.user_db.flow.split(':')
                category_id, channel_to_id = int(flow_args[1]), int(flow_args[2])

                channel_from_id = get_peer_id(channel_ent, add_mark=True)

                check_transfer_channels = await self.check_transfer_channels(
                    channel_from_id, channel_to_id, data='insert_channel')
                if not check_transfer_channels:
                    return

                await self.insert_channel_db(channel_from_id, channel_ent.title, channel_ent.username)

                transfer_db = Transfer(
                    channel_from_id=channel_from_id, channel_to_id=channel_to_id,
                    category_id=category_id, is_working=True
                )
                await transfer_db.save()
                await self.insert_channel(edit=False, message='You have successfully created a transfer!')
                return

            if 'edit_transfer_from' in self.user_db.flow or 'edit_transfer_to' in self.user_db.flow:
                edit_channel_from = True if 'edit_transfer_from' in self.user_db.flow else False

                flow_args = self.user_db.flow.split(':')
                transfer_id = int(flow_args[1])
                transfer_db = await Transfer.filter(id=transfer_id).first()

                channel_ent = await self.get_channel_entity(data=f'category:{transfer_db.category_id}')
                if not channel_ent:
                    return

                channel_id = get_peer_id(channel_ent, add_mark=True)

                if edit_channel_from:
                    check_transfer_channels = await self.check_transfer_channels(
                        channel_id, transfer_db.channel_to_id, data=f'category:{transfer_db.category_id}')
                else:
                    check_transfer_channels = await self.check_transfer_channels(
                        transfer_db.channel_from_id, channel_id, data=f'category:{transfer_db.category_id}')
                if not check_transfer_channels:
                    return

                await self.insert_channel_db(channel_id, channel_ent.title, channel_ent.username)

                if edit_channel_from:
                    transfer_db.channel_from_id = channel_id
                else:
                    transfer_db.channel_to_id = channel_id
                await transfer_db.save()

                await self.category(
                    transfer_db.category_id, edit=False,
                    message='You have successfully changed your transfer!')
                return

        await self.menu(edit=False)

    async def menu(self, edit=True):
        await self.reset_flow()
        try:
            me = await stg.client_user.get_me()
            text = f'Account: {me.first_name}' + (f' {me.last_name}' if me.last_name else str())
        except Exception:
            text = 'Account not authorized'

        _menu = deepcopy(btn.menu)
        _menu.insert(0, [Button.inline(text, 'authorized_account')])

        if edit:
            await self.event.edit('Menu', buttons=_menu)
        else:
            await self.respond('Menu', buttons=_menu)

    async def insert_channel(self, edit=True, message=None):
        await self.reset_flow()

        categories_db = await Category.all()
        if not categories_db:
            await self.event.answer('First create a category using the "Categories by Topics" button.', alert=True)
            return

        buttons = list()
        ctg_number, columns = len(categories_db), 2

        for _ in range((ctg_number // columns) + 1):
            buttons.append(list())
            for category_db in categories_db[:columns]:
                buttons[_].append(Button.inline(category_db.name, f'insert_to_category:{category_db.id}'))
            categories_db = categories_db[columns:]

        buttons.append([Button.inline('« Back', f'menu')])

        if edit:
            await self.event.edit(msg.select_category_for_add_channels if not message else message, buttons=buttons)
        else:
            await self.respond(msg.select_category_for_add_channels if not message else message, buttons=buttons)

    async def insert_channel_db(self, channel_id, title, username):
        channel_db = await Channel.filter(id=channel_id).first()
        if not channel_db:
            channel_db = Channel(id=channel_id, title=title, username=username)
            await channel_db.save()

    async def delay(self):
        await self.reset_flow()
        await self.event.answer('The function is being developed.')

    async def system_updates(self):
        await self.reset_flow()
        await self.event.answer('The function is being developed.')

    async def categories_by_topics(self, edit=True):
        await self.reset_flow()

        buttons = list()
        async for category_db in Category.all():
            buttons.append(
                [Button.inline('❌', f'delete_category:{category_db.id}'),
                 Button.inline('✏️', f'edit_category:{category_db.id}'),
                 Button.inline(category_db.name, f'category:{category_db.id}')]
            )

        buttons.append([Button.inline('« Back', f'menu'), Button.inline('Add category', f'add_category')])

        if edit:
            await self.event.edit('Categories', buttons=buttons)
        else:
            await self.respond('Categories', buttons=buttons)

    async def category(self, category_id, edit=True, message=None):
        await self.reset_flow()

        category_db = await Category.filter(id=category_id).first()

        buttons = list()
        async for transfer_db in Transfer.filter(category_id=int(category_id)).all():
            await transfer_db.fetch_related('channel_from', 'channel_to')
            buttons.append(
                [Button.inline(f'{transfer_db.channel_from.title}', f'edit_transfer_from:{transfer_db.id}'),
                 Button.inline(f'{transfer_db.channel_to.title}', f'edit_transfer_to:{transfer_db.id}'),
                 Button.inline('🟢' if transfer_db.is_working else '🔴', f'edit_transfer_working:{transfer_db.id}')]
            )
        buttons.append([Button.inline('« Back', 'categories_by_topics')])

        text = f'{category_db.name}' + f' | {message}' if message else f'{category_db.name}'
        if edit:
            await self.event.edit(text, buttons=buttons)
        else:
            await self.respond(text, buttons=buttons)

    async def check_transfer_channels(self, channel_from_id, channel_to_id, data=str()):
        async def respond(text):
            buttons = [[Button.inline('« Cancel', data)]]
            await self.respond(text, buttons=buttons)

        transfer_db = await Transfer.filter(
            channel_from_id=channel_from_id, channel_to_id=channel_to_id).first()
        if transfer_db:
            await respond('Error! Such a transfer already exists. Enter another channel:')
            return False

        if channel_from_id == channel_to_id:
            await respond('Error! It cannot be the same channel. Enter another, correct channel:')
            return False
        return True

    async def add_category(self):
        self.user_db.flow = f'add_category'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', 'categories_by_topics')]]
        await self.event.edit('Enter a name for the new category:', buttons=buttons)

    async def edit_category(self, category_id):
        self.user_db.flow = f'edit_category:{category_id}'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', f'categories_by_topics')]]
        await self.event.edit('Enter a new category name:', buttons=buttons)

    async def delete_category(self, category_id, ask=True):
        transfers_db = await Transfer.filter(category_id=category_id).all()
        if transfers_db and ask:
            buttons = [[Button.inline('❌', f'categories_by_topics'),
                        Button.inline('✅', f'delete_category:{category_id}:')]]
            await self.event.edit(
                'The category contains transfers! Are you sure you want to delete it?', buttons=buttons)
            return

        category_db = await Category.filter(id=category_id).first()
        await category_db.delete()
        await self.event.answer('The category has been successfully deleted.')
        await self.categories_by_topics()
        return

    async def get_channel_entity(self, data=str()):
        try:
            channel_ent = await stg.client_bot.get_entity(self.text)
            assert isinstance(channel_ent, types.Channel)
            return channel_ent
        except Exception:
            await self.respond(
                msg.enter_correct_channel_link, buttons=[[Button.inline('« Cancel', data)]])
            return False

    async def edit_transfer_from(self, transfer_id):
        transfer_db = await Transfer.filter(id=transfer_id).first()
        if await self.check_transfer(transfer_db):
            return

        self.user_db.flow = f'edit_transfer_from:{transfer_id}'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', f'category:{transfer_db.category_id}')]]
        await self.event.edit(msg.enter_new_link_from_channel, buttons=buttons)

    async def edit_transfer_to(self, transfer_id):
        transfer_db = await Transfer.filter(id=transfer_id).first()
        if await self.check_transfer(transfer_db):
            return

        self.user_db.flow = f'edit_transfer_to:{transfer_id}'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', f'category:{transfer_db.category_id}')]]
        await self.event.edit(msg.enter_new_link_from_channel, buttons=buttons)

    async def edit_transfer_working(self, transfer_id):
        transfer_db = await Transfer.filter(id=transfer_id).first()
        if await self.check_transfer(transfer_db):
            return

        if transfer_db.is_working:
            transfer_db.is_working = False
        else:
            transfer_db.is_working = True
        await transfer_db.save()
        await self.category(transfer_db.category_id)

    async def insert_to_category(self, category_id):
        self.user_db.flow = f'enter_channel_to:{category_id}'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', f'insert_channel')]]

        await self.event.edit(msg.enter_link_to_channel, buttons=buttons)

    async def authorized_account(self):
        if self.user_db.is_editor:
            await self.event.answer(msg.only_admins_can_change_account)
        elif self.user_db.is_admin:
            await self.event.answer(msg.authorize_new_account_request, alert=True)

    async def check_transfer(self, transfer_db):
        if not transfer_db:
            await self.event.answer('This transfer no longer exists.')
            await self.categories_by_topics()
            return True

    async def check_user(self):
        self.user_db = await User.filter(id=self.user_id).first()

        if self.user_db:
            await self.update_user()
        else:
            self.user_db = User(
                id=self.user_id, first_name=self.user.first_name,
                last_name=self.user.last_name, username=self.user.username)
            await self.user_db.save()

    async def update_user(self):
        changed = False

        if self.user_db.first_name != self.user.first_name:
            changed = True
            self.user_db.first_name = self.user.first_name

        if self.user_db.last_name != self.user.last_name:
            changed = True
            self.user_db.last_name = self.user.last_name

        if self.user_db.username != self.user.username:
            changed = True
            self.user_db.username = self.user.username

        if changed:
            await self.user_db.save()

    async def reconnect_client_user(self):
        await stg.client_user.disconnect()
        await stg.client_user.connect()

    async def reset_flow(self):
        if self.user_db.flow:
            self.user_db.flow = None
            await self.user_db.save()

    async def you_logged_in(self):
        self.user_db.flow = None
        stg.client_user_db.phone_number = stg.client_user_db.phone_number_entered
        stg.client_user_db.phone_number_entered = None
        stg.client_user_db.phone_code_hash = None

        await self.user_db.save()
        await stg.client_user_db.save()

        await self.respond(msg.you_logged_in)

    async def respond(self, *args, silent=False, **kwargs):
        await self.event.respond(*args, silent=silent, **kwargs)
