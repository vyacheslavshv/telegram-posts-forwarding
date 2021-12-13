import re

enter_phone_number = """
Reply only your phone number including area code and country code. No spaces, periods or dashes. Include a leading "+". Like this: +17771112222
"""

enter_confirmation_code = """
Great, we sent the code to your phone!

- Check your telegram inbox. Telegram sent you a 5 digit code.
- If Telegram hasn't sent you anything in the messenger, then check your regular messages on your phone.
- Reply to me with your code like this (no space): /code99999
"""

enter_two_factor_authentication = 'Enter your two-factor authentication password:'

you_logged_in = 'Great, you are logged in!'

authorize_new_account_request = 'To authorize a new account, enter the "/login" command.'

links_examples = """

For example:
- https://t.me/channel
- t.me/channel
- @channel
"""

user_links_examples = """

For example:
- https://t.me/username
- t.me/username
- @username
"""

enter_link_to_channel = 'Enter the link of our channel to which publications will be translated.' + links_examples
enter_link_from_channel = 'Excellent! Now enter the link of channel from which we will transfer the publications.' + links_examples

enter_new_link_to_channel = 'Enter the new link of our channel to which publications will be translated.' + links_examples
enter_new_link_from_channel = 'Enter the new link of channel from which we will transfer the publications.' + links_examples

select_category_for_add_channels = 'Select the category for which you want to add channels.'

# =============================================

you_canceled_login = 'You canceled login'

failed_number = """
Hmm your number failed on my end. Can you confirm the following?:

1. Click on your Telegram settings > profile pic at top, copy the phone number shown.
2. Paste the entire phone number in a new comment below.
3. Ensure you include "+" with your country code.
4. Remove all spaces, all periods.
5. Post one clean comment like this: +17782742525
"""

confirmation_code_has_expired = "The confirmation code has expired. Authenticate again: /login"

phone_code_invalid = """
Oops, that didn't work.

- Check that code again.
- Reply to me with your code like this (no space): /code99999
- To get the code again, enter the "/cancel" and "/login" commands in sequence.
"""

password_entered_is_invalid = """
The password you entered is invalid. Enter your password again. To start authentication again, enter the "/cancel" and "/login" commands in sequence.
"""

only_for_administrators = """
The bot functionality is available only for editors and administrators. 
Contact @Yaronlondon12 to update your status.
"""

only_admins_can_change_account = "Only administrators can change an account."

enter_correct_channel_link = """
Error! Enter the correct channel link.

For example:
- https://t.me/channel
- t.me/channel
- @channel
"""

you_cannot_join_private_channel = """
You cannot join a private channel. Find out what the reason is (maybe you are banned or the link is out of date). 

You must join to add or change a channel. Enter the link again or enter another channel link:
"""

account_not_authorized = "Error! First, authorize your account."

more_than_100_char_stop_word = "You have entered more than 100 characters. Enter a stop word up to 100 characters:"

link_join_chat = re.compile(r'(?:joinchat\/|\+)(\w+)')
