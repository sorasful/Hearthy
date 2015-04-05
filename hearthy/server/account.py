from hearthy.server.collection import Collection
from hearthy.server.account_options import AccountOptions
from hearthy.server.deck import Deck
from hearthy.server.util import get_timestamp

class Account:
    def __init__(self, db, uuid):
        """
        Args:
           db: database
           uuid (uuid.UUID): UUID of the account
        """
        self.db = db
        self.uuid = uuid

        self.prefix = ['accounts', str(uuid)]

        self.account_options = AccountOptions(self.db, self.prefix + ['options'])

    @property
    def options(self):
        return self.account_options

    @property
    def balances(self):
        return self.db[self.prefix + ['balances']]

    @property
    def collection(self):
        return Collection(db=self.db, account=self)

    @property
    def decks(self):
        decks = []
        for dbkey in self.db.prefix_query(self.prefix + ['decks'], False):
            decks.append(Deck(self.db, self, dbkey[-1]))
        return decks

    def get_deck(self, deck_id):
        return Deck(self.db, self, str(deck_id))

    def delete_deck(self, deck_id):
        del self.db[self.prefix + ['decks', str(deck_id)]]

    def set_deck_contents(self, deck_id, card_list):
        key = self.prefix + ['decks', str(deck_id)]
        doc = self.db[key]

        doc['cards'] = card_list

        self.db[key] = doc

    def create_deck(self, deck_name, hero_id):
        ts = get_timestamp()
        deck_id = ts
        deck_id_str = str(deck_id)

        new_deck = {
            'deck_id': deck_id,
            'hero_id': hero_id,
            'cards': [],
            'name': deck_name,
            'ctime': ts
        }

        self.db[self.prefix + ['decks', deck_id_str]] = new_deck
        return new_deck

    @property
    def crafting_cost(self):
        doc = self.db[['crafting_cost']]
        return doc
