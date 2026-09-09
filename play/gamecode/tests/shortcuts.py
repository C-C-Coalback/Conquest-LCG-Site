async def standard_setup(test_game):
    await test_game.update_game_event("P1", ["CHOICE", "0"])
    await test_game.update_game_event("P2", ["CHOICE", "0"])
    test_game.p1.cards = []
    test_game.p2.cards = []


async def skip_to_battle_first_planet(test_game, tyranid_1=False, tyranid_2=False):
    await standard_setup(test_game)
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