"""
Hearthstone Protocol Decoder.
"""

import struct
from hearthy.exceptions import DecodeError, EncodeError
from pegasus import game_pb2, bobnet_pb2

def _iter_messages():
    for module in (bobnet_pb2, game_pb2):
        for name, message_desc in module.DESCRIPTOR.message_types_by_name.items():
            try:
                message_id = message_desc.enum_values_by_name['ID'].number
            except KeyError:
                pass
            else:
                yield message_id, getattr(module, name)
messages_by_id = dict(_iter_messages())

def encode_packet(packet, buf, offset=0):
    try:
        packet_type = packet.ID
    except AttributeError:
        raise EncodeError('No packet type for class {0}'.format(packet.__class__))

    encoded = packet.SerializeToString()

    end = offset + 8 + len(encoded)
    buf[offset:offset+8] = struct.pack('<II', packet_type, len(encoded))
    buf[offset+8:end] = encoded
    return end

def decode_packet(packet_type, buf):
    try:
        message_type = messages_by_id[packet_type]
    except KeyError:
        raise DecodeError('No message with ID {0}'.format(packet_type))
    message = message_type()
    message.MergeFromString(bytes(buf))
    return message

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
