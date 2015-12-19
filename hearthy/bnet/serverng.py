import logging
import time
from hearthy.protocol import mtypes, pegasus_util, pegasus_shared, account
from hearthy.bnet import rpcdef, rpc, utils
from hearthy.proxy import pipe
from hearthy.bnet.splitter_buf import SplitterBuf
from hearthy.protocol.utils import hexdump
from hearthy.bnet.game_utilities_server import GameUtilitiesServer
from hearthy.bnet.game_master_server import GameMasterServer
from hearthy.bnet.authentication_server import InsecureAuthenticationServer
from hearthy.server.filedb import FileDb
from hearthy.server.account_manager import AccountManager

EPOCH = 0xAFFE
SERVER_ID = mtypes.BnetProcessId(Label=0xABCD, Epoch=EPOCH)
CLIENT_ID = mtypes.BnetProcessId(Label=0xB0FF, Epoch=EPOCH)

class DummyServer(rpc.ServiceServer):
    def __init__(self, hval):
        super().__init__()
        self.service = rpc.Service('dummy')
        self.service.hval = hval

    def _handle_packet(self, header, body):
        self.logger.warn('Ignoring packet for unknown service with hash 0x%08x. Header %s', self.service.hval, header)

class ConnectService(rpcdef.ConnectService.Server):
    def __init__(self):
        super().__init__()

    def Connect(self, req):
        import_id = []
        for i, hval in enumerate(req.BindRequest.ImportedServiceHash):
            try:
                server = self.broker.get_export_by_hash(hval)
            except KeyError:
                self.logger.warn('Client requested import of non-exported service with hash 0x%08x', hval)
                server = self.broker.add_export(DummyServer(hval))

            self.logger.info('Client imported %r with id %d', server.service, server.id)
            import_id.append(server.id)

        for item in req.BindRequest.ExportedService:
            imported_service = self.broker._imported_services.get(item.Hash, None)
            if imported_service is None:
                self.logger.warn('Ignoring client export with hash 0x%08x', item.Hash)
            else:
                self.logger.debug('Binding %r to id %s', imported_service, item.Id)
                imported_service.id = item.Id

        # TODO: check that all imported services have been bound

        # Send bind response
        bind_response = mtypes.BnetBindResponse(ImportedServices=import_id)

        resp = mtypes.BnetConnectResponse(
            ServerId=mtypes.BnetProcessId(Label=3868510373,Epoch=int(time.time())),
            ClientId=mtypes.BnetProcessId(Label=1255760,Epoch=int(time.time())),
            BindResult=0,
            BindResponse=bind_response,
            ServerTime=int(time.time()*1000))

        return resp

class PresenceServiceServer(rpcdef.PresenceService.Server):
    pass

class FriendsServiceServer(rpcdef.FriendsService.Server):
    def subscribe_to_friends(self, req):
        # you have no friends :(
        response = mtypes.SubscribeToFriendsResponse(
            max_friends=10,
            max_received_invitations=5,
            max_sent_invitations=5)
        return response

class ResourcesServiceServer(rpcdef.ResourcesService.Server):
    def get_content_handle(self, req):
        program = utils.decode_fourcc(req.program_id)
        stream = utils.decode_fourcc(req.stream_id)
        locale = utils.decode_fourcc(req.locale)
        self.logger.info('get_content_handle for program=%s, stream=%s and locale=%s', program, stream, locale)

        handle = mtypes.BnetContentHandle(
            region=utils.encode_fourcc('REGI'),
            usage=utils.encode_fourcc('USAG'),
            hash=b'\x00'*32
        )
        return handle

class AccountServiceServer(rpcdef.AccountService.Server):
    def get_account_state(self, req):
        account_level_info = mtypes.AccountLevelInfo(
            preferred_region=0xDEADD00D,
            country='Equestria'
        )
        state = mtypes.AccountState(account_level_info=account_level_info)
        return mtypes.GetAccountStateResponse(state=state)

    def get_game_session_info(self, req):
        resp = account.GetGameSessionInfoResponse(
            session_info=account.GameSessionInfo(start_time=int(time.time())))
        return resp

class ChannelInvitationServiceServer(rpcdef.ChannelInvitationService.Server):
    pass

class ClientHandler(rpc.RpcBroker):
    def __init__(self, server, ep, db):
        super().__init__()
        self._server = server
        self._ep = ep
        self._splitter = SplitterBuf()
        self._send_buf = pipe.SimpleBuf()
        self._db = db

        ep.cb = self._ep_cb

        ep.want_pull(True)
        ep.want_push(False)

        auth_client = rpcdef.AuthenticationClient.build_client_proxy()
        notification_client = rpcdef.NotificationListener.build_client_proxy()

        self.add_import(notification_client)

        auth_server = InsecureAuthenticationServer(
            client_handler=self,
            auth_client=self.add_import(auth_client),
            account_manager=AccountManager(self._db)
        )

        self.add_export(ConnectService())
        self.add_export(auth_server)
        self.add_export(FriendsServiceServer())
        self.add_export(ChannelInvitationServiceServer())
        self.add_export(ResourcesServiceServer())
        self.add_export(AccountServiceServer())
        self.add_export(PresenceServiceServer())
        self.add_export(GameUtilitiesServer(self))
        self.add_export(GameMasterServer(notification_client))

        # TODO: only create the services (except AuthenticationService) after login
        # and provide the account object via the service constructor
        self.account = None

    def send_data(self, buf):
        self._send_buf.append(buf)
        self._ep.want_push(True)

    def _ep_cb(self, ep, ev_type, ev_data):
        if ev_type == 'may_pull':
            self._ep.pull(self._splitter)
            while True:
                segment = self._splitter.pull_segment()
                if segment is None:
                    break
                self.handle_packet(segment[0], segment[1])
        elif ev_type == 'may_push':
            if self._send_buf.used > 0:
                self._ep.push(self._send_buf)
            self._ep.want_push(self._send_buf.used)
        elif ev_type == 'closed':
            self.logger.info('Connection closed')

class Server:
    def __init__(self, listen, db):
        provider = pipe.TcpEndpointProvider(listen)
        provider.cb = self._on_connection

        self.db = db

    def _on_connection(self, provider, ev_type, ev_data):
        if ev_type == 'accepted':
            addr_orig, ep = ev_data
            ClientHandler(self, ep, self.db)

if __name__ == '__main__':
    import asyncore
    import logging
    import argparse
    from hearthy.server.filedb import FileDb

    parser = argparse.ArgumentParser(description='Starts the sever.')

    parser.add_argument('--loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING',
                                 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='Sets the verbosity of the log messages')

    parser.add_argument('--port', type=int, default=52525,
                        help='Port to listen on')

    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to listen on')

    parser.add_argument('--db', required=True,
                        help='Path to the database')

    args = parser.parse_args()


    logging.basicConfig(level=getattr(logging, args.loglevel))

    db = FileDb(args.db)
    server = Server((args.host, args.port), db)
    asyncore.loop()
