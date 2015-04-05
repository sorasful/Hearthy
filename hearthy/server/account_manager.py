import uuid
import time

from hearthy.server.account import Account

ACCOUNT_SKELETON = 'account_skeleton'
ACCOUNT_EMAILS = 'emails'

def get_timestamp():
    """Returns the number of milliseconds since January 1, 1970 UTC"""
    return int(time.time())

class AccountManager:
    def __init__(self, db):
        self.db = db

    def create_account(self, email):
        """ Creates a new account

        Args:
           email (str): The e-mail address

        Returns:
           Account: The new account
        """
        new_uuid = uuid.uuid4()
        now = get_timestamp()

        # copy skeleton structure
        self.db.prefix_copy(
            [ACCOUNT_SKELETON],
            ['accounts', str(new_uuid)])

        # associat email with account
        self.db[[ACCOUNT_EMAILS,email]] = {
            'account_id': str(new_uuid),
            'mtime': now,
            'ctime': now
        }

        return Account(db=self.db, uuid=new_uuid)

    def find_by_email(self, email):
        """Finds the account associated with the given email address

        Args:
           email (str): The e-mail address

        Returns:
           Account: The found account
        """
        doc = self.db[[ACCOUNT_EMAILS, email]]

        account_uuid = uuid.UUID(doc['account_id'])
        return Account(db=self.db, uuid=account_uuid)
