import logging
from hearthy.bnet import rpcdef
from hearthy.bnet.account_info import AccountInfo
from hearthy.proto import PegasusUtil_pb2, PegasusShared_pb2
from hearthy.protocol import game_utilities, mtypes

ASSETS_VERSION = 7553

logger = logging.getLogger(__name__)

# Mapping from packet id to the corresponding message class
_utility_packets = {}

# Populate _utility_packets by searching for all protobuf message classes
# that contain a PacketID enumeration class.
for name, desc in PegasusUtil_pb2.DESCRIPTOR.message_types_by_name.items():
    if 'PacketID' in desc.enum_types_by_name:
        message = getattr(PegasusUtil_pb2, name)
        _utility_packets[message.ID] = message

_handlers = {}
def _handles(message_class):
    def regfun(fn):
        if message_class in _handlers:
            raise Exception('found double registration for %s', message_class)
        _handlers[message_class] = fn
        return fn

    return regfun

class GameUtilityHandlers:
    @_handles(PegasusUtil_pb2.DeleteDeck)
    def delete_deck(self, req):
        self.client_handler.account.delete_deck(req.deck)
        return PegasusUtil_pb2.DeckDeleted(deck=req.deck)

    @_handles(PegasusUtil_pb2.GetDeck)
    def get_deck(self, req):
        deck = self.client_handler.account.get_deck(req.deck)
        deck_contents = PegasusUtil_pb2.DeckContents(deck=req.deck)

        for i, card in enumerate(deck.cards):
            deck_card = deck_contents.cards.add(
                handle=i+1,
                prev=i,
                qty=card['count']
            )
            deck_card_def = getattr(deck_card, 'def')
            deck_card_def.asset = card['card_id']
            if card.get('premium', 0) > 0:
                deck_card_def.premium = card['premium']

        print(deck_contents)
        return deck_contents

    @_handles(PegasusUtil_pb2.RenameDeck)
    def deck_rename(self, req):
        """ Changes the name of a deck """
        deck = self.client_handler.account.get_deck(req.deck)
        deck.name = req.name
        deck.save()

        return PegasusUtil_pb2.DeckRenamed(
            deck=deck.id,
            name=deck.name
        )

    @_handles(PegasusUtil_pb2.DeckSetData)
    def deck_set_data(self, req):
        deck_id = req.deck

        card_list = []

        for card in req.cards:
            card_def = getattr(card, 'def')
            card_list.append({
                'card_id': card_def.asset,
                'premium': getattr(card_def, 'premium', 0),
                'count': card.qty
            })

        self.client_handler.account.set_deck_contents(deck_id, card_list)

        # TODO: not 100% sure what to respond
        return PegasusUtil_pb2.DBAction(
            action=PegasusShared_pb2.DB_A_SET_DECK,
            result=PegasusShared_pb2.DB_E_SUCCESS,
            meta_data=deck_id
        )

    @_handles(PegasusUtil_pb2.CreateDeck)
    def create_deck(self, req):
        deck = self.client_handler.account.create_deck(req.name, req.hero)

        return PegasusUtil_pb2.DeckCreated(
            info=PegasusShared_pb2.DeckInfo(
                id=deck['deck_id'],
                name=deck['name'],
                card_back=1,
                hero=deck['hero_id'],
                deck_type=PegasusShared_pb2.DeckInfo.NORMAL_DECK,
                validity=31,
                hero_premium=0,
                card_back_override=False
            )
        )

    @_handles(PegasusUtil_pb2.Subscribe)
    def subscribe(self, req):
        # TOOD: not quite sure what the client is subscribing to...
        return PegasusUtil_pb2.SubscribeResponse(
            route = 12,
            supported_features = 1,
            keep_alive_secs = 300
        )

    @_handles(PegasusUtil_pb2.GetAssetsVersion)
    def get_assets_version(self, req):
        return PegasusUtil_pb2.AssetsVersionResponse(
            version=ASSETS_VERSION
        )

    @_handles(PegasusUtil_pb2.UpdateLogin)
    def update_login(self, req):
        # TODO: what is this for?
        return PegasusUtil_pb2.UpdateLoginComplete()

    @_handles(PegasusUtil_pb2.SetProgress)
    def set_progress(self, req):
        # TODO: what is this for?
        return PegasusUtil_pb2.SetProgressResponse(
            result=PegasusUtil_pb2.SetProgressResponse.SUCCESS
        )

    @_handles(PegasusUtil_pb2.CheckGameLicenses)
    @_handles(PegasusUtil_pb2.CheckAccountLicenses)
    def check_game_license(self, req):
        return PegasusUtil_pb2.CheckLicensesResponse(
            account_level=True,
            success=True
        )

    @_handles(PegasusUtil_pb2.GetAdventureProgress)
    def get_adventure_progress(self, req):
        # TODO: implement adventure
        return PegasusUtil_pb2.AdventureProgressResponse()

    @_handles(PegasusUtil_pb2.GetOptions)
    def get_options(self, req):
        # TODO: implement options
        return PegasusUtil_pb2.ClientOptions()

    @_handles(PegasusUtil_pb2.GetBattlePayConfig)
    def get_battle_pay_config(self, req):
        return PegasusUtil_pb2.BattlePayConfigResponse(
            currency=2,
            unavailable=True,
            secs_before_auto_cancel=600,
            gold_cost_arena=150
        )

    @_handles(PegasusUtil_pb2.GetAchieves)
    def get_achieves(self, req):
        achieves = PegasusUtil_pb2.Achieves()

        # druid, hunter, mage, paladin, priest, rogue, shaman, warlock, warrior
        hero_ach_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        date = PegasusShared_pb2.Date(year=2013,month=12,day=21,
                                      hours=7,min=24,sec=33)

        for x in hero_ach_ids:
            achieves.list.add(
                id=x,
                progress=1,
                ack_progress=1,
                completion_count=1,
                started_count=1,
                date_given=date,
                date_completed=date
            )

        # unlock all heroes
        achieves.list.add(
            id=79,
            progress=9,
            ack_progress=9,
            completion_count=1,
            started_count=1,
            date_given=date,
            date_completed=date
        )

        return achieves

    @_handles(PegasusUtil_pb2.GetAccountInfo)
    def get_account_info(self, req):
        account_info = AccountInfo(self.client_handler.account)
        return account_info.handle(req.request)

class GameUtilitiesServer(rpcdef.GameUtilities.Server):
    def __init__(self, client_handler):
        super().__init__()

        self.client_handler = client_handler

    def process_client_request(self, req):
        blobval = req.attributes[0].value.blobval

        # decode the request
        request_type = blobval[0] | (blobval[1] << 8)
        request_body = blobval[2:]

        # search for the message class that can decode this request
        message_class = _utility_packets[request_type]
        decoded_request = message_class.FromString(request_body)

        self.logger.info('Got utility request - %s - %s',
                         message_class,
                         decoded_request)

        handler = _handlers.get(message_class, None)
        if handler is None:
            self.logger.warn('No handler for utility request - %s - %s',
                             message_class,
                             decoded_request)
            return None

        resp = handler(self, decoded_request)
        if resp is None:
            self.logger.warn('Handler did not return any response for utility request - %s - %s',
                             message_class,
                             decoded_request)
            return None

        return game_utilities.ClientResponse(attributes=[
            mtypes.Attribute(name='?',value=mtypes.BnetVariant(intval=resp.ID)),
            mtypes.Attribute(name='?',value=mtypes.BnetVariant(blobval=resp.SerializeToString()))
        ])
