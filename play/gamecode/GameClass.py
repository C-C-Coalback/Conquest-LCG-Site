import copy
from . import PlayerClass
import random
from .Phases import DeployPhase, CommandPhase, CombatPhase
from . import FindCard
import threading
from .Actions import AttachmentHQActions, AttachmentInPlayActions, HandActions, HQActions, InPlayActions, PlanetActions


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
        for i in range(10):
            self.planet_array.append(self.planet_cards_array[i].get_name())
        random.shuffle(self.planet_array)
        self.planet_array = self.planet_array[:7]
        self.planets_in_play_array = [True, True, True, True, True, False, False]
        self.player_with_deploy_turn = self.name_1
        self.number_with_deploy_turn = "1"
        self.card_pos_to_deploy = -1
        self.planet_pos_to_deploy = -1
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
        self.traits_of_card_to_play = ""
        self.ranged_skirmish_active = False
        self.interrupt_active = False
        self.what_is_being_interrupted = ""
        self.damage_is_taken_one_at_a_time = False
        self.damage_left_to_take = 0
        self.positions_of_units_hq_to_take_damage = []
        self.positions_of_units_to_take_damage = []  # Format: (player_num, planet_num, unit_pos)
        self.positions_attackers_of_units_to_take_damage = []  # Format: (player_num, planet_num, unit_pos) or None
        self.damage_can_be_shielded = []
        self.amount_that_can_be_removed_by_shield = []
        self.card_type_of_selected_card_in_hand = ""
        self.cards_in_search_box = []
        self.name_player_who_is_searching = ""
        self.number_who_is_searching = "1"
        self.what_to_do_with_searched_card = "DRAW"
        self.traits_of_searched_card = None
        self.card_type_of_searched_card = None
        self.faction_of_searched_card = None
        self.max_cost_of_searched_card = None
        self.all_conditions_searched_card_required = False
        self.no_restrictions_on_chosen_card = False
        self.need_to_resolve_battle_ability = False
        self.battle_ability_to_resolve = ""
        self.player_resolving_battle_ability = ""
        self.number_resolving_battle_ability = -1
        self.choices_available = []
        self.name_player_making_choices = ""
        self.choice_context = ""
        self.damage_from_atrox = False
        self.damage_on_units_hq_before_new_damage = []
        self.unit_to_move_position = [-1, -1]
        self.yvarn_active = False
        self.p1_triggered_yvarn = False
        self.p2_triggered_yvarn = False
        self.damage_from_attack = False
        self.attacker_location = [-1, -1, -1]
        self.reactions_needing_resolving = []
        self.positions_of_unit_triggering_reaction = []
        self.player_who_resolves_reaction = []
        self.misc_counter = 0
        self.khymera_to_move_positions = []
        self.position_of_actioned_card = (-1, -1)
        self.position_of_selected_attachment = (-1, -1, -1)
        self.active_effects = []  # Each item should be a tuple containing all relevant info
        self.chosen_first_card = False
        self.chosen_second_card = False
        self.misc_target_planet = -1
        self.misc_target_unit = (-1, -1)
        self.misc_target_attachment = (-1, -1, -1)
        self.misc_player_storage = ""
        self.last_defender_position = (-1, -1)
        self.location_of_indirect = ""
        self.planet_of_indirect = -1
        self.first_card_damaged = True
        self.cato_stronghold_activated = False
        self.allowed_planets_cato_stronghold = []
        self.allowed_units_alaitoc_shrine = []
        self.committing_warlords = False
        self.alaitoc_shrine_activated = False
        self.resolving_search_box = False
        self.banshee_power_sword_extra_attack = 0
        self.may_move_defender = True
        self.fire_warrior_elite_active = False
        self.before_command_struggle = False
        self.after_command_struggle = True
        self.amount_spend_for_tzeentch_firestorm = -1
        self.searching_enemy_deck = False
        self.bottom_cards_after_search = True
        self.shadowsun_chose_hand = True
        self.effects_waiting_on_resolution = []
        self.player_resolving_effect = []
        self.location_hand_attachment_shadowsun = -1
        self.name_attachment_discard_shadowsun = ""
        self.units_damaged_by_attack = []
        self.units_damaged_by_attack_from_sm = []
        self.alternative_shields = ["Indomitable", "Glorious Intervention"]
        self.last_shield_string = ""
        self.pos_shield_card = -1
        self.recently_damaged_units = []
        self.damage_taken_was_from_attack = []
        self.faction_of_attacker = []
        self.furiable_unit_position = (-1, -1)
        self.nullified_card_pos = -1
        self.nullify_context = ""
        self.nullify_count = 0
        self.first_player_nullified = None
        self.cost_card_nullified = 0
        self.nullified_card_name = ""
        self.nullify_enabled = True
        self.nullify_string = ""
        self.communications_relay_enabled = True
        self.bigga_is_betta_active = False
        self.last_info_box_string = ""

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
        await self.send_info_box(force=True)
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

    async def send_info_box(self, force=False):
        info_string = "GAME_INFO/INFO_BOX/"
        if self.phase == "SETUP":
            info_string += "Unspecified/"
        elif self.cards_in_search_box:
            info_string += self.name_player_who_is_searching + "/"
        elif self.effects_waiting_on_resolution:
            info_string += self.player_resolving_effect[0] + "/"
        elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
            info_string += "Unspecified/"
        elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
            info_string += self.player_with_action + "/"
        elif self.choices_available:
            info_string += self.name_player_making_choices + "/"
        elif self.reactions_needing_resolving:
            info_string += self.player_who_resolves_reaction[0] + "/"
        elif self.positions_of_units_to_take_damage:
            if self.positions_of_units_to_take_damage[0][0] == 1:
                info_string += self.name_1 + "/"
            else:
                info_string += self.name_2 + "/"
        elif not self.p1.mobile_resolved or not self.p2.mobile_resolved:
            info_string += "Unspecified/" + "Mobile"
        elif self.battle_ability_to_resolve:
            info_string += self.player_resolving_battle_ability + "/"
        elif self.phase == "DEPLOY":
            info_string += self.player_with_deploy_turn + "/"
        elif self.phase == "COMBAT":
            info_string += self.player_with_combat_turn + "/"
        else:
            info_string += "Unspecified/"
        info_string += "Phase: " + self.phase + "/"
        info_string += "Mode: " + self.mode + "/"
        if self.phase == "SETUP":
            info_string += "Setup/"
        elif self.cards_in_search_box:
            info_string += "Searching: " + self.what_to_do_with_searched_card + "/"
            info_string += "User: " + self.name_player_who_is_searching + "/"
        elif self.effects_waiting_on_resolution:
            info_string += "Effect: " + self.effects_waiting_on_resolution[0] + "/"
            info_string += "User: " + self.player_resolving_effect[0] + "/"
        elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
            info_string += "Indirect damage " + str(self.p1.total_indirect_damage) + \
                           str(self.p2.total_indirect_damage) + "/"
        elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
            info_string += "Ambush discounts/God help you/"
            info_string += self.player_with_action + "/"
        elif self.choices_available:
            info_string += "Choice: " + self.choice_context + "/"
            info_string += "User: " + self.name_player_making_choices + "/"
        elif self.reactions_needing_resolving:
            info_string += "Reaction: " + self.reactions_needing_resolving[0] + "/"
            info_string += "User: " + self.player_who_resolves_reaction[0] + "/"
        elif self.positions_of_units_to_take_damage:
            if self.positions_of_units_to_take_damage[0][0] == 1:
                info_string += "Shield: " + self.name_1 + "/"
            else:
                info_string += "Shield: " + self.name_2 + "/"
        elif not self.p1.mobile_resolved or not self.p2.mobile_resolved:
            info_string += "Mobile window/"
        elif self.battle_ability_to_resolve:
            info_string += "Resolve battle ability: " + self.battle_ability_to_resolve + "/"
            info_string += self.player_resolving_battle_ability + "/"
        elif self.phase == "DEPLOY":
            info_string += "Active: " + self.player_with_deploy_turn + "/"
        elif self.phase == "COMMAND":
            if self.committing_warlords:
                info_string += "Commit Warlords/"
            elif self.before_command_struggle:
                info_string += "Before command struggle/"
            elif self.after_command_struggle:
                info_string += "After command struggle/"
            else:
                info_string += "??????/"
        elif self.phase == "COMBAT":
            if self.ranged_skirmish_active:
                info_string += "Active (RANGED): " + self.player_with_combat_turn + "/"
            else:
                info_string += "Active: " + self.player_with_combat_turn + "/"
        else:
            info_string += "??????/"
        if self.last_info_box_string != info_string:
            await self.game_sockets[0].receive_game_update(info_string)
            self.last_info_box_string = info_string
        elif force:
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

    async def update_game_event_action_applying_discounts(self, name, game_update_string):
        if name == self.player_with_action:
            print("Special apply discounts routine")
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    print("Play card with not all discounts")
                    await DeployPhase.deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                          discounts=self.discounts_applied)
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
            if len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    if name == self.player_with_action:
                        if self.player_with_action == self.name_1:
                            player = self.p1
                        else:
                            player = self.p2
                        if game_update_string[1] == player.get_number():
                            discount_received = player.perform_discount_at_pos_hq(int(game_update_string[2]),
                                                                                  self.faction_of_card_to_play,
                                                                                  self.traits_of_card_to_play)
                            if discount_received > 0:
                                self.discounts_applied += discount_received
                                await player.send_hq()
                            if self.discounts_applied >= self.available_discounts:
                                await DeployPhase.deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                                      discounts=self.discounts_applied)
                                self.mode = "Normal"

    async def aoe_routine(self, primary_player, secondary_player, chosen_planet, amount_aoe):
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
        await self.send_info_box()
        await secondary_player.send_units_at_planet(chosen_planet)

    async def update_game_event_action(self, name, game_update_string):
        if name == self.player_with_action:
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.action_chosen == "":
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        print("Canceled special action")
                        await self.game_sockets[0].receive_game_update(name + " canceled their action request")
                    else:
                        await self.game_sockets[0].receive_game_update("Too far in; action must be concluded now")
            elif len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    await PlanetActions.update_game_event_action_planet(self, name, game_update_string)
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    if self.player_with_action == self.name_1 and game_update_string[1] == "1":
                        await HandActions.update_game_event_action_hand(self, name, game_update_string)
                    elif self.player_with_action == self.name_2 and game_update_string[1] == "2":
                        await HandActions.update_game_event_action_hand(self, name, game_update_string)
                elif game_update_string[0] == "HQ":
                    await HQActions.update_game_event_action_hq(self, name, game_update_string)
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    await InPlayActions.update_game_event_action_in_play(self, name, game_update_string)
            elif len(game_update_string) == 5:
                if game_update_string[0] == "ATTACHMENT" and game_update_string[1] == "HQ":
                    await AttachmentHQActions.update_game_event_action_attachment_hq(self, name, game_update_string)
            elif len(game_update_string) == 6:
                if game_update_string[0] == "ATTACHMENT" and game_update_string[1] == "IN_PLAY":
                    await AttachmentInPlayActions.update_game_event_action_attachment_in_play(self, name,
                                                                                              game_update_string)

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
            if game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == "1":
                    if len(self.p1.cards_in_play[int(game_update_string[2]) + 1]) > int(game_update_string[3]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.cards_in_play[int(game_update_string[2]) + 1]) > int(game_update_string[3]):
                        return True
        if len(game_update_string) == 5:
            if game_update_string[0] == "ATTACHMENT":
                if game_update_string[1] == "HQ":
                    pos_unit = int(game_update_string[3])
                    pos_attachment = int(game_update_string[4])
                    if game_update_string[2] == "1":
                        if len(self.p1.headquarters) > pos_unit:
                            card = self.p1.headquarters[pos_unit]
                            if len(card.get_attachments()) > pos_attachment:
                                return True
                    elif game_update_string[2] == "2":
                        if len(self.p2.headquarters) > pos_unit:
                            card = self.p2.headquarters[pos_unit]
                            if len(card.get_attachments()) > pos_attachment:
                                return True
        if len(game_update_string) == 6:
            if game_update_string[0] == "ATTACHMENT":
                if game_update_string[1] == "IN_PLAY":
                    pos_planet = int(game_update_string[3])
                    pos_unit = int(game_update_string[4])
                    pos_attachment = int(game_update_string[5])
                    if game_update_string[2] == "1":
                        if len(self.p1.cards_in_play[pos_planet + 1]) > pos_unit:
                            card = self.p1.cards_in_play[pos_planet + 1][pos_unit]
                            if len(card.get_attachments()) > pos_attachment:
                                return True
                    elif game_update_string[2] == "2":
                        if len(self.p2.cards_in_play[pos_planet + 1]) > pos_unit:
                            card = self.p2.cards_in_play[pos_planet + 1][pos_unit]
                            if len(card.get_attachments()) > pos_attachment:
                                return True
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
            if self.max_cost_of_searched_card is not None:
                if card.get_cost() > self.max_cost_of_searched_card:
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
            if self.max_cost_of_searched_card is not None:
                if card.get_cost() > self.max_cost_of_searched_card:
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
        card_chosen = None
        if name == self.name_player_who_is_searching:
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.number_who_is_searching == "1":
                        self.p1.bottom_remaining_cards()
                    else:
                        self.p2.bottom_remaining_cards()
                    self.cards_in_search_box = []
                    if self.resolving_search_box:
                        self.resolving_search_box = False
            elif len(game_update_string) == 2:
                if game_update_string[0] == "SEARCH":
                    if self.number_who_is_searching == "1":
                        valid_card = True
                        if not self.no_restrictions_on_chosen_card:
                            card_chosen = FindCard.find_card(self.p1.deck[int(game_update_string[1])],
                                                             self.card_array)
                            valid_card = self.check_if_card_searched_satisfies_conditions(card_chosen)
                        if valid_card:
                            if self.what_to_do_with_searched_card == "DRAW":
                                self.p1.draw_card_at_location_deck(int(game_update_string[1]))
                                await self.p1.send_hand()
                            elif self.what_to_do_with_searched_card == "PLAY TO HQ" and card_chosen is not None:
                                self.p1.add_to_hq(card_chosen)
                                del self.p1.deck[int(game_update_string[1])]
                                if self.resolving_search_box:
                                    self.resolving_search_box = False
                                await self.p1.send_hq()
                            elif self.what_to_do_with_searched_card == "PLAY TO BATTLE" and card_chosen is not None:
                                self.p1.play_card_to_battle_at_location_deck(self.last_planet_checked_for_battle,
                                                                             int(game_update_string[1]), card_chosen)
                                if self.action_chosen == "Drop Pod Assault":
                                    self.p1.discard_card_from_hand(self.p1.aiming_reticle_coords_hand)
                                    self.p1.aiming_reticle_coords_hand = None
                                    self.mode = "Normal"
                                    self.player_with_action = ""
                                    self.action_chosen = ""
                                    await self.p1.send_hand()
                                await self.p1.send_units_at_planet(self.last_planet_checked_for_battle)
                            elif self.what_to_do_with_searched_card == "DISCARD":
                                if self.searching_enemy_deck:
                                    self.p2.discard_card_from_deck(int(game_update_string[1]))
                                    await self.p2.send_discard()
                                else:
                                    self.p1.discard_card_from_deck(int(game_update_string[1]))
                                    await self.p1.send_discard()
                            self.p1.number_cards_to_search -= 1
                            self.p1.bottom_remaining_cards()
                            self.reset_search_values()
                            if self.resolving_search_box:
                                self.resolving_search_box = False
                            if self.battle_ability_to_resolve == "Elouith":
                                await self.resolve_battle_conclusion(name, game_update_string)
                                self.reset_battle_resolve_attributes()
                    else:
                        valid_card = True
                        if not self.no_restrictions_on_chosen_card:
                            card_chosen = FindCard.find_card(self.p2.deck[int(game_update_string[1])],
                                                             self.card_array)
                            valid_card = self.check_if_card_searched_satisfies_conditions(card_chosen)
                        if valid_card:
                            if self.what_to_do_with_searched_card == "DRAW":
                                self.p2.draw_card_at_location_deck(int(game_update_string[1]))
                                await self.p2.send_hand()
                            elif self.what_to_do_with_searched_card == "PLAY TO HQ" and card_chosen is not None:
                                self.p2.add_to_hq(card_chosen)
                                del self.p2.deck[int(game_update_string[1])]
                                if self.resolving_search_box:
                                    self.resolving_search_box = False
                            elif self.what_to_do_with_searched_card == "PLAY TO BATTLE" and card_chosen is not None:
                                self.p2.play_card_to_battle_at_location_deck(self.last_planet_checked_for_battle,
                                                                             int(game_update_string[1]), card_chosen)
                                if self.action_chosen == "Drop Pod Assault":
                                    self.p2.discard_card_from_hand(self.p2.aiming_reticle_coords_hand)
                                    self.p2.aiming_reticle_coords_hand = None
                                    self.mode = "Normal"
                                    self.player_with_action = ""
                                    self.action_chosen = ""
                                    await self.p2.send_hand()
                                await self.p2.send_units_at_planet(self.last_planet_checked_for_battle)
                            elif self.what_to_do_with_searched_card == "DISCARD":
                                if self.searching_enemy_deck:
                                    self.p1.discard_card_from_deck(int(game_update_string[1]))
                                    await self.p1.send_discard()
                                else:
                                    self.p2.discard_card_from_deck(int(game_update_string[1]))
                                    await self.p2.send_discard()
                            self.p2.number_cards_to_search -= 1
                            self.p2.bottom_remaining_cards()
                            self.reset_search_values()
                            if self.resolving_search_box:
                                self.resolving_search_box = False
                            if self.battle_ability_to_resolve == "Elouith":
                                await self.resolve_battle_conclusion(name, game_update_string)
                                self.reset_battle_resolve_attributes()

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
        if self.player_resolving_battle_ability == self.name_2:
            winner = self.p2
        elif self.player_resolving_battle_ability == self.name_1:
            winner = self.p1
        if winner is not None:
            if self.round_number == self.last_planet_checked_for_battle:
                winner.move_all_at_planet_to_hq(self.last_planet_checked_for_battle)
                await winner.send_hq()
                await winner.send_units_at_planet(self.last_planet_checked_for_battle)
                winner.capture_planet(self.last_planet_checked_for_battle,
                                      self.planet_cards_array)
                self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                await winner.send_victory_display()
            self.planet_aiming_reticle_active = False
        self.planet_aiming_reticle_position = -1
        self.p1.reset_extra_attack_eob()
        self.p2.reset_extra_attack_eob()
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
            await self.change_phase("HEADQUARTERS")
            self.automated_headquarters_phase()
            await self.change_phase("DEPLOY")
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
        self.damage_from_atrox = False
        self.reset_battle_resolve_attributes()
        self.reset_choices_available()

    async def complete_nullify(self):
        if self.first_player_nullified == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if self.nullify_count % 2 == 0:
            if self.nullify_context == "Regular Action":
                num_player = "1"
                if self.player_with_action == self.name_2:
                    num_player = "2"
                string = ["HAND", num_player, str(self.nullified_card_pos)]
                await HandActions.update_game_event_action_hand(self, self.player_with_action, string,
                                                                may_nullify=False)
            elif self.nullify_context == "The Fury of Sicarius":
                await self.resolve_fury_sicarius(primary_player, secondary_player)
            elif self.nullify_context == "Indomitable":
                await self.resolve_indomitable(primary_player, secondary_player)
            elif self.nullify_context == "Glorious Intervention":
                primary_player.aiming_reticle_coords_hand = self.pos_shield_card
                primary_player.aiming_reticle_color = "blue"
                await primary_player.send_hand()
                self.effects_waiting_on_resolution.append("Glorious Intervention")
                self.player_resolving_effect.append(primary_player.name_player)
            elif self.nullify_context == "Bigga Is Betta":
                self.nullify_enabled = False
                new_string_list = self.nullify_string.split(sep="/")
                await DeployPhase.update_game_event_deploy_section(self, self.first_player_nullified,
                                                                   new_string_list)
                self.nullify_enabled = True
            elif self.nullify_context == "Foresight" or self.nullify_context == "Superiority":
                self.nullify_enabled = False
                new_string_list = self.nullify_string.split(sep="/")
                await CommandPhase.update_game_event_command_section(self, self.first_player_nullified,
                                                                     new_string_list)
                self.nullify_enabled = True
            elif self.nullify_context == "No Mercy":
                self.choices_available = []
                self.choice_context = ""
                self.name_player_making_choices = ""
                await self.send_search()
                await self.game_sockets[0].receive_game_update("No Mercy window offered")
                self.effects_waiting_on_resolution.append("No Mercy")
                self.player_resolving_effect.append(self.first_player_nullified)
            elif self.nullify_context == "Fall Back":
                self.choices_available = []
                self.name_player_making_choices = self.first_player_nullified
                self.choice_context = "Target Fall Back:"
                for i in range(len(primary_player.stored_cards_recently_destroyed)):
                    card = FindCard.find_card(primary_player.stored_cards_recently_destroyed[i],
                                              self.card_array)
                    if card.check_for_a_trait("Elite") and card.get_is_unit():
                        self.choices_available.append(card.get_name())
                await self.send_search()
        else:
            if self.nullified_card_pos != -1:
                primary_player.discard_card_from_hand(self.nullified_card_pos)
                if self.card_pos_to_deploy > self.nullified_card_pos:
                    self.card_pos_to_deploy -= 1
            elif self.nullified_card_name != "":
                primary_player.discard_card_name_from_hand(self.nullified_card_name)
            primary_player.spend_resources(self.cost_card_nullified)
            if self.nullify_context == "The Fury of Sicarius":
                if self.fury_search(primary_player, secondary_player):
                    await self.send_search()
            elif self.nullify_context == "Indomitable" or self.nullify_context == "Glorious Intervention":
                self.pos_shield_card = -1
        while self.nullify_count > 0:
            if self.first_player_nullified == self.name_1:
                card_pos_discard = self.p2.discard_card_name_from_hand("Nullify")
                if self.p2.aiming_reticle_coords_hand is not None:
                    if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                        self.p2.aiming_reticle_coords_hand -= 1
                self.nullify_count -= 1
                if self.nullify_count > 0:
                    card_pos_discard = self.p1.discard_card_name_from_hand("Nullify")
                    if self.p1.aiming_reticle_coords_hand is not None:
                        if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                            self.p1.aiming_reticle_coords_hand -= 1
                    self.nullify_count -= 1
            else:
                card_pos_discard = self.p1.discard_card_name_from_hand("Nullify")
                if self.p1.aiming_reticle_coords_hand is not None:
                    if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                        self.p1.aiming_reticle_coords_hand -= 1
                self.nullify_count -= 1
                if self.nullify_count > 0:
                    card_pos_discard = self.p2.discard_card_name_from_hand("Nullify")
                    if self.p2.aiming_reticle_coords_hand is not None:
                        if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                            self.p2.aiming_reticle_coords_hand -= 1
                    self.nullify_count -= 1
            if self.card_pos_to_deploy != -1:
                primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
        self.nullify_count = 0
        self.nullify_context = ""
        self.nullify_string = ""
        self.nullified_card_pos = -1
        self.nullified_card_name = ""
        self.cost_card_nullified = 0
        self.first_player_nullified = ""
        self.p1.num_nullify_played = 0
        self.p2.num_nullify_played = 0
        await self.p1.send_hand()
        await self.p2.send_hand()
        await self.p1.send_resources()
        await self.p2.send_resources()
        await self.p1.send_discard()
        await self.p2.send_discard()

    async def resolve_fury_sicarius(self, primary_player, secondary_player):
        primary_player.spend_resources(2)
        primary_player.discard_card_name_from_hand("The Fury of Sicarius")
        await primary_player.send_hand()
        await primary_player.send_discard()
        planet_pos, unit_pos = self.furiable_unit_position
        secondary_player.set_damage_given_pos(planet_pos, unit_pos, 999)
        await self.destroy_check_all_cards()
        await secondary_player.send_units_at_planet(planet_pos)
        await primary_player.send_units_at_planet(planet_pos)

    async def resolve_indomitable(self, primary_player, secondary_player):
        pos_holder = self.positions_of_units_to_take_damage[0]
        player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
        await primary_player.send_resources()
        primary_player.discard_card_from_hand(self.pos_shield_card)
        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        self.pos_shield_card = -1
        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
        if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                self.damage_on_units_list_before_new_damage[0]:
            primary_player.set_damage_given_pos(planet_pos, unit_pos,
                                                self.damage_on_units_list_before_new_damage[0])
        await self.shield_cleanup(primary_player, secondary_player, planet_pos)

    async def resolve_communications_relay(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
            await self.send_search()
            primary_player.exhaust_card_in_hq_given_name("Communications Relay")
            await primary_player.send_hq()
            if self.nullify_context == "Event Action":
                secondary_player.aiming_reticle_coords_hand = None
                secondary_player.aiming_reticle_coords_hand_2 = None
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                self.amount_spend_for_tzeentch_firestorm = 0
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
                await secondary_player.send_discard()
                await secondary_player.send_hand()
            elif self.nullify_context == "In Play Action":
                secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                              self.position_of_actioned_card[1])
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.nullified_card_name == "Zarathur's Flamers":
                    secondary_player.sacrifice_card_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                    await secondary_player.send_discard()
                await secondary_player.send_units_at_planet(self.position_of_actioned_card[0])
                self.position_of_actioned_card = (-1, -1)
            elif self.nullify_context == "Reaction":
                del self.reactions_needing_resolving[0]
                del self.player_who_resolves_reaction[0]
                del self.positions_of_unit_triggering_reaction[0]
            elif self.nullify_context == "Reaction Event":
                del self.reactions_needing_resolving[0]
                del self.player_who_resolves_reaction[0]
                del self.positions_of_unit_triggering_reaction[0]
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
                await secondary_player.send_hq()
                await secondary_player.send_discard()
            elif self.nullify_context == "The Fury of Sicarius":
                secondary_player.spend_resources(2)
                secondary_player.discard_card_name_from_hand("The Fury of Sicarius")
                if self.fury_search(secondary_player, primary_player):
                    await self.send_search()
                await secondary_player.send_discard()
                await secondary_player.send_hand()
            elif self.nullify_context == "Ferrin" or self.nullify_context == "Iridial":
                await self.resolve_battle_conclusion(secondary_player, game_string="")
        elif game_update_string[1] == "1":
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
            self.communications_relay_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            if self.nullified_card_name == "The Fury of Sicarius":
                self.nullify_enabled = False
                await self.resolve_fury_sicarius(secondary_player, primary_player)
                self.nullify_enabled = True
            else:
                await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            await self.send_search()
            self.communications_relay_enabled = True

    async def resolve_choice(self, name, game_update_string):
        if name == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if name == self.name_player_making_choices:
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.choice_context == "Shadowsun attachment from discard:":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.resolving_search_box = False
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
                                if len(winner.deck) > 2:
                                    winner.number_cards_to_search = 3
                                    self.cards_in_search_box = winner.deck[0:winner.number_cards_to_search]
                                    self.name_player_who_is_searching = winner.name_player
                                    self.number_who_is_searching = str(winner.number)
                                    self.what_to_do_with_searched_card = "DRAW"
                                    self.traits_of_searched_card = None
                                    self.card_type_of_searched_card = None
                                    self.faction_of_searched_card = None
                                    self.max_cost_of_searched_card = None
                                    self.no_restrictions_on_chosen_card = True
                                else:
                                    await self.game_sockets[0].receive_game_update("Too few cards in deck for search")
                                    await self.resolve_battle_conclusion(name, game_update_string)
                                await self.send_search()
                            elif self.battle_ability_to_resolve == "Tarrus":
                                winner_count = winner.count_units_in_play_all()
                                loser_count = loser.count_units_in_play_all()
                                if winner_count < loser_count:
                                    self.choices_available = ["Cards", "Resources"]
                                    self.choice_context = "Gains from Tarrus"
                                    await self.send_search()
                                else:
                                    await self.resolve_battle_conclusion(name, game_update_string)
                                    await self.send_search()
                            else:
                                if self.battle_ability_to_resolve == "Y'varn":
                                    self.yvarn_active = True
                                    self.p1_triggered_yvarn = False
                                    self.p2_triggered_yvarn = False
                                self.reset_choices_available()
                                await self.send_search()
                        elif self.choices_available[int(game_update_string[1])] == "No":
                            print("Does not want to resolve battle ability")
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Gains from Tarrus":
                        if self.choices_available[int(game_update_string[1])] == "Cards":
                            if name == self.name_1:
                                for _ in range(3):
                                    self.p1.draw_card()
                            elif name == self.name_2:
                                for _ in range(3):
                                    self.p2.draw_card()
                        elif self.choices_available[int(game_update_string[1])] == "Resources":
                            if name == self.name_1:
                                self.p1.add_resources(3)
                            elif name == self.name_2:
                                self.p2.add_resources(3)
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Amount to spend for Tzeentch's Firestorm:":
                        print(self.choices_available[int(game_update_string[1])])
                        if primary_player.spend_resources(int(game_update_string[1])):
                            self.amount_spend_for_tzeentch_firestorm = int(game_update_string[1])
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                    elif self.choice_context == "Use Nullify?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            self.reactions_needing_resolving.append("Nullify")
                            self.player_who_resolves_reaction.append(name)
                            self.positions_of_unit_triggering_reaction.append([int(primary_player.number), -1, -1])
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            await self.complete_nullify()
                            self.nullify_count = 0
                    elif self.choice_context == "Use Communications Relay?":
                        await self.resolve_communications_relay(name, game_update_string,
                                                                primary_player, secondary_player)
                    elif self.choice_context == "Use No Mercy?":
                        if game_update_string[1] == "0":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.game_sockets[0].receive_game_update(
                                    primary_player.name_player + " wants to play No Mercy; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = -1
                                self.nullified_card_name = "No Mercy"
                                self.cost_card_nullified = 0
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "No Mercy"
                                await self.send_search()
                            else:
                                self.choices_available = []
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                await self.send_search()
                                self.effects_waiting_on_resolution.append("No Mercy")
                                self.player_resolving_effect.append(name)
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            await self.better_shield_card_resolution(
                                secondary_player.name_player, self.last_shield_string, alt_shields=False,
                                can_no_mercy=False)
                    elif self.choice_context == "Target Holy Sepulchre:":
                        target = self.choices_available[int(game_update_string[1])]
                        primary_player.cards.append(target)
                        primary_player.discard.remove(target)
                        primary_player.stored_cards_recently_discarded.remove(target)
                        primary_player.exhaust_card_in_hq_given_name("Holy Sepulchre")
                        self.choices_available = []
                        if self.holy_sepulchre_check(primary_player):
                            for i in range(len(primary_player.stored_cards_recently_discarded)):
                                card = FindCard.find_card(primary_player.stored_cards_recently_discarded[i],
                                                          self.card_array)
                                if card.get_faction() == "Space Marines" and card.get_is_unit():
                                    self.choices_available.append(card.get_name())
                        if not self.choices_available:
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                        await self.send_search()
                        await primary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                    elif self.choice_context == "Target Fall Back:":
                        primary_player.spend_resources(1)
                        target = self.choices_available[int(game_update_string[1])]
                        card = FindCard.find_card(target, self.card_array)
                        primary_player.add_to_hq(card)
                        primary_player.discard.remove(target)
                        primary_player.stored_cards_recently_discarded.remove(target)
                        primary_player.stored_cards_recently_destroyed.remove(target)
                        primary_player.discard_card_name_from_hand("Fall Back!")
                        self.choices_available = []
                        if self.fall_back_check(primary_player):
                            for i in range(len(primary_player.stored_cards_recently_destroyed)):
                                card = FindCard.find_card(primary_player.stored_cards_recently_destroyed[i],
                                                          self.card_array)
                                if card.check_for_a_trait("Elite") and card.get_is_unit():
                                    self.choices_available.append(card.get_name())
                        if not self.choices_available:
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                        await self.send_search()
                        await primary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                    elif self.choice_context == "Target Shrine of Warpflame:":
                        target = self.choices_available[int(game_update_string[1])]
                        primary_player.cards.append(target)
                        primary_player.discard.remove(target)
                        primary_player.exhaust_card_in_hq_given_name("Shrine of Warpflame")
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.resolving_search_box = False
                        await self.send_search()
                        await primary_player.send_hq()
                        await primary_player.send_hand()
                        await primary_player.send_discard()
                    elif self.choice_context == "Use Shrine of Warpflame?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Target Shrine of Warpflame:"
                            print("\n---IN DISCARD---\n")
                            await self.game_sockets[0].receive_game_update("Shrine of Warpflame triggered")
                            print(primary_player.discard)
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                                if card.check_for_a_trait("Tzeentch"):
                                    self.choices_available.append(card.get_name())
                            await self.send_search()
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            await self.send_search()
                    elif self.choice_context == "Use Fall Back?":
                        if game_update_string[1] == "0":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.game_sockets[0].receive_game_update(
                                    primary_player.name_player + " wants to play Fall Back; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = -1
                                self.nullified_card_name = "Fall Back"
                                self.cost_card_nullified = 1
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "Fall Back"
                                await self.send_search()
                            else:
                                self.choices_available = []
                                self.choice_context = "Target Fall Back:"
                                for i in range(len(primary_player.stored_cards_recently_destroyed)):
                                    card = FindCard.find_card(primary_player.stored_cards_recently_destroyed[i],
                                                              self.card_array)
                                    if card.check_for_a_trait("Elite") and card.get_is_unit():
                                        self.choices_available.append(card.get_name())
                                await self.send_search()
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            await self.send_search()
                    elif self.choice_context == "Use Holy Sepulchre?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Target Holy Sepulchre:"
                            for i in range(len(primary_player.stored_cards_recently_discarded)):
                                card = FindCard.find_card(primary_player.stored_cards_recently_discarded[i],
                                                          self.card_array)
                                if card.get_faction() == "Space Marines" and card.get_is_unit():
                                    self.choices_available.append(card.get_name())
                            await self.send_search()
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            await self.send_search()
                    elif self.choice_context == "Use The Fury of Sicarius?":
                        planet_pos, unit_pos = self.furiable_unit_position
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            if secondary_player.nullify_check():
                                await self.game_sockets[0].receive_game_update(
                                    primary_player.name_player + " wants to play The Fury of Sicarius; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = -1
                                self.nullified_card_name = "The Fury of Sicarius"
                                self.cost_card_nullified = 2
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "The Fury of Sicarius"
                                await self.send_search()
                            elif secondary_player.communications_relay_check(planet_pos, unit_pos) and \
                                    self.communications_relay_enabled:
                                await self.game_sockets[0].receive_game_update(
                                    "Communications Relay may be used.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Communications Relay?"
                                self.nullified_card_name = "The Fury of Sicarius"
                                self.cost_card_nullified = 0
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "The Fury of Sicarius"
                                await self.send_search()
                            else:
                                await self.resolve_fury_sicarius(primary_player, secondary_player)
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            await self.destroy_check_all_cards()
                            await primary_player.send_units_at_planet(self.last_planet_checked_for_battle)
                            await secondary_player.send_units_at_planet(self.last_planet_checked_for_battle)
                    elif self.choice_context == "Use alternative shield effect?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            await self.better_shield_card_resolution(name, self.last_shield_string, alt_shields=False)
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_search()
                            if primary_player.cards[self.pos_shield_card] == "Indomitable":
                                if secondary_player.nullify_check():
                                    await self.game_sockets[0].receive_game_update(
                                        primary_player.name_player + " wants to play Indomitable; "
                                                                     "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = self.pos_shield_card
                                    self.nullified_card_name = "Indomitable"
                                    self.cost_card_nullified = 1
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Indomitable"
                                    await self.send_search()
                                elif primary_player.spend_resources(1):
                                    await self.resolve_indomitable(primary_player, secondary_player)
                            elif primary_player.cards[self.pos_shield_card] == "Glorious Intervention":
                                if secondary_player.nullify_check():
                                    await self.game_sockets[0].receive_game_update(
                                        primary_player.name_player + " wants to play Glorious Intervention; "
                                                                     "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = self.pos_shield_card
                                    self.nullified_card_name = "Glorious Intervention"
                                    self.cost_card_nullified = 1
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Glorious Intervention"
                                    await self.send_search()
                                elif primary_player.spend_resources(1):
                                    await primary_player.send_resources()
                                    primary_player.aiming_reticle_coords_hand = self.pos_shield_card
                                    primary_player.aiming_reticle_color = "blue"
                                    await primary_player.send_hand()
                                    self.effects_waiting_on_resolution.append("Glorious Intervention")
                                    self.player_resolving_effect.append(primary_player.name_player)
                    elif self.choice_context == "Shadowsun plays attachment from hand or discard?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            self.shadowsun_chose_hand = True
                            self.location_hand_attachment_shadowsun = -1
                            self.effects_waiting_on_resolution.append("Commander Shadowsun")
                            self.player_resolving_effect.append(name)
                            await self.game_sockets[0].receive_game_update("Choose card in hand")
                        else:
                            self.shadowsun_chose_hand = False
                            self.name_attachment_discard_shadowsun = ""
                            self.choice_context = "Shadowsun attachment from discard:"
                            self.name_player_making_choices = name
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                                if (card.get_card_type() == "Attachment" and card.get_faction() == "Tau" and
                                    card.get_cost() < 3) or card.get_name() == "Shadowsun's Stealth Cadre":
                                    if card.get_name() not in self.choices_available:
                                        self.choices_available.append(card.get_name())
                            if not self.choices_available:
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                await self.game_sockets[0].receive_game_update("No valid cards in discard")
                                self.resolving_search_box = False
                            else:
                                await self.game_sockets[0].receive_game_update("Choose card in discard")
                        await self.send_search()
                    elif self.choice_context == "Shadowsun attachment from discard:":
                        self.name_attachment_discard_shadowsun = self.choices_available[int(game_update_string[1])]
                        await self.game_sockets[0].receive_game_update(
                            "Selected a " + self.name_attachment_discard_shadowsun)
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.effects_waiting_on_resolution.append("Commander Shadowsun")
                        self.player_resolving_effect.append(name)
                        await self.send_search()
                    elif self.choice_context == "Which deck to use Biel-Tan Warp Spiders:":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            player = primary_player
                            self.searching_enemy_deck = False
                        else:
                            player = secondary_player
                            self.searching_enemy_deck = True
                        if len(player.deck) > 1:
                            player.number_cards_to_search = 2
                            self.bottom_cards_after_search = False
                            self.cards_in_search_box = player.deck[0:player.number_cards_to_search]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = str(primary_player.number)
                            self.what_to_do_with_searched_card = "DISCARD"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = None
                            self.faction_of_searched_card = None
                            self.max_cost_of_searched_card = None
                            self.no_restrictions_on_chosen_card = True
                        else:
                            await self.game_sockets[0].receive_game_update("Too few cards in deck")
                        await self.send_search()

    async def resolve_battle_ability_routine(self, name, game_update_string):
        if self.yvarn_active:
            if name == self.name_1:
                if not self.p1_triggered_yvarn:
                    if len(game_update_string) == 1:
                        if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                            await self.game_sockets[0].receive_game_update(self.name_1 + " declines y'varn.")
                            self.p1_triggered_yvarn = True
                    elif len(game_update_string) == 3:
                        if game_update_string[0] == "HAND":
                            if game_update_string[1] == "1":
                                played = self.p1.put_card_in_hand_into_hq(int(game_update_string[2]))
                                if played:
                                    self.p1_triggered_yvarn = True
                                    await self.p1.send_hq()
                                    await self.p1.send_hand()
            elif name == self.name_2:
                if not self.p2_triggered_yvarn:
                    if len(game_update_string) == 1:
                        if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                            await self.game_sockets[0].receive_game_update(self.name_2 + " declines y'varn.")
                            self.p2_triggered_yvarn = True
                    elif len(game_update_string) == 3:
                        if game_update_string[0] == "HAND":
                            if game_update_string[1] == "2":
                                played = self.p2.put_card_in_hand_into_hq(int(game_update_string[2]))
                                if played:
                                    self.p2_triggered_yvarn = True
                                    await self.p2.send_hq()
                                    await self.p2.send_hand()
            if self.p1_triggered_yvarn and self.p2_triggered_yvarn:
                self.yvarn_active = False
                self.reset_choices_available()
                await self.send_search()
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability, game_update_string)
        elif name == self.player_resolving_battle_ability:
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability, game_update_string)
            if self.battle_ability_to_resolve == "Ferrin":
                if len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if game_update_string[1] == "1":
                            if self.p1.cards_in_play[int(game_update_string[2]) + 1][int(game_update_string[3])]. \
                                    get_card_type != "Warlord":
                                can_continue = True
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if self.player_resolving_battle_ability != self.p1.name_player:
                                    if self.p1.communications_relay_check(planet_pos, unit_pos) and \
                                         self.communications_relay_enabled:
                                        await self.game_sockets[0].receive_game_update(
                                            "Communications Relay may be used.")
                                        can_continue = False
                                        self.choices_available = ["Yes", "No"]
                                        self.name_player_making_choices = self.p1.name_player
                                        self.choice_context = "Use Communications Relay?"
                                        self.nullified_card_name = "Ferrin"
                                        self.cost_card_nullified = 0
                                        self.nullify_string = "/".join(game_update_string)
                                        self.first_player_nullified = self.p2.name_player
                                        self.nullify_context = "Ferrin"
                                        await self.send_search()
                                if can_continue:
                                    self.p1.rout_unit(int(game_update_string[2]), int(game_update_string[3]))
                                    await self.p1.send_hq()
                                    await self.p1.send_units_at_planet(int(game_update_string[2]))
                                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                         game_update_string)
                        elif game_update_string[1] == "2":
                            if self.p2.cards_in_play[int(game_update_string[2]) + 1][int(game_update_string[3])]. \
                                    get_card_type != "Warlord":
                                can_continue = True
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if self.player_resolving_battle_ability != self.p2.name_player:
                                    if self.p2.communications_relay_check(planet_pos, unit_pos) and \
                                            self.communications_relay_enabled:
                                        await self.game_sockets[0].receive_game_update(
                                            "Communications Relay may be used.")
                                        can_continue = False
                                        self.choices_available = ["Yes", "No"]
                                        self.name_player_making_choices = self.p2.name_player
                                        self.choice_context = "Use Communications Relay?"
                                        self.nullified_card_name = "Ferrin"
                                        self.cost_card_nullified = 0
                                        self.nullify_string = "/".join(game_update_string)
                                        self.first_player_nullified = self.p1.name_player
                                        self.nullify_context = "Ferrin"
                                        await self.send_search()
                                if can_continue:
                                    self.p2.rout_unit(int(game_update_string[2]), int(game_update_string[3]))
                                    await self.p2.send_hq()
                                    await self.p2.send_units_at_planet(int(game_update_string[2]))
                                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                         game_update_string)
            elif self.battle_ability_to_resolve == "Carnath":
                if len(game_update_string) == 2:
                    if game_update_string[0] == "PLANETS":
                        self.battle_ability_to_resolve = self.planet_array[int(game_update_string[1])]
                        self.choices_available = ["Yes", "No"]
                        self.choice_context = "Resolve Battle Ability?"
                        self.name_player_making_choices = name
                        await self.send_search()
            elif self.battle_ability_to_resolve == "Iridial":
                if len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if game_update_string[1] == "1":
                            can_continue = True
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if self.player_resolving_battle_ability != self.p1.name_player:
                                if self.p1.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    await self.game_sockets[0].receive_game_update(
                                        "Communications Relay may be used.")
                                    can_continue = False
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = self.p1.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p2.name_player
                                    self.nullify_context = "Iridial"
                                    await self.send_search()
                            if can_continue:
                                self.p1.remove_damage_from_pos(int(game_update_string[2]), int(game_update_string[3]), 99)
                                await self.p1.send_units_at_planet(int(game_update_string[2]))
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
                        elif game_update_string[1] == "2":
                            can_continue = True
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if self.player_resolving_battle_ability != self.p2.name_player:
                                if self.p2.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    await self.game_sockets[0].receive_game_update(
                                        "Communications Relay may be used.")
                                    can_continue = False
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = self.p2.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p1.name_player
                                    self.nullify_context = "Iridial"
                                    await self.send_search()
                            if can_continue:
                                self.p2.remove_damage_from_pos(int(game_update_string[2]), int(game_update_string[3]), 99)
                                await self.p2.send_units_at_planet(int(game_update_string[2]))
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
                elif len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        if game_update_string[1] == "1":
                            can_continue = True
                            planet_pos = -2
                            unit_pos = int(game_update_string[2])
                            if self.player_resolving_battle_ability != self.p1.name_player:
                                if self.p1.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    await self.game_sockets[0].receive_game_update(
                                        "Communications Relay may be used.")
                                    can_continue = False
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = self.p1.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p2.name_player
                                    self.nullify_context = "Iridial"
                                    await self.send_search()
                            if can_continue:
                                self.p1.remove_damage_from_pos(-2, int(game_update_string[2]), 99)
                                await self.p1.send_hq()
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
                        elif game_update_string[1] == "2":
                            can_continue = True
                            planet_pos = -2
                            unit_pos = int(game_update_string[2])
                            if self.player_resolving_battle_ability != self.p2.name_player:
                                if self.p2.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    await self.game_sockets[0].receive_game_update(
                                        "Communications Relay may be used.")
                                    can_continue = False
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = self.p2.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p1.name_player
                                    self.nullify_context = "Iridial"
                                    await self.send_search()
                            if can_continue:
                                self.p2.remove_damage_from_pos(-2, int(game_update_string[2]), 99)
                                await self.p2.send_hq()
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
            elif self.battle_ability_to_resolve == "Plannum":
                if len(game_update_string) == 2:
                    if game_update_string[0] == "PLANETS":
                        if self.unit_to_move_position[0] != -1 and self.unit_to_move_position[1] != -1:
                            if self.player_resolving_battle_ability == self.name_1:
                                player = self.p1
                            else:
                                player = self.p2
                            player.reset_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                self.unit_to_move_position[1])
                            player.move_unit_to_planet(self.unit_to_move_position[0], self.unit_to_move_position[1],
                                                       int(game_update_string[1]))
                            if self.unit_to_move_position[0] == -2:
                                await player.send_hq()
                            else:
                                await player.send_units_at_planet(self.unit_to_move_position[0])
                            await player.send_units_at_planet(int(game_update_string[1]))
                            await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                 game_update_string)
                elif len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        if game_update_string[1] == str(self.number_resolving_battle_ability):
                            if self.player_resolving_battle_ability == self.name_1:
                                player = self.p1
                            else:
                                player = self.p2
                            if player.headquarters[int(game_update_string[2])].get_card_type() != "Warlord" and \
                                    player.headquarters[int(game_update_string[2])].get_card_type() != "Support":
                                if self.unit_to_move_position[0] != -1:
                                    player.reset_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                        self.unit_to_move_position[1])
                                self.unit_to_move_position[0] = -2
                                self.unit_to_move_position[1] = int(game_update_string[2])
                                player.set_aiming_reticle_in_play(-2, self.unit_to_move_position[1], "blue")
                                await player.send_hq()
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if game_update_string[1] == str(self.number_resolving_battle_ability):
                            if self.player_resolving_battle_ability == self.name_1:
                                player = self.p1
                            else:
                                player = self.p2
                            if player.cards_in_play[int(game_update_string[2]) + 1][int(game_update_string[3])] \
                                    .get_card_type() != "Warlord" and \
                                    player.cards_in_play[int(game_update_string[2]) + 1][int(game_update_string[3])] \
                                            .get_card_type() != "Support":
                                if self.unit_to_move_position[0] != -1:
                                    player.reset_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                        self.unit_to_move_position[1])
                                self.unit_to_move_position[0] = int(game_update_string[2])
                                self.unit_to_move_position[1] = int(game_update_string[3])
                                player.set_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                  self.unit_to_move_position[1], "blue")
                                await player.send_units_at_planet(self.unit_to_move_position[0])
            elif self.battle_ability_to_resolve == "Atrox Prime":
                if len(game_update_string) == 2:
                    planet_pos = int(game_update_string[1])
                    if self.last_planet_checked_for_battle + 1 == planet_pos or \
                            self.last_planet_checked_for_battle - 1 == planet_pos:
                        if name == self.name_1:
                            print("Resolve AOE")
                            await self.aoe_routine(self.p1, self.p2, planet_pos, 1)
                            self.damage_from_atrox = True
                        elif name == self.name_2:
                            print("Resolve AOE")
                            await self.aoe_routine(self.p2, self.p1, planet_pos, 1)
                            self.damage_from_atrox = True
                elif len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        self.damage_from_atrox = True
                        if game_update_string[1] == "1":
                            player = self.p1
                        else:
                            player = self.p2
                        player.suffer_area_effect_at_hq(1)
                        self.player_who_is_shielding = str(player.name_player)
                        self.number_who_is_shielding = str(player.number)
                        first_one = True
                        for i in range(len(player.headquarters)):
                            if player.headquarters[i].get_card_type() != "Support":
                                if first_one:
                                    player.set_aiming_reticle_in_play(-2, i, "red")
                                    first_one = False
                                else:
                                    player.set_aiming_reticle_in_play(-2, i, "blue")
                        await player.send_hq()

    async def destroy_check_cards_in_hq(self, player):
        i = 0
        while i < len(player.headquarters):
            if player.headquarters[i].get_card_type != "Support":
                if player.check_if_card_is_destroyed(-2, i):
                    player.destroy_card_in_hq(i)
                    i = i - 1
            i = i + 1
        if self.damage_from_atrox:
            await self.resolve_battle_conclusion(self.player_resolving_battle_ability, "")

    async def destroy_check_cards_at_planet(self, player, planet_num):
        i = 0
        while i < len(player.cards_in_play[planet_num + 1]):
            if self.attacker_planet == planet_num and self.attacker_position == i:
                if self.player_with_combat_turn == player.name_player:
                    player.set_aiming_reticle_in_play(planet_num, i, "blue")
            if player.check_if_card_is_destroyed(planet_num, i):
                if self.attacker_planet == planet_num and self.attacker_position == i:
                    self.attacker_planet = -1
                    self.attacker_position = -1
                player.destroy_card_in_play(planet_num, i)
                i = i - 1
            i = i + 1

    def holy_sepulchre_check(self, player):
        if player.search_card_in_hq("Holy Sepulchre", ready_relevant=True):
            for card_name in player.stored_cards_recently_discarded:
                card = FindCard.find_card(card_name, self.card_array)
                if card.get_faction() == "Space Marines" and card.get_is_unit():
                    return True
        return False

    def fall_back_check(self, player):
        if player.search_hand_for_card("Fall Back!"):
            if player.resources > 0:
                for card_name in player.stored_cards_recently_discarded:
                    card = FindCard.find_card(card_name, self.card_array)
                    if card.check_for_a_trait("Elite"):
                        return True
        return False

    async def destroy_check_all_cards(self):
        self.recently_damaged_units = []
        self.damage_taken_was_from_attack = []
        self.faction_of_attacker = []
        self.furiable_unit_position = (-1, -1)
        self.p1.cards_recently_discarded = []
        self.p2.cards_recently_discarded = []
        self.p1.cards_recently_destroyed = []
        self.p2.cards_recently_destroyed = []
        print("All units have been damaged. Move to destruction")
        for i in range(7):
            await self.destroy_check_cards_at_planet(self.p1, i)
            await self.destroy_check_cards_at_planet(self.p2, i)
        await self.destroy_check_cards_in_hq(self.p1)
        await self.destroy_check_cards_in_hq(self.p2)
        self.p1.stored_cards_recently_discarded = copy.deepcopy(self.p1.cards_recently_discarded)
        self.p2.stored_cards_recently_discarded = copy.deepcopy(self.p2.cards_recently_discarded)
        self.p1.stored_cards_recently_destroyed = copy.deepcopy(self.p1.cards_recently_destroyed)
        self.p2.stored_cards_recently_destroyed = copy.deepcopy(self.p2.cards_recently_destroyed)
        if self.fall_back_check(self.p1):
            already_fall_back = False
            for i in range(len(self.reactions_needing_resolving)):
                if self.reactions_needing_resolving[i] == "Fall Back!":
                    if self.player_who_resolves_reaction[i] == self.name_1:
                        already_fall_back = True
            if not already_fall_back:
                self.reactions_needing_resolving.append("Fall Back!")
                self.player_who_resolves_reaction.append(self.name_1)
                self.positions_of_unit_triggering_reaction.append((1, -1, -1))
        if self.fall_back_check(self.p2):
            already_fall_back = False
            for i in range(len(self.reactions_needing_resolving)):
                if self.reactions_needing_resolving[i] == "Fall Back!":
                    if self.player_who_resolves_reaction[i] == self.name_2:
                        already_fall_back = True
            if not already_fall_back:
                self.reactions_needing_resolving.append("Fall Back!")
                self.player_who_resolves_reaction.append(self.name_2)
                self.positions_of_unit_triggering_reaction.append((2, -1, -1))
        if self.holy_sepulchre_check(self.p1):
            already_sepulchre = False
            for i in range(len(self.reactions_needing_resolving)):
                if self.reactions_needing_resolving[i] == "Holy Sepulchre":
                    if self.player_who_resolves_reaction[i] == self.name_1:
                        already_sepulchre = True
            if not already_sepulchre:
                self.reactions_needing_resolving.append("Holy Sepulchre")
                self.player_who_resolves_reaction.append(self.name_1)
                self.positions_of_unit_triggering_reaction.append((1, -1, -1))
        if self.holy_sepulchre_check(self.p2):
            already_sepulchre = False
            for i in range(len(self.reactions_needing_resolving)):
                if self.reactions_needing_resolving[i] == "Holy Sepulchre":
                    if self.player_who_resolves_reaction[i] == self.name_2:
                        already_sepulchre = True
            if not already_sepulchre:
                self.reactions_needing_resolving.append("Holy Sepulchre")
                self.player_who_resolves_reaction.append(self.name_2)
                self.positions_of_unit_triggering_reaction.append((2, -1, -1))
        if self.p2.stored_cards_recently_destroyed:
            if self.p1.search_card_in_hq("Shrine of Warpflame", ready_relevant=True):
                already_warp_flame = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Shrine of Warpflame":
                        if self.player_who_resolves_reaction[i] == self.name_1:
                            already_warp_flame = True
                if not already_warp_flame:
                    self.reactions_needing_resolving.append("Shrine of Warpflame")
                    self.player_who_resolves_reaction.append(self.name_1)
                    self.positions_of_unit_triggering_reaction.append((1, -1, -1))
        if self.p1.stored_cards_recently_destroyed:
            if self.p2.search_card_in_hq("Shrine of Warpflame", ready_relevant=True):
                already_warp_flame = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Shrine of Warpflame":
                        if self.player_who_resolves_reaction[i] == self.name_2:
                            already_warp_flame = True
                if not already_warp_flame:
                    self.reactions_needing_resolving.append("Shrine of Warpflame")
                    self.player_who_resolves_reaction.append(self.name_2)
                    self.positions_of_unit_triggering_reaction.append((2, -1, -1))
        await self.p1.send_resources()
        await self.p2.send_resources()
        await self.p1.send_discard()
        await self.p2.send_discard()

    def advance_damage_aiming_reticle(self):
        pos_holder = self.positions_of_units_to_take_damage[0]
        player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
        if player_num == 1:
            self.p1.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
        elif player_num == 2:
            self.p2.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")

    async def change_phase(self, new_val, refresh_abilities=True):
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.phase = new_val
        if self.phase == "COMMAND":
            self.committing_warlords = True
        sacrifice_locations = self.p1.sacrifice_check_eop()
        if sacrifice_locations:
            for i in range(len(sacrifice_locations)):
                if sacrifice_locations[i]:
                    if i == 0:
                        await self.p1.send_hq()
                    else:
                        await self.p1.send_units_at_planet(i - 1)
            await self.p1.send_discard()
        sacrifice_locations = self.p2.sacrifice_check_eop()
        if sacrifice_locations:
            for i in range(len(sacrifice_locations)):
                if sacrifice_locations[i]:
                    if i == 0:
                        await self.p2.send_hq()
                    else:
                        await self.p2.send_units_at_planet(i - 1)
            await self.p1.send_discard()
        self.p1.reset_extra_attack_eop()
        self.p2.reset_extra_attack_eop()
        self.p1.reset_extra_abilities_eop()
        self.p2.reset_extra_abilities_eop()
        self.p1.reset_all_blanked_eop()
        self.p2.reset_all_blanked_eop()
        if refresh_abilities:
            self.p1.refresh_once_per_phase_abilities()
            self.p2.refresh_once_per_phase_abilities()

    def clear_attacker_aiming_reticle(self):
        player_num, planet_pos, unit_pos = self.attacker_location
        if player_num == 1:
            self.p1.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        elif player_num == 2:
            self.p2.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        self.damage_from_attack = False
        self.attacker_location = [-1, -1, -1]

    async def better_shield_card_resolution(self, name, game_update_string, alt_shields=True, can_no_mercy=True):
        if name == self.player_who_is_shielding:
            pos_holder = self.positions_of_units_to_take_damage[0]
            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
            if player_num == 1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.recently_damaged_units.append(self.positions_of_units_to_take_damage[0])
                    if self.positions_attackers_of_units_to_take_damage[0] is not None:
                        self.damage_taken_was_from_attack.append(True)
                        att_num, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
                        self.faction_of_attacker.append(secondary_player.get_faction_given_pos(att_pla, att_pos))
                        if primary_player.search_attachments_at_pos(planet_pos, unit_pos, "Repulsor Impact Field"):
                            if att_num == 1:
                                self.p1.assign_damage_to_pos(att_pla, att_pos, 2)
                            else:
                                self.p2.assign_damage_to_pos(att_pla, att_pos, 2)
                        if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                            if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Black Heart Ravager":
                                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                                    primary_player.rout_unit(planet_pos, unit_pos)
                                    await primary_player.send_hq()
                    else:
                        self.damage_taken_was_from_attack.append(False)
                        self.faction_of_attacker.append("")
                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        hand_pos = int(game_update_string[2])
                        shields = primary_player.get_shields_given_pos(hand_pos, planet_pos=planet_pos)
                        alt_shield_check = False
                        if alt_shields:
                            if primary_player.cards[hand_pos] in self.alternative_shields:
                                if primary_player.cards[hand_pos] == "Indomitable":
                                    if primary_player.resources > 0:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            if primary_player.get_faction_given_pos(
                                                    planet_pos, unit_pos) == "Space Marines":
                                                alt_shield_check = True
                                                self.pos_shield_card = hand_pos
                                                self.choices_available = ["Shield", "Effect"]
                                                self.name_player_making_choices = name
                                                self.choice_context = "Use alternative shield effect?"
                                                self.last_shield_string = game_update_string
                                                await self.send_search()
                                elif primary_player.cards[hand_pos] == "Glorious Intervention":
                                    if primary_player.resources > 0:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            alt_shield_check = True
                                            self.pos_shield_card = hand_pos
                                            self.choices_available = ["Shield", "Effect"]
                                            self.name_player_making_choices = name
                                            self.choice_context = "Use alternative shield effect?"
                                            self.last_shield_string = game_update_string
                                            await self.send_search()
                        if shields > 0 and not alt_shield_check:
                            print("Just before can shield check")
                            if self.damage_can_be_shielded[0]:
                                no_mercy_possible = False
                                if can_no_mercy:
                                    for i in range(len(secondary_player.cards)):
                                        if secondary_player.cards[i] == "No Mercy":
                                            no_mercy_possible = True
                                if no_mercy_possible:
                                    self.last_shield_string = game_update_string
                                    self.choice_context = "Use No Mercy?"
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    await self.send_search()
                                else:
                                    shields = min(shields, self.amount_that_can_be_removed_by_shield[0])
                                    took_damage = True
                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, shields)
                                    if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                            self.damage_on_units_list_before_new_damage[0]:
                                        primary_player.set_damage_given_pos(
                                            planet_pos, unit_pos, self.damage_on_units_list_before_new_damage[0])
                                        took_damage = False
                                    primary_player.discard_card_from_hand(hand_pos)
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    if took_damage:
                                        self.recently_damaged_units.append(self.positions_of_units_to_take_damage[0])
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            self.damage_taken_was_from_attack.append(True)
                                            att_num, att_pla, att_pos = self.\
                                                positions_attackers_of_units_to_take_damage[0]
                                            self.faction_of_attacker.append(secondary_player.get_faction_given_pos(
                                                att_pla, att_pos
                                            ))
                                            if primary_player.search_attachments_at_pos(planet_pos, unit_pos,
                                                                                        "Repulsor Impact Field"):
                                                if att_num == 1:
                                                    self.p1.assign_damage_to_pos(att_pla, att_pos, 2)
                                                else:
                                                    self.p2.assign_damage_to_pos(att_pla, att_pos, 2)
                                            if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                                                if secondary_player.get_ability_given_pos(att_pla, att_pos) == \
                                                        "Black Heart Ravager":
                                                    if primary_player.cards_in_play[planet_pos + 1][unit_pos]\
                                                            .get_card_type() != "Warlord":
                                                        primary_player.rout_unit(planet_pos, unit_pos)
                                                        await primary_player.send_hq()
                                        else:
                                            self.damage_taken_was_from_attack.append(False)
                                            self.faction_of_attacker.append("")
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                            else:
                                await self.game_sockets[0].receive_game_update("This damage can not be shielded!")
                elif game_update_string[0] == "HQ":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        hq_pos = int(game_update_string[2])
                        if primary_player.headquarters[hq_pos].get_ability() == "Rockcrete Bunker":
                            print("is rockcrete bunker")
                            if primary_player.headquarters[hq_pos].get_ready():
                                print("is ready")
                                primary_player.exhaust_given_pos(-2, hq_pos)
                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                await primary_player.send_hq()
                                if primary_player.get_damage_given_pos(planet_pos, unit_pos) == \
                                        self.damage_on_units_list_before_new_damage[0]:
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                                else:
                                    await primary_player.send_units_at_planet(planet_pos)
            elif len(game_update_string) == 5:
                if planet_pos == -2:
                    if game_update_string[0] == "ATTACHMENT":
                        if game_update_string[1] == "HQ":
                            if game_update_string[2] == self.number_who_is_shielding:
                                if int(game_update_string[3]) == unit_pos:
                                    attachment_pos = int(game_update_string[4])
                                    attachment = primary_player.headquarters[unit_pos].get_attachments()[attachment_pos]
                                    if attachment.get_ability() == "Iron Halo" and attachment.get_ready():
                                        attachment.exhaust_card()
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        self.pos_shield_card = -1
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                                        if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                                self.damage_on_units_list_before_new_damage[0]:
                                            primary_player.set_damage_given_pos(
                                                planet_pos, unit_pos, self.damage_on_units_list_before_new_damage[0])
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
            elif len(game_update_string) == 6:
                if game_update_string[0] == "ATTACHMENT":
                    if game_update_string[1] == "IN_PLAY":
                        if game_update_string[2] == self.number_who_is_shielding:
                            if int(game_update_string[3]) == planet_pos:
                                if int(game_update_string[4]) == unit_pos:
                                    attachment_pos = int(game_update_string[5])
                                    attachment = primary_player.cards_in_play[planet_pos + 1][unit_pos]\
                                        .get_attachments()[attachment_pos]
                                    if attachment.get_ability() == "Iron Halo" and attachment.get_ready():
                                        attachment.exhaust_card()
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        self.pos_shield_card = -1
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                                        if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                                self.damage_on_units_list_before_new_damage[0]:
                                            primary_player.set_damage_given_pos(
                                                planet_pos, unit_pos, self.damage_on_units_list_before_new_damage[0])
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)

    async def resolve_reaction(self, name, game_update_string):
        if name == self.player_who_resolves_reaction[0]:
            if name == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.reactions_needing_resolving[0] == "Power from Pain":
                        await self.game_sockets[0].receive_game_update("No sacrifice for Power from Pain")
                    if self.reactions_needing_resolving[0] == "Cato's Stronghold":
                        self.cato_stronghold_activated = False
                        self.allowed_planets_cato_stronghold = []
                    if self.reactions_needing_resolving[0] == "Foresight":
                        primary_player.aiming_reticle_coords_hand = None
                    if self.reactions_needing_resolving[0] == "Alaitoc Shrine":
                        self.allowed_units_alaitoc_shrine = []
                        self.alaitoc_shrine_activated = False
                    if self.reactions_needing_resolving[0] == "Fire Warrior Elite":
                        self.may_move_defender = False
                        current_planet, current_unit = self.last_defender_position
                        last_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                                   str(current_unit)]
                        await CombatPhase.update_game_event_combat_section(
                            self, secondary_player.name_player, last_game_update_string)
                    if self.reactions_needing_resolving[0] == "Soul Grinder":
                        planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                        unit_pos = self.positions_of_unit_triggering_reaction[0][2]
                        secondary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                        await secondary_player.send_units_at_planet(planet_pos)
                    if self.reactions_needing_resolving[0] == "Nullify":
                        await self.complete_nullify()
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.reactions_needing_resolving[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_info_box()
            elif len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    if self.reactions_needing_resolving[0] == "Foresight":
                        warlord_planet = primary_player.warlord_commit_location
                        new_planet = int(game_update_string[1])
                        if abs(warlord_planet - new_planet) == 1:
                            primary_player.commit_warlord_to_planet_from_planet(warlord_planet, new_planet)
                            del self.positions_of_unit_triggering_reaction[0]
                            del self.reactions_needing_resolving[0]
                            del self.player_who_resolves_reaction[0]
                            await self.send_info_box()
                            await primary_player.send_units_at_planet(new_planet)
                            await primary_player.send_units_at_planet(warlord_planet)
                            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                            primary_player.aiming_reticle_coords_hand = None
                            await primary_player.send_hand()
                            await primary_player.send_discard()
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    if game_update_string[1] == primary_player.get_number():
                        if self.reactions_needing_resolving[0] == "Wailing Wraithfighter":
                            hand_pos = int(game_update_string[2])
                            primary_player.discard_card_from_hand(hand_pos)
                            del self.positions_of_unit_triggering_reaction[0]
                            del self.reactions_needing_resolving[0]
                            del self.player_who_resolves_reaction[0]
                            await primary_player.send_discard()
                            await primary_player.send_hand()
                            await self.send_info_box()
                        elif self.reactions_needing_resolving[0] == "Banshee Power Sword":
                            hand_pos = int(game_update_string[2])
                            primary_player.discard_card_from_hand(hand_pos)
                            self.banshee_power_sword_extra_attack += 1
                            await primary_player.send_discard()
                            await primary_player.send_hand()
                        elif self.reactions_needing_resolving[0] == "Elysian Assault Team":
                            hand_pos = int(game_update_string[2])
                            if primary_player.cards[hand_pos] == "Elysian Assault Team":
                                planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                                card = FindCard.find_card("Elysian Assault Team", self.card_array)
                                primary_player.add_card_to_planet(card, planet_pos)
                                del primary_player.cards[hand_pos]
                                more = False
                                for i in range(len(primary_player.cards)):
                                    if primary_player.cards[i] == "Elysian Assault Team":
                                        more = True
                                if not more:
                                    del self.reactions_needing_resolving[0]
                                    del self.positions_of_unit_triggering_reaction[0]
                                    del self.player_who_resolves_reaction[0]
                                await primary_player.send_hand()
                                await self.send_info_box()
                                await primary_player.send_units_at_planet(planet_pos)
                elif game_update_string[0] == "HQ":
                    unit_pos = int(game_update_string[2])
                    if int(primary_player.get_number()) == int(self.positions_of_unit_triggering_reaction[0][0]):
                        if self.reactions_needing_resolving[0] == "Power from Pain":
                            if primary_player.headquarters[unit_pos].get_card_type() == "Army":
                                primary_player.sacrifice_card_in_hq(unit_pos)
                                del self.positions_of_unit_triggering_reaction[0]
                                del self.reactions_needing_resolving[0]
                                del self.player_who_resolves_reaction[0]
                                await secondary_player.dark_eldar_event_played()
                                await primary_player.send_hq()
                                await primary_player.send_discard()
                                await self.send_info_box()
                        elif self.reactions_needing_resolving[0] == "Nullify":
                            if primary_player.valid_nullify_unit(-2, unit_pos):
                                primary_player.exhaust_given_pos(-2, unit_pos)
                                self.nullify_count += 1
                                primary_player.num_nullify_played += 1
                                if secondary_player.nullify_check():
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    await self.game_sockets[0].receive_game_update(secondary_player.name_player +
                                                                                   " counter nullify offered.")
                                    await self.send_search()
                                else:
                                    await self.complete_nullify()
                                del self.positions_of_unit_triggering_reaction[0]
                                del self.reactions_needing_resolving[0]
                                del self.player_who_resolves_reaction[0]
                                await primary_player.send_hq()
                        elif self.reactions_needing_resolving[0] == "Alaitoc Shrine":
                            if not self.cato_stronghold_activated:
                                if primary_player.get_ability_given_pos(-2, unit_pos) == "Alaitoc Shrine":
                                    if primary_player.get_ready_given_pos(-2, unit_pos):
                                        primary_player.exhaust_given_pos(-2, unit_pos)
                                        self.alaitoc_shrine_activated = True
                                        await primary_player.send_hq()
                        elif self.reactions_needing_resolving[0] == "Cato's Stronghold":
                            if not self.cato_stronghold_activated:
                                if primary_player.get_ability_given_pos(-2, unit_pos) == "Cato's Stronghold":
                                    if primary_player.get_ready_given_pos(-2, unit_pos):
                                        primary_player.exhaust_given_pos(-2, unit_pos)
                                        self.cato_stronghold_activated = True
                                        await primary_player.send_hq()
                        elif self.reactions_needing_resolving[0] == "Murder Cogitator":
                            if primary_player.get_ability_given_pos(-2, unit_pos) == "Murder Cogitator":
                                if primary_player.headquarters[unit_pos].get_ready():
                                    primary_player.exhaust_given_pos(-2, unit_pos)
                                    await primary_player.send_hq()
                                    await primary_player.reveal_top_card_deck()
                                    card = primary_player.get_top_card_deck()
                                    if card is not None:
                                        if card.get_is_unit() and card.get_faction() == "Chaos":
                                            await self.game_sockets[0].receive_game_update("Card is drawn")
                                            primary_player.draw_card()
                                            await primary_player.send_hand()
                                        else:
                                            await self.game_sockets[0].receive_game_update("Card is not drawn")
                                    more = primary_player.search_card_in_hq("Murder Cogitator", ready_relevant=True)
                                    if not more:
                                        del self.positions_of_unit_triggering_reaction[0]
                                        del self.reactions_needing_resolving[0]
                                        del self.player_who_resolves_reaction[0]
                                    await self.send_info_box()
                        elif self.reactions_needing_resolving[0] == "Beasthunter Wyches":
                            if primary_player.get_ability_given_pos(-2, unit_pos) == "Beasthunter Wyches":
                                if primary_player.headquarters[unit_pos].get_reaction_available():
                                    if primary_player.spend_resources(1):
                                        primary_player.headquarters[unit_pos].set_reaction_available(False)
                                        primary_player.summon_token_at_hq("Khymera", 1)
                                        del self.positions_of_unit_triggering_reaction[0]
                                        del self.reactions_needing_resolving[0]
                                        del self.player_who_resolves_reaction[0]
                                        await self.send_info_box()
                                        await primary_player.send_hq()
                                        await primary_player.send_resources()
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    print("Check what player")
                    print(self.player_who_resolves_reaction)
                    if name == self.player_who_resolves_reaction[0]:
                        if self.reactions_needing_resolving[0] == "Power from Pain":
                            if int(primary_player.get_number()) == int(
                                    self.positions_of_unit_triggering_reaction[0][0]):
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                                    primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                                    del self.positions_of_unit_triggering_reaction[0]
                                    del self.reactions_needing_resolving[0]
                                    del self.player_who_resolves_reaction[0]
                                    await secondary_player.dark_eldar_event_played()
                                    await primary_player.send_units_at_planet(planet_pos)
                                    await primary_player.send_discard()
                                    await self.send_info_box()
                        elif self.reactions_needing_resolving[0] == "Nullify":
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if primary_player.valid_nullify_unit(planet_pos, unit_pos):
                                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                primary_player.num_nullify_played += 1
                                self.nullify_count += 1
                                if secondary_player.nullify_check():
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    await self.game_sockets[0].receive_game_update(secondary_player.name_player +
                                                                                   " counter nullify offered.")
                                    await self.send_search()
                                else:
                                    await self.complete_nullify()
                                del self.positions_of_unit_triggering_reaction[0]
                                del self.reactions_needing_resolving[0]
                                del self.player_who_resolves_reaction[0]
                                await primary_player.send_units_at_planet(planet_pos)
                        elif self.reactions_needing_resolving[0] == "Soul Grinder":
                            if primary_player.get_number() == game_update_string[1]:
                                planet_pos_sg = self.positions_of_unit_triggering_reaction[0][1]
                                unit_pos_sg = self.positions_of_unit_triggering_reaction[0][2]
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if planet_pos == planet_pos_sg:
                                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                                        primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                                        secondary_player.reset_aiming_reticle_in_play(planet_pos_sg, unit_pos_sg)
                                        await primary_player.send_units_at_planet(planet_pos)
                                        await secondary_player.send_units_at_planet(planet_pos)
                                        del self.positions_of_unit_triggering_reaction[0]
                                        del self.reactions_needing_resolving[0]
                                        del self.player_who_resolves_reaction[0]
                        elif self.reactions_needing_resolving[0] == "Fire Warrior Elite":
                            if game_update_string[1] == primary_player.get_number():
                                current_planet, current_unit = self.last_defender_position
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if planet_pos == self.positions_of_unit_triggering_reaction[0][1]:
                                    if primary_player.get_ability_given_pos(
                                            planet_pos, unit_pos) == "Fire Warrior Elite":
                                        primary_player.reset_aiming_reticle_in_play(current_planet, current_unit)
                                        self.may_move_defender = False
                                        print("Calling defender in the funny way")
                                        await CombatPhase.update_game_event_combat_section(
                                            self, secondary_player.name_player, game_update_string)
                                        del self.reactions_needing_resolving[0]
                                        del self.player_who_resolves_reaction[0]
                                        del self.positions_of_unit_triggering_reaction[0]
                                        await self.send_info_box()
                        elif self.reactions_needing_resolving[0] == "Eldorath Starbane":
                            print("Reached Starbane code")
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if game_update_string[1] == "1":
                                player_exhausting_unit = self.p1
                            else:
                                player_exhausting_unit = self.p2
                            can_continue = True
                            if player_exhausting_unit.name_player == secondary_player.name_player:
                                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                    can_continue = False
                                    await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
                                elif secondary_player.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    can_continue = False
                                    await self.game_sockets[0].receive_game_update("Communications Relay may be used.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = self.action_chosen
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Reaction"
                                    await self.send_search()
                            if can_continue:
                                if self.positions_of_unit_triggering_reaction[0][1] == planet_pos:
                                    if player_exhausting_unit.cards_in_play[planet_pos + 1][unit_pos]. \
                                            get_card_type() != "Warlord":
                                        player_exhausting_unit.exhaust_given_pos(planet_pos, unit_pos)
                                        del self.positions_of_unit_triggering_reaction[0]
                                        del self.reactions_needing_resolving[0]
                                        del self.player_who_resolves_reaction[0]
                                        await player_exhausting_unit.send_units_at_planet(planet_pos)
                        elif self.reactions_needing_resolving[0] == "Shrouded Harlequin":
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if game_update_string[1] != primary_player.get_number():
                                can_continue = True
                                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                    can_continue = False
                                    await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
                                elif secondary_player.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    can_continue = False
                                    await self.game_sockets[0].receive_game_update("Communications Relay may be used.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = self.action_chosen
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Reaction"
                                    await self.send_search()
                                if can_continue:
                                    secondary_player.exhaust_given_pos(planet_pos, unit_pos)
                                    del self.positions_of_unit_triggering_reaction[0]
                                    del self.reactions_needing_resolving[0]
                                    del self.player_who_resolves_reaction[0]
                                    await secondary_player.send_units_at_planet(planet_pos)
                        elif self.reactions_needing_resolving[0] == "Superiority":
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if game_update_string[1] == "1":
                                player_being_hit = self.p1
                            else:
                                player_being_hit = self.p2
                            can_continue = True
                            if player_being_hit.name_player == secondary_player.name_player:
                                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                                    can_continue = False
                                    await self.game_sockets[0].receive_game_update("Immune to enemy card abilities.")
                                elif secondary_player.communications_relay_check(planet_pos, unit_pos) and \
                                        self.communications_relay_enabled:
                                    can_continue = False
                                    await self.game_sockets[0].receive_game_update("Communications Relay may be used.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Communications Relay?"
                                    self.nullified_card_name = self.action_chosen
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Reaction Event"
                                    await self.send_search()
                            if can_continue:
                                if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
                                    player_being_hit.cards_in_play[planet_pos + 1][unit_pos].hit_by_superiority = True
                                    card_name = player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_name()
                                    text = card_name + ", position " + str(planet_pos) \
                                        + " " + str(unit_pos) + " hit by superiority."
                                    await self.game_sockets[0].receive_game_update(text)
                                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                                    primary_player.aiming_reticle_coords_hand = None
                                    await primary_player.send_discard()
                                    await primary_player.send_hand()
                                    del self.positions_of_unit_triggering_reaction[0]
                                    del self.reactions_needing_resolving[0]
                                    del self.player_who_resolves_reaction[0]
                                    await self.send_info_box()
                        elif self.reactions_needing_resolving[0] == "Alaitoc Shrine":
                            if int(primary_player.get_number()) == int(
                                    self.positions_of_unit_triggering_reaction[0][0]):
                                if self.alaitoc_shrine_activated:
                                    player_num = int(primary_player.get_number())
                                    planet_pos = int(game_update_string[2])
                                    unit_pos = int(game_update_string[3])
                                    full_position = [player_num, planet_pos, unit_pos]
                                    if full_position in self.allowed_units_alaitoc_shrine:
                                        if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                            primary_player.ready_given_pos(planet_pos, unit_pos)
                                            del self.positions_of_unit_triggering_reaction[0]
                                            del self.reactions_needing_resolving[0]
                                            del self.player_who_resolves_reaction[0]
                                            self.alaitoc_shrine_activated = False
                                            self.allowed_units_alaitoc_shrine = []
                                            await primary_player.send_units_at_planet(planet_pos)
                                            await self.send_info_box()
                                        else:
                                            await self.game_sockets[0].receive_game_update("Unit already ready")
                        elif self.reactions_needing_resolving[0] == "Cato's Stronghold":
                            if int(primary_player.get_number()) == int(
                                    self.positions_of_unit_triggering_reaction[0][0]):
                                if self.cato_stronghold_activated:
                                    planet_pos = int(game_update_string[2])
                                    unit_pos = int(game_update_string[3])
                                    if planet_pos in self.allowed_planets_cato_stronghold:
                                        if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                            primary_player.ready_given_pos(planet_pos, unit_pos)
                                            del self.positions_of_unit_triggering_reaction[0]
                                            del self.reactions_needing_resolving[0]
                                            del self.player_who_resolves_reaction[0]
                                            self.allowed_planets_cato_stronghold = []
                                            self.cato_stronghold_activated = False
                                            await primary_player.send_units_at_planet(planet_pos)
                                            await self.send_info_box()
                                        else:
                                            await self.game_sockets[0].receive_game_update("Unit already ready")
                        elif self.reactions_needing_resolving[0] == "Beasthunter Wyches":
                            if int(primary_player.get_number()) == int(
                                    self.positions_of_unit_triggering_reaction[0][0]):
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Beasthunter Wyches":
                                    if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_reaction_available():
                                        if primary_player.spend_resources(1):
                                            primary_player.cards_in_play[planet_pos + 1][unit_pos]. \
                                                set_reaction_available(False)
                                            primary_player.summon_token_at_hq("Khymera", 1)
                                            del self.positions_of_unit_triggering_reaction[0]
                                            del self.reactions_needing_resolving[0]
                                            del self.player_who_resolves_reaction[0]
                                            await self.send_info_box()
                                            await primary_player.send_hq()
                                            await primary_player.send_resources()
                        elif self.reactions_needing_resolving[0] == "Spiritseer Erathal":
                            if primary_player.get_number() == game_update_string[1]:
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if self.attacker_planet == int(game_update_string[2]):
                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                    del self.positions_of_unit_triggering_reaction[0]
                                    del self.reactions_needing_resolving[0]
                                    del self.player_who_resolves_reaction[0]
                                    await self.send_info_box()
                                    await primary_player.send_units_at_planet(planet_pos)
                        elif self.reactions_needing_resolving[0] == "Burna Boyz":
                            if primary_player.get_number() != game_update_string[1]:
                                origin_planet = self.positions_of_unit_triggering_reaction[0][1]
                                if int(game_update_string[2]) == origin_planet:
                                    prev_def_planet, prev_def_pos = self.last_defender_position
                                    target_unit_pos = int(game_update_string[3])
                                    print("\n\nBURNA BOYZ\n\n")
                                    if target_unit_pos == prev_def_pos:
                                        await self.game_sockets[0].receive_game_update("Can't select last defender")
                                    else:
                                        can_continue = True
                                        if secondary_player.get_immune_to_enemy_card_abilities(origin_planet,
                                                                                               target_unit_pos):
                                            can_continue = False
                                            await self.game_sockets[0].receive_game_update(
                                                "Immune to enemy card abilities.")
                                        elif secondary_player.communications_relay_check(origin_planet,
                                                                                         target_unit_pos) and \
                                                self.communications_relay_enabled:
                                            can_continue = False
                                            await self.game_sockets[0].receive_game_update(
                                                "Communications Relay may be used.")
                                            self.choices_available = ["Yes", "No"]
                                            self.name_player_making_choices = secondary_player.name_player
                                            self.choice_context = "Use Communications Relay?"
                                            self.nullified_card_name = self.action_chosen
                                            self.cost_card_nullified = 0
                                            self.nullify_string = "/".join(game_update_string)
                                            self.first_player_nullified = primary_player.name_player
                                            self.nullify_context = "Reaction"
                                            await self.send_search()
                                        if can_continue:
                                            secondary_player.assign_damage_to_pos(origin_planet, target_unit_pos, 1)
                                            secondary_player.set_aiming_reticle_in_play(origin_planet, target_unit_pos,
                                                                                        "blue")
                                            del self.positions_of_unit_triggering_reaction[0]
                                            del self.reactions_needing_resolving[0]
                                            del self.player_who_resolves_reaction[0]
                                            await secondary_player.send_units_at_planet(origin_planet)
                        elif self.reactions_needing_resolving[0] == "Sicarius's Chosen":
                            print("Resolve Sicarius's chosen")
                            origin_planet = self.positions_of_unit_triggering_reaction[0][1]
                            target_planet = int(game_update_string[2])
                            target_pos = int(game_update_string[3])
                            if int(game_update_string[1]) == int(secondary_player.get_number()):
                                if abs(origin_planet - target_planet) == 1:
                                    if secondary_player.cards_in_play[target_planet + 1][
                                            target_pos].get_card_type() == "Army":
                                        can_continue = True
                                        if secondary_player.get_immune_to_enemy_card_abilities(target_planet,
                                                                                               target_pos):
                                            can_continue = False
                                            await self.game_sockets[0].receive_game_update(
                                                "Immune to enemy card abilities.")
                                        elif secondary_player.communications_relay_check(target_planet,
                                                                                         target_pos) and \
                                                self.communications_relay_enabled:
                                            can_continue = False
                                            await self.game_sockets[0].receive_game_update(
                                                "Communications Relay may be used.")
                                            self.choices_available = ["Yes", "No"]
                                            self.name_player_making_choices = secondary_player.name_player
                                            self.choice_context = "Use Communications Relay?"
                                            self.nullified_card_name = self.action_chosen
                                            self.cost_card_nullified = 0
                                            self.nullify_string = "/".join(game_update_string)
                                            self.first_player_nullified = primary_player.name_player
                                            self.nullify_context = "Reaction"
                                            await self.send_search()
                                        if can_continue:
                                            secondary_player.move_unit_to_planet(target_planet,
                                                                                 int(game_update_string[3]),
                                                                                 origin_planet)
                                            new_unit_pos = len(secondary_player.cards_in_play[origin_planet + 1]) - 1
                                            secondary_player.assign_damage_to_pos(origin_planet, new_unit_pos, 1)
                                            secondary_player.set_aiming_reticle_in_play(origin_planet, new_unit_pos,
                                                                                        "red")
                                            del self.positions_of_unit_triggering_reaction[0]
                                            del self.reactions_needing_resolving[0]
                                            del self.player_who_resolves_reaction[0]
                                            await secondary_player.send_units_at_planet(origin_planet)
                                            await secondary_player.send_units_at_planet(target_planet)

    async def resolve_mobile(self, name, game_update_string):
        if self.player_with_initiative == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if not primary_player.mobile_resolved:
            if name == primary_player.name_player:
                if len(game_update_string) == 1:
                    if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                        primary_player.mobile_resolved = True
                        self.unit_to_move_position = [-1, -1]
                        await self.game_sockets[0].receive_game_update(self.p1.name_player + " finished mobile")

                elif len(game_update_string) == 2:
                    if game_update_string[0] == "PLANETS":
                        planet_pos = int(game_update_string[1])
                        if self.unit_to_move_position[0] != -1 and self.unit_to_move_position[1] != -1:
                            if abs(planet_pos - self.unit_to_move_position[0]) == 1:
                                primary_player.reset_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                            self.unit_to_move_position[1])
                                primary_player.set_available_mobile_given_pos(self.unit_to_move_position[0],
                                                                              self.unit_to_move_position[1], False)
                                primary_player.move_unit_to_planet(self.unit_to_move_position[0],
                                                                   self.unit_to_move_position[1], planet_pos)
                                if not primary_player.search_cards_for_available_mobile():
                                    primary_player.mobile_resolved = True
                                await primary_player.send_units_at_planet(self.unit_to_move_position[0])
                                await primary_player.send_units_at_planet(planet_pos)
                                self.unit_to_move_position = [-1, -1]
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if int(game_update_string[1]) == int(primary_player.number):
                            self.unit_to_move_position[0] = int(game_update_string[2])
                            self.unit_to_move_position[1] = int(game_update_string[3])
                            primary_player.set_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                      self.unit_to_move_position[1], "blue")
                            await primary_player.send_units_at_planet(self.unit_to_move_position[0])
        else:
            if name == secondary_player.name_player:
                if len(game_update_string) == 1:
                    if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                        secondary_player.mobile_resolved = True
                        self.unit_to_move_position = [-1, -1]
                        await self.game_sockets[0].receive_game_update(self.p1.name_player + " finished mobile")
                elif len(game_update_string) == 2:
                    if game_update_string[0] == "PLANETS":
                        planet_pos = int(game_update_string[1])
                        if self.unit_to_move_position[0] != -1 and self.unit_to_move_position[1] != -1:
                            if abs(planet_pos - self.unit_to_move_position[0]) == 1:
                                secondary_player.reset_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                              self.unit_to_move_position[1])
                                secondary_player.set_available_mobile_given_pos(self.unit_to_move_position[0],
                                                                                self.unit_to_move_position[1], False)
                                secondary_player.move_unit_to_planet(self.unit_to_move_position[0],
                                                                     self.unit_to_move_position[1], planet_pos)
                                if not secondary_player.search_cards_for_available_mobile():
                                    secondary_player.mobile_resolved = True
                                await secondary_player.send_units_at_planet(self.unit_to_move_position[0])
                                await secondary_player.send_units_at_planet(planet_pos)
                                self.unit_to_move_position = [-1, -1]
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if int(game_update_string[1]) == int(secondary_player.number):
                            self.unit_to_move_position[0] = int(game_update_string[2])
                            self.unit_to_move_position[1] = int(game_update_string[3])
                            secondary_player.set_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                        self.unit_to_move_position[1], "blue")
                            await secondary_player_player.send_units_at_planet(self.unit_to_move_position[0])
        if primary_player.mobile_resolved and secondary_player.mobile_resolved:
            await self.game_sockets[0].receive_game_update("mobile complete")
            self.check_battle(self.round_number)
            self.last_planet_checked_for_battle = self.round_number
            self.set_battle_initiative()
            self.planet_aiming_reticle_active = True
            self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
            await self.send_planet_array()
            self.p1.has_passed = False
            self.p2.has_passed = False
            await self.send_info_box()

    async def apply_indirect_damage(self, name, game_update_string):
        if name == self.name_1 or name == self.name_2:
            if name == self.name_1:
                player = self.p1
            else:
                player = self.p2
            if player.indirect_damage_applied < player.total_indirect_damage:
                if self.location_of_indirect == "HQ" or self.location_of_indirect == "ALL":
                    if len(game_update_string) == 3:
                        if game_update_string[0] == "HQ":
                            if game_update_string[1] == player.get_number():
                                if player.increase_indirect_damage_at_pos(-2, int(game_update_string[2]), 1):
                                    await player.send_hq()
                if (self.location_of_indirect == "PLANET" and self.planet_of_indirect == int(game_update_string[2])) \
                        or self.location_of_indirect == "ALL":
                    if len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            if game_update_string[1] == player.get_number():
                                if player.increase_indirect_damage_at_pos(int(game_update_string[2]),
                                                                          int(game_update_string[3]), 1):
                                    await player.send_units_at_planet(int(game_update_string[2]))
        if self.p1.indirect_damage_applied >= self.p1.total_indirect_damage and \
                self.p2.indirect_damage_applied >= self.p2.total_indirect_damage:
            await self.resolve_indirect_damage_applied()
            self.p1.total_indirect_damage = 0
            self.p2.total_indirect_damage = 0

    async def resolve_indirect_damage_applied(self):
        self.first_card_damaged = True
        await self.p1.transform_indirect_into_damage()
        await self.p2.transform_indirect_into_damage()
        self.first_card_damaged = True

    async def resolve_effect(self, name, game_update_string):
        if name == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if name == self.player_resolving_effect[0]:
            if self.effects_waiting_on_resolution[0] == "Commander Shadowsun":
                if self.shadowsun_chose_hand:
                    if len(game_update_string) == 1:
                        if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                            primary_player.aiming_reticle_coords_hand = None
                            del self.effects_waiting_on_resolution[0]
                            del self.player_resolving_effect[0]
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                    if len(game_update_string) == 3:
                        if game_update_string[0] == "HAND":
                            if game_update_string[1] == primary_player.get_number():
                                if self.location_hand_attachment_shadowsun == -1:
                                    hand_pos = int(game_update_string[2])
                                    card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array)
                                    if (card.get_card_type() == "Attachment" and card.get_faction() == "Tau" and
                                            card.get_cost() < 3) or card.get_name() == "Shadowsun's Stealth Cadre":
                                        self.location_hand_attachment_shadowsun = hand_pos
                                        primary_player.aiming_reticle_coords_hand = hand_pos
                                        primary_player.aiming_reticle_color = "blue"
                                        await primary_player.send_hand()
                    elif len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if planet_pos == primary_player.warlord_commit_location:
                                if game_update_string[1] == primary_player.number:
                                    player_receiving_attachment = primary_player
                                    own_attachment = True
                                else:
                                    player_receiving_attachment = secondary_player
                                    own_attachment = False
                                card = FindCard.find_card(primary_player.cards[self.location_hand_attachment_shadowsun],
                                                          self.card_array)
                                army_unit_as_attachment = False
                                if card.get_name() == "Shadowsun's Stealth Cadre":
                                    army_unit_as_attachment = True
                                if player_receiving_attachment.play_attachment_card_to_in_play(
                                        card, planet_pos, unit_pos, discounts=card.get_cost(),
                                        not_own_attachment=own_attachment,
                                        army_unit_as_attachment=army_unit_as_attachment):
                                    primary_player.remove_card_from_hand(self.location_hand_attachment_shadowsun)
                                    primary_player.aiming_reticle_coords_hand = None
                                    self.shadowsun_chose_hand = False
                                    self.location_hand_attachment_shadowsun = -1
                                    self.resolving_search_box = False
                                    del self.effects_waiting_on_resolution[0]
                                    del self.player_resolving_effect[0]
                                    await player_receiving_attachment.send_units_at_planet(planet_pos)
                                    await primary_player.send_hand()
                                else:
                                    await self.game_sockets[0].receive_game_update("Invalid target")
                else:
                    if len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if planet_pos == primary_player.warlord_commit_location:
                                if game_update_string[1] == primary_player.number:
                                    player_receiving_attachment = primary_player
                                    own_attachment = True
                                else:
                                    player_receiving_attachment = secondary_player
                                    own_attachment = False
                                card = FindCard.find_card(self.name_attachment_discard_shadowsun, self.card_array)
                                army_unit_as_attachment = False
                                if card.get_name() == "Shadowsun's Stealth Cadre":
                                    army_unit_as_attachment = True
                                if player_receiving_attachment.play_attachment_card_to_in_play(
                                        card, planet_pos, unit_pos, discounts=card.get_cost(),
                                        not_own_attachment=own_attachment,
                                        army_unit_as_attachment=army_unit_as_attachment):
                                    i = 0
                                    removed_card = False
                                    while i < len(primary_player.discard) and not removed_card:
                                        if primary_player.discard[i] == self.name_attachment_discard_shadowsun:
                                            removed_card = True
                                            del primary_player.discard[i]
                                    self.name_attachment_discard_shadowsun = ""
                                    self.resolving_search_box = False
                                    del self.effects_waiting_on_resolution[0]
                                    del self.player_resolving_effect[0]
                                    await primary_player.send_discard()
                                    await player_receiving_attachment.send_units_at_planet(planet_pos)
                                else:
                                    await self.game_sockets[0].receive_game_update("Invalid target")
            elif self.effects_waiting_on_resolution[0] == "Glorious Intervention":
                if len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if game_update_string[1] == primary_player.get_number():
                            pos_holder = self.positions_of_units_to_take_damage[0]
                            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
                            sac_planet_pos = int(game_update_string[2])
                            sac_unit_pos = int(game_update_string[3])
                            if sac_planet_pos == planet_pos:
                                if sac_unit_pos != unit_pos:
                                    if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos].\
                                            get_card_type() != "Warlord":
                                        if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos]\
                                                .check_for_a_trait("Warrior") or \
                                                primary_player.cards_in_play[sac_planet_pos + 1][unit_pos]\
                                                .check_for_a_trait("Soldier"):
                                            primary_player.aiming_reticle_coords_hand = None
                                            primary_player.discard_card_from_hand(self.pos_shield_card)
                                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                            self.pos_shield_card = -1
                                            printed_atk = primary_player.cards_in_play[
                                                sac_planet_pos + 1][sac_unit_pos].attack
                                            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                                            if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                                    self.damage_on_units_list_before_new_damage[0]:
                                                primary_player.set_damage_given_pos(
                                                    planet_pos, unit_pos,
                                                    self.damage_on_units_list_before_new_damage[0])
                                            primary_player.sacrifice_card_in_play(sac_planet_pos, sac_unit_pos)
                                            att_num, att_pla, att_pos = \
                                                self.positions_attackers_of_units_to_take_damage[0]
                                            secondary_player.assign_damage_to_pos(att_pla, att_pos, printed_atk)
                                            del self.effects_waiting_on_resolution[0]
                                            del self.player_resolving_effect[0]
                                            await self.shield_cleanup(primary_player, secondary_player, planet_pos)
            elif self.effects_waiting_on_resolution[0] == "No Mercy":
                if len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        if game_update_string[1] == primary_player.number:
                            hq_pos = int(game_update_string[2])
                            if primary_player.headquarters[hq_pos].get_is_unit() and \
                                    primary_player.headquarters[hq_pos].get_unique() and \
                                    primary_player.headquarters[hq_pos].get_ready():
                                primary_player.exhaust_given_pos(-2, hq_pos)
                                await primary_player.send_hq()
                                primary_player.discard_card_name_from_hand("No Mercy")
                                del self.effects_waiting_on_resolution[0]
                                del self.player_resolving_effect[0]
                                await primary_player.send_hand()
                                await primary_player.send_discard()
                                await self.better_shield_card_resolution(secondary_player.name_player, ["pass-P1"],
                                                                         alt_shields=False, can_no_mercy=False)
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if game_update_string[1] == primary_player.number:
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_is_unit() and \
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_unique() and \
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].get_ready():
                                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                await primary_player.send_units_at_planet(planet_pos)
                                primary_player.discard_card_name_from_hand("No Mercy")
                                del self.effects_waiting_on_resolution[0]
                                del self.player_resolving_effect[0]
                                await primary_player.send_hand()
                                await primary_player.send_discard()
                                await self.better_shield_card_resolution(secondary_player.name_player, ["pass-P1"],
                                                                         alt_shields=False, can_no_mercy=False)

    def fury_search(self, player_with_cato, player_without_cato):
        if player_with_cato.search_hand_for_card("The Fury of Sicarius"):
            print("Has fury")
            if player_with_cato.resources > 1:
                print("Has resources")
                if player_without_cato.get_card_type_given_pos(
                        self.recently_damaged_units[0][1],
                        self.recently_damaged_units[0][2]) != "Warlord":
                    print("Not warlord")
                    self.choice_context = "Use The Fury of Sicarius?"
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = player_with_cato.name_player
                    self.furiable_unit_position = (self.recently_damaged_units[0][1],
                                                   self.recently_damaged_units[0][2])
                    return True
        return False

    async def shield_cleanup(self, primary_player, secondary_player, planet_pos):
        del self.positions_of_units_to_take_damage[0]
        del self.damage_on_units_list_before_new_damage[0]
        del self.positions_attackers_of_units_to_take_damage[0]
        del self.damage_can_be_shielded[0]
        if self.positions_of_units_to_take_damage:
            self.advance_damage_aiming_reticle()
        else:
            if self.damage_from_attack:
                self.clear_attacker_aiming_reticle()
            fury_of_cato_check = False
            print("\n---FURY CHECK---\n")
            print(self.recently_damaged_units)
            print(self.damage_taken_was_from_attack)
            print(self.faction_of_attacker)
            for i in range(len(self.recently_damaged_units)):
                if self.damage_taken_was_from_attack[i]:
                    print("Damage was from attack")
                    if self.faction_of_attacker[i] == "Space Marines":
                        print("Attacker was a space marines unit")
                        if self.recently_damaged_units[0][0] == 1:
                            player_with_cato = self.p2
                            player_without_cato = self.p1
                        else:
                            player_with_cato = self.p1
                            player_without_cato = self.p2
                        if self.fury_search(player_with_cato, player_without_cato):
                            fury_of_cato_check = True
                            await self.send_search()
            if not fury_of_cato_check:
                await self.destroy_check_all_cards()
                if self.reactions_needing_resolving:
                    i = 0
                    while i < len(self.reactions_needing_resolving):
                        if self.reactions_needing_resolving[i] == "Mark of Chaos":
                            loc_of_mark = self.positions_of_unit_triggering_reaction[i][1]
                            secondary_player.suffer_area_effect(loc_of_mark, 1)
                            self.number_of_units_left_to_suffer_damage = \
                                secondary_player.get_number_of_units_at_planet(loc_of_mark)
                            if self.number_of_units_left_to_suffer_damage > 0:
                                secondary_player.set_aiming_reticle_in_play(loc_of_mark, 0, "red")
                                for j in range(1, self.number_of_units_left_to_suffer_damage):
                                    secondary_player.set_aiming_reticle_in_play(loc_of_mark, j, "blue")
                            del self.positions_of_unit_triggering_reaction[i]
                            del self.reactions_needing_resolving[i]
                            del self.player_who_resolves_reaction[i]
                            i = i - 1
                        i = i + 1
        await primary_player.send_units_at_planet(planet_pos)
        await secondary_player.send_units_at_planet(planet_pos)
        await primary_player.send_hand()
        await primary_player.send_discard()

    async def update_game_event(self, name, game_update_string, same_thread=False):
        if not same_thread:
            self.condition_main_game.acquire()
        resolved_subroutine = False
        print(game_update_string)
        if self.phase == "SETUP":
            await self.game_sockets[0].receive_game_update("Buttons can't be pressed in setup")
        if self.validate_received_game_string(game_update_string):
            print("String validated as ok")
            if self.cards_in_search_box:
                await self.resolve_card_in_search_box(name, game_update_string)
                if not self.cards_in_search_box:
                    await self.send_search()
            if self.effects_waiting_on_resolution:
                await self.resolve_effect(name, game_update_string)
            elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
                await self.apply_indirect_damage(name, game_update_string)
            elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
                await self.update_game_event_action_applying_discounts(name, game_update_string)
            elif self.choices_available:
                print("Need to resolve a choice")
                await self.resolve_choice(name, game_update_string)
            elif self.reactions_needing_resolving:
                print("Resolve reaction")
                print(self.reactions_needing_resolving[0])
                await self.resolve_reaction(name, game_update_string)
            elif self.positions_of_units_to_take_damage:
                print("Using better shield mechanism")
                await self.better_shield_card_resolution(name, game_update_string)
            elif not self.p1.mobile_resolved or not self.p2.mobile_resolved:
                print("Resolve mobile")
                await self.resolve_mobile(name, game_update_string)
            elif self.battle_ability_to_resolve:
                await self.resolve_battle_ability_routine(name, game_update_string)
            elif self.phase == "DEPLOY":
                await DeployPhase.update_game_event_deploy_section(self, name, game_update_string)
            elif self.phase == "COMMAND":
                await CommandPhase.update_game_event_command_section(self, name, game_update_string)
            elif self.phase == "COMBAT":
                await CombatPhase.update_game_event_combat_section(self, name, game_update_string)
            resolved_subroutine = True
        if self.cards_in_search_box:
            await self.send_search()
        if self.positions_of_units_to_take_damage:
            print("Entering better shield mode")
            pos_holder = self.positions_of_units_to_take_damage[0]
            player_num = pos_holder[0]
            if player_num == 1:
                self.player_who_is_shielding = self.name_1
                self.number_who_is_shielding = "1"
                self.p1.set_aiming_reticle_in_play(pos_holder[1], pos_holder[2], "red")
            elif player_num == 2:
                self.player_who_is_shielding = self.name_2
                self.number_who_is_shielding = "2"
                self.p2.set_aiming_reticle_in_play(pos_holder[1], pos_holder[2], "red")
        if self.reactions_needing_resolving:
            if not self.resolving_search_box:
                if self.reactions_needing_resolving[0] == "Enginseer Augur":
                    self.resolving_search_box = True
                    self.what_to_do_with_searched_card = "PLAY TO HQ"
                    self.traits_of_searched_card = None
                    self.card_type_of_searched_card = "Support"
                    self.faction_of_searched_card = "Astra Militarum"
                    self.max_cost_of_searched_card = 2
                    self.all_conditions_searched_card_required = True
                    self.no_restrictions_on_chosen_card = False
                    if self.player_who_resolves_reaction[0] == self.name_1:
                        self.p1.number_cards_to_search = 6
                        if len(self.p1.deck) > 5:
                            self.cards_in_search_box = self.p1.deck[0:self.p1.number_cards_to_search]
                        else:
                            self.cards_in_search_box = self.p1.deck[0:len(self.p1.deck)]
                        self.name_player_who_is_searching = self.p1.name_player
                        self.number_who_is_searching = str(self.p1.number)
                    else:
                        self.p2.number_cards_to_search = 6
                        if len(self.p2.deck) > 5:
                            self.cards_in_search_box = self.p2.deck[0:self.p2.number_cards_to_search]
                        else:
                            self.cards_in_search_box = self.p2.deck[0:len(self.p2.deck)]
                        self.name_player_who_is_searching = self.p2.name_player
                        self.number_who_is_searching = str(self.p2.number)
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                    await self.send_info_box()
                elif self.reactions_needing_resolving[0] == "Swordwind Farseer":
                    if self.player_who_resolves_reaction[0] == self.name_1:
                        self.p1.number_cards_to_search = 6
                        if len(self.p1.deck) > 5:
                            self.cards_in_search_box = self.p1.deck[0:self.p1.number_cards_to_search]
                        else:
                            self.cards_in_search_box = self.p1.deck[0:len(self.p1.deck)]
                    else:
                        self.p2.number_cards_to_search = 6
                        if len(self.p2.deck) > 5:
                            self.cards_in_search_box = self.p2.deck[0:self.p2.number_cards_to_search]
                        else:
                            self.cards_in_search_box = self.p2.deck[0:len(self.p2.deck)]
                    self.resolving_search_box = True
                    self.name_player_who_is_searching = self.name_player
                    self.number_who_is_searching = str(self.number)
                    self.what_to_do_with_searched_card = "DRAW"
                    self.traits_of_searched_card = None
                    self.card_type_of_searched_card = None
                    self.faction_of_searched_card = None
                    self.no_restrictions_on_chosen_card = True
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                elif self.reactions_needing_resolving[0] == "Earth Caste Technician":
                    if self.player_who_resolves_reaction[0] == self.name_1:
                        self.p1.number_cards_to_search = 6
                        if len(self.p1.deck) > 5:
                            self.cards_in_search_box = self.p1.deck[0:self.p1.number_cards_to_search]
                        else:
                            self.cards_in_search_box = self.p1.deck[0:len(self.p1.deck)]
                    else:
                        self.p2.number_cards_to_search = 6
                        if len(self.p2.deck) > 5:
                            self.cards_in_search_box = self.p2.deck[0:self.p2.number_cards_to_search]
                        else:
                            self.cards_in_search_box = self.p2.deck[0:len(self.p2.deck)]
                    self.resolving_search_box = True
                    self.name_player_who_is_searching = self.name_player
                    self.number_who_is_searching = str(self.number)
                    self.what_to_do_with_searched_card = "DRAW"
                    self.traits_of_searched_card = "Drone"
                    self.card_type_of_searched_card = "Attachment"
                    self.faction_of_searched_card = None
                    self.no_restrictions_on_chosen_card = False
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                elif self.reactions_needing_resolving[0] == "Shrine of Warpflame":
                    self.resolving_search_box = True
                    self.choices_available = ["Yes", "No"]
                    self.choice_context = "Use Shrine of Warpflame?"
                    self.name_player_making_choices = self.player_who_resolves_reaction[0]
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                    await self.send_info_box()
                elif self.reactions_needing_resolving[0] == "Fall Back!":
                    self.resolving_search_box = True
                    self.choices_available = ["Yes", "No"]
                    self.choice_context = "Use Fall Back?"
                    self.name_player_making_choices = self.player_who_resolves_reaction[0]
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                    await self.send_info_box()
                elif self.reactions_needing_resolving[0] == "Holy Sepulchre":
                    self.resolving_search_box = True
                    self.choices_available = ["Yes", "No"]
                    self.choice_context = "Use Holy Sepulchre?"
                    self.name_player_making_choices = self.player_who_resolves_reaction[0]
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                    await self.send_info_box()
                elif self.reactions_needing_resolving[0] == "Commander Shadowsun":
                    await self.game_sockets[0].receive_game_update("Resolve shadowsun")
                    self.resolving_search_box = True
                    self.choices_available = ["Hand", "Discard"]
                    self.choice_context = "Shadowsun plays attachment from hand or discard?"
                    self.name_player_making_choices = self.player_who_resolves_reaction[0]
                    self.misc_target_planet = self.positions_of_unit_triggering_reaction[0][1]
                    del self.reactions_needing_resolving[0]
                    del self.positions_of_unit_triggering_reaction[0]
                    del self.player_who_resolves_reaction[0]
                    await self.send_search()
                    await self.send_info_box()
                i = 0
                while i < len(self.reactions_needing_resolving):
                    if self.reactions_needing_resolving[i] == "Mark of Chaos":
                        if self.positions_of_unit_triggering_reaction[i][0] == 1:
                            secondary_player = self.p2
                        else:
                            secondary_player = self.p1
                        loc_of_mark = self.positions_of_unit_triggering_reaction[i][1]
                        secondary_player.suffer_area_effect(loc_of_mark, 1)
                        self.number_of_units_left_to_suffer_damage = \
                            secondary_player.get_number_of_units_at_planet(loc_of_mark)
                        if self.number_of_units_left_to_suffer_damage > 0:
                            secondary_player.set_aiming_reticle_in_play(loc_of_mark, 0, "red")
                            for j in range(1, self.number_of_units_left_to_suffer_damage):
                                secondary_player.set_aiming_reticle_in_play(loc_of_mark, j, "blue")
                        del self.positions_of_unit_triggering_reaction[i]
                        del self.reactions_needing_resolving[i]
                        del self.player_who_resolves_reaction[i]
                        await secondary_player.send_units_at_planet(loc_of_mark)
                        i = i - 1
                    i = i + 1
        if resolved_subroutine:
            await self.send_info_box()
        print("---\nDEBUG INFO\n---")
        print(self.reactions_needing_resolving)
        print(self.choices_available)
        if not same_thread:
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

    def request_search_for_enemy_card_at_planet(self, number, planet, name_of_card, bloodied_relevant=False,
                                                ready_relevant=False):
        if number == "1":
            if planet == -2:
                is_present = self.p2.search_card_in_hq(name_of_card, bloodied_relevant=bloodied_relevant,
                                                       ready_relevant=ready_relevant)
                return is_present
            is_present = self.p2.search_card_at_planet(planet, name_of_card, bloodied_relevant=bloodied_relevant)
            return is_present
        elif number == "2":
            if planet == -2:
                is_present = self.p1.search_card_in_hq(name_of_card, bloodied_relevant=bloodied_relevant,
                                                       ready_relevant=ready_relevant)
                return is_present
            is_present = self.p1.search_card_at_planet(planet, name_of_card, bloodied_relevant=bloodied_relevant)
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
                winner.move_all_at_planet_to_hq(self.last_planet_checked_for_battle)
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
