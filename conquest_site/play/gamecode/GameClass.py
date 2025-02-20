from . import PlayerClass
import random
from .Phases import DeployPhase, CommandPhase, CombatPhase, HeadquartersPhase
from . import FindCard


def create_planets(planet_array_objects):
    planet_names = []
    for i in range(10):
        string = planet_array_objects[i].get_name()
        planet_names.append(string)
    random.shuffle(planet_names)
    planets_in_play_return = []
    for i in range(7):
        planets_in_play_return.append(planet_names[i])
    return planets_in_play_return


class Game:
    def __init__(self, game_id, player_one_name, player_two_name, card_array, planet_array):
        self.game_sockets = []
        self.card_array = card_array
        self.planet_cards_array = planet_array
        self.game_id = game_id
        self.name_1 = player_one_name
        self.name_2 = player_two_name
        self.current_game_event_p1 = ""
        self.current_game_event_p1 = ""
        self.stored_deck_1 = None
        self.stored_deck_2 = None
        self.p1 = PlayerClass.Player(player_one_name, 1, card_array, self)
        self.p2 = PlayerClass.Player(player_two_name, 2, card_array, self)
        self.phase = "DEPLOY"
        self.round_number = 0
        self.current_board_state = ""
        self.running = True
        self.planet_array = ["Barlus", "Osus IV", "Ferrin", "Elouith", "Iridial", "Y'varn", "Atrox Prime"]
        self.planets_in_play_array = [True, True, True, True, True, False, False]
        self.player_with_deploy_turn = self.name_1
        self.number_with_deploy_turn = "1"
        self.card_pos_to_deploy = -1
        self.last_planet_checked_for_battle = -1
        self.number_with_combat_turn = "1"
        self.player_with_combat_turn = self.name_1
        self.attacker_planet = -1
        self.attacker_position = -1
        self.defender_planet = -1
        self.defender_position = -1

    async def joined_requests_graphics(self):
        await self.p1.send_hand()
        await self.p2.send_hand()
        await self.p1.send_hq()
        await self.p2.send_hq()
        await self.send_planet_array()
        await self.p1.send_units_at_all_planets()
        await self.p2.send_units_at_all_planets()
        await self.p1.send_resources()
        await self.p2.send_resources()

    async def send_planet_array(self):
        planet_string = "GAME_INFO/PLANETS/"
        for i in range(len(self.planet_array)):
            if self.planets_in_play_array[i]:
                planet_string += self.planet_array[i]
            else:
                planet_string += "CardbackRotated"
            if i != 6:
                planet_string += "/"
        await self.game_sockets[0].receive_game_update(planet_string)

    async def update_game_event(self, name, game_update_string):
        print(game_update_string)
        if self.phase == "SETUP":
            await self.game_sockets[0].receive_game_update("Buttons can't be pressed in setup")
        elif self.phase == "DEPLOY":
            print("Need to run deploy turn code.")
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    print("Need to pass")
                    if name == self.player_with_deploy_turn:
                        if self.number_with_deploy_turn == "1":
                            self.number_with_deploy_turn = "2"
                            self.player_with_deploy_turn = self.name_2
                            self.p1.has_passed = True
                        else:
                            self.number_with_deploy_turn = "1"
                            self.player_with_deploy_turn = self.name_1
                            self.p2.has_passed = True
                    if self.p1.has_passed and self.p2.has_passed:
                        print("Both passed, move to warlord movement.")
                        self.phase = "COMMAND"
            if len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    if name == self.player_with_deploy_turn:
                        if game_update_string[1] == self.number_with_deploy_turn:
                            print("Deploy card in hand at pos", game_update_string[2])
                            self.card_pos_to_deploy = int(game_update_string[2])
                            if self.number_with_deploy_turn == "1":
                                played_support = self.p1.play_card_if_support(self.card_pos_to_deploy)
                                if played_support == "SUCCESS/Support":
                                    await self.p1.send_hand()
                                    await self.p1.send_hq()
                                    await self.p1.send_resources()
                                    if not self.p2.has_passed:
                                        self.player_with_deploy_turn = self.name_2
                                        self.number_with_deploy_turn = "2"
                            elif self.number_with_deploy_turn == "2":
                                played_support = self.p2.play_card_if_support(self.card_pos_to_deploy)
                                if played_support == "SUCCESS/Support":
                                    await self.p2.send_hand()
                                    await self.p2.send_hq()
                                    await self.p2.send_resources()
                                    if not self.p1.has_passed:
                                        self.player_with_deploy_turn = self.name_1
                                        self.number_with_deploy_turn = "1"

            elif len(game_update_string) == 2:
                if name == self.player_with_deploy_turn:
                    if self.card_pos_to_deploy != -1:
                        print("Deploy card at planet", game_update_string[1])
                        if self.number_with_deploy_turn == "1":
                            print("P1 plays card")
                            played_card = self.p1.play_card(int(game_update_string[1]),
                                                            position_hand=self.card_pos_to_deploy)
                            if played_card == "SUCCESS":
                                await self.p1.send_hand()
                                await self.p1.send_units_at_planet(int(game_update_string[1]))
                                await self.p1.send_resources()
                                self.card_pos_to_deploy = -1
                                if not self.p2.has_passed:
                                    self.player_with_deploy_turn = self.name_2
                                    self.number_with_deploy_turn = "2"
                        if self.number_with_deploy_turn == "2":
                            print("P2 plays card")
                            played_card = self.p2.play_card(int(game_update_string[1]),
                                                            position_hand=self.card_pos_to_deploy)
                            if played_card == "SUCCESS":
                                await self.p2.send_hand()
                                await self.p2.send_units_at_planet(int(game_update_string[1]))
                                await self.p2.send_resources()
                                self.card_pos_to_deploy = -1
                                if not self.p1.has_passed:
                                    self.player_with_deploy_turn = self.name_1
                                    self.number_with_deploy_turn = "1"
        elif self.phase == "COMMAND":
            print("Run warlord assignment code.")
            if len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    print("Save warlord to this planet")
                    if name == self.name_1:
                        if not self.p1.committed_warlord:
                            self.p1.warlord_commit_location = int(game_update_string[1])
                            self.p1.committed_warlord = True
                    else:
                        if not self.p2.committed_warlord:
                            self.p2.warlord_commit_location = int(game_update_string[1])
                            self.p2.committed_warlord = True
                    if self.p1.committed_warlord and self.p2.committed_warlord:
                        print("Both warlords need to be committed.")
                        print(self.p1.warlord_commit_location, self.p2.warlord_commit_location)
                        self.p1.commit_warlord_to_planet()
                        self.p2.commit_warlord_to_planet()
                        await self.p1.send_hq()
                        await self.p2.send_hq()
                        await self.send_planet_array()
                        await self.p1.send_units_at_all_planets()
                        await self.p2.send_units_at_all_planets()
                        self.resolve_command_struggle()
                        await self.p1.send_hand()
                        await self.p2.send_hand()
                        await self.p1.send_resources()
                        await self.p2.send_resources()
                        self.phase = "COMBAT"
                        self.check_battle(self.round_number)
                        self.last_planet_checked_for_battle = self.round_number
        elif self.phase == "COMBAT":
            if len(game_update_string) == 4:
                print("Unit clicked on.")
                if game_update_string[0] == "IN_PLAY":
                    if name == self.player_with_combat_turn:
                        if self.attacker_position == -1:
                            if game_update_string[1] == self.number_with_combat_turn:
                                chosen_planet = int(game_update_string[2])
                                chosen_unit = int(game_update_string[3])
                                valid_unit = False
                                if chosen_planet == self.last_planet_checked_for_battle:
                                    if self.number_with_combat_turn == "1":
                                        is_ready = self.p1.check_ready_pos(chosen_planet, chosen_unit)
                                        if is_ready:
                                            print("Unit ready, can be used")
                                            valid_unit = True
                                        else:
                                            print("Unit not ready")
                                    if self.number_with_combat_turn == "2":
                                        is_ready = self.p2.check_ready_pos(chosen_planet, chosen_unit)
                                        if is_ready:
                                            print("Unit ready, can be used")
                                            valid_unit = True
                                        else:
                                            print("Unit not ready")
                                if valid_unit:
                                    self.attacker_planet = chosen_planet
                                    self.attacker_position = chosen_unit
                                    print("Attacker:", self.attacker_planet, self.attacker_position)
                                    if self.number_with_combat_turn == "1":
                                        self.p1.exhaust_given_pos(self.attacker_planet, self.attacker_position)
                                        await self.p1.send_units_at_planet(chosen_planet)
                                    elif self.number_with_combat_turn == "2":
                                        self.p2.exhaust_given_pos(self.attacker_planet, self.attacker_position)
                                        await self.p2.send_units_at_planet(chosen_planet)
                        elif self.defender_position == -1:
                            if game_update_string[1] != self.number_with_combat_turn:
                                self.defender_planet = int(game_update_string[2])
                                self.defender_position = int(game_update_string[3])
                                print("Defender:", self.defender_planet, self.defender_position)
                                if self.number_with_combat_turn == "1":
                                    attack_value = self.p1.get_attack_given_pos(self.attacker_planet,
                                                                                self.attacker_position)
                                    unit_dead = self.p2.assign_damage_to_pos(self.defender_planet,
                                                                             self.defender_position,
                                                                             damage=attack_value, can_shield=False)
                                    await self.p2.send_units_at_planet(self.defender_planet)
                                elif self.number_with_combat_turn == "2":
                                    attack_value = self.p2.get_attack_given_pos(self.attacker_planet,
                                                                                self.attacker_position)
                                    unit_dead = self.p1.assign_damage_to_pos(self.defender_planet,
                                                                             self.defender_position,
                                                                             damage=attack_value, can_shield=False)
                                    await self.p1.send_units_at_planet(self.defender_planet)

    def resolve_command_struggle(self):
        storage_command_struggle = [None, None, None, None, None, None, None]
        for i in range(len(self.planet_array)):
            if self.planets_in_play_array[i]:
                print("Resolve command struggle at:", self.planet_array[i])
                storage_command_struggle[i] = self.resolve_command_struggle_at_planet(i)
        for i in range(len(storage_command_struggle)):
            if storage_command_struggle[i] is not None:
                if storage_command_struggle[i][0] == "1":
                    self.p1.add_resources(storage_command_struggle[i][1])
                    for _ in range(storage_command_struggle[i][2]):
                        self.p1.draw_card()
                else:
                    self.p2.add_resources(storage_command_struggle[i][1])
                    for _ in range(storage_command_struggle[i][2]):
                        self.p2.draw_card()

    def resolve_command_struggle_at_planet(self, planet_id):
        command_p1 = self.p1.count_command_at_planet(planet_id)
        command_p2 = self.p2.count_command_at_planet(planet_id)
        if command_p1 > command_p2:
            print("P1 wins command")
            chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
            resources_won = chosen_planet.get_resources()
            cards_won = chosen_planet.get_cards()
            ret_val = ["1", resources_won, cards_won]
            return ret_val
        elif command_p2 > command_p1:
            print("P2 wins command")
            chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
            resources_won = chosen_planet.get_resources()
            cards_won = chosen_planet.get_cards()
            ret_val = ["2", resources_won, cards_won]
            return ret_val

    def check_battle(self, planet_id):
        if planet_id == self.round_number:
            print("First planet: battle occurs at ", planet_id)
            return 1
        if self.p1.check_for_warlord(planet_id):
            print("p1 warlord present. Battle at ", planet_id)
            return 1
        elif self.p2.check_for_warlord(planet_id):
            print("p2 warlord present. Battle at ", planet_id)
            return 1
        return 0
