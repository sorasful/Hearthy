import pytest
from hearthy.bnet.account_info import AccountInfo
from hearthy.server import dbutil
from hearthy.server.account_manager import AccountManager
from hearthy.server.memorydb import MemoryDb
from hearthy.proto import PegasusUtil_pb2

TEST_EMAIL = 'test@domain.invalid'

@pytest.fixture
def new_acc():
    db = MemoryDb()
    dbutil.initialize_db(db)
    am = AccountManager(db)
    return am.create_account(TEST_EMAIL)

def test_initial_gold_balance(new_acc):
    acc = AccountInfo(new_acc)
    response = acc.handle(PegasusUtil_pb2.GetAccountInfo.GOLD_BALANCE)

    assert isinstance(response, PegasusUtil_pb2.GoldBalance)
    assert response.capped_balance == 0

def test_initial_arcane_dust_balance(new_acc):
    acc = AccountInfo(new_acc)
    response = acc.handle(PegasusUtil_pb2.GetAccountInfo.ARCANE_DUST_BALANCE)

    assert isinstance(response, PegasusUtil_pb2.ArcaneDustBalance)
    assert response.balance == 0

if __name__ == '__main__':
    pytest.main()
