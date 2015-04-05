import pytest
from hearthy.server.memorydb import MemoryDb
from hearthy.server import dbutil
from hearthy.server.account_manager import AccountManager

@pytest.fixture
def new_acc():
    db = MemoryDb()
    dbutil.initialize_db(db)
    am = AccountManager(db)
    return am.create_account('test@domain.invalid')

def test_create_deck(new_acc):
    deck_name = 'furious racoon'
    hero_id = 31

    new_deck = new_acc.create_deck(deck_name, hero_id)
    assert new_deck['name'] == deck_name
    assert new_deck['hero_id'] == hero_id

def test_deck_list(new_acc):
    initial_deck_list = list(new_acc.decks)
    assert len(initial_deck_list) == 0

    new_acc.create_deck('test', 123)

    after_deck_list = list(new_acc.decks)
    assert len(after_deck_list) == 1

    assert after_deck_list[0].name == 'test'
    assert after_deck_list[0].hero_id == 123

if __name__ == '__main__':
    pytest.main()
