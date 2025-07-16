# Configuration manuelle du proxy sur macOS

## Méthode 1: pfctl (Recommandée)

### 1. Créer les règles de redirection

```bash
# Créer le fichier de règles
sudo nano /tmp/hearthstone_proxy.conf
```

Contenu du fichier:
```
# Redirection Hearthstone vers proxy local
rdr on lo0 inet proto tcp from any to any port 1119 -> 127.0.0.1 port 1119
rdr on lo0 inet proto tcp from any to any port 3724 -> 127.0.0.1 port 1119
pass out on lo0 proto tcp from any to 127.0.0.1 port 1119
```

### 2. Activer les règles

```bash
# Charger et activer pfctl
sudo pfctl -f /tmp/hearthstone_proxy.conf
sudo pfctl -e
```

### 3. Vérifier la configuration

```bash
# Voir les règles actives
sudo pfctl -s rules
```

## Méthode 2: Modification du fichier hosts

### 1. Sauvegarder le fichier hosts

```bash
sudo cp /etc/hosts /etc/hosts.backup
```

### 2. Modifier /etc/hosts

```bash
sudo nano /etc/hosts
```

Ajouter à la fin:
```
# Hearthstone proxy
127.0.0.1 us.battle.net
127.0.0.1 eu.battle.net
127.0.0.1 kr.battle.net
127.0.0.1 cn.battle.net
```

## Méthode 3: Proxy système (Alternative)

### 1. Ouvrir les Préférences Système

1. Aller dans **Préférences Système** > **Réseau**
2. Sélectionner votre connexion active
3. Cliquer sur **Avancé...**
4. Onglet **Proxies**

### 2. Configurer le proxy

1. Cocher **Proxy web (HTTP)**
2. Serveur: `127.0.0.1`
3. Port: `1119`
4. Répéter pour **Proxy web sécurisé (HTTPS)**

## Méthode 4: Utiliser mitmproxy (Avancée)

### 1. Installer mitmproxy

```bash
brew install mitmproxy
```

### 2. Créer un script de redirection

```python
# redirect_hearthstone.py
from mitmproxy import http
import requests

def request(flow: http.HTTPFlow) -> None:
    if "battle.net" in flow.request.pretty_host:
        # Rediriger vers notre proxy local
        flow.request.host = "127.0.0.1"
        flow.request.port = 1119
```

### 3. Lancer mitmproxy

```bash
mitmdump -s redirect_hearthstone.py -p 8080
```

## Nettoyage après utilisation

### Désactiver pfctl
```bash
sudo pfctl -d
```

### Restaurer hosts
```bash
sudo mv /etc/hosts.backup /etc/hosts
```

### Vider le cache DNS
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

## Dépannage

### Vérifier les ports en écoute
```bash
lsof -i :1119
netstat -an | grep 1119
```

### Tester la connectivité
```bash
telnet 127.0.0.1 1119
```

### Logs système
```bash
# Voir les logs pfctl
sudo pfctl -s info

# Logs réseau
tail -f /var/log/system.log | grep -i network
```

## Sécurité

⚠️ **Important**: Ces modifications affectent le trafic réseau système. Assurez-vous de:

1. Sauvegarder vos configurations
2. Nettoyer après utilisation
3. Ne pas laisser les redirections actives en permanence
4. Comprendre les implications de sécurité