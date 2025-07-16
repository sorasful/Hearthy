"""
Exemple minimaliste pour tester l'interception Hearthstone Battlegrounds
"""

import asyncio
import logging
from typing import Dict, Any

from modern_hearthy.interceptor import ModernInterceptor
from modern_hearthy.types import PacketDirection

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class BattlegroundsMonitor:
    """Moniteur simple pour les événements Battlegrounds"""
    
    def __init__(self):
        self.game_started = False
        self.current_gold = 0
        self.current_tier = 1
        self.heroes_seen = []
    
    def on_battlegrounds_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Callback pour les événements Battlegrounds"""
        
        if event_type == 'battlegrounds_detected':
            logger.info("🎮 Partie Battlegrounds détectée!")
            self.game_started = True
        
        elif event_type == 'hero_revealed':
            hero_id = data.get('card_id', 'Unknown')
            logger.info(f"🦸 Héros révélé: {hero_id}")
            if hero_id not in self.heroes_seen:
                self.heroes_seen.append(hero_id)
        
        elif event_type == 'gold_changed':
            old_gold = self.current_gold
            self.current_gold = data.get('gold', 0)
            logger.info(f"💰 Or: {old_gold} → {self.current_gold}")
        
        elif event_type == 'tavern_tier_changed':
            old_tier = self.current_tier
            self.current_tier = data.get('tier', 1)
            logger.info(f"🏪 Niveau taverne: {old_tier} → {self.current_tier}")
        
        elif event_type == 'entity_revealed':
            entity_id = data.get('entity_id')
            card_id = data.get('card_id', 'Unknown')
            logger.info(f"👁️ Entité révélée: {card_id} (ID: {entity_id})")
        
        elif event_type == 'options_available':
            options = data.get('options', [])
            logger.info(f"⚡ {len(options)} options disponibles")
        
        elif event_type == 'entity_choice':
            entities = data.get('entities', [])
            logger.info(f"🎯 Choix d'entité: {len(entities)} options")
    
    def print_status(self) -> None:
        """Affiche le statut actuel"""
        if self.game_started:
            print(f"\n📊 Statut actuel:")
            print(f"   💰 Or: {self.current_gold}")
            print(f"   🏪 Niveau taverne: {self.current_tier}")
            print(f"   🦸 Héros vus: {len(self.heroes_seen)}")

async def main():
    """Fonction principale"""
    print("🚀 Démarrage du moniteur Hearthstone Battlegrounds")
    print("📡 En attente de connexions sur le port 1119...")
    print("💡 Lancez Hearthstone et démarrez une partie Battlegrounds")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter\n")
    
    # Créer le moniteur
    monitor = BattlegroundsMonitor()
    
    # Créer l'intercepteur
    interceptor = ModernInterceptor(
        port=1119,
        battlegrounds_callback=monitor.on_battlegrounds_event
    )
    
    # Ajouter un handler personnalisé pour certains packets
    def custom_packet_handler(packet_data: Any, direction: PacketDirection):
        """Handler personnalisé pour certains packets"""
        packet_name = packet_data.__class__.__name__ if hasattr(packet_data, '__class__') else 'Unknown'
        
        if direction == PacketDirection.CLIENT_TO_SERVER:
            logger.debug(f"📤 Client → Serveur: {packet_name}")
        else:
            logger.debug(f"📥 Serveur → Client: {packet_name}")
        
        # Toujours accepter le packet
        from modern_hearthy.types import InterceptAction
        return InterceptAction.ACCEPT
    
    # Vous pouvez ajouter des handlers pour des types de packets spécifiques
    # interceptor.add_packet_handler(packet_type_id, custom_packet_handler)
    
    try:
        # Démarrer l'intercepteur
        await interceptor.start()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        monitor.print_status()
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
    finally:
        interceptor.stop()
        print("👋 Moniteur arrêté")

if __name__ == "__main__":
    # Lancer le programme
    asyncio.run(main())