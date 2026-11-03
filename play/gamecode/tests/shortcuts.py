async def standard_setup(test_game, necron_1=False, necron_2=False):
    await test_game.update_game_event("P1", ["CHOICE", "0"])
    await test_game.update_game_event("P2", ["CHOICE", "0"])
    if necron_1:
        await test_game.update_game_event("P1", ["CHOICE", "0"])
    if necron_2:
        await test_game.update_game_event("P2", ["CHOICE", "0"])
    test_game.p1.cards = []
    test_game.p2.cards = []


async def skip_to_battle_first_planet(test_game, tyranid_1=False, tyranid_2=False, necron_1=False, necron_2=False):
    await standard_setup(test_game, necron_1=necron_1, necron_2=necron_2)
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])
    await test_game.update_game_event("P1", ["PLANETS", "0"])
    if tyranid_1:
        await test_game.update_game_event("P1", ["PLANETS", "1"])
    await test_game.update_game_event("P2", ["PLANETS", "0"])
    if tyranid_2:
        await test_game.update_game_event("P2", ["PLANETS", "1"])
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])
    test_game.p1.cards = []
    test_game.p2.cards = []
    await test_game.update_game_event("P1", ["pass-P1"])
    await test_game.update_game_event("P2", ["pass-P1"])

async def click_pass(test_game, player_num):
    if player_num == 1:
        await test_game.update_game_event("P1", ["pass-P1"])
    else:
        await test_game.update_game_event("P2", ["pass-P1"])

async def click_action(test_game, player_num):
    if player_num == 1:
        await test_game.update_game_event("P1", ["action-button"])
    else:
        await test_game.update_game_event("P2", ["action-button"])

async def click_planet(test_game, player_num, planet_num):
    if player_num == 1:
        await test_game.update_game_event("P1", ["PLANETS", str(planet_num)])
    else:
        await test_game.update_game_event("P2", ["PLANETS", str(planet_num)])

async def click_hand(test_game, player_num, hand_pos):
    if player_num == 1:
        await test_game.update_game_event("P1", ["HAND", "1", str(hand_pos)])
    else:
        await test_game.update_game_event("P2", ["HAND", "2", str(hand_pos)])

async def click_hq(test_game, player_num_clicking, player_num_hq, hq_pos):
    if player_num_clicking == 1:
        await test_game.update_game_event("P1", ["HQ", str(player_num_hq), str(hq_pos)])
    else:
        await test_game.update_game_event("P2", ["HQ", str(player_num_hq), str(hq_pos)])

async def click_in_play(test_game, player_num_clicking, player_num_play, planet_pos, unit_pos):
    if player_num_clicking == 1:
        await test_game.update_game_event("P1", ["IN_PLAY", str(player_num_play), str(planet_pos), str(unit_pos)])
    else:
        await test_game.update_game_event("P2", ["IN_PLAY", str(player_num_play), str(planet_pos), str(unit_pos)])

async def click_reserve(test_game, player_num_clicking, player_num_reserve, planet_pos, unit_pos):
    if player_num_clicking == 1:
        await test_game.update_game_event("P1", ["RESERVE", str(player_num_reserve), str(planet_pos), str(unit_pos)])
    else:
        await test_game.update_game_event("P2", ["RESERVE", str(player_num_reserve), str(planet_pos), str(unit_pos)])

async def click_discard(test_game, player_num_clicking, player_num_discard, discard_pos):
    if player_num_clicking == 1:
        await test_game.update_game_event("P1", ["IN_DISCARD", str(player_num_discard), str(discard_pos)])
    else:
        await test_game.update_game_event("P2", ["IN_DISCARD", str(player_num_discard), str(discard_pos)])

async def click_attachment_in_hq(test_game, player_num_clicking, player_num_hq, hq_pos, attachment_pos):
    if player_num_clicking == 1:
        await test_game.update_game_event("P1", ["ATTACHMENT", "HQ", str(player_num_hq), str(hq_pos), str(attachment_pos)])
    else:
        await test_game.update_game_event("P2", ["ATTACHMENT", "HQ", str(player_num_hq), str(hq_pos), str(attachment_pos)])

async def click_attachment_in_play(test_game, player_num_clicking, player_num_play, planet_pos, unit_pos, attachment_pos):
    if player_num_clicking == 1:
        await test_game.update_game_event("P1", ["ATTACHMENT", "IN_PLAY", str(player_num_play), str(planet_pos), str(unit_pos), str(attachment_pos)])
    else:
        await test_game.update_game_event("P2", ["ATTACHMENT", "IN_PLAY", str(player_num_play), str(planet_pos), str(unit_pos), str(attachment_pos)])

async def click_choice(test_game, player_num, choice_num):
    if player_num == 1:
        await test_game.update_game_event("P1", ["CHOICE", str(choice_num)])
    else:
        await test_game.update_game_event("P2", ["CHOICE", str(choice_num)])

async def click_search(test_game, player_num, search_pos):
    if player_num == 1:
        await test_game.update_game_event("P1", ["SEARCH", str(search_pos)])
    else:
        await test_game.update_game_event("P2", ["SEARCH", str(search_pos)])

async def dummy_click(test_game, player_num):
    if player_num == 1:
        await test_game.update_game_event("P1", [])
    else:
        await test_game.update_game_event("P2", [])