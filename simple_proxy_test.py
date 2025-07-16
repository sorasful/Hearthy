#!/usr/bin/env python3
"""
Test simple pour vérifier que le proxy fonctionne
"""

import socket
import threading
import time

def test_proxy_connection():
    """Test basique de connexion au proxy"""
    print("🧪 Test de connexion au proxy...")
    
    try:
        # Tenter de se connecter au port du proxy
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 1119))
        
        if result == 0:
            print("✅ Proxy accessible sur 127.0.0.1:1119")
            sock.close()
            return True
        else:
            print("❌ Impossible de se connecter au proxy")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def simple_echo_server():
    """Serveur d'écho simple pour tester"""
    print("🔧 Démarrage du serveur d'écho de test...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('127.0.0.1', 1119))
        server.listen(1)
        print("📡 Serveur d'écho en écoute sur 127.0.0.1:1119")
        
        while True:
            client, addr = server.accept()
            print(f"🔗 Connexion de {addr}")
            
            try:
                data = client.recv(1024)
                if data:
                    print(f"📥 Reçu: {data[:50]}...")
                    client.send(b"HTTP/1.1 200 OK\r\n\r\nProxy OK")
                client.close()
            except Exception as e:
                print(f"❌ Erreur client: {e}")
                
    except KeyboardInterrupt:
        print("\n⏹️  Serveur arrêté")
    finally:
        server.close()

def test_dns_resolution():
    """Test de résolution DNS"""
    print("🌐 Test de résolution DNS...")
    
    test_hosts = [
        "us.battle.net",
        "eu.battle.net", 
        "battle.net"
    ]
    
    for host in test_hosts:
        try:
            ip = socket.gethostbyname(host)
            if ip == "127.0.0.1":
                print(f"✅ {host} -> {ip} (redirigé)")
            else:
                print(f"⚠️  {host} -> {ip} (non redirigé)")
        except Exception as e:
            print(f"❌ {host} -> Erreur: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 Tests de configuration proxy macOS")
    print("=" * 40)
    
    # Test 1: Résolution DNS
    test_dns_resolution()
    print()
    
    # Test 2: Connexion proxy
    if test_proxy_connection():
        print("✅ Le proxy semble configuré correctement")
    else:
        print("⚠️  Démarrage du serveur de test...")
        
        # Démarrer le serveur de test dans un thread
        server_thread = threading.Thread(target=simple_echo_server, daemon=True)
        server_thread.start()
        
        time.sleep(1)  # Laisser le temps au serveur de démarrer
        
        print("\n📋 Instructions:")
        print("1. Ouvrez un navigateur")
        print("2. Allez sur http://us.battle.net")
        print("3. Vous devriez voir 'Proxy OK'")
        print("4. Appuyez sur Ctrl+C pour arrêter")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Test terminé")

if __name__ == "__main__":
    main()