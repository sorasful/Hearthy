# Modern Hearthy - Intercepteur Hearthstone Battlegrounds

Version modernisée de Hearthy avec support des type hints Python et focus sur le mode Battlegrounds.

## Fonctionnalités

- ✅ Interception réseau moderne avec asyncio
- ✅ Type hints complets pour une meilleure sécurité
- ✅ Détection automatique du mode Battlegrounds
- ✅ Monitoring des événements de jeu (or, niveau taverne, héros, etc.)
- ✅ Architecture modulaire et extensible

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation rapide

1. **Lancer l'intercepteur** :
```bash
python example_minimal.py
```

2. **Configurer Hearthstone** pour utiliser un proxy local (port 1119)

3. **Lancer une partie Battlegrounds** et observer les logs

## Architecture

```
modern_hearthy/
├── types.py              # Définitions de types
├── interceptor.py         # Intercepteur réseau principal
├── protocol/
│   ├── decoder.py        # Décodage des packets
│   └── splitter.py       # Séparation des packets
├── battlegrounds/
│   └── detector.py       # Détection événements Battlegrounds
└── exceptions.py         # Exceptions personnalisées
```

## Événements Battlegrounds détectés

- 🎮 Détection de partie Battlegrounds
- 🦸 Révélation de héros
- 💰 Changements d'or
- 🏪 Changements de niveau de taverne
- 👁️ Révélation d'entités (serviteurs, sorts)
- ⚡ Options disponibles
- 🎯 Choix d'entités

## Configuration réseau

Pour intercepter le trafic Hearthstone, vous devez configurer un proxy ou modifier les paramètres réseau pour rediriger le trafic vers `127.0.0.1:1119`.

## Développement

Le code utilise des type hints modernes et une architecture async pour de meilleures performances et une maintenance facilitée.

### Ajouter un handler personnalisé

```python
def mon_handler(packet_data, direction):
    # Traiter le packet
    return InterceptAction.ACCEPT

interceptor.add_packet_handler(packet_type_id, mon_handler)
```

## Notes importantes

- Ce code nécessite une configuration réseau appropriée pour intercepter le trafic
- Les définitions protobuf originales peuvent être nécessaires pour un décodage complet
- Respectez les conditions d'utilisation de Hearthstone