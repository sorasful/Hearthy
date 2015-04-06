from hearthy.proxy import pipe
from hsproto.bnet.protocol_1_pb2 import Header

class SplitterBuf(pipe.SimpleBuf):
    def __init__(self):
        super().__init__()
        self._header = None

    def pull_segment(self):
        used = self.used

        # read header size
        if used < 2:
            return

        hi, lo = self.peek(2)
        header_size = (hi << 8) | lo

        header = self._header
        if header is None:
            # read header
            if used < 2 + header_size:
                return
            header = self._header = Header.FromString(self.peek(header_size, 2))

        # read body
        if used < 2 + header_size + header.size:
            return

        body = self.peek(header.size, 2 + header_size)

        self._header = None
        self.consume(2 + header_size + header.size)
                     
        return (header, body)
