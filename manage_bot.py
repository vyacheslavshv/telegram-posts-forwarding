import datetime

import utils
import messages as msg
import re
import settings as stg
import buttons as btn

from tables import User, Category, Transfer, Channel, StopWord , SummeryInfo

from telethon.errors import \
    PhoneCodeExpiredError, PasswordHashInvalidError, \
    PhoneCodeInvalidError, UserAlreadyParticipantError, FloodWaitError, \
    ChannelsTooMuchError, InviteHashEmptyError, InviteHashExpiredError, InviteHashInvalidError, \
    SessionPasswordNeededError, UsersTooMuchError, ChannelInvalidError, ChannelPrivateError
from telethon.utils import get_peer_id
from telethon.tl import types
from telethon.tl.custom import Button
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from copy import deepcopy
from tortoise.expressions import Q
from datetime import datetime, timedelta


class ManageBot:

    def __init__(self, event):
        self.event = event

        self.chat_db = None
        self.user_db = None

        self.user_id = utils.get_user_id(event)

        try:
            self.text = self.event.text
        except AttributeError:
            self.text = None

    async def init_(self):
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
        if not await self.check_authorization():
            return
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
        if not await self.check_authorization():
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

            if 'insert_to_summery'in self.user_db.flow:
                channel_ent = await self.get_channel_entity(data='insert_channel')
                if not channel_ent:
                    await self.respond('Error! Cant find channel entity..')
                    return
                else:
                    channel_to_id = get_peer_id(channel_ent, add_mark=True)
                    await self.insert_summery_db(channel_to_id, channel_ent.title, channel_ent.username)
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

            if 'add_admin' in self.user_db.flow:
                buttons = [[Button.inline('« Back', 'admins_list')]]
                flow_args = self.user_db.flow.split(':')
                admin = True if len(flow_args) > 1 else False

                try:
                    user_ent = await stg.client_bot.get_entity(self.text)
                    assert isinstance(user_ent, types.User)
                except FloodWaitError as e:
                    await self.respond(f'Error! Wait {e.seconds} second(s) and try again.', buttons=buttons)
                    return False
                except Exception:
                    stg.logger.exception('add_admin')
                    await self.respond('Error! Enter the correct user link:', buttons=buttons)
                    return False

                user_db = await self.check_new_user(user_ent)
                if admin:
                    user_db.is_admin = True
                else:
                    user_db.is_editor = True
                await user_db.save()

                text = 'You have successfully added the user as ' + ('administrator.' if admin else 'editor.')
                await self.admins_list(text, edit=False)
                return

            if 'add_stop_word' in self.user_db.flow:
                buttons = [[Button.inline('« Back', 'stop_words')]]
                try:
                    stop_word_db = await StopWord.filter(word=self.text).first()
                    if stop_word_db:
                        await self.respond('Such a stop word already exists. Enter another:', buttons=buttons)
                        return
                    if len(self.text) > 100:
                        await self.respond(msg.more_than_100_char_stop_word, buttons=buttons)
                        return
                    stop_word_db = StopWord(word=self.text)
                    await stop_word_db.save()

                except Exception:
                    stg.logger.exception('')
                    await self.respond('Error saving stop word. Enter another:', buttons=buttons)
                    return

                await self.stop_words(edit=False, message='The stop word was saved successfully.')
                return

        await self.menu(edit=False)

    async def admins_list(self, text=str(), edit=True):
        await self.reset_flow()

        admins = await User.filter(Q(is_admin=True) | Q(is_editor=True)).all()

        buttons = list()
        for admin in admins:
            fullname = admin.first_name + (f' {admin.last_name}' if admin.last_name else '') + \
                       (' (admin)' if admin.is_admin else ' (editor)')
            button = Button.url(fullname, f't.me/{admin.username}') if admin.username else Button.inline(fullname, '')
            buttons.append([button, Button.inline('❌', f'delete_admin:{admin.id}')])

        buttons.append([Button.inline('Add admin', 'add_admin:True'), Button.inline('Add editor', 'add_admin')])
        buttons.append([Button.inline('« Back', 'menu')])

        if edit:
            await self.event.edit('Admins' if not text else text, buttons=buttons)
        else:
            await self.respond('Admins' if not text else text, buttons=buttons)

    async def add_admin(self, admin=False):
        self.user_db.flow = 'add_admin:True' if admin else 'add_admin'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', 'admins_list')]]
        await self.event.edit(
            'Enter a link to the user.' + msg.user_links_examples, buttons=buttons, link_preview=False)

    async def delete_admin(self, user_id, delete=False):
        if int(user_id) == self.user_id:
            await self.event.answer('You cannot delete yourself.')
            return

        if not delete:
            buttons = [[Button.inline('No', 'admins_list'), Button.inline('Yes', f'delete_admin:{user_id}:{True}')]]
            await self.event.edit('Are you sure you want to remove this administrator?', buttons=buttons)
            return

        user_db = await User.filter(id=user_id).first()
        user_db.is_admin = False
        user_db.is_editor = False
        await user_db.save()

        await self.event.answer('You have successfully removed the administrator.')
        await self.admins_list()

    async def menu(self, edit=True):
        await self.reset_flow()
        try:
            me = await stg.client_user.get_me()
            text = f'{me.first_name}' + (f' {me.last_name}' if me.last_name else str())
        except Exception:
            text = 'Account not authorized'

        _menu = deepcopy(btn.menu)
        buttons = [Button.inline(text, 'authorized_account')]
        _menu.insert(0, buttons)

        buttons = [Button.inline('Stop words', 'stop_words')]
        if self.user_db.is_admin:
            buttons.append(Button.inline('Admins', 'admins_list'))
        _menu.insert(1, buttons)

        await self.event.edit('Menu', buttons=_menu) if edit else await self.respond('Menu', buttons=_menu)

    async def insert_channel(self, edit=True, message=None):
        await self.reset_flow()

        if edit and not await self.check_authentication():
            await self.event.answer(msg.account_not_authorized)
            return

        categories_db = await Category.all()
        if edit and not categories_db:
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

    async def info_channel(self):
        self.user_db.flow = f'insert_to_summery'
        await self.user_db.save()
        try:
            summary_db = await SummeryInfo.all()
            if summary_db:
                for sum_db in summary_db:
                    buttons = [[Button.inline(f'Channel Exist: {sum_db.title}', f'menu')],[Button.inline('« Back', f'menu')]]
            else:
                buttons = [[Button.inline('« Back', f'menu')]]
        except Exception as e:
            stg.logger.error(f"[info_channel] Exception:{e}")
            buttons = [[Button.inline('« Back', f'menu')]]
            pass
        await self.event.edit("Enter summery channel", buttons=buttons)

    async def insert_summery_db(self,channel_id,title,username):
        summary_db = await SummeryInfo.filter(summary_channel=channel_id).first()
        if not summary_db:
            # date = datetime.now() + timedelta(hours=24)
            date = datetime.today()
            summary_db = SummeryInfo(summary_channel=channel_id, last_update = date, title = title , username = username)
            try:
                await summary_db.save()
                await self.respond("Summary Channel Added!")
            except Exception as e:
                stg.logger.error(f"[insert_summery_db] Exception1:{e}")
        else:
            summary_db.summary_channel = channel_id
            summary_db.title = title
            summary_db.username = username
            try:
                await summary_db.save()
                await self.respond("Summary Channel updated!")
            except Exception as e:
                stg.logger.error(f"[insert_summery_db] Exception2:{e}")
            
        return

    # async def delay(self):
    #     await self.reset_flow()
    #     await self.event.answer('The function is being developed.')

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

    async def approve_post(self, _message_id, _channel_to_id):
        try:
            message_id, channel_to_id = int(_message_id), int(_channel_to_id)
            await stg.client_user.send_message(channel_to_id, stg.event_messages[message_id])
            await self.event.delete()
            await stg.client_user.delete_messages(stg.problematic_channel, message_ids=message_id)
            del stg.event_messages[message_id]
        except FloodWaitError as e:
            stg.user_flood_wait = datetime.now() + timedelta(seconds=e.seconds)
        except KeyError:
            await self.event.answer(
                'Unfortunately, this post cannot be used because the bot has been reloaded.', alert=True)
        except Exception as e:
            stg.logger.exception('forward_message')
            await self.event.answer(
                'An error has occurred. You may not have permissions to send a message to the channel. '
                'Or an error deleting current messages.', alert=True)

    async def reject_post(self, _message_id):
        message_id = int(_message_id)
        await self.event.delete()
        await stg.client_user.delete_messages(stg.problematic_channel, message_ids=message_id)
        del stg.event_messages[message_id]

    async def category(self, category_id, _page=0, edit=True, message=None):
        await self.reset_flow()

        page = int(_page)
        index_by_page = page * stg.TRANSFERS_PER_PAGE
        transfers = await Transfer.filter(
            category_id=int(category_id)).prefetch_related('channel_from', 'channel_to').all()

        transfers_number = len(transfers[index_by_page:])
        transfers = transfers[index_by_page:index_by_page + stg.TRANSFERS_PER_PAGE]
        current_transfers_number = len(transfers)

        buttons = list()
        for row in range(current_transfers_number):
            transfer = transfers[row]
            buttons.append(
                [Button.inline(f'{transfer.channel_from.title}', f'edit_transfer_from:{transfer.id}'),
                 Button.inline(f'{transfer.channel_to.title}', f'edit_transfer_to:{transfer.id}'),
                 Button.inline('🟢' if transfer.is_working else '🔴', f'edit_transfer_working:{transfer.id}'),
                 Button.inline('⚠️' if transfer.channel_from.manual else '🏧',
                               f'edit_channel_working_type:{transfer.channel_from.id}:{category_id}:{_page}')])

        back = False
        current_page_button = Button.inline(f'{page + 1}', '')

        if page > 0:
            buttons.append([Button.inline(f'« {page}', f'category:{category_id}:{page - 1}'), current_page_button])
            back = True

        if transfers_number > stg.TRANSFERS_PER_PAGE:
            button = Button.inline(f'{page + 2} »', f'category:{category_id}:{page + 1}')
            buttons[-1].append(button) if back else buttons.append([button]) \
                if page != 0 else buttons.append([current_page_button, button])

        buttons.append([Button.inline('« Back', 'categories_by_topics')])

        category_db = await Category.filter(id=category_id).first()
        text = f'{category_db.name}' + f' | {message}' if message else f'{category_db.name}'

        await self.event.edit(text, buttons=buttons) if edit else await self.respond(text, buttons=buttons)

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

    async def check_authorization(self):
        if not (self.user_db.is_editor or self.user_db.is_admin):
            await self.respond(msg.only_for_administrators)
            return False
        return True

    async def check_authentication(self):
        try:
            await stg.client_user.get_me()
            return True
        except Exception:
            return False

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

        for transfer_db in transfers_db:
            if transfer_db.channel_to_id in stg.stopped_channels:
                del stg.stopped_channels[transfer_db.channel_to_id]

        category_db = await Category.filter(id=category_id).first()
        await category_db.delete()
        await self.event.answer('The category has been successfully deleted.')
        await self.categories_by_topics()
        return

    async def get_channel_entity(self, data=str()):
        button_cancel = [[Button.inline('« Cancel', data)]]
        try:
            check_link = re.findall(msg.link_join_chat, self.text)
            if check_link:
                try:
                    await stg.client_user(ImportChatInviteRequest(check_link[0]))
                except UserAlreadyParticipantError:
                    pass

            channel_ent = await stg.client_user.get_entity(self.text.replace('+', 'joinchat/'))
            assert isinstance(channel_ent, types.Channel)

            if not check_link:
                await stg.client_user(JoinChannelRequest(channel_ent))

        except FloodWaitError as e:
            await self.respond(
                f'Add channel too often. Wait {e.seconds} second(s) and try again.', buttons=button_cancel)
            return False
        except ChannelsTooMuchError:
            await self.respond(f'You have joined too many channels/supergroups.', buttons=button_cancel)
            return False
        except ChannelInvalidError:
            await self.respond(
                f'Invalid channel object. Make sure to pass the right types, '
                f'for instance making sure that the request is designed for channels '
                f'or otherwise look for a different one more suited.',
                buttons=button_cancel)
            return False
        except ChannelPrivateError:
            await self.respond(
                f'The channel specified is private and you lack permission to access it. '
                f'Another reason may be that you were banned from it.',
                buttons=button_cancel)
            return False
        except InviteHashEmptyError:
            await self.respond(f'The invite hash is empty.', buttons=button_cancel)
            return False
        except InviteHashExpiredError:
            await self.respond(
                f'The chat you tried to join has expired and is not valid anymore.', buttons=button_cancel)
            return False
        except InviteHashInvalidError:
            await self.respond(f'The invite hash is invalid.', buttons=button_cancel)
            return False
        except SessionPasswordNeededError:
            await self.respond(
                f'Two-steps verification is enabled and a password is required.', buttons=button_cancel)
            return False
        except UsersTooMuchError:
            await self.respond(
                f'The maximum number of users has been exceeded (to create a chat, for example).',
                buttons=button_cancel)
            return False
        except Exception:
            stg.logger.exception('get_channel_entity')
            await self.respond(msg.enter_correct_channel_link, buttons=button_cancel)
            return False

        return channel_ent

    async def edit_transfer_from(self, transfer_id):
        transfer_db = await Transfer.filter(id=transfer_id).first()
        if await self.check_transfer(transfer_db):
            return

        if not await self.check_authentication():
            await self.event.answer(msg.account_not_authorized)
            return

        self.user_db.flow = f'edit_transfer_from:{transfer_id}'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', f'category:{transfer_db.category_id}')]]
        await self.event.edit(msg.enter_new_link_from_channel, buttons=buttons)

    async def edit_transfer_to(self, transfer_id):
        transfer_db = await Transfer.filter(id=transfer_id).first()
        if await self.check_transfer(transfer_db):
            return

        if not await self.check_authentication():
            await self.event.answer(msg.account_not_authorized)
            return

        self.user_db.flow = f'edit_transfer_to:{transfer_id}'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', f'category:{transfer_db.category_id}')]]
        await self.event.edit(msg.enter_new_link_to_channel, buttons=buttons)

    async def edit_transfer_working(self, transfer_id):
        transfer_db = await Transfer.filter(id=transfer_id).first()
        if await self.check_transfer(transfer_db):
            return

        if transfer_db.is_working:
            transfer_db.is_working = False
            if transfer_db.channel_to_id in stg.stopped_channels:
                del stg.stopped_channels[transfer_db.channel_to_id]
        else:
            transfer_db.is_working = True
        await transfer_db.save()
        await self.category(transfer_db.category_id)

    async def edit_channel_working_type(self, channel_id, category_id, page):
        channel_db = await Channel.filter(id=channel_id).first()
        if not channel_db:
            await self.category(category_id, page)
            return

        channel_db.manual = False if channel_db.manual else True
        await channel_db.save()

        await self.category(category_id, page)

    async def delete_stop_word(self, stop_word_id, page=0):
        stop_word_db = await StopWord.filter(id=stop_word_id).first()
        if not stop_word_db:
            await self.event.answer('The stop word has already been removed.')
        else:
            await stop_word_db.delete()
            await self.event.answer('Stop word removed.')
        await self.stop_words(_page=page)

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

    async def add_stop_word(self):
        self.user_db.flow = f'add_stop_word'
        await self.user_db.save()

        buttons = [[Button.inline('« Back', 'stop_words')]]
        await self.event.edit('Enter a stop word up to 100 characters:', buttons=buttons)

    async def stop_words(self, _page=0, edit=True, message=str()):
        await self.reset_flow()
        page = int(_page)
        index_by_page = page * stg.STOP_WORDS_PER_PAGE
        stop_words = await StopWord.all()

        stop_words_number = len(stop_words[index_by_page:])
        stop_words = stop_words[index_by_page:index_by_page + stg.STOP_WORDS_PER_PAGE]
        current_stop_words_number = len(stop_words)

        buttons = [[]]
        for row in range(current_stop_words_number):
            button = Button.inline(f'{stop_words[row].word}', f'delete_stop_word:{stop_words[row].id}:{page}')
            if len(buttons[-1]) == 2:
                buttons.append(list())
            buttons[-1].append(button)

        back = False
        current_page_button = Button.inline(f'{page + 1}', '')

        if page > 0:
            buttons.append([Button.inline(f'« {page}', f'stop_words:{page - 1}'), current_page_button])
            back = True

        if stop_words_number > stg.STOP_WORDS_PER_PAGE:
            button = Button.inline(f'{page + 2} »', f'stop_words:{page + 1}')
            buttons[-1].append(button) if back else buttons.append([button]) \
                if page != 0 else buttons.append([current_page_button, button])

        text = 'Added stop words. Click on the stop word to delete it:' if not message else message
        buttons.append([Button.inline('« Back', 'menu'), Button.inline('Add stop word', 'add_stop_word')])
        if edit:
            await self.event.edit(text, buttons=buttons)
        else:
            await self.respond(text, buttons=buttons)

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

    async def check_new_user(self, user_ent):
        user_db = await User.filter(id=user_ent.id).first()
        if not user_db:
            user_db = User(
                id=user_ent.id, first_name=user_ent.first_name,
                last_name=user_ent.last_name, username=user_ent.username)
            await user_db.save()
        return user_db

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

    async def system_updates(self):
        try:
            me = await stg.client_user.get_me()
            text = f'Account "{me.first_name}' + (f' {me.last_name}"' if me.last_name else '"') + ' authorized.\n\n'
        except Exception:
            await self.event.answer('Account not authorized or banned!\n\n')
            return

        if stg.user_flood_wait:
            now = datetime.datetime.now()
            if stg.user_flood_wait > now:
                delta = stg.user_flood_wait - now
                text += f'The account is in flood, it remains to wait: {delta.seconds} seconds.\n\n'

        if stg.stopped_channels:
            stopped_text = 'Not working channels:\n'
            for n, channel_id in enumerate(
                    sorted(stg.stopped_channels, key=lambda x: stg.stopped_channels[x][0]), start=1):
                stopped_text += f'{n}. {stg.stopped_channels[channel_id][0]}' + \
                                f' (@{stg.stopped_channels[channel_id][1]})\n' \
                    if stg.stopped_channels[channel_id][1] else str()
            text += stopped_text

        await self.event.edit(text, buttons=[[Button.inline('« Back', data='menu')]])

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
