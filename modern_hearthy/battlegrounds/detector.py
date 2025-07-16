"""
Battlegrounds mode detection and handling
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import IntEnum

from ..types import BattlegroundsCallback, PacketType, PacketData, PacketDirection

class BattlegroundsPhase(IntEnum):
    """Phases in a Battlegrounds game"""
    UNKNOWN = 0
    HERO_SELECTION = 1
    RECRUIT_PHASE = 2
    COMBAT_PHASE = 3
    GAME_END = 4

@dataclass
class BattlegroundsState:
    """Current state of a Battlegrounds game"""
    phase: BattlegroundsPhase = BattlegroundsPhase.UNKNOWN
    turn: int = 0
    gold: int = 0
    tavern_tier: int = 1
    health: int = 40
    board: List[Dict[str, Any]] = None
    hand: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.board is None:
            self.board = []
        if self.hand is None:
            self.hand = []

class BattlegroundsDetector:
    """Detects and tracks Battlegrounds game state"""
    
    def __init__(self, callback: Optional[BattlegroundsCallback] = None) -> None:
        self.callback = callback
        self.state = BattlegroundsState()
        self.is_battlegrounds = False
    
    def process_packet(self, packet_type: PacketType, data: Any, direction: PacketDirection) -> None:
        """Process a packet to detect Battlegrounds events"""
        
        # Check if this is a Battlegrounds game
        if hasattr(data, 'game_type') and data.game_type == 23:  # Battlegrounds mode
            self.is_battlegrounds = True
            if self.callback:
                self.callback('battlegrounds_detected', {'game_type': 23})
        
        if not self.is_battlegrounds:
            return
        
        # Handle different packet types for Battlegrounds
        if hasattr(data, '__class__'):
            packet_name = data.__class__.__name__
            
            if packet_name == 'PowerHistory':
                self._handle_power_history(data)
            elif packet_name == 'AllOptions':
                self._handle_options(data)
            elif packet_name == 'EntityChoice':
                self._handle_entity_choice(data)
    
    def _handle_power_history(self, power_history: Any) -> None:
        """Handle PowerHistory packets for Battlegrounds events"""
        if not hasattr(power_history, 'list'):
            return
        
        for power in power_history.list:
            if hasattr(power, 'full_entity'):
                self._handle_full_entity(power.full_entity)
            elif hasattr(power, 'tag_change'):
                self._handle_tag_change(power.tag_change)
            elif hasattr(power, 'show_entity'):
                self._handle_show_entity(power.show_entity)
    
    def _handle_full_entity(self, entity: Any) -> None:
        """Handle new entity creation"""
        if hasattr(entity, 'name') and 'HERO' in entity.name:
            if self.callback:
                self.callback('hero_revealed', {
                    'entity_id': entity.entity,
                    'card_id': entity.name
                })
    
    def _handle_tag_change(self, tag_change: Any) -> None:
        """Handle tag changes for game state tracking"""
        # Track gold changes (tag 1668)
        if hasattr(tag_change, 'tag') and tag_change.tag == 1668:
            self.state.gold = tag_change.value
            if self.callback:
                self.callback('gold_changed', {'gold': tag_change.value})
        
        # Track tavern tier (tag 1664)
        elif hasattr(tag_change, 'tag') and tag_change.tag == 1664:
            self.state.tavern_tier = tag_change.value
            if self.callback:
                self.callback('tavern_tier_changed', {'tier': tag_change.value})
    
    def _handle_show_entity(self, entity: Any) -> None:
        """Handle entity reveals (minions, spells, etc.)"""
        if hasattr(entity, 'name'):
            if self.callback:
                self.callback('entity_revealed', {
                    'entity_id': entity.entity,
                    'card_id': entity.name
                })
    
    def _handle_options(self, options: Any) -> None:
        """Handle available options (hero selection, purchases, etc.)"""
        if hasattr(options, 'options'):
            option_list = []
            for option in options.options:
                if hasattr(option, 'entity'):
                    option_list.append({
                        'entity_id': option.entity,
                        'type': getattr(option, 'type', 'unknown')
                    })
            
            if option_list and self.callback:
                self.callback('options_available', {'options': option_list})
    
    def _handle_entity_choice(self, choice: Any) -> None:
        """Handle entity choices (hero selection)"""
        if hasattr(choice, 'entities'):
            entities = []
            for entity in choice.entities:
                entities.append({'entity_id': entity})
            
            if entities and self.callback:
                self.callback('entity_choice', {'entities': entities})