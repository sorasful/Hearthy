from hearthy.protocol.type_builder import Builder
from hearthy.protocol import game_utilities, mtypes

def _anon():
    builder = Builder()

    builder.add('Date', [
        (1, 'year', 'int32'),
        (2, 'month', 'int32'),
        (3, 'day', 'int32'),
        (4, 'hours', 'int32'),
        (5, 'min', 'int32'),
        (6, 'sec', 'int32')
    ])

    builder.add('DeckInfo', [
        (1, 'id', 'int64'),
        (2, 'name', 'string'),
        (3, 'card_back', 'int32'),
        (4, 'hero', 'int32'),
        (5, 'deck_type', 'enum'),
        (6, 'validity', 'int64'),
        (7, 'hero_premium', 'int32'),
        (8, 'card_back_override', 'bool')
    ])
    
    builder.build(globals(), __name__)

_anon()
