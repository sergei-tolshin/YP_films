from datetime import datetime


class SerializedMessage:
    def __init__(self, text, user_id, from_user, timestamp=None,
                 session_id=None, **kwargs):
        self.text = text
        self.user_id = user_id
        self.from_user = from_user
        self.timestamp = timestamp or str(datetime.utcnow())
        self.session_id = session_id
        self.kwargs = kwargs

    def to_dict(self):
        result = {
            'text': self.text,
            'user_id': self.user_id,
            'from_user': self.from_user,
            'timestamp': self.timestamp,
            'session_id': self.session_id,
        }
        for k, v in self.kwargs.items():
            if k not in result:
                result[k] = v
        return result
