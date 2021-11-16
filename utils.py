def get_user_id(event):
    try:
        return event.sender_id
    except AttributeError:
        if event.user_id:
            return event.user_id
        else:
            try:
                return event.action_message.from_id.user_id
            except Exception:
                return None