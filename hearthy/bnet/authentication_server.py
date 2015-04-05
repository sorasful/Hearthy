import uuid
from hearthy.bnet import rpcdef
from hearthy.protocol import mtypes

class InsecureAuthenticationServer(rpcdef.AuthenticationServer.Server):
    """Authentication based solely on the clients e-mail address.

    This implementation is considered insecure as it does not verify in any way
    that the client is in control of the given e-mail address. The usage
    of this implementation should be limited to testing or developement purposes.
    """
    def __init__(self, client_handler, auth_client, account_manager):
        super().__init__()
        self._auth_client = auth_client
        self._account_manager = account_manager
        self._client_handler = client_handler

    def Logon(self, req):
        # The client appears to get confused when the RPC calls completes
        # after the LogonComplete message - therefore we yield the response
        # first which will cause the rpc implementation to queue the response
        # packet immediately.
        yield mtypes.BnetNoData()

        # TODO: do we even need to send LogonQueueUpdate and LogonQueueEnd?
        self._auth_client.LogonQueueUpdate(
              Position=1,
              EstimatedTime=9223372036854775807,
              EtaDeviationInSec=0)
        self._auth_client.LogonQueueEnd()

        # TODO: do we need to send LogonUpdate?
        self._auth_client.LogonUpdate(error_code=0)

        account = self._account_manager.find_by_email(req.email)

        self._client_handler.account = account

        uuid_int = account.uuid.int

        self._auth_client.LogonComplete(
            error_code=0,
            account=mtypes.EntityId(high=0xdead, low=0xbeef),
            game_account=[mtypes.EntityId(
                high = uuid_int >> 64,
                low  = uuid_int & 0xFFFFFFFFFFFFFFFF
            )],
            email=req.email,
            available_region=[0],
            connected_region=0,
            battle_tag='bt',
            geoip_country='country')
