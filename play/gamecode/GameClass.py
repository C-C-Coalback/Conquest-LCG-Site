import copy
from . import PlayerClass
import random
from .Phases import DeployPhase, CommandPhase, CombatPhase, HeadquartersPhase
from . import FindCard
import threading
from .Actions import AttachmentHQActions, AttachmentInPlayActions, HandActions, HQActions, \
    InPlayActions, PlanetActions, DiscardActions
from .Reactions import StartReaction, PlanetsReaction, HandReaction, HQReaction, InPlayReaction


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
        self.phase = "SETUP"
        self.round_number = 0
        self.current_board_state = ""
        self.running = True
        self.planet_array = []
        for i in range(10):
            self.planet_array.append(self.planet_cards_array[i].get_name())
        random.shuffle(self.planet_array)
        self.planet_array = self.planet_array[:7]
        self.planets_in_play_array = [True, True, True, True, True, False, False]
        self.bloodthirst_active = [False, False, False, False, False, False, False]
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
        self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
        self.faction_of_cards_for_indirect = ""
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
        self.positions_of_attacker_of_unit_that_took_damage = []
        self.faction_of_attacker = []
        self.on_kill_effects_of_attacker = []
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
        self.backlash_enabled = True
        self.bigga_is_betta_active = False
        self.last_info_box_string = ""
        self.has_chosen_to_resolve = False
        self.asking_if_reaction = False
        self.already_resolving_reaction = False
        self.last_search_string = ""
        self.asking_which_reaction = True
        self.stored_reaction_indexes = []
        self.manual_bodyguard_resolution = False
        self.name_player_manual_bodyguard = ""
        self.num_bodyguards = 0
        self.body_guard_positions = []
        self.damage_bodyguard = 0
        self.planet_bodyguard = -1
        self.last_player_who_resolved_reaction = ""
        self.infested_planets = [False, False, False, False, False, False, False]
        self.asking_if_remove_infested_planet = False
        self.already_asked_remove_infestation = False
        self.great_scything_talons_value = 0
        self.name_of_card_to_play = ""
        self.damage_moved_to_old_one_eye = 0
        self.old_one_eye_pos = (-1, -1)
        self.misc_target_choice = -1
        self.resolve_destruction_checks_after_reactions = False
        self.ravenous_haruspex_gain = 0
        self.reset_resolving_attack_on_units = False
        self.resolving_consumption = False
        self.stored_area_effect_value = 0
        self.valid_targets_for_dark_possession = [
            "Drop Pod Assault", "Exterminatus", "Preemptive Barrage", "Suppressive Fire",
            "Battle Cry", "Snotling Attack", "Squig Bombin'", "Infernal Gateway",
            "Warpstorm", "Tzeentch's Firestorm", "Promise of Glory", "Pact of the Haemonculi",
            "Power from Pain", "Archon's Terror", "Raid", "Doom", "Gift of Isha",
            "Squadron Redeployment", "Even the Odds", "Calculated Strike",
            "Deception", "Ferocious Strength", "Indescribable Horror", "Clogged with Corpses",
            "Predation", "Spawn Termagants", "Spore Burst", "Dark Cunning", "Consumption",
            "Subdual", "Ecstatic Seizures", "Dark Possession", "Subdual", "Muster the Guard",
            "Noble Deed", "Smash 'n Bash", "Visions of Agony", "Empower", "Calamity",
            "Awake the Sleepers", "Reanimation Protocol", "Recycle", "Mechanical Enhancement",
            "Drudgery", "Extermination", "Fetid Haze", "Dakka Dakka Dakka!", "Soul Seizure",
            "Death from Above", "Kauyon Strike"
        ]
        self.anrakyr_unit_position = -1
        self.anrakyr_deck_choice = self.name_1
        self.name_of_attacked_unit = ""
        self.need_to_reset_tomb_blade_squadron = False
        self.resolve_kill_effects = True
        self.asked_if_resolve_effect = False
        self.card_to_deploy = None
        self.saved_planet_string = ""
        self.dies_to_backlash = ["Sicarius's Chosen", "Captain Markis", "Burna Boyz", "Tomb Blade Squadron",
                                 "Veteran Barbrus", "Klaivex Warleader", "Rotten Plaguebearers"]
        self.nullifying_backlash = ""
        self.choosing_unit_for_nullify = False
        self.name_player_using_nullify = ""
        self.name_player_using_backlash = ""
        self.canceled_card_bonuses = [False, False, False, False, False, False, False]
        self.canceled_resource_bonuses = [False, False, False, False, False, False, False]
        self.units_move_hq_attack = ["Aun'ui Prelate", "Aun'shi", "Ethereal Envoy"]
        self.unit_will_move_after_attack = False
        self.need_to_move_to_hq = False
        self.just_moved_units = False
        self.resolving_kugath_nurglings = False
        self.kugath_nurglings_present_at_planets = [0, 0, 0, 0, 0, 0, 0]
        self.auto_card_destruction = True

    async def send_update_message(self, message):
        if self.game_sockets:
            await self.game_sockets[0].receive_game_update(message)

    def reset_action_data(self):
        self.mode = "Normal"
        self.action_chosen = ""
        self.player_with_action = ""
        self.position_of_actioned_card = (-1, -1)

    def reset_damage_data(self):
        self.damage_on_units_list_before_new_damage = []
        self.positions_of_units_to_take_damage = []
        self.positions_attackers_of_units_to_take_damage = []
        self.amount_that_can_be_removed_by_shield = []
        self.damage_can_be_shielded = []
        self.damage_taken_was_from_attack = []
        self.damage_from_atrox = False
        self.units_damaged_by_attack = []
        self.units_damaged_by_attack_from_sm = []
        if self.stored_mode:
            self.mode = self.stored_mode
        self.furiable_unit_position = (-1, -1)
        self.auto_card_destruction = True

    def reset_effects_data(self):
        self.effects_waiting_on_resolution = []
        self.player_resolving_effect = []
        self.active_effects = []

    def reset_reactions_data(self):
        self.reactions_needing_resolving = []
        self.player_who_resolves_reaction = []
        self.positions_of_unit_triggering_reaction = []
        self.already_resolving_reaction = False

    def get_actions_allowed(self):
        if self.manual_bodyguard_resolution:
            return False
        elif self.resolving_kugath_nurglings:
            return False
        elif self.mode != "Normal":
            return False
        elif self.reactions_needing_resolving:
            return False
        elif self.effects_waiting_on_resolution:
            return False
        elif self.positions_of_units_to_take_damage:
            return False
        elif self.cards_in_search_box:
            return False
        elif self.choices_available:
            return False
        elif self.attacker_position != -1:
            return False
        return True

    async def joined_requests_graphics(self, name):
        self.condition_main_game.acquire()
        await self.p1.send_hand(force=True)
        await self.p2.send_hand(force=True)
        await self.p1.send_hq(force=True)
        await self.p2.send_hq(force=True)
        await self.p1.send_units_at_all_planets(force=True)
        await self.p2.send_units_at_all_planets(force=True)
        await self.p1.send_resources(force=True)
        await self.p2.send_resources(force=True)
        await self.p1.send_discard(force=True)
        await self.p2.send_discard(force=True)
        await self.send_info_box(force=True)
        await self.send_search(force=True)
        await self.p1.send_victory_display()
        await self.p2.send_victory_display()
        await self.send_planet_array(force=True)
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def send_search(self, force=False):
        card_string = ""
        if self.cards_in_search_box and self.name_player_who_is_searching:
            card_string = "/".join(self.cards_in_search_box)
            card_string = "GAME_INFO/SEARCH/" + self.name_player_who_is_searching + "/" \
                          + self.what_to_do_with_searched_card + "/" + card_string
        elif self.choices_available and self.name_player_making_choices:
            card_string = "/".join(self.choices_available)
            card_string = "GAME_INFO/CHOICE/" + self.name_player_making_choices + "/" \
                          + self.choice_context + "/" + card_string
        else:
            card_string = "GAME_INFO/SEARCH//Nothing here"
        if card_string != self.last_search_string or force:
            self.last_search_string = card_string
            await self.send_update_message(card_string)

    async def send_info_box(self, force=False):
        info_string = "GAME_INFO/INFO_BOX/"
        if self.phase == "SETUP":
            info_string += "Unspecified/"
        elif self.resolving_consumption:
            info_string += "Unspecified/"
        elif self.manual_bodyguard_resolution:
            info_string += self.name_player_manual_bodyguard
        elif self.cards_in_search_box:
            info_string += self.name_player_who_is_searching + "/"
        elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
            info_string += "Unspecified/"
        elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
            info_string += self.player_with_action + "/"
        elif self.choices_available:
            info_string += self.name_player_making_choices + "/"
        elif self.effects_waiting_on_resolution:
            info_string += self.player_resolving_effect[0] + "/"
        elif self.positions_of_units_to_take_damage:
            if self.positions_of_units_to_take_damage[0][0] == 1:
                info_string += self.name_1 + "/"
            else:
                info_string += self.name_2 + "/"
        elif self.resolving_kugath_nurglings:
            if self.p1.has_initiative:
                info_string += self.name_1 + "/"
            else:
                info_string += self.name_2 + "/"
        elif self.reactions_needing_resolving:
            info_string += self.player_who_resolves_reaction[0] + "/"
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
        elif self.resolving_consumption:
            info_string += "P1:"
            for i in range(len(self.p1.consumption_sacs_list)):
                if self.p1.consumption_sacs_list[i]:
                    info_string += "True,"
                else:
                    info_string += "False,"
            info_string += "/P2:"
            for i in range(len(self.p2.consumption_sacs_list)):
                if self.p2.consumption_sacs_list[i]:
                    info_string += "True,"
                else:
                    info_string += "False,"
        elif self.manual_bodyguard_resolution:
            info_string += "Manual bodyguard resolution: " + self.name_player_manual_bodyguard + "/"
        elif self.cards_in_search_box:
            info_string += "Searching: " + self.what_to_do_with_searched_card + "/"
            info_string += "User: " + self.name_player_who_is_searching + "/"
        elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
            info_string += "Indirect damage " + str(self.p1.total_indirect_damage) + \
                           str(self.p2.total_indirect_damage) + "/"
        elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
            info_string += "Ambush discounts/God help you/"
            info_string += self.player_with_action + "/"
        elif self.choices_available:
            info_string += "Choice: " + self.choice_context + "/"
            info_string += "User: " + self.name_player_making_choices + "/"
        elif self.effects_waiting_on_resolution:
            info_string += "Effect: " + self.effects_waiting_on_resolution[0] + "/"
            info_string += "User: " + self.player_resolving_effect[0] + "/"
        elif self.positions_of_units_to_take_damage:
            if self.positions_of_units_to_take_damage[0][0] == 1:
                info_string += "Shield: " + self.name_1 + "/"
            else:
                info_string += "Shield: " + self.name_2 + "/"
        elif self.resolving_kugath_nurglings:
            info_string += "Ku'gath Nurglings resolution/"
        elif self.reactions_needing_resolving:
            info_string += "Reaction: " + self.reactions_needing_resolving[0] + "/"
            info_string += "User: " + self.player_who_resolves_reaction[0] + "/"
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
        elif self.phase == "HEADQUARTERS":
            info_string += "HQ action & reaction window/"
        else:
            info_string += "??????/"
        if self.last_info_box_string != info_string or force:
            await self.send_update_message(info_string)
            self.last_info_box_string = info_string

    async def send_planet_array(self, force=False):
        planet_string = "GAME_INFO/PLANETS/"
        for i in range(len(self.planet_array)):
            if self.planets_in_play_array[i]:
                planet_string += self.planet_array[i]
            else:
                planet_string += "CardbackRotated"
            if self.infested_planets[i]:
                planet_string += "|I"
            else:
                planet_string += "|N"
            if self.planet_aiming_reticle_position == i:
                planet_string += "|red|"
            else:
                planet_string += "||"
            for j in range(len(self.p1.attachments_at_planet[i])):
                planet_string += self.p1.attachments_at_planet[i][j].get_name()
                planet_string += ">"
                if self.p1.attachments_at_planet[i][j].get_ready():
                    planet_string += "R"
                else:
                    planet_string += "E"
                if j != len(self.p1.attachments_at_planet[i]) - 1:
                    planet_string += "_"
            planet_string += "|"
            for j in range(len(self.p2.attachments_at_planet[i])):
                planet_string += self.p2.attachments_at_planet[i][j].get_name()
                planet_string += ">"
                if self.p2.attachments_at_planet[i][j].get_ready():
                    planet_string += "R"
                else:
                    planet_string += "E"
                if j != len(self.p2.attachments_at_planet[i]) - 1:
                    planet_string += "_"
            if i != 6:
                planet_string += "/"
        if planet_string != self.saved_planet_string or force:
            self.saved_planet_string = planet_string
            await self.send_update_message(planet_string)

    async def update_game_event_applying_discounts(self, name, game_update_string):
        if self.card_to_deploy is not None:
            if self.player_with_action == self.name_1:
                player = self.p1
                secondary_player = self.p2
            else:
                player = self.p2
                secondary_player = self.p1
            if self.phase == "DEPLOY":
                if self.number_with_deploy_turn == "1":
                    player = self.p1
                    secondary_player = self.p2
                else:
                    player = self.p2
                    secondary_player = self.p1
            if name == player.name_player:
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
                        if game_update_string[1] == player.get_number():
                            discount_received = player.perform_discount_at_pos_hq(int(game_update_string[2]),
                                                                                  self.card_to_deploy.get_faction(),
                                                                                  self.card_to_deploy.get_traits(),
                                                                                  self.planet_aiming_reticle_position)
                            if discount_received > 0:
                                self.discounts_applied += discount_received
                            if self.discounts_applied >= self.available_discounts:
                                await DeployPhase.deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                                      discounts=self.discounts_applied)
                                self.mode = "Normal"
                    elif game_update_string[0] == "HAND":
                        if self.card_to_deploy.get_card_type() == "Army":
                            discount_received, damage = player.perform_discount_at_pos_hand(
                                int(game_update_string[2]),
                                self.card_to_deploy.get_faction()
                            )
                            if discount_received > 0:
                                if secondary_player.nullify_check() and self.nullify_enabled:
                                    await self.send_update_message(
                                        player.name_player + " wants to play Bigga Is Betta; "
                                                             "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = int(game_update_string[2])
                                    self.nullified_card_name = "Bigga Is Betta"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = player.name_player
                                    self.nullify_context = "Bigga Is Betta"
                                else:
                                    self.discounts_applied += discount_received
                                    player.discard_card_from_hand(int(game_update_string[2]))
                                    if self.card_pos_to_deploy > int(game_update_string[2]):
                                        self.card_pos_to_deploy -= 1
                                    if damage > 0:
                                        self.damage_for_unit_to_take_on_play.append(damage)
                                    if self.discounts_applied >= self.available_discounts:
                                        await DeployPhase.deploy_card_routine(self, name,
                                                                              self.planet_aiming_reticle_position,
                                                                              discounts=self.discounts_applied)
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if self.card_to_deploy.get_card_type() == "Army":
                            discount_received = player.perform_discount_at_pos_in_play(int(game_update_string[2]),
                                                                                       int(game_update_string[3]),
                                                                                       self.card_to_deploy.get_traits())
                            if discount_received > 0:
                                self.discounts_applied += discount_received
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

    async def update_game_event_action(self, name, game_update_string):
        if name == self.player_with_action:
            if name == self.name_1:
                if self.p1.force_due_to_dark_possession:
                    game_update_string = ["HAND", "1", str(self.p1.pos_card_dark_possession)]
            elif name == self.name_2:
                if self.p2.force_due_to_dark_possession:
                    game_update_string = ["HAND", "2", str(self.p2.pos_card_dark_possession)]
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.action_chosen == "":
                        self.mode = self.stored_mode
                        self.player_with_action = ""
                        print("Canceled special action")
                        await self.send_update_message(name + " canceled their action request")
                    elif self.action_chosen == "Smash 'n Bash":
                        print("Try to stop smash n bash")
                        if self.chosen_first_card:
                            await self.send_update_message("Stopping Smash 'n Bash early")
                            self.action_cleanup()
                    else:
                        await self.send_update_message("Too far in; action must be concluded now")
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
                elif game_update_string[0] == "IN_DISCARD":
                    await DiscardActions.update_game_event_action_discard(self, name, game_update_string)
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
        if self.p1.force_due_to_dark_possession:
            self.p1.dark_possession_remove_after_play = True
        if self.p2.force_due_to_dark_possession:
            self.p2.dark_possession_remove_after_play = True
        if not self.action_chosen and self.p1.dark_possession_remove_after_play:
            if self.p1.discard:
                del self.p1.discard[-1]
            self.p1.dark_possession_remove_after_play = False
        if not self.action_chosen and self.p2.dark_possession_remove_after_play:
            if self.p2.discard:
                del self.p2.discard[-1]
            self.p2.dark_possession_remove_after_play = False
        self.p1.force_due_to_dark_possession = False
        self.p2.force_due_to_dark_possession = False

    def determine_last_planet(self):
        last = -1
        for i in range(len(self.planets_in_play_array)):
            if self.planets_in_play_array[i]:
                last = i
        return last

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
            elif game_update_string[0] == "IN_DISCARD":
                if game_update_string[1] == "1":
                    if len(self.p1.discard) > int(game_update_string[2]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.discard) > int(game_update_string[2]):
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
                elif game_update_string[1] == "PLANETS":
                    player_num = int(game_update_string[2])
                    pos_planet = int(game_update_string[3])
                    pos_attachment = int(game_update_string[4])
                    if player_num == 1:
                        if -1 < pos_planet < 7:
                            if len(self.p1.attachments_at_planet[pos_planet]) > pos_attachment:
                                return True
                    elif player_num == 2:
                        if -1 < pos_planet < 7:
                            if len(self.p2.attachments_at_planet[pos_planet]) > pos_attachment:
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

    async def start_mulligan(self):
        self.choices_available = ["Yes", "No"]
        self.choice_context = "Mulligan Opening Hand?"
        self.name_player_making_choices = self.name_1

    def reset_search_values(self):
        self.searching_enemy_deck = False
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
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    if self.number_who_is_searching == game_update_string[1]:
                        if self.number_who_is_searching == "1":
                            player = self.p1
                        else:
                            player = self.p2
                        if player.get_ability_given_pos(-2, int(game_update_string[2])) == "Dome of Crystal Seers":
                            if player.get_ready_given_pos(-2, int(game_update_string[2])):
                                if not self.searching_enemy_deck:
                                    player.exhaust_given_pos(-2, int(game_update_string[2]))
                                    player.number_cards_to_search += 3
                                    if len(player.deck) >= player.number_cards_to_search:
                                        self.cards_in_search_box = player.deck[0:player.number_cards_to_search]
                                    else:
                                        self.cards_in_search_box = player.deck[0:player.deck]
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
                            elif self.what_to_do_with_searched_card == "PLAY TO HQ" and card_chosen is not None:
                                self.p1.add_to_hq(card_chosen)
                                del self.p1.deck[int(game_update_string[1])]
                                if self.resolving_search_box:
                                    self.resolving_search_box = False
                            elif self.what_to_do_with_searched_card == "PLAY TO BATTLE" and card_chosen is not None:
                                self.p1.play_card_to_battle_at_location_deck(self.last_planet_checked_for_battle,
                                                                             int(game_update_string[1]), card_chosen)
                                if self.action_chosen == "Drop Pod Assault":
                                    self.p1.discard_card_from_hand(self.p1.aiming_reticle_coords_hand)
                                    self.p1.aiming_reticle_coords_hand = None
                                    self.mode = "Normal"
                                    self.player_with_action = ""
                                    self.action_chosen = ""
                            elif self.what_to_do_with_searched_card == "DISCARD":
                                if self.searching_enemy_deck:
                                    self.p2.discard_card_from_deck(int(game_update_string[1]))
                                else:
                                    self.p1.discard_card_from_deck(int(game_update_string[1]))
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
                            elif self.what_to_do_with_searched_card == "DISCARD":
                                if self.searching_enemy_deck:
                                    self.p1.discard_card_from_deck(int(game_update_string[1]))
                                else:
                                    self.p2.discard_card_from_deck(int(game_update_string[1]))
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
                winner.capture_planet(self.last_planet_checked_for_battle,
                                      self.planet_cards_array)
                self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                await winner.send_victory_display()
            self.planet_aiming_reticle_active = False
        self.planet_aiming_reticle_position = -1
        self.p1.reset_extra_attack_eob()
        self.p2.reset_extra_attack_eob()
        self.p1.reset_extra_health_eob()
        self.p2.reset_extra_health_eob()
        another_battle = self.find_next_planet_for_combat()
        if another_battle:
            self.set_battle_initiative()
            self.p1.has_passed = False
            self.p2.has_passed = False
            self.mode = "Normal"
            self.planet_aiming_reticle_active = True
            self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
        else:
            await self.change_phase("HEADQUARTERS")
            await self.send_update_message(
                "Window provided for reactions and actions during HQ phase."
            )
        self.damage_from_atrox = False
        self.reset_battle_resolve_attributes()
        # self.reset_choices_available()

    async def complete_nullify(self):
        resolve_nullify_discard = True
        if self.first_player_nullified == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if self.nullifying_backlash:
            if self.name_player_using_backlash == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
        if self.nullify_count % 2 == 0:
            if self.nullifying_backlash:
                self.nullifying_backlash = False
                await self.complete_backlash(primary_player, secondary_player)
            elif self.nullify_context == "Regular Action":
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
                self.effects_waiting_on_resolution.append("Glorious Intervention")
                self.player_resolving_effect.append(primary_player.name_player)
            elif self.nullify_context == "Bigga Is Betta":
                self.nullify_enabled = False
                new_string_list = self.nullify_string.split(sep="/")
                await DeployPhase.update_game_event_deploy_section(self, self.first_player_nullified,
                                                                   new_string_list)
                self.nullify_enabled = True
            elif self.nullify_context == "Foresight" or self.nullify_context == "Superiority" or \
                    self.nullify_context == "Blackmane's Hunt":
                self.nullify_enabled = False
                new_string_list = self.nullify_string.split(sep="/")
                await CommandPhase.update_game_event_command_section(self, self.first_player_nullified,
                                                                     new_string_list)
                self.nullify_enabled = True
            elif self.nullify_context == "No Mercy":
                self.choices_available = []
                self.choice_context = ""
                self.name_player_making_choices = ""
                await self.send_update_message("No Mercy window offered")
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
        else:
            if self.nullifying_backlash:
                primary_player.discard_card_name_from_hand("Backlash")
                primary_player.spend_resources(1)
                self.choices_available = []
                self.choice_context = ""
                self.name_player_making_choices = ""
                self.nullifying_backlash = False
                new_string_list = self.nullify_string.split(sep="/")
                print("String used:", new_string_list)
                resolve_nullify_discard = False
                await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
                self.nullifying_backlash = True
                while self.nullify_count > 0:
                    if self.name_player_using_backlash == self.name_1:
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
            else:
                if self.nullified_card_pos != -1:
                    primary_player.discard_card_from_hand(self.nullified_card_pos)
                    if self.card_pos_to_deploy > self.nullified_card_pos:
                        self.card_pos_to_deploy -= 1
                elif self.nullified_card_name != "":
                    primary_player.discard_card_name_from_hand(self.nullified_card_name)
                primary_player.spend_resources(self.cost_card_nullified)
                if self.nullify_context == "The Fury of Sicarius":
                    pass
                elif self.nullify_context == "Indomitable" or self.nullify_context == "Glorious Intervention":
                    self.pos_shield_card = -1
                primary_player.aiming_reticle_coords_hand = None
                primary_player.aiming_reticle_coords_hand_2 = None
        if resolve_nullify_discard:
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
                if self.card_pos_to_deploy != -1 and self.nullify_context == "Bigga Is Betta":
                    primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
        self.nullify_count = 0
        if self.choice_context != "Use Interrupt?":
            self.nullify_context = ""
            self.nullify_string = ""
            self.nullified_card_pos = -1
            self.nullified_card_name = ""
            self.cost_card_nullified = 0
            self.first_player_nullified = ""
        self.p1.num_nullify_played = 0
        self.p2.num_nullify_played = 0

    async def resolve_fury_sicarius(self, primary_player, secondary_player):
        primary_player.spend_resources(2)
        primary_player.discard_card_name_from_hand("The Fury of Sicarius")
        planet_pos, unit_pos = self.furiable_unit_position
        secondary_player.set_damage_given_pos(planet_pos, unit_pos, 999)
        await self.destroy_check_all_cards()

    async def resolve_indomitable(self, primary_player, secondary_player):
        pos_holder = self.positions_of_units_to_take_damage[0]
        player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
        primary_player.discard_card_from_hand(self.pos_shield_card)
        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        self.pos_shield_card = -1
        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
        if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                self.damage_on_units_list_before_new_damage[0]:
            primary_player.set_damage_given_pos(planet_pos, unit_pos,
                                                self.damage_on_units_list_before_new_damage[0])
        await self.shield_cleanup(primary_player, secondary_player, planet_pos)

    async def complete_backlash(self, primary_player, secondary_player):
        self.choices_available = []
        self.choice_context = ""
        self.name_player_making_choices = ""
        primary_player.spend_resources(1)
        primary_player.discard_card_name_from_hand("Backlash")
        print(self.nullified_card_name)
        print(self.nullify_context)
        if self.nullify_context == "Event Action":
            secondary_player.aiming_reticle_coords_hand = None
            secondary_player.aiming_reticle_coords_hand_2 = None
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            self.amount_spend_for_tzeentch_firestorm = 0
            secondary_player.discard_card_name_from_hand(self.nullified_card_name)
        elif self.nullify_context == "In Play Action":
            secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                          self.position_of_actioned_card[1])
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            if self.nullified_card_name == "Zarathur's Flamers":
                secondary_player.sacrifice_card_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            if self.nullified_card_name in self.dies_to_backlash:
                secondary_player.destroy_card_in_play(self.position_of_actioned_card[0],
                                                      self.position_of_actioned_card[1])
            self.position_of_actioned_card = (-1, -1)
        elif self.nullify_context == "Reaction":
            if self.nullified_card_name in self.dies_to_backlash:
                secondary_player.destroy_card_in_play(self.positions_of_unit_triggering_reaction[0][1],
                                                      self.positions_of_unit_triggering_reaction[0][2])
            self.delete_reaction()
        elif self.nullify_context == "Reaction Event":
            self.delete_reaction()
            secondary_player.discard_card_name_from_hand(self.nullified_card_name)
        elif self.nullify_context == "Ferrin" or self.nullify_context == "Iridial":
            await self.resolve_battle_conclusion(secondary_player, game_string="")

    async def resolve_backlash(self, name, game_update_string, primary_player, secondary_player, may_nullify=True):
        if game_update_string[1] == "0":
            if secondary_player.nullify_check() and may_nullify:
                self.nullifying_backlash = True
                self.name_player_using_backlash = primary_player.name_player
                await self.send_update_message(
                    primary_player.name_player + " wants to play Backlash; "
                                                 "Nullify window offered.")
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Nullify?"
            else:
                await self.complete_backlash(primary_player, secondary_player)
        elif game_update_string[1] == "1":
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
            self.communications_relay_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.communications_relay_enabled = True

    async def resolve_communications_relay(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
            primary_player.exhaust_card_in_hq_given_name("Communications Relay")
            if self.nullify_context == "Event Action":
                secondary_player.aiming_reticle_coords_hand = None
                secondary_player.aiming_reticle_coords_hand_2 = None
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                self.amount_spend_for_tzeentch_firestorm = 0
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
            elif self.nullify_context == "In Play Action":
                secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                              self.position_of_actioned_card[1])
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.nullified_card_name == "Zarathur's Flamers":
                    secondary_player.sacrifice_card_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
            elif self.nullify_context == "Reaction":
                self.delete_reaction()
            elif self.nullify_context == "Reaction Event":
                self.delete_reaction()
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
                """
                elif self.nullify_context == "The Fury of Sicarius":
                    secondary_player.spend_resources(2)
                    secondary_player.discard_card_name_from_hand("The Fury of Sicarius")
                """
            elif self.nullify_context == "Ferrin" or self.nullify_context == "Iridial":
                await self.resolve_battle_conclusion(secondary_player, game_string="")
        elif game_update_string[1] == "1":
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
            self.communications_relay_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.communications_relay_enabled = True

    def action_cleanup(self):
        self.action_chosen = ""
        self.player_with_action = ""
        self.mode = "Normal"
        self.p1.harbinger_of_eternity_active = False
        self.p2.harbinger_of_eternity_active = False
        if self.phase == "DEPLOY":
            if self.number_with_deploy_turn == "1":
                self.player_with_deploy_turn = self.name_2
                self.number_with_deploy_turn = "2"
            elif self.number_with_deploy_turn == "2":
                self.player_with_deploy_turn = self.name_1
                self.number_with_deploy_turn = "1"

    def move_reaction_to_front(self, reaction_pos):
        self.reactions_needing_resolving.insert(
            0, self.reactions_needing_resolving.pop(reaction_pos)
        )
        self.player_who_resolves_reaction.insert(
            0, self.player_who_resolves_reaction.pop(reaction_pos)
        )
        self.positions_of_unit_triggering_reaction.insert(
            0, self.positions_of_unit_triggering_reaction.pop(reaction_pos)
        )
        print(self.reactions_needing_resolving)
        self.asking_if_reaction = True

    async def create_necrons_wheel_choice(self, player):
        self.resolving_search_box = True
        self.choices_available = ["Space Marines", "Tau", "Eldar", "Dark Eldar",
                                  "Chaos", "Orks", "Astra Militarum"]
        self.name_player_making_choices = player.name_player
        self.choice_context = "Choose Enslaved Faction:"

    async def resolve_choice(self, name, game_update_string):
        if name == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if name == self.name_player_making_choices:
            print("Choice context:", self.choice_context)
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.choice_context == "Shadowsun attachment from discard:":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.resolving_search_box = False
                    if self.choice_context == "Awake the Sleepers":
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.choices_available = []
                        self.resolving_search_box = False
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        primary_player.shuffle_deck()
                        self.action_cleanup()
            if len(game_update_string) == 2:
                if game_update_string[0] == "CHOICE":
                    if self.choice_context == "Choose Which Reaction":
                        print("\nGot to asking which reaction\n")
                        self.asking_which_reaction = False
                        reaction_pos = int(game_update_string[1])
                        reaction_pos = self.stored_reaction_indexes[reaction_pos]
                        print(reaction_pos)
                        self.move_reaction_to_front(reaction_pos)
                        self.has_chosen_to_resolve = False
                    elif self.choice_context == "Use Nullify?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.choosing_unit_for_nullify = True
                            self.name_player_using_nullify = primary_player.name_player
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.complete_nullify()
                            self.nullify_count = 0
                    elif self.choice_context == "Interrupt Effect?":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        print("Choice chosen:", chosen_choice)
                        if chosen_choice == "No Interrupt":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.communications_relay_enabled = False
                            self.backlash_enabled = False
                            new_string_list = self.nullify_string.split(sep="/")
                            await self.update_game_event(secondary_player.name_player, new_string_list,
                                                         same_thread=True)
                            self.communications_relay_enabled = True
                            self.backlash_enabled = True
                        elif chosen_choice == "Communications Relay":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Communications Relay?"
                        elif chosen_choice == "Backlash":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Backlash?"
                    elif self.choice_context == "Use Backlash?":
                        await self.resolve_backlash(name, game_update_string, primary_player, secondary_player)
                    elif self.choice_context == "Use Communications Relay?":
                        await self.resolve_communications_relay(name, game_update_string,
                                                                primary_player, secondary_player)
                    elif self.asking_if_reaction and self.reactions_needing_resolving \
                            and not self.resolving_search_box:
                        print("Asking if reaction")
                        self.asking_if_reaction = False
                        if game_update_string[1] == "0":
                            self.has_chosen_to_resolve = True
                        elif game_update_string[1] == "1":
                            self.delete_reaction()
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                    elif self.asking_if_remove_infested_planet:
                        if game_update_string[1] == "0":
                            self.infested_planets[self.last_planet_checked_for_battle] = False
                        self.asking_if_remove_infested_planet = False
                        self.already_asked_remove_infestation = True
                        await self.resolve_winning_combat(primary_player, secondary_player)
                    elif self.choice_context == "Resolve Battle Ability?":
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
                                    await self.resolve_battle_conclusion(name, game_update_string)
                            elif self.battle_ability_to_resolve == "Barlus":
                                loser.discard_card_at_random()
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
                                    await self.send_update_message("Too few cards in deck for search")
                                    await self.resolve_battle_conclusion(name, game_update_string)
                            elif self.battle_ability_to_resolve == "Tarrus":
                                winner_count = winner.count_units_in_play_all()
                                loser_count = loser.count_units_in_play_all()
                                if winner_count < loser_count:
                                    self.choices_available = ["Cards", "Resources"]
                                    self.choice_context = "Gains from Tarrus"
                                else:
                                    await self.resolve_battle_conclusion(name, game_update_string)
                            else:
                                if self.battle_ability_to_resolve == "Y'varn":
                                    self.yvarn_active = True
                                    self.p1_triggered_yvarn = False
                                    self.p2_triggered_yvarn = False
                                self.reset_choices_available()
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
                    elif self.choice_context == "Mulligan Opening Hand?":
                        if game_update_string[1] == "0":
                            primary_player.mulligan_done = True
                            primary_player.mulligan_hand()
                            await self.send_update_message(
                                self.name_player_making_choices + " mulligans their opening hand.")
                        elif game_update_string[1] == "1":
                            primary_player.mulligan_done = True
                            await self.send_update_message(
                                self.name_player_making_choices + " declines to mulligan their opening hand.")
                        if primary_player.mulligan_done and not secondary_player.mulligan_done:
                            self.name_player_making_choices = self.name_2
                            await self.send_update_message(
                                self.name_player_making_choices + " may mulligan their hand.")
                        if primary_player.mulligan_done and secondary_player.mulligan_done:
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.send_update_message(
                                "Both players setup, good luck and have fun!")
                            if self.p1.warlord_faction == "Necrons":
                                await self.create_necrons_wheel_choice(self.p1)
                            elif self.p2.warlord_faction == "Necrons":
                                await self.create_necrons_wheel_choice(self.p2)
                    elif self.choice_context == "Choose Enslaved Faction:":
                        chosen_faction = self.choices_available[int(game_update_string[1])]
                        primary_player.chosen_enslaved_faction = True
                        primary_player.enslaved_faction = chosen_faction
                        self.resolving_search_box = False
                        await self.send_update_message(
                            primary_player.name_player + " enslaved the " + chosen_faction + "!"
                        )
                        if not secondary_player.chosen_enslaved_faction and \
                                secondary_player.warlord_faction == "Necrons":
                            await self.create_necrons_wheel_choice(secondary_player)
                        else:
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                    elif self.choice_context == "Use Reanimating Warriors?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            self.chosen_first_card = False
                            self.asked_if_resolve_effect = True
                            self.misc_target_unit = (-1, -1)
                        if game_update_string[1] == "1":
                            del self.effects_waiting_on_resolution[0]
                            del self.player_resolving_effect[0]
                    elif self.choice_context == "Retreat Warlord?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                resolving_attack = False
                            primary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
                            primary_player.retreat_unit(self.attacker_planet, self.attacker_position)
                            self.reset_combat_positions()
                            self.number_with_combat_turn = secondary_player.get_number()
                            self.player_with_combat_turn = secondary_player.get_name_player()
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                    elif self.choice_context == "Target Dark Possession:":
                        primary_player.force_due_to_dark_possession = True
                        primary_player.cards.append(self.choices_available[int(game_update_string[1])])
                        primary_player.pos_card_dark_possession = len(primary_player.cards) - 1
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        await self.update_game_event_action(name, game_update_string)
                    elif self.choice_context == "Archon's Palace":
                        if game_update_string[1] == "0":
                            self.canceled_card_bonuses[self.misc_target_planet] = True
                        elif game_update_string[1] == "1":
                            self.canceled_resource_bonuses[self.misc_target_planet] = True
                        self.choice_context = ""
                        self.choices_available = []
                        self.name_player_making_choices = ""
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.action_cleanup()
                    elif self.choice_context == "Use Dark Possession?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Target Dark Possession:"
                            for i in range(len(secondary_player.discard)):
                                if secondary_player.discard[i] in self.valid_targets_for_dark_possession and \
                                        secondary_player.discard[i] not in self.choices_available:
                                    self.choices_available.append(secondary_player.discard[i])
                            if not self.choices_available:
                                await self.send_update_message(
                                    "No Valid Targets for Dark Possession!"
                                )
                                self.choices_available = []
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                primary_player.dark_possession_active = False
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            primary_player.dark_possession_active = False
                    elif self.choice_context == "Target Doom Scythe Invader:":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                        self.resolving_search_box = False
                        card = FindCard.find_card(target_choice, self.card_array)
                        primary_player.add_card_to_planet(card, pla)
                        primary_player.discard.remove(target_choice)
                        self.delete_reaction()
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                    elif self.choice_context == "Target Dread Monolith:":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        planet, pos = self.position_of_actioned_card
                        primary_player.reset_aiming_reticle_in_play(planet, pos)
                        card = FindCard.find_card(target_choice, self.card_array)
                        primary_player.add_card_to_planet(card, planet)
                        primary_player.discard.remove(target_choice)
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.action_cleanup()
                    elif self.choice_context == "Visions of Agony Discard:":
                        secondary_player.discard_card_from_hand(int(game_update_string[1]))
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.action_cleanup()
                        await primary_player.dark_eldar_event_played()
                        primary_player.torture_event_played()
                    elif self.choice_context == "Use No Mercy?":
                        if game_update_string[1] == "0":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
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
                            else:
                                self.choices_available = []
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                self.effects_waiting_on_resolution.append("No Mercy")
                                self.player_resolving_effect.append(name)
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
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
                    elif self.choice_context == "Anrakyr: Select which discard:":
                        found_card = False
                        can_play_card = False
                        card_name = ""
                        if game_update_string[1] == "0":
                            self.anrakyr_deck_choice = primary_player.name_player
                            i = len(primary_player.discard) - 1
                            while i > -1 and not found_card:
                                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                                if card.get_is_unit():
                                    name = card.get_name()
                                    found_card = True
                                    self.anrakyr_unit_position = i
                                    if card.get_faction() == "Necrons" or card.get_faction() == "Neutral" or \
                                            card.get_faction() == primary_player.enslaved_faction:
                                        if card.get_cost() > primary_player.resources:
                                            can_play_card = False
                                        else:
                                            can_play_card = True
                                i -= 1
                        else:
                            self.anrakyr_deck_choice = secondary_player.name_player
                            i = len(secondary_player.discard) - 1
                            while i > -1 and not found_card:
                                card = FindCard.find_card(secondary_player.discard[i], self.card_array)
                                if card.get_is_unit():
                                    name = card.get_name()
                                    found_card = True
                                    self.anrakyr_unit_position = i
                                    if card.get_faction() == "Necrons" or card.get_faction() == "Neutral" or \
                                            card.get_faction() == primary_player.enslaved_faction:
                                        if card.get_cost() > primary_player.resources:
                                            can_play_card = False
                                        else:
                                            can_play_card = True
                                i -= 1
                        if found_card:
                            if not can_play_card:
                                await self.send_update_message(
                                    "Can not play the topmost unit in that discard pile!"
                                )
                                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                            self.position_of_actioned_card[1])
                                self.action_cleanup()
                            else:
                                await self.send_update_message(
                                    "Anrakyr is playing: " + name
                                )
                        else:
                            await self.send_update_message(
                                "Did not find a valid card!"
                            )
                            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                        self.position_of_actioned_card[1])
                            self.action_cleanup()
                        self.name_player_making_choices = ""
                        self.choices_available = []
                        self.choice_context = ""
                    elif self.choice_context == "Repair Bay":
                        card_name = self.choices_available[int(game_update_string[1])]
                        primary_player.deck.insert(0, card_name)
                        primary_player.discard.remove(card_name)
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                    elif self.choice_context == "Target Leviathan Hive Ship:":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        primary_player.exhaust_card_in_hq_given_name("Leviathan Hive Ship")
                        self.choices_available = ["0", "1", "2", "3", "4", "5", "6"]
                        self.choice_context = "Planet Target Leviathan Hive Ship"
                    elif self.choice_context == "Planet Target Leviathan Hive Ship":
                        chosen_planet = int(game_update_string[1])
                        if self.planets_in_play_array[chosen_planet]:
                            card = FindCard.find_card(self.misc_target_choice, self.card_array)
                            primary_player.add_card_to_planet(card, chosen_planet, already_exhausted=True)
                            try:
                                primary_player.discard.remove(self.misc_target_choice)
                                primary_player.stored_cards_recently_discarded.remove(self.misc_target_choice)
                                primary_player.stored_cards_recently_destroyed.remove(self.misc_target_choice)
                            except ValueError:
                                pass
                            self.misc_target_choice = -1
                            self.choices_available = []
                            self.resolving_search_box = False
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.delete_reaction()
                    elif self.choice_context == "Target Fall Back:":
                        primary_player.spend_resources(1)
                        target = self.choices_available[int(game_update_string[1])]
                        card = FindCard.find_card(target, self.card_array)
                        primary_player.add_to_hq(card)
                        try:
                            primary_player.discard.remove(target)
                            primary_player.stored_cards_recently_discarded.remove(target)
                            primary_player.stored_cards_recently_destroyed.remove(target)
                        except ValueError:
                            pass
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
                    elif self.choice_context == "Target Shrine of Warpflame:":
                        target = self.choices_available[int(game_update_string[1])]
                        primary_player.cards.append(target)
                        primary_player.discard.remove(target)
                        primary_player.exhaust_card_in_hq_given_name("Shrine of Warpflame")
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.resolving_search_box = False
                    elif self.choice_context == "Choose target for Canoptek Scarab Swarm:":
                        target = self.choices_available[int(game_update_string[1])]
                        primary_player.cards.append(target)
                        primary_player.discard.remove(target)
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.delete_reaction()
                        self.resolving_search_box = False
                    elif self.choice_context == "Autarch Celachia":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.action_chosen = ""
                        self.player_with_action = ""
                        self.mode = "Normal"
                        planet_pos, unit_pos = self.position_of_actioned_card
                        primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
                        if game_update_string[1] == "0":
                            primary_player.increase_eor_value("Area Effect", 1, planet_pos, unit_pos)
                            await self.send_update_message(
                                "Autarch Celachia gained Area Effect (1)."
                            )
                        if game_update_string[1] == "1":
                            primary_player.increase_eor_value("Armorbane", 1, planet_pos, unit_pos)
                            await self.send_update_message(
                                "Autarch Celachia gained Armorbane."
                            )
                        if game_update_string[1] == "2":
                            primary_player.increase_eor_value("Mobile", 1, planet_pos, unit_pos)
                            await self.send_update_message(
                                "Autarch Celachia gained Mobile."
                            )
                        self.position_of_actioned_card = (-1, -1)
                    elif self.choice_context == "Keyword copied from Brood Chamber":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                    elif self.choice_context == "Move how much damage to Old One Eye?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        hurt_planet = self.misc_target_planet
                        hurt_pos = self.misc_target_unit
                        old_one_planet, old_one_pos = self.old_one_eye_pos
                        if game_update_string[1] == "0":
                            pass
                        elif game_update_string[1] == "1":
                            self.damage_moved_to_old_one_eye += 1
                            primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                            primary_player.assign_damage_to_pos(old_one_planet, old_one_pos, 1,
                                                                can_shield=False, is_reassign=True)
                            primary_player.set_aiming_reticle_in_play(old_one_planet, old_one_pos, "blue")
                            self.amount_that_can_be_removed_by_shield[0] -= 1
                        elif game_update_string[1] == "2":
                            self.damage_moved_to_old_one_eye += 2
                            primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 2)
                            primary_player.assign_damage_to_pos(old_one_planet, old_one_pos, 2,
                                                                can_shield=False, is_reassign=True)
                            primary_player.set_aiming_reticle_in_play(old_one_planet, old_one_pos, "blue")
                            self.amount_that_can_be_removed_by_shield[0] -= 2
                        self.misc_target_planet = -1
                        self.misc_target_unit = -1
                        if self.amount_that_can_be_removed_by_shield[0] < 1:
                            primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                            await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
                    elif self.choice_context == "Use Shrine of Warpflame?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Target Shrine of Warpflame:"
                            print("\n---IN DISCARD---\n")
                            await self.send_update_message("Shrine of Warpflame triggered")
                            print(primary_player.discard)
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                                if card.check_for_a_trait("Tzeentch"):
                                    self.choices_available.append(card.get_name())
                            if not self.choices_available:
                                await self.send_update_message(
                                    "No valid targets for Shrine of Warpflame")
                                self.resolving_search_box = False
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                    elif self.choice_context == "Spore Burst":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                    elif self.choice_context == "Heavy Venom Cannon":
                        planet, unit, att = self.misc_target_attachment
                        self.choice_context = ""
                        self.choices_available = []
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            if planet == -2:
                                primary_player.headquarters[unit].armorbane_eop = True
                                primary_player.headquarters[unit].get_attachments()[att].set_once_per_phase_used(True)
                                name = primary_player.headquarters[unit].get_name()
                                await self.send_update_message(
                                    name + " gained armorbane from Heavy Venom Cannon!"
                                )
                            else:
                                primary_player.cards_in_play[planet + 1][unit].armorbane_eop = True
                                primary_player.cards_in_play[planet + 1][unit].get_attachments()[
                                    att].set_once_per_phase_used(True)
                                name = primary_player.cards_in_play[planet + 1][unit].get_name()
                                await self.send_update_message(
                                    name + " gained armorbane from Heavy Venom Cannon!"
                                )
                        elif game_update_string[1] == "1":
                            if planet == -2:
                                primary_player.headquarters[unit].area_effect_eop += 2
                                primary_player.headquarters[unit].get_attachments()[att].set_once_per_phase_used(True)
                                name = primary_player.headquarters[unit].get_name()
                                await self.send_update_message(
                                    name + " gained area effect (2) from Heavy Venom Cannon!"
                                )
                            else:
                                primary_player.cards_in_play[planet + 1][unit].area_effect_eop += 2
                                primary_player.cards_in_play[planet + 1][unit].get_attachments()[att]. \
                                    set_once_per_phase_used(True)
                                name = primary_player.cards_in_play[planet + 1][unit].get_name()
                                await self.send_update_message(
                                    name + " gained area effect (2) from Heavy Venom Cannon!"
                                )
                        self.player_with_action = ""
                        self.mode = "Normal"
                        self.action_chosen = ""
                    elif self.choice_context == "Use Fall Back?":
                        if game_update_string[1] == "0":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
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
                            else:
                                self.choices_available = []
                                self.choice_context = "Target Fall Back:"
                                for i in range(len(primary_player.stored_cards_recently_destroyed)):
                                    card = FindCard.find_card(primary_player.stored_cards_recently_destroyed[i],
                                                              self.card_array)
                                    if card.check_for_a_trait("Elite") and card.get_is_unit():
                                        self.choices_available.append(card.get_name())
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                    elif self.choice_context == "Use Holy Sepulchre?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Target Holy Sepulchre:"
                            for i in range(len(primary_player.stored_cards_recently_discarded)):
                                card = FindCard.find_card(primary_player.stored_cards_recently_discarded[i],
                                                          self.card_array)
                                if card.get_faction() == "Space Marines" and card.get_is_unit():
                                    self.choices_available.append(card.get_name())
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                    elif self.choice_context == "Use Leviathan Hive Ship?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Target Leviathan Hive Ship:"
                            for i in range(len(primary_player.stored_cards_recently_destroyed)):
                                card = FindCard.find_card(primary_player.stored_cards_recently_destroyed[i],
                                                          self.card_array)
                                if card.get_is_unit():
                                    if card.has_hive_mind and card.get_cost() < 4:
                                        self.choices_available.append(card.get_name())
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                    elif self.choice_context == "Use an extra source of damage?":
                        if self.choices_available[int(game_update_string[1])] == "The Fury of Sicarius":
                            self.choice_context = "Use The Fury of Sicarius?"
                            self.choices_available = ["Yes", "No"]
                        else:
                            self.auto_card_destruction = True
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                    elif self.choice_context == "Use The Fury of Sicarius?":
                        planet_pos, unit_pos = self.furiable_unit_position
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            if secondary_player.nullify_check():
                                await self.send_update_message(
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
                            else:
                                await self.resolve_fury_sicarius(primary_player, secondary_player)
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.destroy_check_all_cards()
                    elif self.choice_context == "Use alternative shield effect?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.better_shield_card_resolution(name, self.last_shield_string, alt_shields=False)
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            if primary_player.cards[self.pos_shield_card] == "Indomitable":
                                if secondary_player.nullify_check():
                                    await self.send_update_message(
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
                                elif primary_player.spend_resources(1):
                                    await self.resolve_indomitable(primary_player, secondary_player)
                            elif primary_player.cards[self.pos_shield_card] == "Glorious Intervention":
                                if secondary_player.nullify_check():
                                    await self.send_update_message(
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
                                elif primary_player.spend_resources(1):
                                    primary_player.aiming_reticle_coords_hand = self.pos_shield_card
                                    primary_player.aiming_reticle_color = "blue"
                                    self.effects_waiting_on_resolution.append("Glorious Intervention")
                                    self.player_resolving_effect.append(primary_player.name_player)
                    elif self.choice_context == "Awake the Sleepers":
                        target_name = self.choices_available[int(game_update_string[1])]
                        primary_player.deck.append(target_name)
                        primary_player.discard.remove(target_name)
                        del self.choices_available[int(game_update_string[1])]
                        if not self.choices_available:
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                            primary_player.aiming_reticle_coords_hand = None
                            await self.send_update_message(
                                "No valid targets for Awake the Sleepers"
                            )
                            primary_player.shuffle_deck()
                            self.action_cleanup()
                    elif self.choice_context == "Drudgery":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.resolving_search_box = False

                    elif self.choice_context == "Toxic Venomthrope: Gain Card or Resource?" or \
                            self.choice_context == "Homing Beacon: Gain Card or Resource?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            primary_player.draw_card()
                        elif game_update_string[1] == "1":
                            primary_player.add_resources(1)
                        self.delete_reaction()
                    elif self.choice_context == "Sautekh Complex: Gain Card or Resource?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            primary_player.draw_card()
                        elif game_update_string[1] == "1":
                            primary_player.add_resources(1)
                        self.delete_reaction()
                    elif self.choice_context == "Shadowsun plays attachment from hand or discard?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            self.shadowsun_chose_hand = True
                            self.location_hand_attachment_shadowsun = -1
                            self.effects_waiting_on_resolution.append("Commander Shadowsun")
                            self.player_resolving_effect.append(name)
                            await self.send_update_message("Choose card in hand")
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
                                await self.send_update_message("No valid cards in discard")
                                self.resolving_search_box = False
                            else:
                                await self.send_update_message("Choose card in discard")
                    elif self.choice_context == "Shadowsun attachment from discard:":
                        self.name_attachment_discard_shadowsun = self.choices_available[int(game_update_string[1])]
                        await self.send_update_message(
                            "Selected a " + self.name_attachment_discard_shadowsun)
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.effects_waiting_on_resolution.append("Commander Shadowsun")
                        self.player_resolving_effect.append(name)
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
                            await self.send_update_message("Too few cards in deck")

    async def resolve_battle_ability_routine(self, name, game_update_string):
        if self.yvarn_active:
            if name == self.name_1:
                if not self.p1_triggered_yvarn:
                    if len(game_update_string) == 1:
                        if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                            await self.send_update_message(self.name_1 + " declines y'varn.")
                            self.p1_triggered_yvarn = True
                    elif len(game_update_string) == 3:
                        if game_update_string[0] == "HAND":
                            if game_update_string[1] == "1":
                                played = self.p1.put_card_in_hand_into_hq(int(game_update_string[2]))
                                if played:
                                    self.p1_triggered_yvarn = True
            elif name == self.name_2:
                if not self.p2_triggered_yvarn:
                    if len(game_update_string) == 1:
                        if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                            await self.send_update_message(self.name_2 + " declines y'varn.")
                            self.p2_triggered_yvarn = True
                    elif len(game_update_string) == 3:
                        if game_update_string[0] == "HAND":
                            if game_update_string[1] == "2":
                                played = self.p2.put_card_in_hand_into_hq(int(game_update_string[2]))
                                if played:
                                    self.p2_triggered_yvarn = True
            if self.p1_triggered_yvarn and self.p2_triggered_yvarn:
                self.yvarn_active = False
                self.reset_choices_available()
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
                                    possible_interrupts = self.p1.interrupt_cancel_target_check(planet_pos, unit_pos)
                                    if possible_interrupts:
                                        can_continue = False
                                        await self.send_update_message(
                                            "Some sort of interrupt may be used.")
                                        self.choices_available = possible_interrupts
                                        self.choices_available.insert(0, "No Interrupt")
                                        self.name_player_making_choices = self.p1.name_player
                                        self.choice_context = "Interrupt Effect?"
                                        self.nullified_card_name = "Ferrin"
                                        self.cost_card_nullified = 0
                                        self.nullify_string = "/".join(game_update_string)
                                        self.first_player_nullified = self.p2.name_player
                                        self.nullify_context = "Ferrin"
                                if can_continue:
                                    self.p1.rout_unit(int(game_update_string[2]), int(game_update_string[3]))
                                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                         game_update_string)
                        elif game_update_string[1] == "2":
                            if self.p2.cards_in_play[int(game_update_string[2]) + 1][int(game_update_string[3])]. \
                                    get_card_type != "Warlord":
                                can_continue = True
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if self.player_resolving_battle_ability != self.p2.name_player:
                                    possible_interrupts = self.p2.interrupt_cancel_target_check(planet_pos, unit_pos)
                                    if possible_interrupts:
                                        can_continue = False
                                        await self.send_update_message(
                                            "Some sort of interrupt may be used.")
                                        self.choices_available = possible_interrupts
                                        self.choices_available.insert(0, "No Interrupt")
                                        self.name_player_making_choices = self.p2.name_player
                                        self.choice_context = "Interrupt Effect?"
                                        self.nullified_card_name = "Ferrin"
                                        self.cost_card_nullified = 0
                                        self.nullify_string = "/".join(game_update_string)
                                        self.first_player_nullified = self.p1.name_player
                                        self.nullify_context = "Ferrin"
                                if can_continue:
                                    self.p2.rout_unit(int(game_update_string[2]), int(game_update_string[3]))
                                    await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                         game_update_string)
            elif self.battle_ability_to_resolve == "Carnath":
                if len(game_update_string) == 2:
                    if game_update_string[0] == "PLANETS":
                        self.battle_ability_to_resolve = self.planet_array[int(game_update_string[1])]
                        self.choices_available = ["Yes", "No"]
                        self.choice_context = "Resolve Battle Ability?"
                        self.name_player_making_choices = name
            elif self.battle_ability_to_resolve == "Iridial":
                if len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if game_update_string[1] == "1":
                            can_continue = True
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if self.player_resolving_battle_ability != self.p1.name_player:
                                possible_interrupts = self.p1.interrupt_cancel_target_check(planet_pos, unit_pos)
                                if possible_interrupts:
                                    can_continue = False
                                    await self.send_update_message(
                                        "Some sort of interrupt may be used.")
                                    self.choices_available = possible_interrupts
                                    self.choices_available.insert(0, "No Interrupt")
                                    self.name_player_making_choices = self.p1.name_player
                                    self.choice_context = "Interrupt Effect?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p2.name_player
                                    self.nullify_context = "Iridial"
                            if can_continue:
                                self.p1.remove_damage_from_pos(int(game_update_string[2]), int(game_update_string[3]),
                                                               99)
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
                        elif game_update_string[1] == "2":
                            can_continue = True
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if self.player_resolving_battle_ability != self.p2.name_player:
                                possible_interrupts = self.p2.interrupt_cancel_target_check(planet_pos, unit_pos)
                                if possible_interrupts:
                                    can_continue = False
                                    await self.send_update_message(
                                        "Some sort of interrupt may be used.")
                                    self.choices_available = possible_interrupts
                                    self.choices_available.insert(0, "No Interrupt")
                                    self.name_player_making_choices = self.p2.name_player
                                    self.choice_context = "Interrupt Effect?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p1.name_player
                                    self.nullify_context = "Iridial"
                            if can_continue:
                                self.p2.remove_damage_from_pos(int(game_update_string[2]), int(game_update_string[3]),
                                                               99)
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
                elif len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        if game_update_string[1] == "1":
                            can_continue = True
                            planet_pos = -2
                            unit_pos = int(game_update_string[2])
                            if self.player_resolving_battle_ability != self.p1.name_player:
                                possible_interrupts = self.p1.interrupt_cancel_target_check(planet_pos, unit_pos)
                                if possible_interrupts:
                                    can_continue = False
                                    await self.send_update_message(
                                        "Some sort of interrupt may be used.")
                                    self.choices_available = possible_interrupts
                                    self.choices_available.insert(0, "No Interrupt")
                                    self.name_player_making_choices = self.p1.name_player
                                    self.choice_context = "Interrupt Effect?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p2.name_player
                                    self.nullify_context = "Iridial"
                            if can_continue:
                                self.p1.remove_damage_from_pos(-2, int(game_update_string[2]), 99)
                                await self.resolve_battle_conclusion(self.player_resolving_battle_ability,
                                                                     game_update_string)
                        elif game_update_string[1] == "2":
                            can_continue = True
                            planet_pos = -2
                            unit_pos = int(game_update_string[2])
                            if self.player_resolving_battle_ability != self.p2.name_player:
                                possible_interrupts = self.p2.interrupt_cancel_target_check(planet_pos, unit_pos)
                                if possible_interrupts:
                                    can_continue = False
                                    await self.send_update_message(
                                        "Some sort of interrupt may be used.")
                                    self.choices_available = possible_interrupts
                                    self.choices_available.insert(0, "No Interrupt")
                                    self.name_player_making_choices = self.p2.name_player
                                    self.choice_context = "Interrupt Effect?"
                                    self.nullified_card_name = "Iridial"
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = self.p1.name_player
                                    self.nullify_context = "Iridial"
                            if can_continue:
                                self.p2.remove_damage_from_pos(-2, int(game_update_string[2]), 99)
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

    async def destroy_check_cards_in_hq(self, player):
        i = 0
        destroyed_something = False
        while i < len(player.headquarters):
            if player.headquarters[i].get_card_type != "Support":
                if player.check_if_card_is_destroyed(-2, i):
                    player.destroy_card_in_hq(i)
                    destroyed_something = True
                    i = i - 1
            i = i + 1
        if self.damage_from_atrox:
            await self.resolve_battle_conclusion(self.player_resolving_battle_ability, "")

    async def resolve_on_kill_effects(self, i):
        print("--------\nON KILL EFFECTS\n--------")
        num, planet, pos = self.recently_damaged_units[i]
        if num == 1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if primary_player.check_if_card_is_destroyed(planet, pos):
            if self.on_kill_effects_of_attacker[i]:
                for j in range(len(self.on_kill_effects_of_attacker[i])):
                    if self.on_kill_effects_of_attacker[i][j] == "Bone Sabres":
                        self.create_reaction("Bone Sabres", secondary_player.name_player,
                                             (int(secondary_player.number), planet, pos))
                    if self.on_kill_effects_of_attacker[i][j] == "Ravenous Haruspex":
                        self.create_reaction("Ravenous Haruspex", secondary_player.name_player,
                                             (int(secondary_player.number), planet, pos))
                        self.ravenous_haruspex_gain = primary_player.get_cost_given_pos(planet, pos)
                    if self.on_kill_effects_of_attacker[i][j] == "Patrolling Wraith":
                        self.create_reaction("Patrolling Wraith", secondary_player.name_player,
                                             (int(secondary_player.number), planet, pos))
                        self.name_of_attacked_unit = primary_player.get_name_given_pos(planet, pos)
            if self.positions_of_attacker_of_unit_that_took_damage[i] is not None:
                if primary_player.search_hand_for_card("Vengeance!"):
                    self.create_reaction("Vengeance!", primary_player.name_player,
                                         (int(primary_player.number), planet, pos))

    async def destroy_check_cards_at_planet(self, player, planet_num):
        i = 0
        destroyed_something = False
        while i < len(player.cards_in_play[planet_num + 1]):
            if self.attacker_planet == planet_num and self.attacker_position == i:
                if self.player_with_combat_turn == player.name_player:
                    player.set_aiming_reticle_in_play(planet_num, i, "blue")
            if player.check_if_card_is_destroyed(planet_num, i):
                if self.attacker_planet == planet_num and self.attacker_position == i:
                    self.attacker_planet = -1
                    self.attacker_position = -1
                player.destroy_card_in_play(planet_num, i)
                destroyed_something = True
                i = i - 1
            i = i + 1
        if destroyed_something:
            self.bloodthirst_active[planet_num] = True

    def holy_sepulchre_check(self, player):
        if player.search_card_in_hq("Holy Sepulchre", ready_relevant=True):
            for card_name in player.stored_cards_recently_discarded:
                card = FindCard.find_card(card_name, self.card_array)
                if card.get_faction() == "Space Marines" and card.get_is_unit():
                    return True
        return False

    def leviathan_hive_ship_check(self, player):
        if player.search_card_in_hq("Leviathan Hive Ship", ready_relevant=True):
            for card_name in player.stored_cards_recently_destroyed:
                card = FindCard.find_card(card_name, self.card_array)
                if card.get_is_unit():
                    if card.has_hive_mind and card.get_cost() < 4:
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

    async def complete_destruction_checks(self):
        if not self.reactions_needing_resolving:
            self.p1.stored_cards_recently_discarded = copy.deepcopy(self.p1.cards_recently_discarded)
            self.p2.stored_cards_recently_discarded = copy.deepcopy(self.p2.cards_recently_discarded)
            self.p1.stored_cards_recently_destroyed = copy.deepcopy(self.p1.cards_recently_destroyed)
            self.p2.stored_cards_recently_destroyed = copy.deepcopy(self.p2.cards_recently_destroyed)
        else:
            self.p1.stored_cards_recently_discarded += copy.deepcopy(self.p1.cards_recently_discarded)
            self.p2.stored_cards_recently_discarded += copy.deepcopy(self.p2.cards_recently_discarded)
            self.p1.stored_cards_recently_destroyed += copy.deepcopy(self.p1.cards_recently_destroyed)
            self.p2.stored_cards_recently_destroyed += copy.deepcopy(self.p2.cards_recently_destroyed)
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
        if self.leviathan_hive_ship_check(self.p1):
            already_hive_ship = False
            for i in range(len(self.reactions_needing_resolving)):
                if self.reactions_needing_resolving[i] == "Leviathan Hive Ship":
                    if self.player_who_resolves_reaction[i] == self.name_1:
                        aready_hive_ship = True
            if not already_hive_ship:
                self.create_reaction("Leviathan Hive Ship", self.name_1, (1, -1, -1))
        if self.leviathan_hive_ship_check(self.p2):
            already_hive_ship = False
            for i in range(len(self.reactions_needing_resolving)):
                if self.reactions_needing_resolving[i] == "Leviathan Hive Ship":
                    if self.player_who_resolves_reaction[i] == self.name_2:
                        aready_hive_ship = True
            if not already_hive_ship:
                self.create_reaction("Leviathan Hive Ship", self.name_2, (2, -1, -1))
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
        if self.p1.warlord_just_got_destroyed and not self.p2.warlord_just_got_destroyed:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_2 + "; sufficient icons on captured planets."
                                               "----GAME END----"
            )
        elif not self.p1.warlord_just_got_destroyed and self.p1.warlord_just_got_destroyed:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_1 + "; sufficient icons on captured planets."
                                               "----GAME END----"
            )
        elif self.p1.warlord_just_got_destroyed and self.p2.warlord_just_got_destroyed:
            await self.send_update_message(
                "----GAME END----"
                "Both warlords just died. I guess it is a draw?"
                "----GAME END----"
            )
        self.reset_resolving_attack_on_units = True
        if self.resolving_kugath_nurglings:
            self.set_targeting_icons_kugath_nurglings()

    async def destroy_check_all_cards(self):
        if not self.reactions_needing_resolving and not self.effects_waiting_on_resolution:
            print("\n\nABOUT TO EXECUTE:", self.on_kill_effects_of_attacker)
            for i in range(len(self.recently_damaged_units)):
                await self.resolve_on_kill_effects(i)
            self.recently_damaged_units = []
            self.damage_taken_was_from_attack = []
            self.positions_of_attacker_of_unit_that_took_damage = []
            self.faction_of_attacker = []
            self.on_kill_effects_of_attacker = []
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
            await self.complete_destruction_checks()
        else:
            self.resolve_destruction_checks_after_reactions = True
            # await self.game_sockets[0].receive_game_update(
            #     "Some damage/destruction reactions need to be resolved before actual destruction is done."
            # )

    def advance_damage_aiming_reticle(self):
        if self.positions_of_units_to_take_damage:
            pos_holder = self.positions_of_units_to_take_damage[0]
            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
            if player_num == 1:
                self.p1.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
            elif player_num == 2:
                self.p2.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")

    def conclude_mind_shackle_scarab(self):
        i = 0
        while i < len(self.p1.headquarters):
            if self.p1.headquarters[i].mind_shackle_scarab_effect:
                self.p1.headquarters[i].mind_shackle_scarab_effect = False
                self.take_control_of_card(self.p2, self.p1, -2, i)
                i -= 1
            i += 1
        i = 0
        while i < len(self.p2.headquarters):
            if self.p2.headquarters[i].mind_shackle_scarab_effect:
                self.p2.headquarters[i].mind_shackle_scarab_effect = False
                self.take_control_of_card(self.p1, self.p2, -2, i)
                i -= 1
            i += 1
        for planet_pos in range(7):
            i = 0
            while i < len(self.p1.cards_in_play[planet_pos + 1]):
                if self.p1.cards_in_play[planet_pos + 1][i].mind_shackle_scarab_effect:
                    self.p1.cards_in_play[planet_pos + 1][i].mind_shackle_scarab_effect = False
                    self.take_control_of_card(self.p2, self.p1, planet_pos, i)
                    i -= 1
                i += 1
            i = 0
            while i < len(self.p2.cards_in_play[planet_pos + 1]):
                if self.p2.cards_in_play[planet_pos + 1][i].mind_shackle_scarab_effect:
                    self.p2.cards_in_play[planet_pos + 1][i].mind_shackle_scarab_effect = False
                    self.take_control_of_card(self.p1, self.p2, planet_pos, i)
                    i -= 1
                i += 1

    async def change_phase(self, new_val, refresh_abilities=True):
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.p1.muster_the_guard_count = 0
        self.p2.muster_the_guard_count = 0
        last_phase = self.phase
        self.phase = new_val
        if self.phase == "COMMAND":
            self.committing_warlords = True
        sacrifice_locations = self.p1.sacrifice_check_eop()
        sacrifice_locations = self.p2.sacrifice_check_eop()
        self.conclude_mind_shackle_scarab()
        self.p1.reset_extra_attack_eop()
        self.p2.reset_extra_attack_eop()
        self.p1.reset_extra_abilities_eop()
        self.p2.reset_extra_abilities_eop()
        self.p1.reset_all_blanked_eop()
        self.p2.reset_all_blanked_eop()
        self.canceled_resource_bonuses = [False, False, False, False, False, False, False]
        self.canceled_card_bonuses = [False, False, False, False, False, False, False]
        if refresh_abilities:
            self.p1.refresh_once_per_phase_abilities()
            self.p2.refresh_once_per_phase_abilities()
        print("\nDEBUG NECRONS\n", self.phase, last_phase, "\n\n")
        if self.phase == "DEPLOY" and last_phase != "SETUP":
            print("resetting necrons enslaved factions")
            self.p1.chosen_enslaved_faction = False
            self.p2.chosen_enslaved_faction = False
            if self.p1.warlord_faction == "Necrons":
                await self.create_necrons_wheel_choice(self.p1)
            elif self.p2.warlord_faction == "Necrons":
                await self.create_necrons_wheel_choice(self.p2)
        self.create_reactions_phase_begins()

    async def calculate_automatic_discounts_unit(self, planet_chosen, card, player):
        if card.get_ability() == "Burrowing Trygon":
            num_termagants = player.get_most_termagants_at_single_planet()
            self.discounts_applied += num_termagants
        if card.get_faction() == "Astra Militarum":
            self.discounts_applied += player.muster_the_guard_count

    async def calculate_available_discounts_unit(self, planet_chosen, card, player):
        self.available_discounts = player.search_hq_for_discounts(card.get_faction(),
                                                                  card.get_traits(),
                                                                  planet_chosen=planet_chosen)
        hand_disc = player.search_hand_for_discounts(card.get_faction())
        self.available_discounts += hand_disc
        if hand_disc > 0:
            await self.send_update_message(
                "Bigga Is Betta detected, may be used as a discount."
            )
        temp_av_disc, _ = player. \
            search_same_planet_for_discounts(self.faction_of_card_to_play, planet_pos=planet_chosen)
        if card.get_ability() == "Burrowing Trygon":
            num_termagants = player.get_most_termagants_at_single_planet()
            self.available_discounts += num_termagants
        if card.get_faction() == "Astra Militarum":
            self.available_discounts += player.muster_the_guard_count
        self.available_discounts += player.search_all_planets_for_discounts(self.traits_of_card_to_play)
        self.available_discounts += temp_av_disc

    def create_reactions_phase_begins(self):
        self.p1.perform_own_reactions_on_phase_change(self.phase)
        self.p2.perform_own_reactions_on_phase_change(self.phase)

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
                    if planet_pos != -2:
                        if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Reanimating Warriors" \
                                and not primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_phase_used:
                            self.effects_waiting_on_resolution.append("Reanimating Warriors")
                            self.player_resolving_effect.append(primary_player.name_player)
                    if self.positions_attackers_of_units_to_take_damage[0] is not None:
                        self.damage_taken_was_from_attack.append(True)
                        self.positions_of_attacker_of_unit_that_took_damage.append(
                            self.positions_attackers_of_units_to_take_damage[0])
                        att_num, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
                        self.faction_of_attacker.append(secondary_player.get_faction_given_pos(att_pla, att_pos))
                        self.on_kill_effects_of_attacker.append(
                            secondary_player.get_on_kill_effects_of_attacker(att_pla, att_pos))
                        print("\n\nSAVED ON KILL EFFECTS\n\n", self.on_kill_effects_of_attacker)
                        if primary_player.search_attachments_at_pos(planet_pos, unit_pos, "Repulsor Impact Field"):
                            self.create_reaction("Repulsor Impact Field", primary_player.name_player,
                                                 (int(secondary_player.number), att_pla, att_pos))
                        if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Solarite Avetys":
                            if not secondary_player.get_flying_given_pos(att_pla, att_pos):
                                self.create_reaction("Solarite Avetys", primary_player.name_player,
                                                     (int(secondary_player.number), planet_pos, unit_pos))
                        if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                            if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Volatile Pyrovore":
                                self.create_reaction("Volatile Pyrovore", primary_player.name_player,
                                                     (int(secondary_player.number), att_pla, att_pos))
                            if planet_pos != -2:
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Treacherous Lhamaean":
                                    self.create_reaction("Treacherous Lhamaean", primary_player.name_player,
                                                         (int(primary_player.number), planet_pos, unit_pos))
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                        == "Swarmling Termagants":
                                    self.create_reaction("Swarmling Termagants",
                                                         primary_player.name_player,
                                                         (int(primary_player.number), planet_pos,
                                                          unit_pos))
                        if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Deathskull Lootas":
                            self.create_reaction("Deathskull Lootas", secondary_player.name_player,
                                                 (int(secondary_player.number), planet_pos, unit_pos))
                        if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                                if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Black Heart Ravager":
                                    self.create_reaction("Black Heart Ravager", secondary_player.name_player,
                                                         (int(primary_player.number), planet_pos, unit_pos))
                                if secondary_player.search_attachments_at_pos(att_pla, att_pos, "Pincer Tail"):
                                    self.create_reaction("Pincer Tail", secondary_player.name_player, pos_holder)
                    else:
                        self.damage_taken_was_from_attack.append(False)
                        self.positions_of_attacker_of_unit_that_took_damage.append(None)
                        self.faction_of_attacker.append("")
                        self.on_kill_effects_of_attacker.append([])
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
                                elif primary_player.cards[hand_pos] == "Glorious Intervention":
                                    if primary_player.resources > 0:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            alt_shield_check = True
                                            self.pos_shield_card = hand_pos
                                            self.choices_available = ["Shield", "Effect"]
                                            self.name_player_making_choices = name
                                            self.choice_context = "Use alternative shield effect?"
                                            self.last_shield_string = game_update_string
                        if shields > 0 and not alt_shield_check:
                            print("Just before can shield check")
                            if self.damage_can_be_shielded[0]:
                                no_mercy_possible = False
                                if can_no_mercy:
                                    for i in range(len(secondary_player.cards)):
                                        if secondary_player.cards[i] == "No Mercy":
                                            no_mercy_possible = True
                                if no_mercy_possible:
                                    no_mercy_possible = secondary_player.search_ready_unique_unit()
                                if no_mercy_possible:
                                    self.last_shield_string = game_update_string
                                    self.choice_context = "Use No Mercy?"
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                else:
                                    shields = min(shields, self.amount_that_can_be_removed_by_shield[0])
                                    took_damage = True
                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, shields)
                                    """
                                    if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                            self.damage_on_units_list_before_new_damage[0]:
                                        primary_player.set_damage_given_pos(
                                            planet_pos, unit_pos, self.damage_on_units_list_before_new_damage[0])
                                        took_damage = False
                                    """
                                    primary_player.discard_card_from_hand(hand_pos)
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    if took_damage:
                                        self.recently_damaged_units.append(self.positions_of_units_to_take_damage[0])
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            self.damage_taken_was_from_attack.append(True)
                                            self.positions_of_attacker_of_unit_that_took_damage.append(
                                                self.positions_attackers_of_units_to_take_damage[0]
                                            )
                                            att_num, att_pla, att_pos = self. \
                                                positions_attackers_of_units_to_take_damage[0]
                                            self.faction_of_attacker.append(secondary_player.get_faction_given_pos(
                                                att_pla, att_pos
                                            ))
                                            self.on_kill_effects_of_attacker.append(
                                                secondary_player.get_on_kill_effects_of_attacker(att_pla, att_pos))
                                            if planet_pos != -2:
                                                if primary_player.cards_in_play[planet_pos + 1][
                                                    unit_pos].get_ability() == "Reanimating Warriors" \
                                                        and not primary_player.cards_in_play[planet_pos + 1][
                                                        unit_pos].once_per_phase_used:
                                                    self.effects_waiting_on_resolution.append("Reanimating Warriors")
                                                    self.player_resolving_effect.append(primary_player.name_player)
                                            if primary_player.search_attachments_at_pos(planet_pos, unit_pos,
                                                                                        "Repulsor Impact Field"):
                                                self.create_reaction("Repulsor Impact Field",
                                                                     primary_player.name_player,
                                                                     (int(secondary_player.number), att_pla, att_pos))
                                            if primary_player.get_ability_given_pos(planet_pos,
                                                                                    unit_pos) == "Solarite Avetys":
                                                if not secondary_player.get_flying_given_pos(att_pla, att_pos):
                                                    self.create_reaction("Solarite Avetys", primary_player.name_player,
                                                                         (int(secondary_player.number), planet_pos,
                                                                          unit_pos))
                                            if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                                                if primary_player.get_ability_given_pos(
                                                        planet_pos, unit_pos) == "Volatile Pyrovore":
                                                    self.create_reaction("Volatile Pyrovore",
                                                                         primary_player.name_player,
                                                                         (int(secondary_player.number), att_pla,
                                                                          att_pos))
                                                if planet_pos != -2:
                                                    if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                                            == "Treacherous Lhamaean":
                                                        self.create_reaction("Treacherous Lhamaean",
                                                                             primary_player.name_player,
                                                                             (int(primary_player.number), planet_pos,
                                                                              unit_pos))
                                                    if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                                            == "Swarmling Termagants":
                                                        self.create_reaction("Swarmling Termagants",
                                                                             primary_player.name_player,
                                                                             (int(primary_player.number), planet_pos,
                                                                              unit_pos))
                                            if secondary_player.get_ability_given_pos(att_pla, att_pos) \
                                                    == "Deathskull Lootas":
                                                self.create_reaction("Deathskull Lootas", secondary_player.name_player,
                                                                     (int(secondary_player.number), planet_pos,
                                                                      unit_pos))
                                            if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                                                if primary_player.cards_in_play[planet_pos + 1][unit_pos] \
                                                        .get_card_type() != "Warlord":
                                                    if secondary_player.get_ability_given_pos(att_pla, att_pos) == \
                                                            "Black Heart Ravager":
                                                        self.create_reaction("Black Heart Ravager",
                                                                             secondary_player.name_player,
                                                                             (int(primary_player.number), planet_pos,
                                                                              unit_pos))
                                                    if secondary_player.search_attachments_at_pos(att_pla, att_pos,
                                                                                                  "Pincer Tail"):
                                                        self.create_reaction("Pincer Tail",
                                                                             secondary_player.name_player,
                                                                             pos_holder)
                                        else:
                                            self.damage_taken_was_from_attack.append(False)
                                            self.positions_of_attacker_of_unit_that_took_damage.append(None)
                                            self.faction_of_attacker.append("")
                                            self.on_kill_effects_of_attacker.append([])
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                            else:
                                await self.send_update_message("This damage can not be shielded!")
                elif game_update_string[0] == "HQ":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        hq_pos = int(game_update_string[2])
                        if primary_player.headquarters[hq_pos].get_ability() == "Rockcrete Bunker":
                            print("is rockcrete bunker")
                            if primary_player.headquarters[hq_pos].get_ready():
                                print("is ready")
                                primary_player.exhaust_given_pos(-2, hq_pos)
                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                self.amount_that_can_be_removed_by_shield[0] -= 1
                                if primary_player.get_damage_given_pos(planet_pos, unit_pos) == \
                                        self.damage_on_units_list_before_new_damage[0]:
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Kustom Field Generator":
                            if primary_player.headquarters[hq_pos].get_ready():
                                hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                                if primary_player.get_faction_given_pos(hurt_planet, hurt_pos) == "Orks":
                                    if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                        primary_player.exhaust_given_pos(-2, hq_pos)
                                        damage = self.amount_that_can_be_removed_by_shield[0]
                                        primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage)
                                        primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                        self.location_of_indirect = "PLANET"
                                        self.planet_of_indirect = hurt_planet
                                        self.faction_of_cards_for_indirect = "Orks"
                                        self.valid_targets_for_indirect = ["Army", "Synapse", "Warlord", "Token"]
                                        primary_player.indirect_damage_applied = 0
                                        primary_player.total_indirect_damage = damage
                                        await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
                        elif primary_player.headquarters[hq_pos].get_name() == "Old One Eye":
                            hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                            if primary_player.get_ability_given_pos(hurt_planet, hurt_pos) == "Lurking Hormagaunt":
                                if self.damage_moved_to_old_one_eye == 0:
                                    self.choices_available = ["0", "1", "2"]
                                    if self.amount_that_can_be_removed_by_shield[0] == 1:
                                        self.choices_available = ["0", "1"]
                                    self.choice_context = "Move how much damage to Old One Eye?"
                                    self.name_player_making_choices = primary_player.name_player
                                    self.misc_target_planet = hurt_planet
                                    self.misc_target_unit = hurt_pos
                                    self.old_one_eye_pos = (-2, hq_pos)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Adamant Hive Guard":
                            hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                            if primary_player.get_name_given_pos(hurt_planet, hurt_pos) == "Termagant" or \
                                    primary_player.get_has_hive_mind_given_pos(hurt_planet, hurt_pos):
                                damage = self.amount_that_can_be_removed_by_shield[0]
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage)
                                primary_player.assign_damage_to_pos_hq(hq_pos, damage, can_shield=False)
                                primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        planet_pos = int(game_update_string[2])
                        unit_pos = int(game_update_string[3])
                        if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_name() == "Old One Eye":
                            hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                            if primary_player.get_ability_given_pos(hurt_planet, hurt_pos) == "Lurking Hormagaunt":
                                if self.damage_moved_to_old_one_eye == 0:
                                    self.choices_available = ["0", "1", "2"]
                                    if self.amount_that_can_be_removed_by_shield[0] == 1:
                                        self.choices_available = ["0", "1"]
                                    self.choice_context = "Move how much damage to Old One Eye?"
                                    self.name_player_making_choices = primary_player.name_player
                                    self.misc_target_planet = hurt_planet
                                    self.misc_target_unit = hurt_pos
                                    self.old_one_eye_pos = (planet_pos, unit_pos)
                        elif primary_player.cards_in_play[planet_pos + 1][unit_pos] \
                                .get_ability() == "Adamant Hive Guard":
                            hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                            if primary_player.get_name_given_pos(hurt_planet, hurt_pos) == "Termagant" or \
                                    primary_player.get_has_hive_mind_given_pos(hurt_planet, hurt_pos):
                                damage = self.amount_that_can_be_removed_by_shield[0]
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage)
                                primary_player.assign_damage_to_pos(planet_pos, unit_pos, damage,
                                                                    can_shield=False, is_reassign=True)
                                primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
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
                                    attachment = primary_player.cards_in_play[planet_pos + 1][unit_pos] \
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

    def combat_reset_eocr_values(self):
        self.p1.reset_eocr_values()
        self.p2.reset_eocr_values()

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
                        await self.send_update_message("No sacrifice for Power from Pain")
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
                    if self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
                        planet_pos, unit_pos = self.misc_target_unit
                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    if self.reactions_needing_resolving[0] == "Soul Grinder":
                        planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                        unit_pos = self.positions_of_unit_triggering_reaction[0][2]
                        secondary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    if self.reactions_needing_resolving[0] == "Nullify":
                        await self.complete_nullify()
                    self.delete_reaction()
            elif len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    await PlanetsReaction.resolve_planet_reaction(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    await HandReaction.resolve_hand_reaction(self, name, game_update_string,
                                                             primary_player, secondary_player)
                elif game_update_string[0] == "HQ":
                    await HQReaction.resolve_hq_reaction(self, name, game_update_string,
                                                         primary_player, secondary_player)
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    await InPlayReaction.resolve_in_play_reaction(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif len(game_update_string) == 5:
                if game_update_string[0] == "ATTACHMENT":
                    if game_update_string[1] == "PLANETS":
                        player_num = int(game_update_string[2])
                        planet_pos = int(game_update_string[3])
                        attachment_pos = int(game_update_string[4])
                        if int(primary_player.number) == player_num:
                            if self.reactions_needing_resolving[0] == "Defense Battery":
                                if not self.chosen_first_card:
                                    if primary_player.attachments_at_planet[planet_pos][attachment_pos].get_ability() \
                                            == "Defense Battery":
                                        if primary_player.attachments_at_planet[planet_pos][attachment_pos]. \
                                                defense_battery_activated:
                                            if primary_player.attachments_at_planet[planet_pos][attachment_pos]. \
                                                    get_ready():
                                                primary_player.attachments_at_planet[planet_pos][attachment_pos]. \
                                                    exhaust_card()
                                                self.chosen_first_card = True
                                                primary_player.attachments_at_planet[planet_pos][attachment_pos]. \
                                                    defense_battery_activated = False

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
                        await self.send_update_message(self.p1.name_player + " finished mobile")

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
                                self.unit_to_move_position = [-1, -1]
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if int(game_update_string[1]) == int(primary_player.number):
                            self.unit_to_move_position[0] = int(game_update_string[2])
                            self.unit_to_move_position[1] = int(game_update_string[3])
                            primary_player.set_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                      self.unit_to_move_position[1], "blue")
        else:
            if name == secondary_player.name_player:
                if len(game_update_string) == 1:
                    if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                        secondary_player.mobile_resolved = True
                        self.unit_to_move_position = [-1, -1]
                        await self.send_update_message(self.p1.name_player + " finished mobile")
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
                                self.unit_to_move_position = [-1, -1]
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if int(game_update_string[1]) == int(secondary_player.number):
                            self.unit_to_move_position[0] = int(game_update_string[2])
                            self.unit_to_move_position[1] = int(game_update_string[3])
                            secondary_player.set_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                        self.unit_to_move_position[1], "blue")
        if primary_player.mobile_resolved and secondary_player.mobile_resolved:
            await self.send_update_message("mobile complete")
            self.check_battle(self.round_number)
            self.last_planet_checked_for_battle = self.round_number
            self.begin_combat_round()
            self.set_battle_initiative()
            self.planet_aiming_reticle_active = True
            self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
            self.p1.has_passed = False
            self.p2.has_passed = False

    async def apply_indirect_damage(self, name, game_update_string):
        if name == self.name_1 or name == self.name_2:
            if name == self.name_1:
                player = self.p1
            else:
                player = self.p2
            if player.indirect_damage_applied < player.total_indirect_damage:
                if len(game_update_string) == 1:
                    if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                        player.indirect_damage_applied = 999
                        await self.send_update_message(
                            player.name_player + " stops placing indirect damage"
                        )
                if self.location_of_indirect == "HQ" or self.location_of_indirect == "ALL":
                    if len(game_update_string) == 3:
                        if game_update_string[0] == "HQ":
                            if game_update_string[1] == player.get_number():
                                if player.get_card_type_given_pos(-2, int(game_update_string[2])) in \
                                        self.valid_targets_for_indirect:
                                    if player.get_faction_given_pos(
                                            -2, int(game_update_string[2])) == \
                                            self.faction_of_cards_for_indirect or not \
                                            self.faction_of_cards_for_indirect:
                                        player.increase_indirect_damage_at_pos(-2, int(game_update_string[2]), 1)
                if (self.location_of_indirect == "PLANET" and self.planet_of_indirect == int(game_update_string[2])) \
                        or self.location_of_indirect == "ALL":
                    if len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            if game_update_string[1] == player.get_number():
                                if player.get_card_type_given_pos(
                                        int(game_update_string[2]), int(game_update_string[3])) \
                                        in self.valid_targets_for_indirect:
                                    if player.get_faction_given_pos(
                                            int(game_update_string[2]), int(game_update_string[3])) == \
                                            self.faction_of_cards_for_indirect or not \
                                            self.faction_of_cards_for_indirect:
                                        player.increase_indirect_damage_at_pos(int(game_update_string[2]),
                                                                               int(game_update_string[3]), 1)
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
        print("Resolving effect")
        if name == self.player_resolving_effect[0]:
            print("name check ok")
            if self.effects_waiting_on_resolution[0] == "Reanimating Warriors":
                print("reanimating warriors")
                if not self.asked_if_resolve_effect:
                    self.choices_available = ["Yes", "No"]
                    self.choice_context = "Use Reanimating Warriors?"
                    self.name_player_making_choices = name
                else:
                    if len(game_update_string) == 2 and self.chosen_first_card:
                        print("planets")
                        if game_update_string[0] == "PLANETS":
                            print("planets 2")
                            origin_planet, origin_pos = self.misc_target_unit
                            target_planet = int(game_update_string[1])
                            if abs(origin_planet - target_planet) == 1:
                                primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                                primary_player.move_unit_to_planet(origin_planet, origin_pos, target_planet)
                                del self.effects_waiting_on_resolution[0]
                                del self.player_resolving_effect[0]
                                self.asked_if_resolve_effect = False
                                self.chosen_first_card = False
                    elif len(game_update_string) == 4 and not self.chosen_first_card:
                        print("in play")
                        if game_update_string[0] == "IN_PLAY":
                            print("in play 2")
                            if game_update_string[1] == primary_player.number:
                                print("in play 3")
                                planet_pos = int(game_update_string[2])
                                unit_pos = int(game_update_string[3])
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == \
                                        "Reanimating Warriors" \
                                        and not primary_player.cards_in_play[planet_pos + 1][unit_pos] \
                                        .once_per_phase_used:
                                    if primary_player.check_damage_too_great_given_pos(planet_pos, unit_pos) == 0:
                                        self.chosen_first_card = True
                                        self.misc_target_unit = (planet_pos, unit_pos)
                                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                                        primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            elif self.effects_waiting_on_resolution[0] == "Commander Shadowsun":
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
                                else:
                                    await self.send_update_message("Invalid target")
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
                                else:
                                    await self.send_update_message("Invalid target")
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
                                    if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos]. \
                                            get_card_type() != "Warlord":
                                        if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos] \
                                                .check_for_a_trait("Warrior") or \
                                                primary_player.cards_in_play[sac_planet_pos + 1][unit_pos] \
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
                                primary_player.discard_card_name_from_hand("No Mercy")
                                del self.effects_waiting_on_resolution[0]
                                del self.player_resolving_effect[0]
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
                                primary_player.discard_card_name_from_hand("No Mercy")
                                del self.effects_waiting_on_resolution[0]
                                del self.player_resolving_effect[0]
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
                    """
                    self.choice_context = "Use The Fury of Sicarius?"
                    self.choices_available = ["Yes", "No"]
                    self.name_player_making_choices = player_with_cato.name_player
                    """
                    self.furiable_unit_position = (self.recently_damaged_units[0][1],
                                                   self.recently_damaged_units[0][2])
                    return True
        return False

    def delete_reaction(self):
        if self.reactions_needing_resolving:
            self.asking_which_reaction = True
            self.already_resolving_reaction = False
            self.last_player_who_resolved_reaction = self.player_who_resolves_reaction[0]
            del self.reactions_needing_resolving[0]
            del self.player_who_resolves_reaction[0]
            del self.positions_of_unit_triggering_reaction[0]
        if not self.reactions_needing_resolving:
            self.p1.reset_defense_batteries()
            self.p2.reset_defense_batteries()

    async def shield_cleanup(self, primary_player, secondary_player, planet_pos):
        if self.positions_attackers_of_units_to_take_damage[0] is not None:
            player_num, planet_pos, unit_pos = self.positions_attackers_of_units_to_take_damage[0]
            if player_num == 1:
                self.p1.reset_aiming_reticle_in_play(planet_pos, unit_pos)
            elif player_num == 2:
                self.p2.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        del self.positions_of_units_to_take_damage[0]
        del self.damage_on_units_list_before_new_damage[0]
        del self.positions_attackers_of_units_to_take_damage[0]
        del self.damage_can_be_shielded[0]
        self.damage_moved_to_old_one_eye = 0
        if self.positions_of_units_to_take_damage:
            self.advance_damage_aiming_reticle()
        else:
            if self.damage_from_attack:
                self.clear_attacker_aiming_reticle()
            print(self.recently_damaged_units)
            print(self.damage_taken_was_from_attack)
            print(self.positions_of_attacker_of_unit_that_took_damage)
            print(self.faction_of_attacker)
            print(self.on_kill_effects_of_attacker)
            sources_extra_on_damage, player_names = self.extra_damage_possible()
            if sources_extra_on_damage:
                sources_extra_on_damage.append("None")
                self.choices_available = sources_extra_on_damage
                self.auto_card_destruction = False
                self.choice_context = "Use an extra source of damage?"
                self.name_player_making_choices = player_names[0]
                """
                self.choice_context = "Use The Fury of Sicarius?"
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = player_with_cato.name_player
                """
            else:
                await self.destroy_check_all_cards()

    def extra_damage_possible(self):
        print("\nCALLING EXTRA DAMAGE\n")
        sources = []
        valid_players = []
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
                        if "The Fury of Sicarius" not in sources:
                            sources.append("The Fury of Sicarius")
                            valid_players.append(player_with_cato.name_player)
        return sources, valid_players

    async def update_reactions(self, name, game_update_string, count=0):
        if count < 10:
            print(self.already_resolving_reaction)
            print(self.resolving_search_box)
            print(self.effects_waiting_on_resolution)
            if self.reactions_needing_resolving and not self.already_resolving_reaction and not \
                    self.resolving_search_box and not self.effects_waiting_on_resolution \
                    and not self.positions_of_units_to_take_damage:
                p_one_count, p_two_count = self.count_number_reactions_for_each_player()
                print("p_one count: ", p_one_count, "p_two count: ", p_two_count)
                if (self.player_with_initiative == self.name_1 and p_one_count > 0 and
                    self.last_player_who_resolved_reaction != self.name_1) or \
                        (p_one_count > 0 and p_two_count == 0):
                    print("\n\nREACTION UPDATE P1\n\n")
                    self.stored_reaction_indexes = self.get_positions_of_players_reactions(self.name_1)
                    if p_one_count > 1:

                        if self.asking_which_reaction:
                            self.choices_available = self.get_name_reactions_of_players_reactions(self.name_1)
                            self.choice_context = "Choose Which Reaction"
                            self.name_player_making_choices = self.name_1
                        elif not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = self.reactions_needing_resolving[0]
                            self.name_player_making_choices = self.player_who_resolves_reaction[0]
                            self.asking_if_reaction = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_reaction = True
                            await StartReaction.start_resolving_reaction(self, name, game_update_string)
                    else:
                        reaction_pos = self.stored_reaction_indexes[0]
                        self.move_reaction_to_front(reaction_pos)
                        self.asking_which_reaction = False
                        if not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = self.reactions_needing_resolving[0]
                            self.name_player_making_choices = self.player_who_resolves_reaction[0]
                            self.asking_if_reaction = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_reaction = True
                            await StartReaction.start_resolving_reaction(self, name, game_update_string)
                else:
                    self.stored_reaction_indexes = self.get_positions_of_players_reactions(self.name_2)
                    if p_two_count > 1:
                        if self.asking_which_reaction:
                            self.choices_available = self.get_name_reactions_of_players_reactions(self.name_2)
                            self.choice_context = "Choose Which Reaction"
                            self.name_player_making_choices = self.name_2
                        elif not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = self.reactions_needing_resolving[0]
                            self.name_player_making_choices = self.player_who_resolves_reaction[0]
                            self.asking_if_reaction = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_reaction = True
                            await StartReaction.start_resolving_reaction(self, name, game_update_string)
                    else:
                        reaction_pos = self.stored_reaction_indexes[0]
                        self.move_reaction_to_front(reaction_pos)
                        self.asking_which_reaction = False
                        if not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = self.reactions_needing_resolving[0]
                            self.name_player_making_choices = self.player_who_resolves_reaction[0]
                            self.asking_if_reaction = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_reaction = True
                            await StartReaction.start_resolving_reaction(self, name, game_update_string)

    async def resolve_manual_bodyguard(self, name, game_update_string):
        if name == self.name_player_manual_bodyguard:
            if name == self.name_1:
                player = self.p1
                other_play = self.p2
            else:
                player = self.p2
                other_play = self.p1
            if len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if game_update_string[1] == player.number:
                        if int(game_update_string[2]) == self.planet_bodyguard:
                            selected_unit = int(game_update_string[3])
                            if selected_unit in self.body_guard_positions:
                                player.assign_damage_to_pos(self.planet_bodyguard, selected_unit,
                                                            1, is_reassign=True, can_shield=False)
                                self.body_guard_positions.remove(selected_unit)
                                self.damage_bodyguard -= 1
                                await self.send_update_message(
                                    "Resolved a Bodyguard. Damage left to resolve: " + str(self.damage_bodyguard)
                                )
                                if self.damage_bodyguard <= 0:
                                    self.manual_bodyguard_resolution = False
                                    self.body_guard_positions = []
                                    self.name_player_manual_bodyguard = ""
                                    await self.send_update_message(
                                        "Manual Bodyguard resolution completed."
                                    )
                                    other_play.reset_all_aiming_reticles_play_hq()
                                    self.planet_bodyguard = -1

    async def nullification_unit(self, name, game_update_string):
        if self.name_player_using_nullify == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if name == self.name_player_using_nullify:
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    await self.complete_nullify()
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    if primary_player.number == game_update_string[1]:
                        if primary_player.valid_nullify_unit(-2, int(game_update_string[2])):
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            primary_player.num_nullify_played += 1
                            self.nullify_count += 1
                            if secondary_player.nullify_check():
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                await self.send_update_message(secondary_player.name_player +
                                                               " counter nullify offered.")
                            else:
                                await self.complete_nullify()
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if primary_player.number == game_update_string[1]:
                        if primary_player.valid_nullify_unit(int(game_update_string[2]), int(game_update_string[3])):
                            primary_player.exhaust_given_pos(int(game_update_string[2]), int(game_update_string[3]))
                            primary_player.num_nullify_played += 1
                            self.nullify_count += 1
                            if secondary_player.nullify_check():
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                await self.send_update_message(secondary_player.name_player +
                                                               " counter nullify offered.")
                            else:
                                await self.complete_nullify()

    async def consumption_resolution(self, name, game_update_string):
        if len(game_update_string) == 1:
            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                if name == self.name_1:
                    self.p1.consumption_sacs_list = [True, True, True, True, True, True, True]
                    await self.send_update_message(
                        self.name_2 + " stops sacrificing units for consumption."
                    )
                elif name == self.name_2:
                    self.p2.consumption_sacs_list = [True, True, True, True, True, True, True]
                    await self.send_update_message(
                        self.name_1 + " stops sacrificing units for consumption."
                    )
        if len(game_update_string) == 4:
            if name == self.name_1 and game_update_string[1] == "1":
                if not self.p1.consumption_sacs_list[int(game_update_string[2])]:
                    if self.p1.sacrifice_card_in_play(int(game_update_string[2]), int(game_update_string[3])):
                        self.p1.consumption_sacs_list[int(game_update_string[2])] = True
            elif name == self.name_2 and game_update_string[1] == "2":
                if not self.p2.consumption_sacs_list[int(game_update_string[2])]:
                    if self.p2.sacrifice_card_in_play(int(game_update_string[2]), int(game_update_string[3])):
                        self.p2.consumption_sacs_list[int(game_update_string[2])] = True
        if self.p1.consumption_sacs_list == [True, True, True, True, True, True, True] and \
                self.p2.consumption_sacs_list == [True, True, True, True, True, True, True]:
            self.resolving_consumption = False
            await self.send_update_message("Consumption Finished")
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            if self.player_with_deploy_turn == self.name_1:
                self.player_with_deploy_turn = self.name_2
                self.number_with_deploy_turn = "2"
            elif self.player_with_deploy_turn == self.name_2:
                self.player_with_deploy_turn = self.name_1
                self.number_with_deploy_turn = "1"

    def check_end_kugath_nurglings(self):
        for i in range(7):
            for j in range(len(self.p1.cards_in_play[i + 1])):
                if self.p1.cards_in_play[i + 1][j].valid_kugath_nurgling_target:
                    if self.p1.cards_in_play[i + 1][j].damage_from_kugath_nurgling < \
                            self.calc_kugath_nurgling_triggers_at_planet(i):
                        return False
            for j in range(len(self.p2.cards_in_play[i + 1])):
                if self.p2.cards_in_play[i + 1][j].valid_kugath_nurgling_target:
                    if self.p2.cards_in_play[i + 1][j].damage_from_kugath_nurgling < \
                            self.calc_kugath_nurgling_triggers_at_planet(i):
                        return False
        self.reset_all_valid_targets_kugath_nurglings()
        return True

    def calc_kugath_nurgling_triggers_at_planet(self, i):
        nurg_count = 0
        nurg_count += self.p1.count_copies_at_planet(i, "Ku'gath's Nurglings", ability=True)
        nurg_count += self.p2.count_copies_at_planet(i, "Ku'gath's Nurglings", ability=True)
        self.kugath_nurglings_present_at_planets[i] = nurg_count
        return nurg_count

    async def resolution_of_kugath_nurglings(self, name, game_update_string):
        if self.p1.has_initiative:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if name == primary_player.name_player:
            if len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    num = int(game_update_string[1])
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    if num == 1:
                        if self.p1.cards_in_play[planet_pos + 1][unit_pos].valid_kugath_nurgling_target:
                            if self.p1.cards_in_play[planet_pos + 1][unit_pos].damage_from_kugath_nurgling < \
                                    self.calc_kugath_nurgling_triggers_at_planet(planet_pos):
                                self.p1.cards_in_play[planet_pos + 1][unit_pos].damage_from_kugath_nurgling += 1
                                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 1)
                    else:
                        if self.p2.cards_in_play[planet_pos + 1][unit_pos].valid_kugath_nurgling_target:
                            if self.p2.cards_in_play[planet_pos + 1][unit_pos].damage_from_kugath_nurgling < \
                                    self.calc_kugath_nurgling_triggers_at_planet(planet_pos):
                                self.p2.cards_in_play[planet_pos + 1][unit_pos].damage_from_kugath_nurgling += 1
                                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 1)

    def set_targeting_icons_kugath_nurglings(self):
        for i in range(7):
            for j in range(len(self.p1.cards_in_play[i + 1])):
                if self.p1.cards_in_play[i + 1][j].valid_kugath_nurgling_target:
                    if self.p1.cards_in_play[i + 1][j].damage_from_kugath_nurgling < \
                            self.calc_kugath_nurgling_triggers_at_planet(i):
                        self.p1.set_aiming_reticle_in_play(i, j, "blue")
            for j in range(len(self.p2.cards_in_play[i + 1])):
                if self.p2.cards_in_play[i + 1][j].valid_kugath_nurgling_target:
                    if self.p2.cards_in_play[i + 1][j].damage_from_kugath_nurgling < \
                            self.calc_kugath_nurgling_triggers_at_planet(i):
                        self.p2.set_aiming_reticle_in_play(i, j, "blue")

    def reset_all_valid_targets_kugath_nurglings(self):
        self.resolving_kugath_nurglings = False
        for i in range(7):
            for j in range(len(self.p1.cards_in_play[i + 1])):
                self.p1.cards_in_play[i + 1][j].valid_kugath_nurgling_target = False
                self.p1.cards_in_play[i + 1][j].damage_from_kugath_nurgling = 0
            for j in range(len(self.p2.cards_in_play[i + 1])):
                self.p2.cards_in_play[i + 1][j].valid_kugath_nurgling_target = False
                self.p2.cards_in_play[i + 1][j].damage_from_kugath_nurgling = 0

    async def update_game_event(self, name, game_update_string, same_thread=False):
        if not same_thread:
            self.condition_main_game.acquire()
        resolved_subroutine = False
        print(game_update_string)
        if self.phase == "SETUP":
            await self.send_update_message("Buttons can't be pressed in setup")
        elif self.validate_received_game_string(game_update_string):
            print("String validated as ok")
            if self.choosing_unit_for_nullify:
                await self.nullification_unit(name, game_update_string)
            if self.resolving_consumption:
                await self.consumption_resolution(name, game_update_string)
            elif self.manual_bodyguard_resolution:
                await self.resolve_manual_bodyguard(name, game_update_string)
            elif self.cards_in_search_box:
                await self.resolve_card_in_search_box(name, game_update_string)
            elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
                await self.apply_indirect_damage(name, game_update_string)
            elif self.mode == "DISCOUNT":
                await self.update_game_event_applying_discounts(name, game_update_string)
            elif self.choices_available:
                print("Need to resolve a choice")
                await self.resolve_choice(name, game_update_string)
            elif self.effects_waiting_on_resolution:
                await self.resolve_effect(name, game_update_string)
            elif self.positions_of_units_to_take_damage:
                print("Using better shield mechanism")
                await self.better_shield_card_resolution(name, game_update_string)
            elif self.resolving_kugath_nurglings:
                await self.resolution_of_kugath_nurglings(name, game_update_string)
            elif self.reactions_needing_resolving:
                print("Resolve reaction")
                print(self.reactions_needing_resolving[0])
                await self.resolve_reaction(name, game_update_string)
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
            elif self.phase == "HEADQUARTERS":
                await HeadquartersPhase.update_game_event_headquarters_section(self, name, game_update_string)
            resolved_subroutine = True
        if self.phase == "DEPLOY":
            if self.p1.has_passed and self.p2.has_passed:
                print("Both passed, move to warlord movement.")
                await self.change_phase("COMMAND")
        if self.resolving_kugath_nurglings:
            if self.check_end_kugath_nurglings():
                await self.send_update_message("Leaving Ku'gath Nurglings")
        if self.just_moved_units:
            self.just_moved_units = False
            if self.p1.search_for_card_everywhere("Ku'gath's Nurglings") or \
                    self.p2.search_for_card_everywhere("Ku'gath's Nurglings"):
                self.kugath_nurglings_present_at_planets = [0, 0, 0, 0, 0, 0, 0]
                for i in range(7):
                    self.calc_kugath_nurgling_triggers_at_planet(i)
                if not all(x == 0 for x in self.kugath_nurglings_present_at_planets):
                    self.resolving_kugath_nurglings = True
                    await self.send_update_message(
                        "Ku'gath's Nurglings firing against a moved unit. Proceeding to Ku'gath's Nurglings mode."
                    )
                    self.set_targeting_icons_kugath_nurglings()
                else:
                    self.reset_all_valid_targets_kugath_nurglings()
            else:
                self.reset_all_valid_targets_kugath_nurglings()
        await self.update_reactions(name, game_update_string)
        await self.update_reactions(name, game_update_string)
        if not self.reactions_needing_resolving:
            self.last_player_who_resolved_reaction = ""
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
        if self.resolve_destruction_checks_after_reactions:
            if not self.reactions_needing_resolving and not self.positions_of_units_to_take_damage:
                if self.auto_card_destruction:
                    self.resolve_destruction_checks_after_reactions = False
                    await self.destroy_check_all_cards()
        if not self.resolve_destruction_checks_after_reactions and not self.positions_of_units_to_take_damage and \
                not self.reactions_needing_resolving and not self.effects_waiting_on_resolution \
                and not self.choices_available and self.p1.mobile_resolved and self.p2.mobile_resolved and \
                self.mode == "Normal":
            if self.need_to_reset_tomb_blade_squadron:
                self.need_to_reset_tomb_blade_squadron = False
                self.p1.reset_card_name_misc_ability("Tomb Blade Squadron")
                self.p2.reset_card_name_misc_ability("Tomb Blade Squadron")
            if self.need_to_move_to_hq:
                self.p1.ethereal_movement_resolution()
                self.p2.ethereal_movement_resolution()
                self.need_to_move_to_hq = False
                self.unit_will_move_after_attack = False
            if self.auto_card_destruction:
                await self.destroy_check_all_cards()
        if self.reset_resolving_attack_on_units:
            self.reset_resolving_attack_on_units = False
        print("---\nDEBUG INFO\n---")
        print(self.reactions_needing_resolving)
        print(self.choices_available)
        if self.phase == "DEPLOY":
            if self.number_with_deploy_turn == "1":
                if self.p1.has_passed:
                    self.number_with_deploy_turn = "2"
                    self.player_with_deploy_turn = self.name_2
            elif self.number_with_deploy_turn == "2":
                if self.p2.has_passed:
                    self.number_with_deploy_turn = "1"
                    self.player_with_deploy_turn = self.name_1
        await self.send_search()
        await self.send_info_box()
        await self.p1.send_units_at_all_planets()
        await self.p1.send_hq()
        await self.p1.send_hand()
        await self.p1.send_discard()
        await self.p1.send_resources()
        await self.p2.send_units_at_all_planets()
        await self.p2.send_hq()
        await self.p2.send_hand()
        await self.p2.send_discard()
        await self.p2.send_resources()
        await self.send_planet_array()
        if not same_thread:
            self.condition_main_game.notify_all()
            self.condition_main_game.release()

    def get_name_reactions_of_players_reactions(self, name):
        reaction_positions_list = []
        for i in range(len(self.reactions_needing_resolving)):
            if self.player_who_resolves_reaction[i] == name:
                reaction_positions_list.append(self.reactions_needing_resolving[i])
        return reaction_positions_list

    def get_positions_of_players_reactions(self, name):
        reaction_positions_list = []
        for i in range(len(self.reactions_needing_resolving)):
            if self.player_who_resolves_reaction[i] == name:
                reaction_positions_list.append(i)
        return reaction_positions_list

    def count_number_reactions_for_each_player(self):
        count_1 = 0
        count_2 = 0
        for i in range(len(self.reactions_needing_resolving)):
            if self.player_who_resolves_reaction[i] == self.name_1:
                count_1 += 1
            else:
                count_2 += 1
        return count_1, count_2

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
        if self.infested_planets[self.last_planet_checked_for_battle] and \
                self.last_planet_checked_for_battle != self.round_number and not self.already_asked_remove_infestation \
                and winner.warlord_faction != "Tyranids":
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Remove Infestation?"
            self.asking_if_remove_infested_planet = True
            self.name_player_making_choices = winner.name_player
            await self.send_update_message(
                winner.name_player + " has the right to clear infestation from " + planet_name)
        else:
            self.already_asked_remove_infestation = False
            print("Resolve battle ability of:", planet_name)
            self.need_to_resolve_battle_ability = True
            self.battle_ability_to_resolve = planet_name
            self.player_resolving_battle_ability = winner.name_player
            self.number_resolving_battle_ability = str(winner.number)
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Resolve Battle Ability?"
            self.name_player_making_choices = winner.name_player
            await self.send_update_message(winner.name_player + " has the right to use"
                                                                " the battle ability of " + planet_name)
            if not self.need_to_resolve_battle_ability:
                if self.round_number == self.last_planet_checked_for_battle:
                    winner.move_all_at_planet_to_hq(self.last_planet_checked_for_battle)
                    winner.capture_planet(self.last_planet_checked_for_battle,
                                          self.planet_cards_array)
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                    await winner.send_victory_display()

    async def check_combat_end(self, name):
        self.combat_reset_eocr_values()
        p1_has_units = self.p1.check_if_units_present(self.last_planet_checked_for_battle)
        p2_has_units = self.p2.check_if_units_present(self.last_planet_checked_for_battle)
        if p1_has_units and p2_has_units:
            pass
        else:
            if p1_has_units:
                await self.resolve_winning_combat(self.p1, self.p2)
            if p2_has_units:
                await self.resolve_winning_combat(self.p2, self.p1)
            if not p1_has_units and not p2_has_units:
                if self.round_number == self.last_planet_checked_for_battle:
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                await self.resolve_battle_conclusion(name, ["", ""])

    def create_reaction(self, reaction_name, player_name, unit_tuple):
        self.reactions_needing_resolving.append(reaction_name)
        self.player_who_resolves_reaction.append(player_name)
        self.positions_of_unit_triggering_reaction.append(unit_tuple)

    def begin_combat_round(self):
        self.bloodthirst_active = [False, False, False, False, False, False, False]
        self.p1.resolve_combat_round_begins(self.last_planet_checked_for_battle)
        self.p2.resolve_combat_round_begins(self.last_planet_checked_for_battle)

    def take_control_of_card(self, primary_player, secondary_player, planet_pos, unit_pos):
        if planet_pos == -2:
            primary_player.headquarters.append(secondary_player.headquarters[unit_pos])
            del secondary_player.headquarters[unit_pos]
            return None
        primary_player.cards_in_play[planet_pos + 1].append(secondary_player.cards_in_play[planet_pos + 1][unit_pos])
        del secondary_player.cards_in_play[planet_pos + 1][unit_pos]
        return None

    def reset_values_for_new_round(self):
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.mode = "Normal"
        self.p1.round_ends_reset_values()
        self.p2.round_ends_reset_values()
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
        self.p1.used_reanimation_protocol = False
        self.p2.used_reanimation_protocol = False
        self.p1.draw_card()
        self.p1.draw_card()
        self.p2.draw_card()
        self.p2.draw_card()
        self.p1.retreat_warlord()
        self.p2.retreat_warlord()
        self.p1.move_synapse_to_hq()
        self.p2.move_synapse_to_hq()
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
        self.p1.refresh_all_once_per_round()
        self.p2.refresh_all_once_per_round()
        if self.round_number == 0:
            self.planets_in_play_array[5] = True
        elif self.round_number == 1:
            self.planets_in_play_array[6] = True
        self.round_number += 1
        if self.round_number > 6:
            self.phase = "FIN/IF WINNER UNDECIDED,/PLAYER WHO WON LAST/BATTLE IS THE WINNER/GO HOME."
        self.swap_initiative()

    def swap_initiative(self):
        if self.player_with_initiative == self.name_1:
            self.player_with_initiative = self.name_2
            self.number_with_initiative = "2"
        else:
            self.player_with_initiative = self.name_1
            self.number_with_initiative = "1"

    def begin_battle(self, planet_pos):
        self.last_planet_checked_for_battle = planet_pos
        self.p1.resolve_battle_begins(planet_pos)
        self.p2.resolve_battle_begins(planet_pos)

    def find_next_planet_for_combat(self):
        i = self.last_planet_checked_for_battle + 1
        while i < len(self.planet_array):
            if self.planets_in_play_array[i]:
                p1_has_warlord = self.p1.check_for_warlord(i)
                p2_has_warlord = self.p2.check_for_warlord(i)
                if not p1_has_warlord and not p2_has_warlord:
                    p1_has_warlord = self.p1.check_savage_warrior_prime_present(i)
                    p2_has_warlord = self.p2.check_savage_warrior_prime_present(i)
                if p1_has_warlord or p2_has_warlord:
                    self.begin_battle(i)
                    self.begin_combat_round()
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
        if not self.p1_has_warlord and not self.p2_has_warlord:
            self.p1_has_warlord = self.p1.check_savage_warrior_prime_present(self.last_planet_checked_for_battle)
            self.p2_has_warlord = self.p2.check_savage_warrior_prime_present(self.last_planet_checked_for_battle)
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
        elif self.p1.check_savage_warrior_prime_present(planet_id):
            print("p1 warlord present. Battle at ", planet_id)
            self.ranged_skirmish_active = True
            return 1
        elif self.p2.check_savage_warrior_prime_present(planet_id):
            print("p2 warlord present. Battle at ", planet_id)
            self.ranged_skirmish_active = True
            return 1
        return 0
