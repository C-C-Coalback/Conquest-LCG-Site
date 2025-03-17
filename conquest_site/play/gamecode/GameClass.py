import copy
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
        self.planet_array = []
        for i in range(7):
            self.planet_array.append(self.planet_cards_array[i].get_name())
        random.shuffle(self.planet_array)
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
        self.damage_on_units_list_before_new_damage = []
        self.mode = "Normal"
        self.stored_mode = self.mode
        self.condition_main_game = threading.Condition()
        self.condition_sub_game = threading.Condition()
        self.condition_discounting = threading.Condition()
        self.planet_aiming_reticle_active = False
        self.planet_aiming_reticle_position = -1
        self.number_of_units_left_to_suffer_damage = 0
        self.next_unit_to_suffer_damage = -1
        self.resources_need_sending_outside_normal_sends = False
        self.cards_need_sending_outside_normal_sends = False
        self.hqs_need_sending_outside_normal_sends = False
        self.actions_allowed = True
        self.player_with_action = ""
        self.action_chosen = ""
        self.available_discounts = 0
        self.discounts_applied = 0
        self.damage_for_unit_to_take_on_play = []
        self.faction_of_card_to_play = ""
        self.ranged_skirmish_active = False
        self.interrupt_active = False
        self.what_is_being_interrupted = ""
        self.damage_is_taken_one_at_a_time = False
        self.damage_left_to_take = 0
        self.positions_of_units_to_take_damage = []
        self.card_type_of_selected_card_in_hand = ""
        self.cards_in_search_box = []
        self.name_player_who_is_searching = "alex"
        self.number_who_is_searching = "1"
        self.what_to_do_with_searched_card = "DRAW"
        self.traits_of_searched_card = None
        self.card_type_of_searched_card = None
        self.faction_of_searched_card = None
        self.all_conditions_searched_card_required = False
        self.no_restrictions_on_chosen_card = False
        self.need_to_resolve_battle_ability = False
        self.battle_ability_to_resolve = ""
        self.player_resolving_battle_ability = ""
        self.number_resolving_battle_ability = -1
        self.choices_available = []
        self.name_player_making_choices = ""
        self.choice_context = ""

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
        await self.send_search()
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def send_search(self):
        if self.cards_in_search_box and self.name_player_who_is_searching:
            card_string = "/".join(self.cards_in_search_box)
            card_string = "GAME_INFO/SEARCH/" + self.name_player_who_is_searching + "/" + card_string
            await self.game_sockets[0].receive_game_update(card_string)
        elif self.choices_available and self.name_player_making_choices:
            card_string = "/".join(self.choices_available)
            card_string = "GAME_INFO/CHOICE/" + self.name_player_making_choices + "/" + card_string
            await self.game_sockets[0].receive_game_update(card_string)
        else:
            card_string = "GAME_INFO/SEARCH/"
            await self.game_sockets[0].receive_game_update(card_string)

    async def send_info_box(self):
        info_string = "GAME_INFO/INFO_BOX/"
        if self.phase == "DEPLOY":
            if self.mode == "SHIELD":
                info_string += self.player_who_is_shielding + "/"
            else:
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
            if self.mode == "SHIELD":
                info_string += "Active: " + self.player_who_is_shielding + "/"
            else:
                info_string += "Active: " + self.player_with_deploy_turn + "/"
        elif self.phase == "COMBAT":
            if self.ranged_skirmish_active:
                if self.mode == "SHIELD":
                    info_string += "Active (RANGED): " + self.player_who_is_shielding + "/"
                else:
                    info_string += "Active (RANGED): " + self.player_with_combat_turn + "/"
            else:
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
        if self.mode == "SHIELD":
            await self.shield_card_during_deploy(name, game_update_string)
        elif self.mode == "ACTION":
            await self.update_game_event_action(name, game_update_string)
        elif len(game_update_string) == 1:
            if game_update_string[0] == "action-button":
                if self.actions_allowed and self.mode != "ACTION":
                    print("Need to run action code")
                    if self.player_with_deploy_turn == name:
                        self.stored_mode = self.mode
                        self.mode = "ACTION"
                        self.player_with_action = name
                        print("Special deploy action")
                        await self.game_sockets[0].receive_game_update(name + " wants to take an action.")
                elif self.mode == "ACTION":
                    self.mode = self.stored_mode
                    self.stored_mode = ""
                    await self.game_sockets[0].receive_game_update(name + " cancelled their action request.")
            elif game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                print("Need to pass")
                if name == self.player_with_deploy_turn:
                    if self.mode == "ACTION":
                        self.mode = self.stored_mode
                        self.stored_mode = ""
                        await self.game_sockets[0].receive_game_update(name + " cancelled their action request.")
                    elif self.mode == "Normal":
                        if self.number_with_deploy_turn == "1":
                            self.number_with_deploy_turn = "2"
                            self.player_with_deploy_turn = self.name_2
                            self.p1.has_passed = True
                            self.discounts_applied = 0
                            self.available_discounts = 0
                        else:
                            self.number_with_deploy_turn = "1"
                            self.player_with_deploy_turn = self.name_1
                            self.p2.has_passed = True
                            self.discounts_applied = 0
                            self.available_discounts = 0
                    elif self.mode == "DISCOUNT":
                        print("Play card with not all discounts")
                        await self.deploy_card_routine(name, self.planet_aiming_reticle_position,
                                                       discounts=self.discounts_applied)
                if self.p1.has_passed and self.p2.has_passed:
                    print("Both passed, move to warlord movement.")
                    self.phase = "COMMAND"
                await self.send_info_box()
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                if self.mode == "DISCOUNT":
                    if name == self.player_with_deploy_turn:
                        if game_update_string[1] == self.number_with_deploy_turn:
                            if self.card_type_of_selected_card_in_hand == "Army":
                                if self.number_with_deploy_turn == "1":
                                    player = self.p1
                                else:
                                    player = self.p2
                                discount_received, damage = player.perform_discount_at_pos_hand(
                                    int(game_update_string[2]),
                                    self.faction_of_card_to_play
                                )
                                if discount_received > 0:
                                    self.discounts_applied += discount_received
                                    player.discard_card_from_hand(int(game_update_string[2]))
                                    if self.card_pos_to_deploy > int(game_update_string[2]):
                                        self.card_pos_to_deploy -= 1
                                    if damage > 0:
                                        self.damage_for_unit_to_take_on_play.append(damage)
                                    if self.discounts_applied >= self.available_discounts:
                                        await self.deploy_card_routine(name, self.planet_aiming_reticle_position,
                                                                       discounts=self.discounts_applied)
                                    else:
                                        await player.send_hand()
                                        await player.send_discard()
                elif self.mode == "Normal":
                    if name == self.player_with_deploy_turn:
                        print(game_update_string[1] == self.number_with_deploy_turn)
                        if game_update_string[1] == self.number_with_deploy_turn:
                            print("Deploy card in hand at pos", game_update_string[2])
                            previous_card_pos_to_deploy = self.card_pos_to_deploy
                            self.card_pos_to_deploy = int(game_update_string[2])
                            if self.number_with_deploy_turn == "1":
                                primary_player = self.p1
                                secondary_player = self.p2
                            else:
                                primary_player = self.p2
                                secondary_player = self.p1
                            card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
                            self.faction_of_card_to_play = card.get_faction()
                            if card.get_card_type() == "Support":
                                played_support = primary_player.play_card_if_support(self.card_pos_to_deploy,
                                                                                     already_checked=True, card=card)[0]
                                primary_player.aiming_reticle_color = ""
                                primary_player.aiming_reticle_coords_hand = -1
                                print(played_support)
                                if played_support == "SUCCESS":
                                    await primary_player.send_hand()
                                    await primary_player.send_hq()
                                    await primary_player.send_resources()
                                    if not secondary_player.has_passed:
                                        self.player_with_deploy_turn = secondary_player.get_name_player()
                                        self.number_with_deploy_turn = secondary_player.get_number()
                                        await self.send_info_box()
                                self.card_pos_to_deploy = -1
                            elif card.get_card_type() == "Army":
                                primary_player.aiming_reticle_color = "blue"
                                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                                self.card_type_of_selected_card_in_hand = "Army"
                                await primary_player.send_hand()
                            elif card.get_card_type() == "Attachment":
                                primary_player.aiming_reticle_color = "blue"
                                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                                self.card_type_of_selected_card_in_hand = "Attachment"
                                await primary_player.send_hand()
                            else:
                                self.card_type_of_selected_card_in_hand = ""
                                self.card_pos_to_deploy = previous_card_pos_to_deploy
            elif game_update_string[0] == "HQ":
                if name == self.player_with_deploy_turn:
                    if game_update_string[1] == self.number_with_deploy_turn:
                        if self.mode == "Normal":
                            await self.deploy_card_routine_attachment(name, game_update_string)
                        if self.mode == "DISCOUNT":
                            if self.number_with_deploy_turn == "1":
                                player = self.p1
                            else:
                                player = self.p2
                            if self.card_type_of_selected_card_in_hand == "Army":
                                discount_received = player.perform_discount_at_pos_hq(int(game_update_string[2]),
                                                                                      self.faction_of_card_to_play)
                                if discount_received > 0:
                                    self.discounts_applied += discount_received
                                if self.discounts_applied >= self.available_discounts:
                                    await self.deploy_card_routine(name, self.planet_aiming_reticle_position,
                                                                   discounts=self.discounts_applied)
                                    self.mode = "Normal"

        elif len(game_update_string) == 2:
            if name == self.player_with_deploy_turn:
                if self.card_pos_to_deploy != -1:
                    if self.number_with_deploy_turn == "1":
                        player = self.p1
                    else:
                        player = self.p2
                    self.available_discounts = player.search_hq_for_discounts(self.faction_of_card_to_play)
                    self.available_discounts += player.search_hand_for_discounts(self.faction_of_card_to_play)
                    if self.available_discounts > 0:
                        self.stored_mode = self.mode
                        self.mode = "DISCOUNT"
                        self.planet_aiming_reticle_position = int(game_update_string[1])
                        self.planet_aiming_reticle_active = True
                        await self.send_planet_array()
                        await self.send_info_box()
                    else:
                        await self.deploy_card_routine(name, game_update_string[1])
        elif len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if self.mode == "Normal":
                    if name == self.player_with_deploy_turn:
                        await self.deploy_card_routine_attachment(name, game_update_string)

    async def deploy_card_routine_attachment(self, name, game_update_string):
        if game_update_string[0] == "HQ":
            game_update_string = ["HQ", game_update_string[1], "-2", game_update_string[2]]
        print("Deploy attachment to: player ", game_update_string[1], "planet ", game_update_string[2],
              "position ", game_update_string[3])
        print("Position of card in hand: ", self.card_pos_to_deploy)
        if self.number_with_deploy_turn == "1":
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_gaining_attachment = self.p1
        else:
            player_gaining_attachment = self.p2
        card = primary_player.get_card_in_hand(self.card_pos_to_deploy)
        can_continue = False
        army_unit_as_attachment = False
        non_attachs_that_can_be_played_as_attach = ["Gun Drones", "Shadowsun's Stealth Cadre"]
        if card.get_card_type() == "Attachment":
            can_continue = True
        elif card.get_ability() in non_attachs_that_can_be_played_as_attach:
            can_continue = True
            army_unit_as_attachment = True
        if can_continue:
            limited = card.get_limited()
            print("Limited state of card:", limited)
            print("Name of card:", card.get_name())
            if not primary_player.can_play_limited and limited:
                pass
            else:
                if primary_player.get_number() == player_gaining_attachment.get_number():
                    print("Playing own card")
                    played_card = primary_player.play_attachment_card_to_in_play(card, int(game_update_string[2]),
                                                                                 int(game_update_string[3]),
                                                                                 army_unit_as_attachment=
                                                                                 army_unit_as_attachment)
                    enemy_card = False
                else:
                    played_card = False
                    if primary_player.spend_resources(int(card.get_cost())):
                        played_card = secondary_player.play_attachment_card_to_in_play(
                            card, int(game_update_string[2]), int(game_update_string[3]), not_own_attachment=True,
                            army_unit_as_attachment=army_unit_as_attachment)
                        if not played_card:
                            primary_player.add_resources(int(card.get_cost()))
                    enemy_card = True
                if played_card:
                    if limited:
                        primary_player.can_play_limited = False
                    primary_player.remove_card_from_hand(self.card_pos_to_deploy)
                    print("Succeeded (?) in playing attachment")
                    primary_player.aiming_reticle_coords_hand = -1
                    await primary_player.send_hand()
                    if enemy_card:
                        if game_update_string[2] == "-2":
                            await secondary_player.send_hq()
                        else:
                            await secondary_player.send_units_at_planet(int(game_update_string[2]))
                    else:
                        if game_update_string[2] == "-2":
                            await primary_player.send_hq()
                        else:
                            await primary_player.send_units_at_planet(int(game_update_string[2]))
                    await primary_player.send_resources()
                    if not secondary_player.has_passed:
                        self.player_with_deploy_turn = secondary_player.get_name_player()
                        self.number_with_deploy_turn = secondary_player.get_number()
                        await self.send_info_box()
                    self.card_pos_to_deploy = -1
                    self.mode = "Normal"
                    self.card_type_of_selected_card_in_hand = ""
                    self.faction_of_card_to_play = ""

    async def shield_card_during_deploy(self, name, game_update_string):
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.player_who_is_shielding:
                    await self.deploy_resolve_shield_of_unit(name, -1)
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                if name == self.player_who_is_shielding:
                    if game_update_string[1] == self.number_who_is_shielding:
                        await self.deploy_resolve_shield_of_unit(name, int(game_update_string[2]))

    async def deploy_resolve_shield_of_unit(self, name, hand_pos):
        unit_dead = False
        if name == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        primary_player.reset_aiming_reticle_in_play(self.planet_of_damaged_unit, self.position_of_damaged_unit)
        shield_on_card = 0
        if hand_pos != -1:
            shield_on_card = primary_player.get_shields_given_pos(hand_pos)
            primary_player.discard_card_from_hand(hand_pos)
            await primary_player.send_hand()
            await primary_player.send_discard()
        amount_to_shield = shield_on_card
        if self.damage_is_taken_one_at_a_time:
            if amount_to_shield > 1:
                amount_to_shield = 1
        primary_player.remove_damage_from_pos(self.planet_of_damaged_unit, self.position_of_damaged_unit,
                                              amount_to_shield)
        if primary_player.get_damage_given_pos(self.planet_of_damaged_unit, self.position_of_damaged_unit) < \
                self.damage_on_unit_before_new_damage:
            primary_player.set_damage_given_pos(self.planet_of_damaged_unit, self.position_of_damaged_unit,
                                                self.damage_on_unit_before_new_damage)
        if primary_player.check_if_card_is_destroyed(self.planet_of_damaged_unit, self.position_of_damaged_unit):
            unit_dead = True
            primary_player.destroy_card_in_play(self.planet_of_damaged_unit, self.position_of_damaged_unit)
            if self.resources_need_sending_outside_normal_sends:
                await primary_player.send_resources()
                await secondary_player.send_resources()
                self.resources_need_sending_outside_normal_sends = False
            if primary_player.warlord_just_got_bloodied:
                primary_player.warlord_just_got_bloodied = False
                await primary_player.send_hq()
            await primary_player.send_discard()
        will_switch_back_to_normal = True
        if not unit_dead and self.damage_is_taken_one_at_a_time:
            self.damage_left_to_take -= 1
            will_switch_back_to_normal = False
            primary_player.set_aiming_reticle_in_play(self.planet_of_damaged_unit,
                                                      self.position_of_damaged_unit, "red")
            if self.damage_left_to_take < 1:
                self.damage_left_to_take = 0
                self.damage_is_taken_one_at_a_time = False
                will_switch_back_to_normal = True
                primary_player.reset_aiming_reticle_in_play(self.planet_of_damaged_unit, self.position_of_damaged_unit)
        if unit_dead:
            self.damage_is_taken_one_at_a_time = False
            self.damage_left_to_take = False
        if will_switch_back_to_normal:
            self.mode = "Normal"
        await self.send_info_box()
        await primary_player.send_units_at_planet(self.planet_of_damaged_unit)
        await secondary_player.send_units_at_planet(self.planet_of_damaged_unit)

    async def deploy_card_routine(self, name, planet_pos, discounts=0):
        print("Deploy card at planet", planet_pos)
        if self.number_with_deploy_turn == "1":
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        damage_to_take = sum(self.damage_for_unit_to_take_on_play)
        print("position hand of unit: ", self.card_pos_to_deploy)
        print("Damage to take: ", damage_to_take)
        played_card, position_of_unit = primary_player.play_card(int(planet_pos),
                                                                 position_hand=self.card_pos_to_deploy,
                                                                 discounts=discounts,
                                                                 damage_to_take=damage_to_take)
        if played_card == "SUCCESS":
            self.mode = "Normal"
            if damage_to_take > 0:
                self.damage_on_unit_before_new_damage = 0
                self.player_who_is_shielding = primary_player.get_name_player()
                self.number_who_is_shielding = str(primary_player.get_number())
                self.planet_of_damaged_unit = int(planet_pos)
                self.position_of_damaged_unit = position_of_unit
                self.damage_is_taken_one_at_a_time = True
                self.damage_left_to_take = damage_to_take
                self.mode = "SHIELD"
                print("Position of the damaged unit:", planet_pos, position_of_unit)
                primary_player.set_aiming_reticle_in_play(int(planet_pos), position_of_unit, "red")
            await primary_player.send_hand()
            await secondary_player.send_hand()
            await primary_player.send_discard()
            await secondary_player.send_discard()
            await primary_player.send_units_at_planet(int(planet_pos))
            await primary_player.send_resources()
            if not secondary_player.has_passed:
                self.player_with_deploy_turn = secondary_player.get_name_player()
                self.number_with_deploy_turn = secondary_player.get_number()
                await self.send_info_box()
        self.damage_for_unit_to_take_on_play = []
        self.card_pos_to_deploy = -1
        primary_player.aiming_reticle_color = None
        primary_player.aiming_reticle_coords_hand = None
        self.planet_aiming_reticle_active = False
        self.planet_aiming_reticle_position = -1
        self.discounts_applied = 0
        self.available_discounts = 0
        self.faction_of_card_to_play = ""
        await primary_player.send_hand()
        await primary_player.send_hq()
        await self.send_planet_array()
        print("Finished deploying card")

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
                    await self.p1.send_units_at_all_planets()
                    await self.p2.send_units_at_all_planets()
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

    async def update_game_event_combat_section(self, name, game_update_string):
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if self.mode == "SHIELD":
                    if name == self.player_who_is_shielding:
                        await self.resolve_shield_of_unit_from_attack(name, -1)
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
                            if self.ranged_skirmish_active:
                                print("Both players passed, end ranged skirmish")
                                self.p1.has_passed = False
                                self.p2.has_passed = False
                                self.reset_combat_turn()
                                self.ranged_skirmish_active = False
                                await self.send_info_box()
                            else:
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
                            if self.attacker_position != -1 and self.defender_position == -1:
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
                                    for i in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                                        self.damage_on_units_list_before_new_damage.append(secondary_player.
                                                                                           get_damage_given_pos
                                                                                           (chosen_planet, i))
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
                                    self.damage_on_unit_before_new_damage = -1
                                    await self.send_info_box()
                                    await secondary_player.send_units_at_planet(chosen_planet)
        elif len(game_update_string) == 3:
            if game_update_string[0] == "HAND":
                print("Card in hand clicked on")
                if self.mode == "SHIELD":
                    if name == self.player_who_is_shielding:
                        if game_update_string[1] == self.number_who_is_shielding:
                            hand_pos = int(game_update_string[2])
                            await self.resolve_shield_of_unit_from_attack(name, hand_pos)
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
                                player.exhaust_given_pos(chosen_planet, chosen_unit)
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
                                can_continue = False
                                if self.ranged_skirmish_active:
                                    is_ranged = player.get_ranged_given_pos(chosen_planet, chosen_unit)
                                    if is_ranged:
                                        can_continue = True
                                else:
                                    can_continue = True
                                if can_continue:
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
                            can_continue = True
                            if secondary_player.cards_in_play[self.defender_planet + 1][self.defender_position]\
                                    .get_ability() == "Honored Librarian":
                                for i in range(len(secondary_player.cards_in_play[self.defender_planet + 1])):
                                    if secondary_player.cards_in_play[self.defender_planet + 1][i]\
                                            .get_ability() != "Honored Librarian":
                                        can_continue = False
                            if can_continue:
                                if primary_player.get_ability_given_pos(self.attacker_planet,
                                                                        self.attacker_position) == "Starbane's Council":
                                    if not secondary_player.get_ready_given_pos(self.defender_planet,
                                                                                self.defender_position):
                                        attack_value += 2
                                if attack_value > 0:
                                    att_flying = primary_player.get_flying_given_pos(self.attacker_planet,
                                                                                     self.attacker_position)
                                    def_flying = secondary_player.get_flying_given_pos(self.defender_planet,
                                                                                       self.defender_position)
                                    att_ignores_flying = primary_player.get_ignores_flying_given_pos(
                                        self.attacker_planet, self.attacker_position)
                                    if primary_player.get_ability_given_pos(
                                            self.attacker_planet, self.attacker_position) == "Silvered Blade Avengers":
                                        if secondary_player.cards_in_play[
                                            self.defender_planet + 1][self.defender_position]\
                                                .get_card_type() != "Warlord":
                                            secondary_player.exhaust_given_pos(self.defender_planet,
                                                                               self.defender_position)
                                    # Flying check
                                    if def_flying and not att_flying and not att_ignores_flying:
                                        attack_value = attack_value / 2 + (attack_value % 2 > 0)
                                    self.damage_on_unit_before_new_damage = \
                                        secondary_player.get_damage_given_pos(self.defender_planet,
                                                                              self.defender_position)
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
                                    secondary_player.set_aiming_reticle_in_play(self.defender_planet,
                                                                                self.defender_position, "red")
                                    if armorbane_check and attack_value > 0:
                                        await self.resolve_shield_of_unit_from_attack(secondary_player.get_name(), -1)
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
                            else:
                                self.defender_planet = -1
                                self.defender_position = -1

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
                    elif ability == "Doom":
                        print("Resolve Doom")
                        primary_player.destroy_all_cards_in_hq(ignore_uniques=True, units_only=True)
                        secondary_player.destroy_all_cards_in_hq(ignore_uniques=True, units_only=True)
                        primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        await primary_player.send_hq()
                        await secondary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await primary_player.send_resources()
                        await self.send_info_box()
                    elif ability == "Pact of the Haemonculi":
                        print("Resolve PotH")
                        self.action_chosen = "Pact of the Haemonculi"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    elif ability == "Exterminatus":
                        print("Resolve Exterminatus")
                        self.action_chosen = "Exterminatus"
                        primary_player.aiming_reticle_color = "blue"
                        primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
                        await primary_player.send_hand()
                        await primary_player.send_resources()
                    else:
                        primary_player.add_resources(card.get_cost())
                        await self.game_sockets[0].receive_game_update(card.get_name() + " not "
                                                                                         "implemented")

    async def update_game_event_action(self, name, game_update_string):
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                self.mode = self.stored_mode
                self.player_with_action = ""
                print("Canceled special action")
                await self.game_sockets[0].receive_game_update(name + " canceled their action request")
        elif len(game_update_string) == 2:
            if game_update_string[0] == "PLANETS":
                chosen_planet = int(game_update_string[1])
                if self.action_chosen == "Exterminatus":
                    if self.round_number != chosen_planet:
                        if self.number_with_deploy_turn == "1":
                            primary_player = self.p1
                            secondary_player = self.p2
                        else:
                            primary_player = self.p2
                            secondary_player = self.p2
                        self.p1.destroy_all_cards_at_planet(chosen_planet)
                        self.p2.destroy_all_cards_at_planet(chosen_planet)
                        primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                        primary_player.aiming_reticle_color = None
                        primary_player.aiming_reticle_coords_hand = None
                        self.card_pos_to_deploy = -1
                        self.player_with_action = ""
                        self.action_chosen = ""
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
                        self.mode = self.stored_mode
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                        await self.p1.send_units_at_planet(chosen_planet)
                        await self.p2.send_units_at_planet(chosen_planet)
                        await self.send_info_box()
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
            elif game_update_string[0] == "HQ":
                if self.phase == "DEPLOY":
                    if name == self.player_with_deploy_turn:
                        if game_update_string[1] == self.number_with_deploy_turn:
                            if self.action_chosen == "Pact of the Haemonculi":
                                if self.number_with_deploy_turn == "1":
                                    primary_player = self.p1
                                    secondary_player = self.p2
                                else:
                                    primary_player = self.p2
                                    secondary_player = self.p2
                                if primary_player.sacrifice_card_in_hq(int(game_update_string[2])):
                                    primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                                    secondary_player.discard_card_at_random()
                                    primary_player.draw_card()
                                    primary_player.draw_card()
                                    primary_player.aiming_reticle_color = None
                                    primary_player.aiming_reticle_coords_hand = None
                                    self.card_pos_to_deploy = -1
                                    self.player_with_action = ""
                                    self.action_chosen = ""
                                    self.player_with_deploy_turn = secondary_player.name_player
                                    self.number_with_deploy_turn = secondary_player.number
                                    self.mode = self.stored_mode
                                    await primary_player.send_hand()
                                    await secondary_player.send_hand()
                                    await primary_player.send_hq()
        elif len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if self.phase == "DEPLOY":
                    if name == self.player_with_deploy_turn:
                        if game_update_string[1] == self.number_with_deploy_turn:
                            if self.action_chosen == "Pact of the Haemonculi":
                                if self.number_with_deploy_turn == "1":
                                    primary_player = self.p1
                                    secondary_player = self.p2
                                else:
                                    primary_player = self.p2
                                    secondary_player = self.p2
                                if primary_player.sacrifice_card_in_play(int(game_update_string[2]),
                                                                         int(game_update_string[3])):
                                    primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                                    secondary_player.discard_card_at_random()
                                    primary_player.draw_card()
                                    primary_player.draw_card()
                                    primary_player.aiming_reticle_color = None
                                    primary_player.aiming_reticle_coords_hand = None
                                    self.card_pos_to_deploy = -1
                                    self.player_with_action = ""
                                    self.action_chosen = ""
                                    self.player_with_deploy_turn = secondary_player.name_player
                                    self.number_with_deploy_turn = secondary_player.number
                                    self.mode = self.stored_mode
                                    await primary_player.send_hand()
                                    await secondary_player.send_hand()
                                    await primary_player.send_units_at_planet(int(game_update_string[2]))

    def validate_received_game_string(self, game_update_string):
        if len(game_update_string) == 1:
            return True
        if len(game_update_string) == 2:
            if game_update_string[0] == "SEARCH":
                if len(self.cards_in_search_box) > int(game_update_string[1]):
                    return True
            if game_update_string[0] == "PLANETS":
                return True
            if game_update_string[0] == "CHOICE":
                if len(self.choices_available) > int(game_update_string[1]):
                    return True
        if len(game_update_string) == 3:
            if game_update_string[0] == "HQ":
                if game_update_string[1] == "1":
                    if len(self.p1.headquarters) > int(game_update_string[2]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.headquarters) > int(game_update_string[2]):
                        return True
            elif game_update_string[0] == "HAND":
                if game_update_string[1] == "1":
                    if len(self.p1.cards) > int(game_update_string[2]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.cards) > int(game_update_string[2]):
                        return True
        if len(game_update_string) == 4:
            if game_update_string[0] == "ATTACHMENT":
                print("Attachment selecting not supported")
            elif game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == "1":
                    if len(self.p1.cards_in_play[int(game_update_string[2]) + 1]) > int(game_update_string[3]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.cards_in_play[int(game_update_string[2]) + 1]) > int(game_update_string[3]):
                        return True
        if len(game_update_string) == 5:
            print("Attachment selecting not supported")
        print("Bad string")
        return False

    def check_if_card_searched_satisfies_conditions(self, card):
        if not self.all_conditions_searched_card_required:
            if self.faction_of_searched_card is not None:
                if card.get_faction() == self.faction_of_searched_card:
                    return True
            if self.card_type_of_searched_card is not None:
                if card.get_card_type() == self.card_type_of_searched_card:
                    return True
            if self.traits_of_searched_card is not None:
                if self.traits_of_searched_card in card.get_traits():
                    return True
            return False
        else:
            if self.faction_of_searched_card is not None:
                if card.get_faction() != self.faction_of_searched_card:
                    return False
            if self.card_type_of_searched_card is not None:
                if card.get_card_type() != self.card_type_of_searched_card:
                    return False
            if self.traits_of_searched_card is not None:
                if self.traits_of_searched_card not in card.get_traits():
                    return False
            return True

    def reset_search_values(self):
        self.what_to_do_with_searched_card = "DRAW"
        self.traits_of_searched_card = None
        self.card_type_of_searched_card = None
        self.faction_of_searched_card = None
        self.all_conditions_searched_card_required = False
        self.no_restrictions_on_chosen_card = False
        self.cards_in_search_box = []

    async def resolve_card_in_search_box(self, name, game_update_string):
        if name == self.name_player_who_is_searching:
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.number_who_is_searching == "1":
                        self.p1.bottom_remaining_cards()
                    else:
                        self.p2.bottom_remaining_cards()
                    self.cards_in_search_box = []
            elif len(game_update_string) == 2:
                if game_update_string[0] == "SEARCH":
                    if self.what_to_do_with_searched_card == "DRAW":
                        if self.number_who_is_searching == "1":
                            valid_card = True
                            if not self.no_restrictions_on_chosen_card:
                                card_chosen = FindCard.find_card(self.p1.deck[int(game_update_string[1])],
                                                                 self.card_array)
                                valid_card = self.check_if_card_searched_satisfies_conditions(card_chosen)
                            if valid_card:
                                self.p1.draw_card_at_location_deck(int(game_update_string[1]))
                                self.p1.number_cards_to_search -= 1
                                await self.p1.send_hand()
                                self.p1.bottom_remaining_cards()
                                self.reset_search_values()
                                if self.battle_ability_to_resolve == "Plannum":
                                    self.reset_battle_resolve_attributes()
                        else:
                            valid_card = True
                            if not self.no_restrictions_on_chosen_card:
                                card_chosen = FindCard.find_card(self.p2.deck[int(game_update_string[1])],
                                                                 self.card_array)
                                valid_card = self.check_if_card_searched_satisfies_conditions(card_chosen)
                            if valid_card:
                                self.p2.draw_card_at_location_deck(int(game_update_string[1]))
                                self.p2.number_cards_to_search -= 1
                                await self.p2.send_hand()
                                self.p2.bottom_remaining_cards()
                                self.reset_search_values()
                                if self.battle_ability_to_resolve == "Elouith":
                                    self.reset_battle_resolve_attributes()
                                    await self.resolve_battle_conclusion(name, game_update_string)

    def reset_choices_available(self):
        self.choices_available = []
        self.name_player_making_choices = ""
        self.choice_context = ""

    def reset_battle_resolve_attributes(self):
        self.need_to_resolve_battle_ability = False
        self.battle_ability_to_resolve = ""
        self.player_resolving_battle_ability = ""
        self.number_resolving_battle_ability = -1

    async def resolve_battle_conclusion(self, name, game_string):
        winner = None
        if name == self.name_2:
            winner = self.p2
        elif name == self.name_1:
            winner = self.p1
        if winner is not None:
            if self.round_number == self.last_planet_checked_for_battle:
                winner.retreat_all_at_planet(self.last_planet_checked_for_battle)
                await winner.send_hq()
                await winner.send_units_at_planet(self.last_planet_checked_for_battle)
                winner.capture_planet(self.last_planet_checked_for_battle,
                                      self.planet_cards_array)
                self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                await winner.send_victory_display()
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
        self.reset_battle_resolve_attributes()
        self.reset_choices_available()

    async def resolve_choice(self, name, game_update_string):
        if name == self.name_player_making_choices:
            if len(game_update_string) == 2:
                if game_update_string[0] == "CHOICE":
                    if self.choice_context == "Resolve Battle Ability?":
                        if self.choices_available[int(game_update_string[1])] == "Yes":
                            print("Wants to resolve battle ability")
                            if name == self.name_2:
                                winner = self.p2
                                loser = self.p1
                            else:
                                winner = self.p1
                                loser = self.p2
                            if self.battle_ability_to_resolve == "Osus IV":
                                if loser.spend_resources(1):
                                    winner.add_resources(1)
                                    await winner.send_resources()
                                    await loser.send_resources()
                                    await self.resolve_battle_conclusion(name, game_update_string)
                            elif self.battle_ability_to_resolve == "Barlus":
                                loser.discard_card_at_random()
                                await loser.send_hand()
                                await loser.send_discard()
                                await self.resolve_battle_conclusion(name, game_update_string)
                            elif self.battle_ability_to_resolve == "Elouith":
                                winner.number_cards_to_search = 3
                                self.cards_in_search_box = winner.deck[0:winner.number_cards_to_search]
                                self.name_player_who_is_searching = winner.name_player
                                self.number_who_is_searching = str(winner.number)
                                self.what_to_do_with_searched_card = "DRAW"
                                self.traits_of_searched_card = None
                                self.card_type_of_searched_card = None
                                self.faction_of_searched_card = None
                                self.no_restrictions_on_chosen_card = True
                                await self.send_search()
                        elif self.choices_available[int(game_update_string[1])] == "No":
                            print("Does not want to resolve battle ability")
                            await self.resolve_battle_conclusion(name, game_update_string)

    async def update_game_event(self, name, game_update_string):
        self.condition_main_game.acquire()
        print(game_update_string)
        if self.phase == "SETUP":
            await self.game_sockets[0].receive_game_update("Buttons can't be pressed in setup")
        if self.validate_received_game_string(game_update_string):
            print("String validated as ok")
            if self.cards_in_search_box:
                print("Need to resolve search box")
                await self.resolve_card_in_search_box(name, game_update_string)
                if not self.cards_in_search_box:
                    await self.send_search()
            elif self.choices_available:
                print("Need to resolve a choice")
                await self.resolve_choice(name, game_update_string)
            elif self.phase == "DEPLOY":
                await self.update_game_event_deploy_section(name, game_update_string)
            elif self.phase == "COMMAND":
                await self.update_game_event_command_section(name, game_update_string)
            elif self.phase == "COMBAT":
                await self.update_game_event_combat_section(name, game_update_string)
        if self.cards_in_search_box:
            await self.send_search()
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

    def request_number_of_enemy_units_in_discard(self, number):
        if number == "1":
            return self.p2.count_units_in_discard()
        elif number == "2":
            return self.p1.count_units_in_discard()
        return None

    def add_resources_to_opponent(self, number, amount):
        self.resources_need_sending_outside_normal_sends = True
        if int(number) == 1:
            self.p2.add_resources(amount)
        elif int(number) == 2:
            self.p1.add_resources(amount)

    def summon_enemy_token_at_hq(self, number, token_name, amount):
        self.hqs_need_sending_outside_normal_sends = True
        if int(number) == 1:
            self.p2.summon_token_at_hq(token_name, amount)
        elif int(number) == 2:
            self.p1.summon_token_at_hq(token_name, amount)

    def discard_card_at_random_from_opponent(self, number):
        print("\nGot to discard at random request\n")
        number = int(number)
        print(number == 1)
        print(number == 2)
        print(number == "1")
        print(number == "2")
        if number == 1:
            print("Discard p2")
            self.p2.discard_card_at_random()
        elif number == 2:
            print("Discard p1")
            self.p1.discard_card_at_random()

    async def resolve_shield_of_unit_from_attack(self, name, hand_pos):
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
        if self.damage_on_units_list_before_new_damage:
            self.damage_on_unit_before_new_damage = self.damage_on_units_list_before_new_damage[0]
            del self.damage_on_units_list_before_new_damage[0]
        if primary_player.get_damage_given_pos(self.defender_planet, self.defender_position) < \
                self.damage_on_unit_before_new_damage:
            primary_player.set_damage_given_pos(self.defender_planet, self.defender_position,
                                                self.damage_on_unit_before_new_damage)
        self.number_of_units_left_to_suffer_damage -= 1

        if self.number_of_units_left_to_suffer_damage <= 0:
            i = 0
            while i < len(primary_player.cards_in_play[self.defender_planet + 1]):
                unit_dead = primary_player.check_if_card_is_destroyed(self.defender_planet, i)
                if unit_dead:
                    primary_player.destroy_card_in_play(self.defender_planet, i)
                    if self.hqs_need_sending_outside_normal_sends:
                        await primary_player.send_hq()
                        await secondary_player.send_hq()
                        self.hqs_need_sending_outside_normal_sends = False
                    if self.resources_need_sending_outside_normal_sends:
                        await primary_player.send_resources()
                        await secondary_player.send_resources()
                        self.resources_need_sending_outside_normal_sends = False
                    if self.cards_need_sending_outside_normal_sends:
                        await primary_player.send_hand()
                        await secondary_player.send_hand()
                        self.cards_need_sending_outside_normal_sends = False
                    if primary_player.warlord_just_got_bloodied:
                        primary_player.warlord_just_got_bloodied = False
                        await primary_player.send_hq()
                    await primary_player.send_discard()
                    i = i - 1
                i = i + 1
            self.number_of_units_left_to_suffer_damage = 0
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_shielding_values()
            self.mode = "Normal"
            self.actions_allowed = True
        else:
            self.next_unit_to_suffer_damage += 1
            self.defender_position = self.next_unit_to_suffer_damage
            primary_player.set_aiming_reticle_in_play(self.defender_planet, self.defender_position, "red")

        await self.send_info_box()
        await primary_player.send_units_at_planet(self.attacker_planet)
        await secondary_player.send_units_at_planet(self.attacker_planet)
        if self.number_of_units_left_to_suffer_damage <= 0:
            self.reset_combat_positions()

    async def resolve_winning_combat(self, winner, loser):
        planet_name = self.planet_array[self.last_planet_checked_for_battle]
        print("Resolve battle ability of:", planet_name)
        self.need_to_resolve_battle_ability = True
        self.battle_ability_to_resolve = planet_name
        self.player_resolving_battle_ability = winner.name_player
        self.number_resolving_battle_ability = str(winner.number)
        self.choices_available = ["Yes", "No"]
        self.choice_context = "Resolve Battle Ability?"
        self.name_player_making_choices = winner.name_player
        await self.game_sockets[0].receive_game_update(winner.name_player + " has the right to use"
                                                                            " the battle ability of " + planet_name)
        await self.send_search()
        if not self.need_to_resolve_battle_ability:
            if self.round_number == self.last_planet_checked_for_battle:
                winner.retreat_all_at_planet(self.last_planet_checked_for_battle)
                await winner.send_hq()
                await winner.send_units_at_planet(self.last_planet_checked_for_battle)
                winner.capture_planet(self.last_planet_checked_for_battle,
                                      self.planet_cards_array)
                self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                await winner.send_victory_display()

    async def check_combat_end(self, name):
        p1_has_units = self.p1.check_if_units_present(self.last_planet_checked_for_battle)
        p2_has_units = self.p2.check_if_units_present(self.last_planet_checked_for_battle)
        if p1_has_units and p2_has_units:
            await self.send_info_box()
        else:
            if p1_has_units:
                await self.resolve_winning_combat(self.p1, self.p2)
            if p2_has_units:
                await self.resolve_winning_combat(self.p2, self.p1)
            if not p1_has_units and not p2_has_units:
                if self.round_number == self.last_planet_checked_for_battle:
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                await self.resolve_battle_conclusion(name, ["", ""])

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
        self.actions_allowed = True
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
        i = 0
        while i < len(self.p1.headquarters):
            if self.p1.headquarters[i].get_ability() == "Promethium Mine":
                self.p1.headquarters[i].decrement_counter()
                self.p1.add_resources(1)
                if self.p1.headquarters[i].get_counter() <= 0:
                    self.p1.destroy_card_in_hq(i)
                    i = i - 1
            i = i + 1
        i = 0
        while i < len(self.p2.headquarters):
            if self.p2.headquarters[i].get_ability() == "Promethium Mine":
                self.p2.headquarters[i].decrement_counter()
                self.p2.add_resources(1)
                if self.p2.headquarters[i].get_counter() <= 0:
                    self.p2.destroy_card_in_hq(i)
                    i = i - 1
            i = i + 1
        self.p1.set_can_play_limited(True)
        self.p2.set_can_play_limited(True)
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
                    self.ranged_skirmish_active = True
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
            extra_resources, extra_cards = self.p1.get_bonus_winnings_at_planet(planet_id)
            resources_won += extra_resources
            cards_won += extra_cards
            ret_val = ["1", resources_won, cards_won]
            if self.p1.search_card_in_hq("Omega Zero Command"):
                self.p1.summon_token_at_planet("Guardsman", planet_id)
            return ret_val
        elif command_p2 > command_p1:
            print("P2 wins command")
            chosen_planet = FindCard.find_planet_card(self.planet_array[planet_id], self.planet_cards_array)
            resources_won = chosen_planet.get_resources()
            cards_won = chosen_planet.get_cards()
            extra_resources, extra_cards = self.p2.get_bonus_winnings_at_planet(planet_id)
            resources_won += extra_resources
            cards_won += extra_cards
            ret_val = ["2", resources_won, cards_won]
            if self.p2.search_card_in_hq("Omega Zero Command"):
                self.p2.summon_token_at_planet("Guardsman", planet_id)
            return ret_val
        return None

    def check_battle(self, planet_id):
        if planet_id == self.round_number:
            print("First planet: battle occurs at ", planet_id)
            self.ranged_skirmish_active = True
            return 1
        if self.p1.check_for_warlord(planet_id):
            print("p1 warlord present. Battle at ", planet_id)
            self.ranged_skirmish_active = True
            return 1
        elif self.p2.check_for_warlord(planet_id):
            print("p2 warlord present. Battle at ", planet_id)
            self.ranged_skirmish_active = True
            return 1
        return 0
