class Deck:
    def __init__(self, db, account, deck_id):
        self.db = db
        self.account = account
        self.deck_id = deck_id
        self.is_loaded = False
        self.data = None

    def save(self):
        self.db[self.account.prefix + ['decks', self.deck_id]] = self.data

    @property
    def id(self):
        return int(self.deck_id)

    @property
    def cards(self):
        self.load()
        return self.data['cards']

    @property
    def name(self):
        self.load()
        return self.data['name']

    @name.setter
    def name(self, name):
        self.load()
        self.data['name'] = name

    @property
    def hero_id(self):
        self.load()
        return self.data['hero_id']

    def load(self):
        if not self.is_loaded:
            self.data = self.db[self.account.prefix + ['decks', self.deck_id]]
            self.is_loaded = True
