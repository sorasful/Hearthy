import logging
from hearthy.protocol.enums import GameOption
from hearthy.proto import PegasusUtil_pb2, PegasusShared_pb2

PRECON = PegasusUtil_pb2.DeckList()
for i in [7,31,274,637,671,813,893,930,1066]:
    PRECON.decks.add(id=i,
                     name="precon",
                     card_back=13,
                     hero=i,
                     deck_type=PegasusShared_pb2.DeckInfo.PRECON_DECK,
                     validity=31,
                     hero_premium=0,
                     card_back_override=False)

logger = logging.getLogger(__name__)

# Registration of GetAccountInfo handlers
_handlers = {}

def _handles(info_id):
    def regfun(fn):
        if info_id in _handlers:
            raise Exception('Double registration for info_id {}'.format(info_id))

        _handlers[info_id] = fn
        return fn

    return regfun

class AccountInfo:
    def __init__(self, account):
        self.account = account

    def handle(self, info_id):
        handler = _handlers.get(info_id, None)
        if handler is None:
            logger.warn('No handler found for info_id %d (%s)',
                        info_id,
                        PegasusUtil_pb2.GetAccountInfo.Request.Name(info_id))
            return None
        return _handlers[info_id](self)

    @_handles(PegasusUtil_pb2.GetAccountInfo.MEDAL_INFO)
    def get_medal_info(self):
        # TODO: currently not implemented
        return PegasusUtil_pb2.MedalInfo(
            season_wins=0,
            stars=20,
            streak=0,
            star_level=9,
            level_start=20,
            level_end=23,
            can_lose=True
        )

    @_handles(PegasusUtil_pb2.GetAccountInfo.DECK_LIST)
    def get_deck_list(self):
        deck_list = PegasusUtil_pb2.DeckList()
        deck_list.CopyFrom(PRECON)

        for deck in self.account.decks:
            deck_list.decks.add(id=deck.id,
                                name=deck.name,
                                card_back=13,
                                hero=deck.hero_id,
                                deck_type=PegasusShared_pb2.DeckInfo.NORMAL_DECK,
                                validity=31,
                                hero_premium=0,
                                card_back_override=False)

        return deck_list

    @_handles(PegasusUtil_pb2.GetAccountInfo.CARD_VALUES)
    def get_card_values(self):
        # TODO: figure out what card_nerf_index is used for
        cv = PegasusUtil_pb2.CardValues(card_nerf_index=5)
        for item in self.account.crafting_cost['list']:
            entry = cv.cards.add(buy=item['buy'],sell=item['sell'],nerfed=False)
            entry.card.asset = item['card_id']
            if item.get('premium', 0) > 0:
                entry.card.premium = item['premium']
        return cv

    @_handles(PegasusUtil_pb2.GetAccountInfo.BOOSTERS)
    def get_boosters(self):
        return PegasusUtil_pb2.BoosterList()

    @_handles(PegasusUtil_pb2.GetAccountInfo.FEATURES)
    def get_features(self):
        return PegasusUtil_pb2.GuardianVars(showUserUI=1)

    @_handles(PegasusUtil_pb2.GetAccountInfo.CAMPAIGN_INFO)
    def get_campaign_info(self):
        return PegasusUtil_pb2.ProfileProgress(
            progress=6,
            best_forge=10,
            last_forge=PegasusShared_pb2.Date(
                year=2015,
                month=3,
                day=31,
                hours=17,
                min=3,
                sec=54
            )
        )

    @_handles(PegasusUtil_pb2.GetAccountInfo.CARD_BACKS)
    def get_card_backs(self):
        return PegasusUtil_pb2.CardBacks(
            default_card_back=13,
            card_backs=list(range(1,20)))

    @_handles(PegasusUtil_pb2.GetAccountInfo.GOLD_BALANCE)
    def get_gold_balance(self):
        """ Returns the current gold balance. """
        balance = self.account.balances['gold']

        return PegasusUtil_pb2.GoldBalance(
            capped_balance=balance,
            bonus_balance=0,
            cap=999999,
            cap_warning=999999)

    @_handles(PegasusUtil_pb2.GetAccountInfo.ARCANE_DUST_BALANCE)
    def get_arcane_dust_balance(self):
        """ Returns the current arcane dust balance. """
        balance = self.account.balances['arcane_dust']
        return PegasusUtil_pb2.ArcaneDustBalance(balance=balance)

    @_handles(PegasusUtil_pb2.GetAccountInfo.NOTICES)
    def get_notices(self):
        # TODO: currently not implemented
        return PegasusUtil_pb2.ProfileNotices()

    @_handles(PegasusUtil_pb2.GetAccountInfo.REWARD_PROGRESS)
    def get_reward_progress(self):
        # TODO: currently not implemented
        return PegasusUtil_pb2.RewardProgress(
            season_end=PegasusShared_pb2.Date(
                year=2015,
                month=4,
                day=30,
                hours=22,
                min=0,
                sec=0
            ),
            wins_per_gold=3,
            gold_per_reward=10,
            max_gold_per_day=100,
            season_number=18,
            xp_solo_limit=60,
            max_hero_level=60,
            next_quest_cancel=PegasusShared_pb2.Date(
                year=2015,
                month=4,
                day=1,
                hours=0,
                min=0,
                sec=0
            ),
            event_timing_mod=-0.0833333283662796
        )

    @_handles(PegasusUtil_pb2.GetAccountInfo.PLAYER_RECORD)
    def get_player_records(self):
        # TODO: currently not implemented
        return PegasusUtil_pb2.PlayerRecords()

    @_handles(PegasusUtil_pb2.GetAccountInfo.CLIENT_OPTIONS)
    def get_client_options(self):
        opts = PegasusUtil_pb2.ClientOptions()

        for name, value in self.account.options:
            opt = opts.options.add(index=GameOption[name])
            setattr(opt, value['type'], value['payload'])

        return opts

    @_handles(PegasusUtil_pb2.GetAccountInfo.COLLECTION)
    def get_collection(self):
        coll = PegasusUtil_pb2.Collection()
        for card_item in self.account.collection.cards['list']:
            entry = coll.stacks.add()
            entry.count = card_item['count']
            entry.num_seen = entry.count

            entry.card_def.asset = card_item['card_id']
            if card_item.get('premium', 0) > 0:
                entry.card_def.premium = card_item['premium']

            entry.latest_insert_date.year = 2010
            entry.latest_insert_date.month = 1
            entry.latest_insert_date.day = 1
            entry.latest_insert_date.hours = 0
            entry.latest_insert_date.min = 0
            entry.latest_insert_date.sec = 0

        return coll

    @_handles(PegasusUtil_pb2.GetAccountInfo.HERO_XP)
    def get_hero_xp(self):
        # TODO: not implemented
        xp = PegasusUtil_pb2.HeroXP()

        for i in range(2,11):
            xp.xp_infos.add(class_id=i,level=60,curr_xp=1480,max_xp=1480)

        return xp

    @_handles(PegasusUtil_pb2.GetAccountInfo.BOOSTER_TALLY)
    def get_booster_tally(self):
        # TODO: not implemented
        return PegasusUtil_pb2.BoosterTallyList()

    @_handles(PegasusUtil_pb2.GetAccountInfo.DECK_LIMIT)
    def get_profile_deck_limit(self):
        # TODO: not implemented
        return PegasusUtil_pb2.ProfileDeckLimit(deck_limit=9)

    @_handles(PegasusUtil_pb2.GetAccountInfo.MASSIVE_LOGIN)
    def get_massive_login(self):
        return PegasusUtil_pb2.MassiveLoginReply(
            profile_progress=self.get_campaign_info(),
            medal_info=self.get_medal_info(),
            deck_list=self.get_deck_list(),
            gold_balance=self.get_gold_balance(),
            arcane_dust_balance=self.get_arcane_dust_balance(),
            profile_deck_limit=self.get_profile_deck_limit(),
            reward_progress=self.get_reward_progress(),
            player_records=self.get_player_records(),
            card_backs=self.get_card_backs()
        )
