"""
Test simple pour vérifier que l'intercepteur fonctionne
"""

import asyncio
import logging
from modern_hearthy.protocol.splitter import ModernSplitter
from modern_hearthy.protocol.decoder import decoder

# Test du splitter
def test_splitter():
    """Test basique du splitter"""
    print("🧪 Test du splitter...")
    
    splitter = ModernSplitter()
    
    # Simuler des données de packet
    test_data = b'\x01\x00\x00\x00\x04\x00\x00\x00test'  # Type 1, longueur 4, données "test"
    
    packets = list(splitter.feed(test_data))
    
    if packets:
        packet_type, packet_data = packets[0]
        print(f"✅ Packet décodé: Type={packet_type}, Data={packet_data}")
    else:
        print("❌ Aucun packet décodé")

# Test du decoder
def test_decoder():
    """Test basique du decoder"""
    print("🧪 Test du decoder...")
    
    # Le decoder nécessite les définitions protobuf pour fonctionner complètement
    try:
        result = decoder.decode_packet(1, b'test')
        if result:
            print(f"✅ Décodage réussi: {result}")
        else:
            print("⚠️ Décodage impossible (définitions protobuf manquantes)")
    except Exception as e:
        print(f"⚠️ Erreur de décodage (normal sans protobuf): {e}")

async def test_interceptor():
    """Test basique de l'intercepteur"""
    print("🧪 Test de l'intercepteur...")
    
    from modern_hearthy.interceptor import ModernInterceptor
    
    def test_callback(event_type, data):
        print(f"📡 Événement: {event_type} - {data}")
    
    interceptor = ModernInterceptor(
        port=1120,  # Port différent pour le test
        battlegrounds_callback=test_callback
    )
    
    print("✅ Intercepteur créé avec succès")
    
    # Test de démarrage rapide (arrêt immédiat)
    try:
        # Créer une tâche pour démarrer l'intercepteur
        server_task = asyncio.create_task(interceptor.start())
        
        # Attendre un peu puis arrêter
        await asyncio.sleep(0.1)
        interceptor.stop()
        server_task.cancel()
        
        print("✅ Test d'intercepteur réussi")
    except Exception as e:
        print(f"⚠️ Erreur d'intercepteur: {e}")

async def main():
    """Tests principaux"""
    print("🚀 Lancement des tests Modern Hearthy\n")
    
    test_splitter()
    print()
    
    test_decoder()
    print()
    
    await test_interceptor()
    print()
    
    print("✅ Tests terminés!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())