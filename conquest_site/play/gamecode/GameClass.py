from . import PlayerClass
import random
from .Phases import DeployPhase, CommandPhase, CombatPhase, HeadquartersPhase
from . import FindCard
import threading


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
        self.p1_has_warlord = False
        self.p2_has_warlord = False
        self.number_with_initiative = "1"
        self.player_with_initiative = self.name_1
        self.number_reset_combat_turn = "1"
        self.player_reset_combat_turn = self.name_1
        self.number_who_is_shielding = None
        self.player_who_is_shielding = None
        self.planet_of_damaged_unit = None
        self.position_of_damaged_unit = None
        self.damage_on_unit_before_new_damage = None
        self.mode = "Normal"
        self.stored_mode = self.mode
        self.condition_main_game = threading.Condition()
        self.condition_sub_game = threading.Condition()
        self.planet_aiming_reticle_active = False
        self.planet_aiming_reticle_position = -1
        self.number_of_units_left_to_suffer_damage = 0
        self.next_unit_to_suffer_damage = -1
        self.resources_need_sending_outside_normal_sends = False
        self.actions_allowed = True
        self.player_with_action = ""

    async def joined_requests_graphics(self, name):
        self.condition_main_game.acquire()
        await self.p1.send_hand()
        await self.p2.send_hand()
        await self.p1.send_hq()
        await self.p2.send_hq()
        await self.send_planet_array()
        await self.p1.send_units_at_all_planets()
        await self.p2.send_units_at_all_planets()
        await self.p1.send_resources()
        await self.p2.send_resources()
        await self.p1.send_discard()
        await self.p2.send_discard()
        await self.send_info_box()
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def send_info_box(self):
        info_string = "GAME_INFO/INFO_BOX/"
        if self.phase == "DEPLOY":
            info_string += self.player_with_deploy_turn + "/"
        elif self.phase == "COMBAT":
            if self.mode == "SHIELD":
                info_string += self.player_who_is_shielding + "/"
            else:
                info_string += self.player_with_combat_turn + "/"
        else:
            info_string += "Unspecified/"
        info_string += "Phase: " + self.phase + "/"
        info_string += "Mode: " + self.mode + "/"
        if self.phase == "DEPLOY":
            info_string += "Active: " + self.player_with_deploy_turn + "/"
        elif self.phase == "COMBAT":
            if self.mode == "SHIELD":
                info_string += "Active: " + self.player_who_is_shielding + "/"
            else:
                info_string += "Active: " + self.player_with_combat_turn + "/"
        await self.game_sockets[0].receive_game_update(info_string)

    async def send_planet_array(self):
        planet_string = "GAME_INFO/PLANETS/"
        if not self.planet_aiming_reticle_active:
            for i in range(len(self.planet_array)):
                if self.planets_in_play_array[i]:
                    planet_string += self.planet_array[i]
                else:
                    planet_string += "CardbackRotated"
                if i != 6:
                    planet_string += "/"
            await self.game_sockets[0].receive_game_update(planet_string)
        else:
            for i in range(len(self.planet_array)):
                if self.planets_in_play_array[i]:
                    planet_string += self.planet_array[i]
                else:
                    planet_string += "CardbackRotated"
                if self.planet_aiming_reticle_position == i:
                    planet_string += "|red"
                if i != 6:
                    planet_string += "/"
            await self.game_sockets[0].receive_game_update(planet_string)

    async def update_game_event_deploy_section(self, name, game_update_string):
        print("Need to run deploy turn code.")
        print(self.player_with_deploy_turn, self.number_with_deploy_turn)
        print(name == self.player_with_deploy_turn)
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
                await self.send_info_box()
        if len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                if name == self.player_with_deploy_turn:
                    print(game_update_string[1] == self.number_with_deploy_turn)
                    if game_update_string[1] == self.number_with_deploy_turn:
                        print("Deploy card in hand at pos", game_update_string[2])
                        self.card_pos_to_deploy = int(game_update_string[2])
                        if self.number_with_deploy_turn == "1":
                            primary_player = self.p1
                            secondary_player = self.p2
                        else:
                            primary_player = self.p2
                            secondary_player = self.p1
                        card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
                        if card.get_card_type() == "Support":
                            played_support = primary_player.play_card_if_support(self.card_pos_to_deploy,
                                                                                 already_checked=True, card=card)
                            if played_support == "SUCCESS/Support":
                                await primary_player.send_hand()
                                await primary_player.send_hq()
                                await primary_player.send_resources()
                                if not secondary_player.has_passed:
                                    self.player_with_deploy_turn = secondary_player.get_name_player()
                                    self.number_with_deploy_turn = secondary_player.get_number()
                                    await self.send_info_box()
                        elif card.get_card_type() == "Army":
                            primary_player.aiming_reticle_color = "blue"
                            primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                            await primary_player.send_hand()
                        else:
                            self.card_pos_to_deploy = -1
        elif len(game_update_string) == 2:
            if name == self.player_with_deploy_turn:
                if self.card_pos_to_deploy != -1:
                    print("Deploy card at planet", game_update_string[1])
                    if self.number_with_deploy_turn == "1":
                        primary_player = self.p1
                        secondary_player = self.p2
                    else:
                        primary_player = self.p2
                        secondary_player = self.p1
                    played_card = primary_player.play_card(int(game_update_string[1]),
                                                           position_hand=self.card_pos_to_deploy)
                    if played_card == "SUCCESS":
                        await primary_player.send_hand()
                        await primary_player.send_units_at_planet(int(game_update_string[1]))
                        await primary_player.send_resources()
                        if not secondary_player.has_passed:
                            self.player_with_deploy_turn = secondary_player.get_name_player()
                            self.number_with_deploy_turn = secondary_player.get_number()
                            await self.send_info_box()
                    self.card_pos_to_deploy = -1
                    primary_player.aiming_reticle_color = None
                    primary_player.aiming_reticle_coords_hand = None
                    await primary_player.send_hand()
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def update_game_event_command_section(self, name, game_update_string):
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
                    self.set_battle_initiative()
                    self.planet_aiming_reticle_active = True
                    self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                    await self.send_planet_array()
                    self.p1.has_passed = False
                    self.p2.has_passed = False
                    await self.send_info_box()
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def update_game_event_combat_section(self, name, game_update_string):
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if self.mode == "SHIELD":
                    if name == self.player_who_is_shielding:
                        await self.resolve_shield_of_unit(name, -1)
                elif name == self.player_with_combat_turn:
                    if self.number_with_combat_turn == "1":
                        self.number_with_combat_turn = "2"
                        self.player_with_combat_turn = self.name_2
                        self.p1.has_passed = True
                        self.reset_combat_positions()
                    else:
                        self.number_with_combat_turn = "1"
                        self.player_with_combat_turn = self.name_1
                        self.p2.has_passed = True
                        self.reset_combat_positions()
                    if self.p1.has_passed and self.p2.has_passed:
                        if self.mode == "Normal":
                            print("Both players passed, need to run combat round end.")
                            self.p1.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p2.ready_all_at_planet(self.last_planet_checked_for_battle)
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.reset_combat_turn()
                            await self.p1.send_units_at_planet(self.last_planet_checked_for_battle)
                            await self.p2.send_units_at_planet(self.last_planet_checked_for_battle)
                            self.mode = "RETREAT"
                            await self.check_combat_end(name)
                        elif self.mode == "RETREAT":
                            self.p1.has_passed = False
                            self.p2.has_passed = False
                            self.reset_combat_turn()
                            self.mode = "Normal"
                            await self.check_combat_end(name)
                    else:
                        await self.send_info_box()
        elif len(game_update_string) == 2:
            if game_update_string[0] == "PLANETS":
                if self.mode == "Normal":
                    if name == self.player_with_combat_turn:
                        chosen_planet = int(game_update_string[1])
                        if chosen_planet == self.last_planet_checked_for_battle:
                            if self.attacker_position != -1:
                                if self.number_with_combat_turn == "1":
                                    primary_player = self.p1
                                    secondary_player = self.p2
                                else:
                                    primary_player = self.p2
                                    secondary_player = self.p1
                                amount_aoe = primary_player.cards_in_play[chosen_planet + 1][
                                    self.attacker_position].get_area_effect()
                                if amount_aoe > 0:
                                    print("Player needs to suffer area effect (", str(amount_aoe), ")")
                                    secondary_player.suffer_area_effect(chosen_planet, amount_aoe)
                                    self.number_of_units_left_to_suffer_damage = \
                                        secondary_player.get_number_of_units_at_planet(chosen_planet)
                                    if self.number_of_units_left_to_suffer_damage > 0:
                                        secondary_player.set_aiming_reticle_in_play(chosen_planet, 0, "red")
                                        for i in range(1, self.number_of_units_left_to_suffer_damage):
                                            secondary_player.set_aiming_reticle_in_play(chosen_planet, i, "blue")
                                    self.mode = "SHIELD"
                                    self.player_who_is_shielding = secondary_player.get_name_player()
                                    self.number_who_is_shielding = secondary_player.get_number()
                                    self.next_unit_to_suffer_damage = 0
                                    self.defender_position = self.next_unit_to_suffer_damage
                                    self.defender_planet = chosen_planet
                                    self.damage_on_unit_before_new_damage = amount_aoe
                                    await self.send_info_box()
                                    await secondary_player.send_units_at_planet(chosen_planet)
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                print("Card in hand clicked on")
                if self.mode == "SHIELD":
                    if name == self.player_who_is_shielding:
                        if game_update_string[1] == self.number_who_is_shielding:
                            hand_pos = int(game_update_string[2])
                            await self.resolve_shield_of_unit(name, hand_pos)
        elif len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                print("Unit clicked on.")
                if name == self.player_with_combat_turn:
                    if self.mode == "RETREAT":
                        if game_update_string[1] == self.number_with_combat_turn:
                            chosen_planet = int(game_update_string[2])
                            chosen_unit = int(game_update_string[3])
                            print("Retreat unit", chosen_planet, chosen_unit)
                            if chosen_planet == self.last_planet_checked_for_battle:
                                if self.number_with_combat_turn == "1":
                                    player = self.p1
                                else:
                                    player = self.p2
                                player.retreat_unit(chosen_planet, chosen_unit)
                                await player.send_units_at_planet(self.last_planet_checked_for_battle)
                                await player.send_hq()
                    elif self.attacker_position == -1:
                        if game_update_string[1] == self.number_with_combat_turn:
                            chosen_planet = int(game_update_string[2])
                            chosen_unit = int(game_update_string[3])
                            valid_unit = False
                            if chosen_planet == self.last_planet_checked_for_battle:
                                if self.number_with_combat_turn == "1":
                                    player = self.p1
                                else:
                                    player = self.p2
                                is_ready = player.check_ready_pos(chosen_planet, chosen_unit)
                                if is_ready:
                                    print("Unit ready, can be used")
                                    valid_unit = True
                                    player.set_aiming_reticle_in_play(chosen_planet, chosen_unit, "blue")
                                else:
                                    print("Unit not ready")
                            if valid_unit:
                                self.attacker_planet = chosen_planet
                                self.attacker_position = chosen_unit
                                print("Attacker:", self.attacker_planet, self.attacker_position)
                                if self.number_with_combat_turn == "1":
                                    player = self.p1
                                else:
                                    player = self.p2
                                player.exhaust_given_pos(self.attacker_planet, self.attacker_position)
                                await player.send_units_at_planet(chosen_planet)
                    elif self.defender_position == -1:
                        if game_update_string[1] != self.number_with_combat_turn:
                            armorbane_check = False
                            self.defender_planet = int(game_update_string[2])
                            self.defender_position = int(game_update_string[3])
                            print("Defender:", self.defender_planet, self.defender_position)
                            if self.number_with_combat_turn == "1":
                                primary_player = self.p1
                                secondary_player = self.p2
                            else:
                                primary_player = self.p2
                                secondary_player = self.p1
                            attack_value = primary_player.get_attack_given_pos(self.attacker_planet,
                                                                               self.attacker_position)
                            if attack_value > 0:
                                att_flying = primary_player.get_flying_given_pos(self.attacker_planet,
                                                                                 self.attacker_position)
                                def_flying = secondary_player.get_flying_given_pos(self.defender_planet,
                                                                                   self.defender_position)
                                # Flying check
                                if def_flying and not att_flying:
                                    attack_value = attack_value / 2 + (attack_value % 2 > 0)
                                unit_dead = secondary_player.assign_damage_to_pos(self.defender_planet,
                                                                                  self.defender_position,
                                                                                  damage=attack_value)
                                armorbane_check = primary_player.get_armorbane_given_pos(self.attacker_planet,
                                                                                         self.attacker_position)
                                self.mode = "SHIELD"
                                self.player_who_is_shielding = secondary_player.get_name_player()
                                self.number_who_is_shielding = secondary_player.get_number()
                                self.planet_of_damaged_unit = self.defender_planet
                                self.position_of_damaged_unit = self.defender_position
                                self.damage_on_unit_before_new_damage = \
                                    secondary_player.get_damage_given_pos(self.defender_planet, self.defender_position)
                                secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                            self.defender_position, "red")
                                if armorbane_check and attack_value > 0:
                                    await self.resolve_shield_of_unit(secondary_player.get_name(), -1)
                            else:
                                primary_player.reset_aiming_reticle_in_play(self.attacker_planet,
                                                                            self.attacker_position)

                                await primary_player.send_units_at_planet(self.attacker_planet)
                            if not armorbane_check or attack_value < 1:
                                await secondary_player.send_units_at_planet(self.defender_planet)
                            if attack_value < 1:
                                self.reset_combat_positions()
                                self.number_with_combat_turn = secondary_player.get_number()
                                self.player_with_combat_turn = secondary_player.get_name_player()
                                name = secondary_player.get_name_player()
                            if not armorbane_check or attack_value < 1:
                                await self.send_info_box()
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def update_game_event_deploy_action_hand(self, name, game_update_string):
        print("Deploy special action, card in hand at pos", game_update_string[2])
        self.card_pos_to_deploy = int(game_update_string[2])
        if self.number_with_deploy_turn == "1":
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
        ability = card.get_ability()
        print(card.get_allowed_phases_while_in_hand(), self.phase)
        print(card.get_has_action_while_in_hand())
        if card.get_has_action_while_in_hand():
            if card.get_allowed_phases_while_in_hand() == self.phase or \
                    card.get_allowed_phases_while_in_hand() == "ALL":
                if primary_player.spend_resources(card.get_cost()):
                    if ability == "Promise of Glory":
                        print("Resolve Promise of Glory")
                        primary_player.summon_token_at_hq("Cultist", amount=2)
                        primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        await primary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                        await self.send_info_box()
                    else:
                        primary_player.add_resources(card.get_cost())
                        await self.game_sockets[0].receive_game_update(card.get_name() + "not "
                                                                                         "implemented")
        self.condition_sub_game.notify_all()
        self.condition_sub_game.release()

    async def update_game_event_action(self, name, game_update_string):
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                self.mode = self.stored_mode
                self.player_with_action = ""
                print("Canceled special action")
                await self.game_sockets[0].receive_game_update(name + " canceled their action request")
        elif len(game_update_string) == 2:
            pass
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                if self.phase == "DEPLOY":
                    if name == self.player_with_deploy_turn:
                        if game_update_string[1] == self.number_with_deploy_turn:
                            self.condition_sub_game.acquire()
                            await self.update_game_event_deploy_action_hand(name, game_update_string)
                            self.condition_sub_game.acquire()
                            self.condition_sub_game.notify_all()
                            self.condition_sub_game.release()
        elif len(game_update_string) == 4:
            pass
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def update_game_event(self, name, game_update_string):
        self.condition_main_game.acquire()
        print(game_update_string)
        if self.phase == "SETUP":
            await self.game_sockets[0].receive_game_update("Buttons can't be pressed in setup")
        elif len(game_update_string) == 1:
            if game_update_string[0] == "action-button":
                if self.actions_allowed and self.mode != "ACTION":
                    print("Need to run action code")
                    if self.phase == "DEPLOY":
                        if self.player_with_deploy_turn == name:
                            self.stored_mode = self.mode
                            self.mode = "ACTION"
                            self.player_with_action = name
                            print("Special deploy action")
                            await self.game_sockets[0].receive_game_update(name + " wants to take an action.")
                    else:
                        self.stored_mode = self.mode
                        self.mode = "ACTION"
                        self.player_with_action = name
                        print("Special action")
                        await self.game_sockets[0].receive_game_update(name + " wants to take an action.")
        if self.mode == "ACTION":
            await self.update_game_event_action(name, game_update_string)
        elif self.phase == "DEPLOY":
            await self.update_game_event_deploy_section(name, game_update_string)
        elif self.phase == "COMMAND":
            await self.update_game_event_command_section(name, game_update_string)
        elif self.phase == "COMBAT":
            await self.update_game_event_combat_section(name, game_update_string)
        else:
            self.condition_main_game.notify_all()
            self.condition_main_game.release()

    def reset_combat_positions(self):
        self.defender_position = -1
        self.defender_planet = -1
        self.attacker_position = -1
        self.attacker_planet = -1

    def reset_shielding_values(self):
        self.number_who_is_shielding = None
        self.player_who_is_shielding = None
        self.planet_of_damaged_unit = None
        self.position_of_damaged_unit = None
        self.damage_on_unit_before_new_damage = None

    def request_search_for_enemy_card_at_planet(self, number, planet, name_of_card, bloodied_relevant=False):
        if number == "1":
            is_present = self.p2.search_card_at_planet(planet, name_of_card, bloodied_relevant)
            return is_present
        elif number == "2":
            is_present = self.p1.search_card_at_planet(planet, name_of_card, bloodied_relevant)
            return is_present
        return None

    def request_number_of_enemy_units_at_planet(self, number, planet):
        if number == "1":
            count = self.p2.get_number_of_units_at_planet(planet)
            return count
        elif number == "2":
            count = self.p1.get_number_of_units_at_planet(planet)
            return count
        return None

    def add_resources_to_opponent(self, number, amount):
        self.resources_need_sending_outside_normal_sends = True
        if number == 1:
            self.p2.add_resources(amount)
        elif number == 2:
            self.p1.add_resources(amount)

    async def resolve_shield_of_unit(self, name, hand_pos):
        unit_dead = False
        print("Info shielding:", self.defender_planet, self.defender_position)
        if name == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        primary_player.reset_aiming_reticle_in_play(self.defender_planet, self.defender_position)
        shield_on_card = 0
        if hand_pos != -1:
            shield_on_card = primary_player.get_shields_given_pos(hand_pos)
            primary_player.discard_card_from_hand(hand_pos)
            await primary_player.send_hand()
            await primary_player.send_discard()
        amount_to_shield = shield_on_card
        primary_player.remove_damage_from_pos(self.defender_planet, self.defender_position,
                                              amount_to_shield)
        if primary_player.get_damage_given_pos(self.defender_planet, self.defender_position) < 0:
            primary_player.set_damage_given_pos(self.defender_planet, self.defender_position, 0)
        if primary_player.check_if_card_is_destroyed(self.defender_planet, self.defender_position):
            unit_dead = True
            primary_player.destroy_card_in_play(self.defender_planet, self.defender_position)
            if self.resources_need_sending_outside_normal_sends:
                await primary_player.send_resources()
                await secondary_player.send_resources()
                self.resources_need_sending_outside_normal_sends = False
            if primary_player.warlord_just_got_bloodied:
                primary_player.warlord_just_got_bloodied = False
                await primary_player.send_hq()
            await primary_player.send_discard()
        self.number_of_units_left_to_suffer_damage -= 1

        if self.number_of_units_left_to_suffer_damage <= 0:
            self.number_of_units_left_to_suffer_damage = 0
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_shielding_values()
            self.mode = "Normal"
        else:
            if not unit_dead:
                self.next_unit_to_suffer_damage += 1
            self.defender_position = self.next_unit_to_suffer_damage
            primary_player.set_aiming_reticle_in_play(self.defender_planet, self.defender_position, "red")

        await self.send_info_box()
        await primary_player.send_units_at_planet(self.attacker_planet)
        await secondary_player.send_units_at_planet(self.attacker_planet)
        if self.number_of_units_left_to_suffer_damage <= 0:
            self.reset_combat_positions()

    async def check_combat_end(self, name):
        p1_has_units = self.p1.check_if_units_present(self.last_planet_checked_for_battle)
        p2_has_units = self.p2.check_if_units_present(self.last_planet_checked_for_battle)
        if p1_has_units and p2_has_units:
            await self.send_info_box()
        else:
            if p1_has_units:
                print("Player 1 wins battle")
                if self.round_number == self.last_planet_checked_for_battle:
                    self.p1.retreat_all_at_planet(self.last_planet_checked_for_battle)
                    await self.p1.send_hq()
                    await self.p1.send_units_at_planet(self.last_planet_checked_for_battle)
                    self.p1.capture_planet(self.last_planet_checked_for_battle,
                                           self.planet_cards_array)
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                    await self.p1.send_victory_display()
            if p2_has_units:
                print("Player 2 wins battle")
                if self.round_number == self.last_planet_checked_for_battle:
                    self.p2.retreat_all_at_planet(self.last_planet_checked_for_battle)
                    await self.p2.send_hq()
                    await self.p2.send_units_at_planet(self.last_planet_checked_for_battle)
                    self.p2.capture_planet(self.last_planet_checked_for_battle,
                                           self.planet_cards_array)
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                    await self.p2.send_victory_display()
            if not p1_has_units and not p2_has_units:
                if self.round_number == self.last_planet_checked_for_battle:
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
            self.planet_aiming_reticle_active = False
            self.planet_aiming_reticle_position = -1
            another_battle = self.find_next_planet_for_combat()
            if another_battle:
                self.set_battle_initiative()
                self.p1.has_passed = False
                self.p2.has_passed = False
                self.mode = "Normal"
                self.planet_aiming_reticle_active = True
                self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                await self.send_planet_array()
                await self.send_info_box()
            else:
                self.phase = "HEADQUARTERS"
                self.automated_headquarters_phase()
                self.reset_values_for_new_round()
                await self.p1.send_hq()
                await self.p1.send_units_at_all_planets()
                await self.p1.send_resources()
                await self.p1.send_hand()
                await self.p2.send_hq()
                await self.p2.send_units_at_all_planets()
                await self.p2.send_resources()
                await self.p2.send_hand()
                await self.send_planet_array()
                await self.send_info_box()

    def reset_values_for_new_round(self):
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.mode = "Normal"
        self.p1.committed_warlord = False
        self.p2.committed_warlord = False
        if self.player_with_initiative == self.name_1:
            self.player_with_deploy_turn = self.name_1
            self.number_with_deploy_turn = "1"
            self.player_with_combat_turn = self.name_1
            self.number_with_combat_turn = "1"
        else:
            self.player_with_deploy_turn = self.name_2
            self.number_with_deploy_turn = "2"
            self.player_with_combat_turn = self.name_2
            self.number_with_combat_turn = "2"

    def automated_headquarters_phase(self):
        self.p1.add_resources(4)
        self.p2.add_resources(4)
        self.p1.draw_card()
        self.p1.draw_card()
        self.p2.draw_card()
        self.p2.draw_card()
        self.p1.retreat_warlord()
        self.p2.retreat_warlord()
        self.p1.ready_all_in_play()
        self.p2.ready_all_in_play()
        if self.round_number == 0:
            self.planets_in_play_array[5] = True
        elif self.round_number == 1:
            self.planets_in_play_array[6] = True
        self.round_number += 1
        self.phase = "DEPLOY"
        self.swap_initiative()

    def swap_initiative(self):
        if self.player_with_initiative == self.name_1:
            self.player_with_initiative = self.name_2
            self.number_with_initiative = "2"
        else:
            self.player_with_initiative = self.name_1
            self.number_with_initiative = "1"

    def find_next_planet_for_combat(self):
        i = self.last_planet_checked_for_battle + 1
        while i < len(self.planet_array):
            if self.planets_in_play_array[i]:
                p1_has_warlord = self.p1.check_for_warlord(i)
                p2_has_warlord = self.p2.check_for_warlord(i)
                if p1_has_warlord or p2_has_warlord:
                    self.last_planet_checked_for_battle = i
                    return True
            i = i + 1
        return False

    def reset_combat_turn(self):
        self.player_with_combat_turn = self.player_reset_combat_turn
        self.number_with_combat_turn = self.number_reset_combat_turn

    def set_battle_initiative(self):
        self.p1_has_warlord = self.p1.check_for_warlord(self.last_planet_checked_for_battle)
        self.p2_has_warlord = self.p2.check_for_warlord(self.last_planet_checked_for_battle)
        if self.p1_has_warlord == self.p2_has_warlord:
            self.number_with_combat_turn = self.number_with_initiative
            self.player_with_combat_turn = self.player_with_initiative
            self.number_reset_combat_turn = self.number_with_combat_turn
            self.player_reset_combat_turn = self.player_with_combat_turn
        elif self.p1_has_warlord:
            self.number_with_combat_turn = "1"
            self.player_with_combat_turn = self.name_1
            self.number_reset_combat_turn = self.number_with_combat_turn
            self.player_reset_combat_turn = self.player_with_combat_turn
        elif self.p2_has_warlord:
            self.number_with_combat_turn = "2"
            self.player_with_combat_turn = self.name_2
            self.number_reset_combat_turn = self.number_with_combat_turn
            self.player_reset_combat_turn = self.player_with_combat_turn

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
