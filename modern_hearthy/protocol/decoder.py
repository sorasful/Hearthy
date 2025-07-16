"""
Modern protocol decoder with type hints
"""

import struct
from typing import Dict, Type, Optional, Any, Union
from dataclasses import dataclass

from ..types import PacketType, PacketData
from ..exceptions import DecodeError, EncodeError

@dataclass
class DecodedPacket:
    """Represents a decoded packet"""
    packet_type: PacketType
    data: Any
    raw_data: PacketData

class ModernDecoder:
    """Modern packet decoder with type safety"""
    
    def __init__(self) -> None:
        self._message_types: Dict[PacketType, Type] = {}
        self._initialize_message_types()
    
    def _initialize_message_types(self) -> None:
        """Initialize message type mappings"""
        try:
            # Try to import protobuf definitions if available
            from pegasus import game_pb2, bobnet_pb2
            
            for module in (bobnet_pb2, game_pb2):
                for name, message_desc in module.DESCRIPTOR.message_types_by_name.items():
                    try:
                        message_id = message_desc.enum_values_by_name['ID'].number
                        self._message_types[message_id] = getattr(module, name)
                    except KeyError:
                        continue
        except ImportError:
            print("Warning: Protobuf definitions not available. Limited functionality.")
    
    def decode_packet(self, packet_type: PacketType, data: PacketData) -> Optional[DecodedPacket]:
        """Decode a packet with type safety"""
        try:
            message_class = self._message_types.get(packet_type)
            if not message_class:
                return None
            
            message = message_class()
            message.MergeFromString(bytes(data))
            
            return DecodedPacket(
                packet_type=packet_type,
                data=message,
                raw_data=data
            )
        except Exception as e:
            raise DecodeError(f"Failed to decode packet type {packet_type}: {e}")
    
    def encode_packet(self, packet: Any) -> Tuple[PacketType, PacketData]:
        """Encode a packet with type safety"""
        try:
            packet_type = packet.ID
            encoded = packet.SerializeToString()
            return packet_type, encoded
        except AttributeError:
            raise EncodeError(f'No packet type for class {packet.__class__}')

# Global decoder instance
decoder = ModernDecoder()