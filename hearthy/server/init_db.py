from hearthy.server.filedb import FileDb
from hearthy.server.account_manager import AccountManager
from hearthy.server.dbutil import initialize_db

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) != 2:
        print('Usage: {0} <dbdir>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        os.makedirs(sys.argv[1])
    
    tmpdir = os.path.join(sys.argv[1], 'tmp')
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    db = FileDb(sys.argv[1])
    initialize_db(db)

    am = AccountManager(db)
    am.create_account('waifu@blizzard.com')
