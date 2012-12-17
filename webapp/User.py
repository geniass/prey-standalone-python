from flask.ext.login import *


class User(UserMixin):
    def __init__(self, name, id, active=True):
            self.name = name
            self.id = id
            self.active = active




