#!/usr/bin/env python3
"""
Script pour configurer automatiquement le proxy sur macOS
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """Exécute une commande shell"""
    print(f"🔧 Exécution: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return None

def check_requirements():
    """Vérifie les prérequis"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier si on est sur macOS
    if sys.platform != "darwin":
        print("❌ Ce script est conçu pour macOS uniquement")
        return False
    
    # Vérifier les permissions admin
    if os.geteuid() != 0:
        print("⚠️  Ce script nécessite les permissions administrateur")
        print("   Relancez avec: sudo python3 setup_proxy_mac.py")
        return False
    
    return True

def setup_pfctl_redirect():
    """Configure pfctl pour rediriger le trafic Hearthstone"""
    print("\n🔀 Configuration de la redirection pfctl...")
    
    # Créer le fichier de règles pfctl
    pf_rules = """
# Règles pour rediriger Hearthstone vers notre proxy
# Ports Hearthstone: 1119 (jeu), 3724 (Battle.net)

# Redirection du trafic sortant vers notre proxy local
rdr on lo0 inet proto tcp from any to any port 1119 -> 127.0.0.1 port 1119
rdr on lo0 inet proto tcp from any to any port 3724 -> 127.0.0.1 port 1119

# Permettre le trafic local
pass out on lo0 proto tcp from any to 127.0.0.1 port 1119
"""
    
    pf_file = "/tmp/hearthstone_proxy.conf"
    with open(pf_file, 'w') as f:
        f.write(pf_rules)
    
    print(f"📝 Règles pfctl créées dans {pf_file}")
    
    # Charger les règles
    run_command(f"pfctl -f {pf_file}")
    run_command("pfctl -e")  # Activer pfctl
    
    print("✅ Redirection pfctl configurée")
    return pf_file

def setup_hosts_redirect():
    """Modifie /etc/hosts pour rediriger les serveurs Hearthstone"""
    print("\n🌐 Configuration de la redirection DNS...")
    
    hosts_entries = [
        "127.0.0.1 us.battle.net",
        "127.0.0.1 eu.battle.net", 
        "127.0.0.1 kr.battle.net",
        "127.0.0.1 cn.battle.net",
        "127.0.0.1 blzddist1-a.akamaihd.net",
        "127.0.0.1 level3.blizzard.com"
    ]
    
    # Sauvegarder le fichier hosts original
    run_command("cp /etc/hosts /etc/hosts.backup.hearthstone")
    
    # Ajouter nos entrées
    with open("/etc/hosts", "a") as f:
        f.write("\n# Hearthstone proxy redirect\n")
        for entry in hosts_entries:
            f.write(f"{entry}\n")
    
    print("✅ Redirection DNS configurée")
    print("💾 Sauvegarde créée: /etc/hosts.backup.hearthstone")

def create_proxy_script():
    """Crée un script pour démarrer le proxy facilement"""
    script_content = '''#!/bin/bash
# Script pour démarrer le proxy Hearthstone

echo "🚀 Démarrage du proxy Hearthstone Battlegrounds..."
echo "📡 Port d'écoute: 1119"
echo "🎮 Lancez Hearthstone après avoir vu ce message"
echo ""

cd "$(dirname "$0")"
python3 example_minimal.py
'''
    
    with open("start_proxy.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("start_proxy.sh", 0o755)
    print("✅ Script de démarrage créé: start_proxy.sh")

def cleanup():
    """Nettoie la configuration"""
    print("\n🧹 Nettoyage de la configuration...")
    
    # Désactiver pfctl
    run_command("pfctl -d", check=False)
    
    # Restaurer hosts
    if os.path.exists("/etc/hosts.backup.hearthstone"):
        run_command("mv /etc/hosts.backup.hearthstone /etc/hosts")
        print("✅ Fichier hosts restauré")
    
    # Supprimer les fichiers temporaires
    for file in ["/tmp/hearthstone_proxy.conf"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Supprimé: {file}")

def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        if not check_requirements():
            sys.exit(1)
        cleanup()
        print("✅ Nettoyage terminé")
        return
    
    print("🔧 Configuration du proxy Hearthstone pour macOS")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Configuration
        setup_pfctl_redirect()
        setup_hosts_redirect()
        create_proxy_script()
        
        print("\n" + "=" * 50)
        print("✅ Configuration terminée!")
        print("\n📋 Étapes suivantes:")
        print("1. Lancez le proxy: ./start_proxy.sh")
        print("2. Démarrez Hearthstone")
        print("3. Allez dans Battlegrounds")
        print("4. Observez les logs dans le terminal")
        print("\n🧹 Pour nettoyer: sudo python3 setup_proxy_mac.py cleanup")
        
    except KeyboardInterrupt:
        print("\n⏹️  Configuration interrompue")
        cleanup()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        cleanup()

if __name__ == "__main__":
    main()