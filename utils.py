from collections import OrderedDict


class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop("size_limit", None)
        OrderedDict.__init__(self, *args, **kwargs)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


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