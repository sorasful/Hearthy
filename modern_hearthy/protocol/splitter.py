"""
Modern packet splitter with type hints and async support
"""

import struct
from typing import Iterator, Tuple, Optional
from ..types import PacketType, PacketData
from ..exceptions import BufferFullException

class ModernSplitter:
    """Modern packet splitter with type safety"""
    
    def __init__(self, max_buffer_size: int = 16 * 1024) -> None:
        self._buffer = bytearray(max_buffer_size)
        self._offset = 0
        self._needed = 8
        self._packet_type: Optional[PacketType] = None
        self._max_buffer_size = max_buffer_size
    
    def feed(self, data: bytes) -> Iterator[Tuple[PacketType, PacketData]]:
        """Feed data to the splitter and yield complete packets"""
        new_offset = self._offset + len(data)
        
        if new_offset > self._max_buffer_size:
            raise BufferFullException("Buffer size exceeded")
        
        self._buffer[self._offset:new_offset] = data
        
        while new_offset >= self._needed:
            if self._packet_type is None:
                # Parse header
                packet_type, packet_length = struct.unpack('<II', self._buffer[:8])
                self._needed = packet_length + 8
                self._packet_type = packet_type
            else:
                # Extract packet data
                packet_data = bytes(self._buffer[8:self._needed])
                yield (self._packet_type, packet_data)
                
                # Reset for next packet
                new_offset -= self._needed
                self._buffer[:new_offset] = self._buffer[self._needed:self._needed + new_offset]
                self._needed = 8
                self._packet_type = None
        
        self._offset = new_offset
    
    def reset(self) -> None:
        """Reset the splitter state"""
        self._offset = 0
        self._needed = 8
        self._packet_type = None