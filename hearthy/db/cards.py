from hearthstone import cardxml

from hearthy.exceptions import CardNotFound


def _build_card_map():
    cards, xml_ = cardxml.load('hs-data/CardDefs.xml')
    return {card_id: card.name for card_id, card in cards.items()}

_id_to_card = _build_card_map()

def get_by_id(cardid):
    try:
        return _id_to_card[cardid]
    except KeyError:
        raise CardNotFound('Could not find card with id {0}'.format(cardid))
