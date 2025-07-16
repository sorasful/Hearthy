"""
Type definitions for modern Hearthy
"""

from typing import Protocol, Union, Optional, Dict, Any, Callable, List, Tuple
from enum import IntEnum
import asyncio

class GameMode(IntEnum):
    """Game modes in Hearthstone"""
    UNKNOWN = 0
    PRACTICE = 1
    FRIENDLY = 2
    RANKED = 3
    ARENA = 4
    TUTORIAL = 5
    CASUAL = 6
    TAVERNBRAWL = 16
    BATTLEGROUNDS = 23

class PacketDirection(IntEnum):
    """Direction of packet flow"""
    CLIENT_TO_SERVER = 0
    SERVER_TO_CLIENT = 1

class InterceptAction(IntEnum):
    """Actions that can be taken on intercepted packets"""
    ACCEPT = 0
    REJECT = 1
    MODIFY = 2

# Type aliases
PacketData = bytes
PacketType = int
StreamId = int
EntityId = int
TagId = int
TagValue = int

# Protocol definitions
class PacketHandler(Protocol):
    """Protocol for packet handlers"""
    def handle_packet(self, packet_type: PacketType, data: PacketData, direction: PacketDirection) -> InterceptAction:
        ...

class BattlegroundsHandler(Protocol):
    """Protocol for Battlegrounds-specific handlers"""
    def on_battlegrounds_start(self, game_data: Dict[str, Any]) -> None:
        ...
    
    def on_hero_selection(self, heroes: List[Dict[str, Any]]) -> None:
        ...
    
    def on_minion_purchase(self, minion_data: Dict[str, Any]) -> None:
        ...
    
    def on_combat_result(self, combat_data: Dict[str, Any]) -> None:
        ...

# Callback types
PacketCallback = Callable[[PacketType, PacketData, PacketDirection], InterceptAction]
BattlegroundsCallback = Callable[[str, Dict[str, Any]], None]