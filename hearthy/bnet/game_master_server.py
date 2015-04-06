from hearthy.bnet.rpcdef import GameMaster
from hsproto.bnet.protocol import game_master_pb2
from hsproto.bnet.protocol.game_master_pb2 import ConnectInfo
from hsproto.bnet.protocol.attribute_pb2 import Attribute, Variant
from hsproto.bnet.protocol_0_pb2 import EntityId

class GameMasterServer(GameMaster.Server):
    def __init__(self, notification_client):
        super().__init__()
        self.notification_client = notification_client

    def find_game(self, req):
        resp = game_master_pb2.FindGameResponse(
            request_id=999,
            factory_id=999,
            queued=False
        )

        yield resp

        # other "supported" attributes are game_handle containing a GameHandle message
        # and sender_id which has unknown purpose
        self.notification_client.on_notification_received(
            target_id=EntityId(high=0,low=0),
            type='G_RESULT',
            attribute = [
                Attribute(
                    name='connection_info',
                    value=Variant(message_value=ConnectInfo(
                        member_id=EntityId(high=0,low=0),
                        host='127.0.0.1',
                        port=1234,
                        token=b'carrot',
                        attribute=[
                            Attribute(name='version',
                                      value=Variant(string_value='v123')),
                            Attribute(name='game',
                                      value=Variant(int_value=123)),
                            Attribute(name='id',
                                      value=Variant(int_value=111)),
                            Attribute(name='resumable',
                                      value=Variant(bool_value=True)),
                            Attribute(name='spectator_password',
                                      value=Variant(string_value='spec_pass'))
                        ]
                    ).SerializeToString())
                )
            ]
        )
