from flask.ext.login import *


class User(UserMixin):
    def __init__(self, email, _id, active=True):
            self.email = email
            self._id = _id
            self.active = active

    def get_id(self):
        return str(self._id).decode('utf-8')
