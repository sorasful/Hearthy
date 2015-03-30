from hearthy.protocol.type_builder import Builder
from hearthy.protocol import game_utilities, pegasus_shared, mtypes

def _anon():
    builder = Builder()

    builder.add('AssetsVersionResponse', [
        (1, 'version', 'int32')
    ])

    builder.add('UpdateLogin', [
        (1, 'reply_required', 'bool')
    ])

    builder.add('UpdateLoginComplete', [])

    builder.add('SetProgress', [
        (1, 'value', 'int64[]')
    ])

    builder.add('SetProgressResponse', [
        (1, 'result', 'enum'),
        (2, 'progress', 'int64')
    ])

    builder.add('CheckAccountLicenses', [])
    builder.add('CheckGameLicense', [])
    builder.add('CheckLicensesResponse', [
        (1, 'accountLevel', 'bool'),
        (2, 'success', 'bool'),
    ])

    builder.add('GetAccountInfo', [
        (1, 'request', 'enum')
    ])

    builder.add('AdventureOptions', [
        (1, 'adventure_id', 'int32'),
        (2, 'options', 'uint64')
    ])

    builder.add('ProfileProgress', [
        (1, 'progress', 'int64'),
        (2, 'best_forge', 'int32'),
        (3, 'last_forge', pegasus_shared.Date),
        (4, 'display_banner', 'int32'),
        (5, 'adventure_options', 'AdventureOptions[]')
    ])

    builder.add('MedalInfo', [
        (3, 'season_wins', 'int32'),
        (6, 'stars', 'int32'),
        (7, 'streak', 'int32'),
        (8, 'star_level', 'int32'),
        (9, 'level_start', 'int32'),
        (10, 'level_end', 'int32'),
        (11, 'can_lose', 'bool'),
        (13, 'legend_rank', 'int32')
    ])

    builder.add('DeckList', [
        (1, 'decks', [pegasus_shared.DeckInfo])
    ])

    builder.add('ProfileDeckLimit', [
        (1, 'deck_limit', 'int32')
    ])

    builder.add('GoldBalance', [
        (1, 'capped_balance', 'int64'),
        (2, 'bonus_balance', 'int64'),
        (3, 'cap', 'int64'),
        (4, 'cap_warning', 'int64')
    ])

    builder.add('ArcaneDustBalance', [
        (1, 'balance', 'int64')
    ])

    builder.add('RewardProgress', [
        (1, 'season_end', pegasus_shared.Date),
        (2, 'wins_per_gold', 'int32'),
        (3, 'gold_per_reward', 'int32'),
        (4, 'max_gold_per_day', 'int32'),
        (5, 'season_number', 'int32'),
        (8, 'pack_id', 'int32'),
        (9, 'xp_solo_limit', 'int32'),
        (10, 'max_hero_level', 'int32'),
        (11, 'next_quest_cancel', pegasus_shared.Date),
        (12, 'event_timing_mod', 'float')
    ])

    builder.add('PlayerRecord', [
        (1, 'type', 'int32'),
        (2, 'data', 'int32'),
        (3, 'wins', 'int32'),
        (4, 'losses', 'int32'),
        (5, 'ties', 'int32')
    ])

    builder.add('PlayerRecords', [
        (1, 'records', 'PlayerRecord[]')
    ])

    builder.add('CardBacks', [
        (1, 'default_card_back', 'int32'),
        (2, 'card_backs', 'int32[]')
    ])

    builder.add('SpecialEventTiming', [
        (1, 'event', 'string'),
        (2, 'start', 'uint64'),
        (3, 'end', 'uint64')
    ])

    builder.add("ClientTracking", [
        (1, "info", "string"),
    ])

    builder.add('MassiveLoginReply', [
        (1, 'profile_progress', 'ProfileProgress'),
        (2, 'medal_info', 'MedalInfo'),
        (3, 'deck_list', 'DeckList'),
        (4, 'profile_deck_limit', 'ProfileDeckLimit'),
        (5, 'gold_balance', 'GoldBalance'),
        (6, 'arcane_dust_balance', 'ArcaneDustBalance'),
        (7, 'reward_progress', 'RewardProgress'),
        (8, 'player_records', 'PlayerRecords'),
        (9, 'card_backs', 'CardBacks'),
        (10, 'special_event_timing', 'SpecialEventTiming[]')
    ])

    builder.build(globals(), __name__)

_anon()

AssetsVersionResponse.packet_id = 0x130
UpdateLogin.packet_id = 0xcd
UpdateLoginComplete.packet_id = 0x133
ClientTracking.packet_id = 228
SetProgress.packet_id = 230
SetProgressResponse.packet_id = 0x128
CheckGameLicense.packet_id = 276
CheckAccountLicenses.packet_id = 267
CheckLicensesResponse.packet_id = 277
GetAccountInfo.packet_id = 0xc9
MassiveLoginReply.packet_id = 300

def to_client_response_pb2(packet):
    return game_utilities.ClientResponse(attributes=[
        mtypes.Attribute(name='?', value=mtypes.BnetVariant(intval=packet.ID)),
        mtypes.Attribute(name='?', value=mtypes.BnetVariant(blobval=packet.SerializeToString()))
    ])

def to_client_response(packet):
    buf = bytearray(1024)
    end = packet.encode_buf(buf)

    packet_id = packet.packet_id

    return game_utilities.ClientResponse(attributes=[
        mtypes.Attribute(name='?',value=mtypes.BnetVariant(intval=packet_id)),
        mtypes.Attribute(name='?',value=mtypes.BnetVariant(blobval=bytes(buf[:end])))
    ])
