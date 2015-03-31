import sys
import re
import base64

import google.protobuf.reflection
from hearthy.proto import PegasusUtil_pb2

RE_LINE = re.compile('D ([0-9.:]+) QueuePacketReceived LOG: QueuePacketReceived p = ([a-zA-Z0-9+\/=]+); p\.Type = ([0-9]+)')

decoders = {}

for name, desc in PegasusUtil_pb2.DESCRIPTOR.message_types_by_name.items():
    if 'PacketID' in desc.enum_types_by_name:
        decoder = getattr(PegasusUtil_pb2, name)
        decoders[decoder.ID] = decoder

with open(sys.argv[1]) as f:
    for line in f:
        m = RE_LINE.match(line)
        if m is None:
            continue

        time = m.group(1)
        binary = base64.b64decode(m.group(2))
        packet_id = int(m.group(3))

        decoder = decoders[packet_id]
        print('Time: {}, Packet ID {}, Decoder: {}'.format(time, packet_id, decoder.__name__))
        print(decoders[packet_id].FromString(binary))
        print('-----------------------------------')
