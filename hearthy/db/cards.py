from hearthy.exceptions import CardNotFound
from .carddefs import cards as _id_to_card

def get_by_id(cardid):
    try:
        return _id_to_card[cardid]
    except KeyError:
        raise CardNotFound('Could not find card with id {0}'.format(cardid))
