#!/bin/bash

# Script de démarrage complet pour le proxy Hearthstone sur macOS

echo "🚀 Configuration et démarrage du proxy Hearthstone Battlegrounds"
echo "================================================================"

# Vérifier les permissions
if [[ $EUID -ne 0 ]]; then
   echo "❌ Ce script nécessite les permissions administrateur"
   echo "   Relancez avec: sudo ./start_hearthstone_proxy.sh"
   exit 1
fi

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🧹 Nettoyage en cours..."
    
    # Désactiver pfctl
    pfctl -d 2>/dev/null
    
    # Restaurer hosts si sauvegarde existe
    if [ -f "/etc/hosts.backup.hearthstone" ]; then
        mv /etc/hosts.backup.hearthstone /etc/hosts
        echo "✅ Fichier hosts restauré"
    fi
    
    # Supprimer fichiers temporaires
    rm -f /tmp/hearthstone_proxy.conf
    
    # Vider le cache DNS
    dscacheutil -flushcache
    killall -HUP mDNSResponder 2>/dev/null
    
    echo "✅ Nettoyage terminé"
    exit 0
}

# Capturer Ctrl+C
trap cleanup INT TERM

echo "🔧 Étape 1: Configuration de la redirection réseau..."

# Créer les règles pfctl
cat > /tmp/hearthstone_proxy.conf << EOF
# Redirection Hearthstone vers proxy local
rdr on lo0 inet proto tcp from any to any port 1119 -> 127.0.0.1 port 1119
rdr on lo0 inet proto tcp from any to any port 3724 -> 127.0.0.1 port 1119
pass out on lo0 proto tcp from any to 127.0.0.1 port 1119
EOF

# Activer pfctl
pfctl -f /tmp/hearthstone_proxy.conf
pfctl -e

echo "✅ Redirection pfctl configurée"

echo "🌐 Étape 2: Configuration DNS..."

# Sauvegarder hosts
cp /etc/hosts /etc/hosts.backup.hearthstone

# Ajouter redirections DNS
cat >> /etc/hosts << EOF

# Hearthstone proxy redirect
127.0.0.1 us.battle.net
127.0.0.1 eu.battle.net
127.0.0.1 kr.battle.net
127.0.0.1 cn.battle.net
127.0.0.1 blzddist1-a.akamaihd.net
127.0.0.1 level3.blizzard.com
EOF

echo "✅ Redirection DNS configurée"

# Vider le cache DNS
dscacheutil -flushcache
killall -HUP mDNSResponder

echo "🚀 Étape 3: Démarrage du proxy Python..."
echo ""
echo "📋 Instructions:"
echo "1. Le proxy va démarrer sur le port 1119"
echo "2. Lancez Hearthstone APRÈS avoir vu le message de démarrage"
echo "3. Allez dans le mode Battlegrounds"
echo "4. Observez les logs dans ce terminal"
echo "5. Appuyez sur Ctrl+C pour tout arrêter et nettoyer"
echo ""

# Démarrer le proxy Python (en tant qu'utilisateur normal)
REAL_USER=$(who am i | awk '{print $1}')
REAL_HOME=$(eval echo ~$REAL_USER)

cd "$(dirname "$0")"
sudo -u $REAL_USER python3 example_minimal.py

# Nettoyage automatique à la fin
cleanup