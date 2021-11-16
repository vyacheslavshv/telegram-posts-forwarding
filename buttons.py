from telethon.tl.custom import Button


menu = [
    [Button.inline('Insertion channels', 'insert_channel'),
     Button.inline('Delay', 'delay')],
    [Button.inline('System updates', 'system_updates'),
     Button.inline('Categories by Topics', 'categories_by_topics')]]

cancel_channel_insertion = [[Button.inline('« Cancel', 'insert_channel')]]
