"""
Hearthstone Protocol Decoder.
"""

from enum import IntEnum
import struct
from hearthy.protocol import mtypes
from hearthy.exceptions import DecodeError, EncodeError

class PacketType(IntEnum):
    GET_GAME_STATE = 1
    CHOOSE_OPTION = 2
    CHOOSE_ENTITIES = 3
    PRE_CAST = 4
    DEBUG_MESSAGE = 5
    CLIENT_PACKET = 6
    START_GAME_STATE = 7
    FINISH_GAME_STATE = 8
    TURN_TIMER = 9
    NACK_OPTION = 10
    GIVE_UP = 11
    GAME_CANCELLED = 12
    FORCED_ENTITY_CHOICE = 13
    ALL_OPTIONS = 14
    USER_UI = 15
    GAME_SETUP = 16
    ENTITY_CHOICE = 17
    PRE_LOAD = 18
    POWER_HISTORY = 19
    NOTIFICATION = 21
    SPECTATOR_HANDSHAKE = 22
    SERVER_RESULT = 23
    SPECTATOR_NOTIFY = 24
    INVITE_TO_SPECTATE = 25
    REMOVE_SPECTATORS = 26

    AUTO_LOGIN = 103
    BEGIN_PLAYING = 113
    DEBUG_CONSOLE_COMMAND = 123
    DEBUG_CONSOLE_RESPONSE = 124
    GAME_STARTING = 114
    PING = 115
    PONG = 116
    AURORA_HANDSHAKE = 168

_packet_type_map = [
    (PacketType.POWER_HISTORY, mtypes.PowerHistory),
    (PacketType.USER_UI, mtypes.UserUI),
    (PacketType.TURN_TIMER, mtypes.TurnTimer),
    (PacketType.START_GAME_STATE, mtypes.StartGameState),
    (PacketType.PRE_LOAD, mtypes.PreLoad),
    (PacketType.PRE_CAST, mtypes.PreCast),
    (PacketType.NOTIFICATION, mtypes.Notification),
    (PacketType.NACK_OPTION, mtypes.NAckOption),
    (PacketType.GIVE_UP, mtypes.GiveUp),
    (PacketType.GET_GAME_STATE, mtypes.GetGameState),
    (PacketType.GAME_SETUP, mtypes.GameSetup),
    (PacketType.GAME_CANCELLED, mtypes.GameCancelled),
    (PacketType.FINISH_GAME_STATE, mtypes.FinishGameState),
    (PacketType.ENTITY_CHOICE, mtypes.EntityChoice),
    (PacketType.DEBUG_MESSAGE, mtypes.DebugMessage),
    (PacketType.CLIENT_PACKET, mtypes.ClientPacket),
    (PacketType.CHOOSE_OPTION, mtypes.ChooseOption),
    (PacketType.CHOOSE_ENTITIES, mtypes.ChooseEntities),
    (PacketType.ALL_OPTIONS, mtypes.AllOptions),
    (PacketType.BEGIN_PLAYING, mtypes.BeginPlaying),
    (PacketType.AURORA_HANDSHAKE, mtypes.AuroraHandshake),
    (PacketType.GAME_STARTING, mtypes.GameStarting),
    (PacketType.DEBUG_CONSOLE_COMMAND, mtypes.DebugConsoleCommand),
    (PacketType.DEBUG_CONSOLE_RESPONSE, mtypes.DebugConsoleResponse),
    (PacketType.PING, mtypes.Ping),
    (PacketType.PONG, mtypes.Pong),
    (PacketType.FORCED_ENTITY_CHOICE, mtypes.ForcedEntityChoice),
    (PacketType.SERVER_RESULT, mtypes.ServerResult),
    (PacketType.SPECTATOR_NOTIFY, mtypes.SpectatorNotify),
    (PacketType.SPECTATOR_HANDSHAKE, mtypes.SpectatorHandshake),
    (PacketType.INVITE_TO_SPECTATE, mtypes.InviteToSpectate)
]

_packet_type_handlers = dict(_packet_type_map)
_packet_type_id = dict((y,x) for x,y in _packet_type_map)

def encode_packet(packet, buf, offset=0):
    end = packet.encode_buf(buf, offset + 8)
    packet_type = _packet_type_id.get(packet.__class__, None)

    if packet_type is None:
        raise EncodeError('No packet type for class {0}'.format(packet.__class__))

    buf[offset:offset+8] = struct.pack('<II', packet_type, end - offset - 8)
    return end

def decode_packet(packet_type, buf):
    handler = _packet_type_handlers.get(packet_type, None)
    if handler is None:
        import pdb; pdb.set_trace()
        raise DecodeError('No handler for packet type {0}'.format(packet_type))

    return handler.decode_buf(buf)

if __name__ == '__main__':
    import sys
    from .utils import Splitter

    if len(sys.argv) < 2:
        print('Usage: {0} <raw dump file>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'rb') as f:
        s = Splitter()
        while True:
            buf = f.read(8*1024)
            if len(buf) == 0:
                break
            for atype, buf in s.feed(buf):
                print(decode_packet(atype, buf))
