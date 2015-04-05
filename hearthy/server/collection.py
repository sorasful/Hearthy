from hearthy.server.util import get_timestamp

class Collection:
    KEY = 'collection'

    def __init__(self, account, db):
        self.db = db
        self.account = account
        self.prefix = account.prefix + [self.KEY]

        self.refresh()

    def refresh(self):
        self.data = self.db[self.prefix]

    @property
    def cards(self):
        return self.db[self.prefix]
