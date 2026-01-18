import copy
from . import PlayerClass
import random
from .Phases import DeployPhase, CommandPhase, CombatPhase, HeadquartersPhase, PlanetBattleAbilities
from . import FindCard
import threading
from .Actions import AttachmentHQActions, AttachmentInPlayActions, HandActions, HQActions, \
    InPlayActions, PlanetActions, DiscardActions
from .Reactions import StartReaction, PlanetsReaction, HandReaction, HQReaction, InPlayReaction, DiscardReaction, \
    AttachmentInPlayReaction, AttachmentHQReaction
from .Interrupts import StartInterrupt, InPlayInterrupts, PlanetInterrupts, HQInterrupts, HandInterrupts, \
    AttachmentHQInterrupts, AttachmentInPlayInterrupts
from .Intercept import InPlayIntercept, HQIntercept
from . import CardClasses
import os


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
    def __init__(self, game_id, player_one_name, player_two_name, card_array, planet_array, cards_dict, apoka,
                 apoka_errata_cards, sector="Traxis", deck_1="", deck_2="", forced_planet_array=None):
        self.game_sockets = []
        self.card_array = card_array
        self.cards_dict = cards_dict
        self.apoka_errata_cards = apoka_errata_cards
        self.cards_that_have_errata = []
        for i in range(len(self.apoka_errata_cards)):
            self.cards_that_have_errata.append(self.apoka_errata_cards[i].get_name())
        self.planet_cards_array = planet_array
        self.apoka = apoka
        self.battle_in_progress = False
        self.game_id = game_id
        self.name_1 = player_one_name
        self.name_2 = player_two_name
        self.current_game_event_p1 = ""
        self.damage_is_taken_one_at_a_time = True
        self.current_game_event_p1 = ""
        self.stored_deck_1 = None
        self.stored_deck_2 = None
        self.units_immune_to_aoe = ["Undying Saint", "Dodging Land Speeder", "Sanctified Aggressor",
                                    "Incubus of the Severed", "Lurking Termagant"]
        self.attack_being_resolved = False
        self.attack_resolution_cleanup = False
        self.p1 = PlayerClass.Player(player_one_name, 1, card_array, cards_dict, apoka_errata_cards, self)
        self.p2 = PlayerClass.Player(player_two_name, 2, card_array, cards_dict, apoka_errata_cards, self)
        self.phase = "SETUP"
        self.round_number = 0
        self.current_board_state = ""
        self.running = True
        self.planet_array = []
        self.sector = sector
        self.cult_duplicity_available = True
        self.forced_battle_abilities = []
        self.atrox_origin = -1
        regular_planets_setup = True
        if forced_planet_array is not None:
            if len(forced_planet_array) == 7:
                for i in range(len(forced_planet_array)):
                    planet_card_exists = FindCard.check_if_planet_exists(forced_planet_array[i], planet_array)
                    if planet_card_exists:
                        if forced_planet_array[i] not in self.planet_array:
                            self.planet_array.append(forced_planet_array[i])
            if len(self.planet_array) == 7:
                regular_planets_setup = False
            else:
                self.planet_array = []
        if regular_planets_setup:
            if sector == "Traxis":
                for i in range(10):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
            elif sector == "Gardis":
                for i in range(10, 20):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
            elif sector == "Veros":
                for i in range(20, 30):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
            elif sector == "The Breach":
                for i in range(30, 40):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
            elif sector == "Nepthis":
                for i in range(40, 50):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
            elif sector == "Sargos":
                for i in range(50, 60):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
            else:
                for i in range(10):
                    self.planet_array.append(self.planet_cards_array[i].get_name())
        for i in range(40, 50):
            self.forced_battle_abilities.append(self.planet_cards_array[i].get_name())
        self.available_breach_planets = []
        for i in range(30, 40):
            self.available_breach_planets.append(self.planet_cards_array[i].get_name())
        if not forced_planet_array:
            random.shuffle(self.planet_array)
        self.planets_removed_from_game = copy.deepcopy(self.planet_array[-3:])
        self.planet_array = self.planet_array[:7]
        self.original_planet_array = copy.deepcopy(self.planet_array)
        self.planets_in_play_array = [True, True, True, True, True, False, False]
        self.replaced_planets = [False, False, False, False, False, False, False]
        self.bloodthirst_active = [False, False, False, False, False, False, False]
        self.player_with_deploy_turn = self.name_1
        self.number_with_deploy_turn = "1"
        self.card_pos_to_deploy = -1
        self.planet_pos_to_deploy = -1
        self.all_traits = []
        self.most_recently_revealed_planet = -1
        self.sweep_active = False
        for i in range(len(self.card_array)):
            card = self.preloaded_find_card(self.card_array[i].get_name())
            traits = card.get_traits()
            traits = traits.split(".")
            for trait in traits:
                done_trimming = False
                while not done_trimming:
                    if len(trait) == 0:
                        done_trimming = True
                    elif trait[0] == " ":
                        trait = trait[1:]
                    else:
                        done_trimming = True
                if trait not in self.all_traits and trait:
                    self.all_traits.append(trait)
        self.last_planet_checked_for_battle = -1
        self.number_with_combat_turn = "1"
        self.herald_of_the_waagh_active = False
        self.player_with_combat_turn = self.name_1
        self.attacker_planet = -1
        self.attacker_position = -1
        self.defender_planet = -1
        self.defender_position = -1
        self.p1_has_warlord = False
        self.p2_has_warlord = False
        self.allow_damage_abilities_defender = True
        self.damage_abilities_defender_active = False
        self.number_with_initiative = "1"
        self.player_with_initiative = self.name_1
        self.number_reset_combat_turn = "1"
        self.player_reset_combat_turn = self.name_1
        self.number_who_is_shielding = None
        self.player_who_is_shielding = None
        self.planet_of_damaged_unit = None
        self.position_of_damaged_unit = None
        self.discard_fully_prevented = False
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
        self.interrupting_discard_effect_active = False
        self.actions_allowed = True
        self.storm_of_silence_friendly_unit = True
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
        self.attachment_deployed_flag = False
        self.damage_left_to_take = 0
        self.goliath_rockgrinder_value = 0
        self.may_use_faith = True
        self.may_use_retaliate = True
        self.positions_of_units_hq_to_take_damage = []
        self.positions_of_units_to_take_damage = []  # Format: (player_num, planet_num, unit_pos)
        self.positions_attackers_of_units_to_take_damage = []  # Format: (player_num, planet_num, unit_pos) or None
        self.damage_is_preventable = []
        self.card_names_triggering_damage = []
        self.damage_can_be_shielded = []
        self.amount_that_can_be_removed_by_shield = []
        self.card_type_of_selected_card_in_hand = ""
        self.cards_in_search_box = []
        self.name_player_who_is_searching = ""
        self.number_who_is_searching = "1"
        self.what_to_do_with_searched_card = "DRAW"
        self.shuffle_after = False
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
        self.ghost_ark_of_orikan = -1
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
        self.additional_reactions_info = []
        self.delayed_reactions_needing_resolving = []
        self.delayed_positions_of_unit_triggering_reaction = []
        self.delayed_player_who_resolves_reaction = []
        self.delayed_additional_reactions_info = []
        self.misc_counter = 0
        self.wounded_scream_blanked = False
        self.khymera_to_move_positions = []
        self.position_of_actioned_card = (-1, -1)
        self.position_of_selected_attachment = (-1, -1, -1)
        self.active_effects = []  # Each item should be a tuple containing all relevant info
        self.chosen_first_card = False
        self.chosen_second_card = False
        self.misc_target_planet = -1
        self.misc_target_unit = (-1, -1)
        self.misc_target_unit_2 = (-1, -1)
        self.misc_target_attachment = (-1, -1, -1)
        self.misc_player_storage = ""
        self.last_defender_position = (-1, -1, -1)
        self.location_of_indirect = ""
        self.indirect_exhaust_only = False
        self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
        self.faction_of_cards_for_indirect = ""
        self.forbidden_traits_indirect = ""
        self.planet_of_indirect = -1
        self.first_card_damaged = True
        self.sweep_value = 0
        self.combat_round_number = 0
        self.cato_stronghold_activated = False
        self.allowed_planets_cato_stronghold = []
        self.allowed_units_alaitoc_shrine = []
        self.committing_warlords = False
        self.resolving_search_box = False
        self.banshee_power_sword_extra_attack = 0
        self.may_move_defender = True
        self.additional_attack_effects_allowed = True
        self.fire_warrior_elite_active = False
        self.before_command_struggle = False
        self.after_command_struggle = True
        self.amount_spend_for_tzeentch_firestorm = -1
        self.searching_enemy_deck = False
        self.bottom_cards_after_search = True
        self.shadowsun_chose_hand = True
        self.rearranging_deck = False
        self.name_player_rearranging_deck = ""
        self.deck_part_being_rearranged = []
        self.number_cards_to_rearrange = 0
        self.interrupts_waiting_on_resolution = []
        self.player_resolving_interrupts = []
        self.positions_of_units_interrupting = []
        self.extra_interrupt_info = []
        self.location_hand_attachment_shadowsun = -1
        self.name_attachment_discard_shadowsun = ""
        self.units_damaged_by_attack = []
        self.units_damaged_by_attack_from_sm = []
        self.alternative_shields = ["Indomitable", "Glorious Intervention", "Faith Denies Death", "Uphold His Honor",
                                    "Back to the Shadows", "I Do Not Serve"]
        self.last_shield_string = []
        self.pos_shield_card = -1
        self.recently_damaged_units = []
        self.damage_taken_was_from_attack = []
        self.positions_of_attacker_of_unit_that_took_damage = []
        self.faction_of_attacker = []
        self.card_names_that_caused_damage = []
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
        self.intercept_active = False
        self.name_player_intercept = ""
        self.communications_relay_enabled = True
        self.storm_of_silence_enabled = True
        self.slumbering_gardens_enabled = True
        self.colony_shield_generator_enabled = True
        self.intercept_enabled = True
        self.backlash_enabled = True
        self.bigga_is_betta_active = False
        self.last_info_box_string = ""
        self.has_chosen_to_resolve = False
        self.asking_if_reaction = False
        self.asking_if_interrupt = False
        self.already_resolving_reaction = False
        self.already_resolving_interrupt = False
        self.spray_and_pray_amounts = []
        self.last_search_string = ""
        self.last_deck_string_1 = ""
        self.last_deck_string_2 = ""
        self.asking_which_reaction = True
        self.asking_which_interrupt = True
        self.stored_reaction_indexes = []
        self.stored_interrupt_indexes = []
        self.manual_bodyguard_resolution = False
        self.name_player_manual_bodyguard = ""
        self.num_bodyguards = 0
        self.body_guard_positions = []
        self.alt_shield_mode_active = False
        self.alt_shield_name = ""
        self.damage_bodyguard = 0
        self.planet_bodyguard = -1
        self.imperial_blockades_active = [0, 0, 0, 0, 0, 0, 0]
        self.last_player_who_resolved_reaction = ""
        self.last_player_who_resolved_interrupt = ""
        self.infested_planets = [False, False, False, False, False, False, False]
        self.asking_if_remove_infested_planet = False
        self.already_asked_remove_infestation = False
        self.great_scything_talons_value = 0
        self.name_of_card_to_play = ""
        self.damage_moved_to_old_one_eye = 0
        self.old_one_eye_pos = (-1, -1)
        self.misc_target_choice = -1
        self.masters_of_the_webway = False
        self.misc_target_player = ""
        self.resolve_destruction_checks_after_reactions = False
        self.ravenous_haruspex_gain = 0
        self.reset_resolving_attack_on_units = False
        self.resolving_consumption = False
        self.stored_area_effect_value = 0
        self.area_effect_active = False
        self.max_aoe_targets = 3
        self.kaerux_erameas_active = False
        self.misc_misc = None
        self.misc_misc_2 = None
        self.different_atrox_origin = -1
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
            "Death from Above", "Kauyon Strike", "Rally the Charge", "Doombolt", "Searing Brand",
            "Tense Negotiations", "Cacophonic Choir", "Slake the Thirst", "Rakarth's Experimentations",
            "Squiggify", "The Emperor's Warrant", "For the Tau'va", "Summary Execution", "Bond of Brotherhood",
            "Sowing Chaos", "Blood For The Blood God!", "Inevitable Betrayal", "Rok Bombardment", "Mind War",
            "Mont'ka Strike", "Biomass Sacrifice", "Rapid Assault", "Eldritch Storm", "Sudden Adaptation",
            "Path of the Leader", "Bolster the Defense", "Warp Rift", "No Surprises", "A Thousand Cuts",
            "Keep Firing!", "Vivisection", "Repent!", "Ominous Wind", "Daemonic Incursion", "Piercing Wail",
            "The Siege Masters", "The Bloodied Host", "Our Last Stand", "Kwik' Konstruckshun",
            "Painboy Surjery", "Looted Skrap", "Indiscriminate Bombing", "Kommando Cunning", "Everlasting Rage",
            "Torturer of Worlds", "The Orgiastic Feast", "Supply Line Incursion", "Triumvirate of Ynnead",
            "Theater of War", "Clash of Wings", "Lost in the Webway", "Access to the Black Library",
            "Breach and Clear", "Consumed by the Kindred", "Guerrilla Tactics", "Tempting Ceasefire",
            "Daring Assault", "Behind Enemy Lines", "Overrun", "Rapid Evolution", "Accelerated Gestation",
            "Planet Absorption", "Reinforced Synaptic Network", "The Strength of the Enemy",
            "Eldritch Reaping", "Imperial Blockade"
        ]
        self.forced_reactions = ["Anxious Infantry Platoon", "Warlock Destructor", "Treacherous Lhamaean",
                                 "Sickening Helbrute", "Shard of the Deceiver", "Drifting Spore Mines",
                                 "Reinforced Synaptic Network", "Saint Erika", "Charging Juggernaut",
                                 "Mobilize the Chapter Initiation", "Trapped Objective", "Kabal of the Ebon Law",
                                 "Erida Commit", "Jaricho Commit", "Beckel Commit", "Willing Submission",
                                 "The Blinded Princess", "Champion of Khorne", "Arrogant Haemonculus",
                                 "Tras the Corrupter", "Unstoppable Tide", "Forge Master Dominus BLD",
                                 "Spray and Pray", "Grey Hunters", "Shambling Revenant", "Flayer Affliction",
                                 "Avatar of Khaine", "Aun'la Prince", "Carnifex", "Gleeful Plague Beast"]
        if self.apoka:
            self.forced_reactions.append("Syren Zythlex")
        self.anrakyr_unit_position = -1
        self.anrakyr_deck_choice = self.name_1
        self.name_of_attacked_unit = ""
        self.deploy_exhausted = False
        self.need_to_reset_tomb_blade_squadron = False
        self.resolve_kill_effects = True
        self.vamii_complex_discount = 0
        self.reactions_on_end_deploy_phase = False
        self.asked_if_resolve_effect = False
        self.card_to_deploy = None
        self.saved_planet_string = ""
        self.starmist_raiment = False
        self.dies_to_backlash = ["Sicarius's Chosen", "Captain Markis", "Burna Boyz", "Tomb Blade Squadron",
                                 "Veteran Barbrus", "Klaivex Warleader", "Rotten Plaguebearers",
                                 "Imperial Fists Siege Force", "Prodigal Sons Disciple", "Fire Prism",
                                 "Invasive Genestealers", "Kabalite Harriers", "The Emperor's Champion",
                                 "8th Company Assault Squad", "Crush of Sky-Slashers", "Vezuel's Hunters",
                                 "Mandrake Cutthroat", "Shrieking Exarch", "Mars Alpha Exterminator",
                                 "Hydrae Stalker", "Dutiful Castellan", "Frenzied Wulfen", "Inspiring Sergeant",
                                 "Pinning Razorback", "Wrathful Dreadnought", "Junk Chucka Kommando",
                                 "Patient Infiltrator", "Slave-powered Wagons", "Lekor Blight-Tongue",
                                 "Plagueburst Crawler", "Arrogant Haemonculus", "Luring Troupe", "Agnok's Shadows",
                                 "Goff Shokboyz", "Inexperienced Weirdboy", "Thundering Wraith",
                                 "Khornate Heldrake", "Incubus Cleavers", "Voidscarred Corsair",
                                 "Peacekeeper Drone", "Broadside Shas'vre", "Psychic Zoanthrope"]
        self.nullifying_backlash = False
        self.nullifying_storm_of_silence = False
        self.choosing_unit_for_nullify = False
        self.name_player_using_nullify = ""
        self.name_player_using_backlash = ""
        self.canceled_card_bonuses = [False, False, False, False, False, False, False]
        self.canceled_resource_bonuses = [False, False, False, False, False, False, False]
        self.units_move_hq_attack = ["Aun'ui Prelate", "Aun'shi", "Ethereal Envoy", "Herald of the Tau'va",
                                     "Frontline Counsellor", "Aun'la Prince", "Exertion Drone"]
        self.unit_will_move_after_attack = False
        self.need_to_move_to_hq = False
        self.just_moved_units = False
        self.resolving_kugath_nurglings = False
        self.kugath_nurglings_present_at_planets = [0, 0, 0, 0, 0, 0, 0]
        self.resolving_nurgling_bomb = False
        self.player_resolving_nurgling_bomb = ""
        self.auto_card_destruction = True
        self.card_type_defender = ""
        self.defender_is_flying_or_mobile = False
        self.defender_is_also_warlord = False
        self.valid_crushing_blow_triggers = ["Space Marines", "Sicarius's Chosen", "Veteran Barbrus",
                                             "Ragnar Blackmane", "Morkai Rune Priest"]
        self.forced_interrupts = ["Flayed Ones Revenants", "Chapter Champion Varn", "Zen Xi Aonia",
                                  "The Broken Sigil Sacrifice Unit", "Shok Troopa", "Incubus Cleavers",
                                  "Industrial Boom"]
        self.planets_free_for_know_no_fear = [True, True, True, True, True, True, True]
        self.player_using_battle_ability = ""
        self.ebon_chalice_value = 0
        self.searing_brand_cancel_enabled = True
        self.guardian_mesh_armor_enabled = True
        self.guardian_mesh_armor_active = False
        self.maksim_squadron_enabled = True
        self.distorted_talos_enabled = True
        self.distorted_talos_active = False
        self.woken_machine_spirit_enabled = False
        self.maksim_squadron_active = False
        self.woken_machine_spirit_active = False
        self.tense_negotiations_active = False
        self.theater_of_war_active = False
        self.forbidden_theater_of_war = ""
        self.shining_blade_active = False
        self.value_doom_siren = 0
        self.misc_counter_2 = 0
        self.actions_between_battle = False
        self.last_planet_checked_command_struggle = -1
        self.planet_aiming_reticle_active = True
        self.during_command_struggle = False
        self.before_command_at_planet_resolves = False
        self.during_command_at_planet_resolves = False
        self.after_command_at_planet_resolves = False
        self.interrupts_before_cs_allowed = True
        self.interrupts_during_cs_allowed = True
        self.reactions_after_cs_allowed = True
        self.name_winner_cs = ""
        self.total_gains_command_struggle = [None, None, None, None, None, None, None]
        self.resolve_remaining_cs_after_reactions = False
        self.additional_icons_planets_eop = [[], [], [], [], [], [], []]
        self.additional_icons_planets_eob = [[], [], [], [], [], [], []]
        self.reactions_on_winning_combat_being_executed = False
        self.reactions_on_winning_combat_permitted = True
        self.name_player_who_won_combat = ""
        self.damage_amounts_baarzul = []
        self.omega_ambush_active = False
        self.sanguinary_ambush_active = False
        self.shadow_thorns_body_allowed = True
        self.sacaellums_finest_active = False
        self.eldritch_council_value = 0
        self.list_reactions_on_winning_combat = ["Accept Any Challenge", "Inspirational Fervor",
                                                 "Declare the Crusade", "Gut and Pillage", "Scavenging Run"]
        self.queued_sound = ""
        self.queued_message = ""
        self.energy_weapon_sounds = ["Space Marines", "Tau", "Eldar", "Necrons", "Chaos"]
        self.gunfire_weapon_sounds = ["Astra Militarum", "Orks", "Dark Eldar", "Tyranids", "Neutral"]
        self.deepstrike_allowed = True
        self.stored_deploy_string = []
        self.deepstrike_deployment_active = False
        self.start_battle_deepstrike = False
        self.num_player_deepstriking = "1"
        self.name_player_deepstriking = self.name_1
        self.choosing_target_for_deepstruck_attachment = False
        self.deepstruck_attachment_pos = (-1, -1)
        self.xv805_enforcer_active = False
        self.asking_if_use_xv805_enforcer = False
        self.asking_amount_xv805_enforcer = False
        self.amount_xv805_enforcer = 0
        self.damage_index_xv805 = -1
        self.player_using_xv805 = ""
        self.og_pos_xv805_target = (-1, -1)
        self.liatha_available = True
        self.liatha_active = False
        self.current_card_id = 0
        self.current_flamers_id = 0
        self.current_librarian_id = 0
        self.flamers_damage_active = False
        self.id_of_the_active_flamer = -1
        self.bloodrain_tempest_active = False
        self.shrieking_exarch_cost_payed = False
        self.paying_shrieking_exarch_cost = False
        self.jungle_trench_count = 0
        self.may_block_with_ols = True
        self.cards_with_dash_cost = ["Seething Mycetic Spore", "Grand Master Belial"]
        self.stored_discard_and_target = []  # (effect name, player num)
        self.interrupts_discard_enemy_allowed = True
        self.queued_moves = []  # (player num, planet pos, unit pos, destination)
        self.sororitas_command_squad_value = 0
        self.retaliate_used = False
        self.jaricho_target = -1
        self.active_jaricho_battle = False
        self.jaricho_actual_triggered_planet = -1
        self.nectavus_active = False
        self.nectavus_target = -1
        self.nectavus_actual_current_planet = -1
        self.grand_plan_queued = []  # (planet name, target round, num getting planet, p1 planned, p2 planned)
        self.grand_plan_active = False
        self.trium_count = 0
        self.trium_tracker = ("name", -1)
        self.sent_setup_info_already = False
        self.reactions_on_destruction_permitted = True
        self.last_initiative_string = ""
        if deck_1:
            deck_name = deck_1
            path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + self.name_1 + "/" + deck_name
            if os.path.exists(path_to_player_decks):
                print("Success")
                with open(path_to_player_decks, 'r') as f:
                    deck_content = f.read()
                print(deck_content)
                self.p1.setup_player_no_send(deck_content, self.planet_array)
        if deck_2:
            deck_name = deck_2
            path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + self.name_2 + "/" + deck_name
            if os.path.exists(path_to_player_decks):
                print("Success")
                with open(path_to_player_decks, 'r') as f:
                    deck_content = f.read()
                print(deck_content)
                self.p2.setup_player_no_send(deck_content, self.planet_array)

    async def send_queued_message(self):
        if self.queued_message:
            await self.send_update_message(self.queued_message)
            self.queued_message = ""

    def safety_check(self):
        if self.choices_available:
            print("Choices are available")
            return False
        if self.amount_that_can_be_removed_by_shield:
            print("damage is being done")
            return False
        if self.reactions_needing_resolving:
            print("reactions are being done")
            return False
        if self.interrupts_waiting_on_resolution:
            print("interrupts are being done")
            return False
        if self.action_chosen:
            print("action being done")
            return False
        if self.rearranging_deck:
            print("rearranging deck")
            return False
        if self.mode != "Normal":
            print("mode is not normal")
            return False
        return True

    async def send_queued_sound(self):
        if self.queued_sound:
            print("sending sound")
            await self.send_update_message("GAME_INFO/SOUND/" + self.queued_sound)
            self.queued_sound = ""

    def get_planet_name(self, planet_pos):
        planet_card = FindCard.find_planet_card(self.planet_array[planet_pos], self.planet_cards_array)
        return planet_card.get_name()

    def get_red_icon(self, planet_pos):
        planet_card = FindCard.find_planet_card(self.planet_array[planet_pos], self.planet_cards_array)
        if planet_card.get_red():
            return True
        if "red" in self.additional_icons_planets_eop[planet_pos]:
            return True
        if "red" in self.additional_icons_planets_eob[planet_pos]:
            return True
        return False

    def get_blue_icon(self, planet_pos):
        planet_card = FindCard.find_planet_card(self.planet_array[planet_pos], self.planet_cards_array)
        if planet_card.get_blue():
            return True
        if "blue" in self.additional_icons_planets_eop[planet_pos]:
            return True
        if "blue" in self.additional_icons_planets_eob[planet_pos]:
            return True
        return False

    def get_green_icon(self, planet_pos):
        planet_card = FindCard.find_planet_card(self.planet_array[planet_pos], self.planet_cards_array)
        if planet_card.get_green():
            return True
        if "green" in self.additional_icons_planets_eop[planet_pos]:
            return True
        if "green" in self.additional_icons_planets_eob[planet_pos]:
            return True
        return False

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
        self.card_names_triggering_damage = []
        self.amount_that_can_be_removed_by_shield = []
        self.damage_can_be_shielded = []
        self.damage_is_preventable = []
        self.damage_taken_was_from_attack = []
        self.damage_from_atrox = False
        self.units_damaged_by_attack = []
        self.units_damaged_by_attack_from_sm = []
        if self.stored_mode:
            self.mode = self.stored_mode
        self.furiable_unit_position = (-1, -1)
        self.auto_card_destruction = True

    def reset_effects_data(self):
        self.already_resolving_interrupt = False
        self.interrupts_waiting_on_resolution = []
        self.player_resolving_interrupts = []
        self.positions_of_units_interrupting = []
        self.extra_interrupt_info = []
        self.active_effects = []

    def reset_reactions_data(self):
        self.reactions_needing_resolving = []
        self.player_who_resolves_reaction = []
        self.positions_of_unit_triggering_reaction = []
        self.additional_reactions_info = []
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
        elif self.interrupts_waiting_on_resolution:
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
        await self.send_decks(force=True)
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
        await self.p1.send_removed_cards(force=True)
        await self.p2.send_removed_cards(force=True)
        await self.send_info_box(force=True)
        await self.send_search(force=True)
        await self.p1.send_victory_display()
        await self.p2.send_victory_display()
        await self.send_planet_array(force=True)
        await self.send_initiative(force=True)
        self.condition_main_game.notify_all()
        self.condition_main_game.release()

    async def send_decks(self, force=False):
        card_one = "Cardback"
        card_two = "Cardback"
        if self.p1.deck:
            if self.p2.search_card_in_hq("Urien's Oubliette"):
                card_one = self.p1.deck[0]
        if self.p2.deck:
            if self.p1.search_card_in_hq("Urien's Oubliette"):
                card_two = self.p2.deck[0]
        card_one = card_one + "/" + str(len(self.p1.deck))
        card_two = card_two + "/" + str(len(self.p2.deck))
        if force or self.last_deck_string_1 != card_one:
            self.last_deck_string_1 = card_one
            await self.send_update_message("GAME_INFO/DECK/1/" + card_one)
        if force or self.last_deck_string_2 != card_two:
            self.last_deck_string_2 = card_two
            await self.send_update_message("GAME_INFO/DECK/2/" + card_two)

    async def send_search(self, force=False):
        card_string = ""
        if self.rearranging_deck:
            card_string = "/".join(self.deck_part_being_rearranged)
            card_string = "GAME_INFO/CHOICE/" + self.name_player_rearranging_deck + "/" \
                          + "Rearranging Deck" + "/" + card_string
        elif self.cards_in_search_box and self.name_player_who_is_searching:
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

    async def send_initiative(self, force=False):
        initiative_string = "GAME_INFO/INITIATIVE/"
        if self.last_planet_checked_for_battle != -1:
            if self.p1.has_initiative_for_battle:
                initiative_string += "1"
            else:
                initiative_string += "2"
        else:
            if self.player_with_initiative == self.name_1:
                initiative_string += "1"
            else:
                initiative_string += "2"
        if initiative_string != self.last_initiative_string or force:
            self.last_initiative_string = initiative_string
            await self.send_update_message(initiative_string)

    async def send_info_box(self, force=False):
        info_string = "GAME_INFO/INFO_BOX/"
        if self.phase == "SETUP":
            info_string += "Unspecified/"
        elif self.resolving_consumption:
            info_string += "Unspecified/"
        elif self.manual_bodyguard_resolution:
            info_string += self.name_player_manual_bodyguard + "/"
        elif self.rearranging_deck:
            info_string += self.name_player_rearranging_deck + "/"
        elif self.cards_in_search_box:
            info_string += self.name_player_who_is_searching + "/"
        elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
            info_string += "Unspecified/"
        elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
            info_string += self.player_with_action + "/"
        elif self.choices_available:
            info_string += self.name_player_making_choices + "/"
        elif self.resolving_nurgling_bomb:
            info_string += self.player_resolving_nurgling_bomb + "/"
        elif self.interrupts_waiting_on_resolution:
            info_string += self.player_resolving_interrupts[0] + "/"
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
            info_string += "Unspecified/" + "Mobile/"
        elif self.battle_ability_to_resolve:
            info_string += self.player_resolving_battle_ability + "/"
        elif self.phase == "COMBAT" or self.herald_of_the_waagh_active:
            if self.start_battle_deepstrike:
                info_string += self.name_player_deepstriking + "/"
            else:
                info_string += self.player_with_combat_turn + "/"
        elif self.phase == "DEPLOY":
            info_string += self.player_with_deploy_turn + "/"
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
            info_string += "/"
        elif self.manual_bodyguard_resolution:
            info_string += "Manual bodyguard resolution: " + self.name_player_manual_bodyguard + "/"
        elif self.rearranging_deck:
            info_string += "Rearranging deck: " + self.name_player_rearranging_deck + "/"
        elif self.cards_in_search_box:
            info_string += "Searching: " + self.what_to_do_with_searched_card + "/"
            info_string += "User: " + self.name_player_who_is_searching + "/"
        elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
            info_string += "Indirect damage: P1: " + str(self.p1.total_indirect_damage) + " P2: " + \
                           str(self.p2.total_indirect_damage) + "/"
        elif self.action_chosen == "Ambush" and self.mode == "DISCOUNT":
            info_string += "Ambush discounts/God help you/"
            info_string += self.player_with_action + "/"
        elif self.choices_available:
            info_string += "Choice: " + self.choice_context + "/"
            info_string += "User: " + self.name_player_making_choices + "/"
        elif self.resolving_nurgling_bomb:
            info_string += "Nurgling Bomb Resolution/"
            info_string += self.player_resolving_nurgling_bomb + "/"
        elif self.interrupts_waiting_on_resolution:
            info_string += "Effect: " + self.interrupts_waiting_on_resolution[0] + "/"
            info_string += "User: " + self.player_resolving_interrupts[0] + "/"
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
        elif self.phase == "COMBAT" or self.herald_of_the_waagh_active:
            if self.start_battle_deepstrike:
                info_string += "Deepstrike: " + self.name_player_deepstriking + "/"
            elif self.ranged_skirmish_active:
                info_string += "Active (RANGED): " + self.player_with_combat_turn + "/"
            else:
                info_string += "Active: " + self.player_with_combat_turn + "/"
        elif self.phase == "DEPLOY":
            info_string += "Active: " + self.player_with_deploy_turn + "/"
        elif self.phase == "COMMAND":
            if self.committing_warlords:
                info_string += "Commit Warlords/"
            elif self.before_command_struggle:
                info_string += "Before command struggle/"
            elif self.after_command_struggle:
                info_string += "After command struggle/"
            elif self.during_command_struggle:
                info_string += "During command struggle/"
            else:
                info_string += "??????/"
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
            planet_string += "|"
            info_string = ""
            if self.imperial_blockades_active[i]:
                info_string += "Imperial Blockades: " + str(self.imperial_blockades_active[i]) + ".\n"
            if self.p1.rok_bombardment_active and i == self.last_planet_checked_for_battle:
                info_string += self.name_1 + ": " + str(len(self.p1.rok_bombardment_active)) + " Rok Bombardments.\n"
            if self.p2.rok_bombardment_active and i == self.last_planet_checked_for_battle:
                info_string += self.name_2 + ": " + str(len(self.p2.rok_bombardment_active)) + " Rok Bombardments.\n"
            if self.p1.mork_blessings_count and i == self.last_planet_checked_for_battle:
                info_string += self.name_1 + ": " + str(self.p1.mork_blessings_count) + " Blessings of Mork.\n"
            if self.p2.mork_blessings_count and i == self.last_planet_checked_for_battle:
                info_string += self.name_2 + ": " + str(self.p2.mork_blessings_count) + " Blessings of Mork.\n"
            if self.bloodthirst_active[i]:
                info_string += "Bloodthirst is active.\n"
            if self.wounded_scream_blanked and self.get_planet_name(i) == "Wounded Scream":
                info_string += "Blanked.\n"
            if self.replaced_planets[i]:
                info_string += "Original Planet: " + self.original_planet_array[i] + "\n"
            if self.additional_icons_planets_eob[i]:
                info_string += "Additional Icons (EOB)\n"
                if "blue" in self.additional_icons_planets_eob[i]:
                    info_string += "Technology (Blue)\n"
                if "green" in self.additional_icons_planets_eob[i]:
                    info_string += "Strongpoint (Green)\n"
                if "red" in self.additional_icons_planets_eob[i]:
                    info_string += "Material (Red)\n"
            if self.additional_icons_planets_eop[i]:
                info_string += "Additional Icons (EOP)\n"
                if "blue" in self.additional_icons_planets_eob[i]:
                    info_string += "Technology (Blue)\n"
                if "green" in self.additional_icons_planets_eob[i]:
                    info_string += "Strongpoint (Green)\n"
                if "red" in self.additional_icons_planets_eob[i]:
                    info_string += "Material (Red)\n"
            if self.p1.sac_altar_rewards[i]:
                info_string += "Sacrifical Altar " + self.name_1 + " (" \
                               + str(self.p1.sac_altar_rewards[i]) + ").\n"
            if self.p2.sac_altar_rewards[i]:
                info_string += "Sacrifical Altar " + self.name_2 + " (" \
                               + str(self.p2.sac_altar_rewards[i]) + ").\n"
            if self.p1.looted_skrap_active and self.p1.looted_skrap_planet == i:
                info_string += "Looted Skrap " + self.name_1 + " (" + str(self.p1.looted_skrap_count) + ").\n"
            if self.p2.looted_skrap_active and self.p2.looted_skrap_planet == i:
                info_string += "Looted Skrap " + self.name_2 + " (" + str(self.p2.looted_skrap_count) + ").\n"
            if self.p1.the_princes_might_active[i]:
                info_string += "The Prince's Might " + self.name_1 + ".\n"
            if self.p2.the_princes_might_active[i]:
                info_string += "The Prince's Might " + self.name_2 + ".\n"
            if not info_string:
                info_string = "None"
            planet_string += info_string
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
                if len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        if game_update_string[1] == player.get_number():
                            discount_received = player.perform_discount_at_pos_hq(
                                int(game_update_string[2]), self.card_to_deploy.get_faction(),
                                self.card_to_deploy.get_traits(), self.planet_aiming_reticle_position,
                                name_of_card=self.card_to_deploy.get_name())
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
                                self.card_to_deploy.get_faction(),
                                self.card_to_deploy.get_traits()
                            )
                            card_name = player.cards[int(game_update_string[2])]
                            if discount_received > 0:
                                if secondary_player.nullify_check() and self.nullify_enabled:
                                    await self.send_update_message(
                                        player.name_player + " wants to play " + card_name + "; "
                                                                                             "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = int(game_update_string[2])
                                    self.nullified_card_name = card_name
                                    self.cost_card_nullified = 0
                                    self.nullify_string = "/".join(game_update_string)
                                    self.first_player_nullified = player.name_player
                                    self.nullify_context = card_name
                                else:
                                    self.discounts_applied += discount_received
                                    player.optimized_landing_used = True
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
                            discount_received = player.perform_discount_at_pos_in_play(
                                int(game_update_string[2]), int(game_update_string[3]),
                                self.card_to_deploy.get_traits(), name_of_card=self.card_to_deploy.get_name())
                            if discount_received > 0:
                                self.discounts_applied += discount_received
                            if self.discounts_applied >= self.available_discounts:
                                await DeployPhase.deploy_card_routine(self, name, self.planet_aiming_reticle_position,
                                                                      discounts=self.discounts_applied)
                                self.mode = "Normal"
                elif len(game_update_string) == 5:
                    if game_update_string[0] == "ATTACHMENT":
                        if game_update_string[1] == "HQ":
                            if game_update_string[2] == player.get_number():
                                discount_received = player.perform_discount_at_pos_hq_attachment(
                                    int(game_update_string[3]), int(game_update_string[4]),
                                    self.card_to_deploy.get_faction(), self.card_to_deploy.get_traits(),
                                    self.planet_aiming_reticle_position)
                                if discount_received > 0:
                                    self.discounts_applied += discount_received
                                if self.discounts_applied >= self.available_discounts:
                                    await DeployPhase.deploy_card_routine(self, name,
                                                                          self.planet_aiming_reticle_position,
                                                                          discounts=self.discounts_applied)
                                    self.mode = "Normal"
                elif len(game_update_string) == 6:
                    if game_update_string[0] == "ATTACHMENT":
                        if game_update_string[1] == "IN_PLAY":
                            if game_update_string[2] == player.get_number():
                                if self.card_to_deploy.get_card_type() == "Army":
                                    discount_received = player.perform_discount_at_pos_in_play_attachment(
                                        int(game_update_string[3]), int(game_update_string[4]),
                                        int(game_update_string[5]), self.card_to_deploy.get_traits())
                                    if discount_received > 0:
                                        self.discounts_applied += discount_received
                                    if self.discounts_applied >= self.available_discounts:
                                        await DeployPhase.deploy_card_routine(self, name,
                                                                              self.planet_aiming_reticle_position,
                                                                              discounts=self.discounts_applied)
                                        self.mode = "Normal"

    async def aoe_routine(self, primary_player, secondary_player, chosen_planet, amount_aoe, faction="",
                          shadow_field_possible=False, rickety_warbuggy=False, actual_aoe=False):
        secondary_player.suffer_area_effect(chosen_planet, amount_aoe, faction=faction,
                                            shadow_field_possible=shadow_field_possible,
                                            rickety_warbuggy=rickety_warbuggy, actual_area_effect=True)
        self.number_of_units_left_to_suffer_damage = \
            secondary_player.get_number_of_units_at_planet(chosen_planet)
        if self.number_of_units_left_to_suffer_damage > 0:
            for i in range(1, self.number_of_units_left_to_suffer_damage):
                genestealer_hybrids_relevant = False
                if actual_aoe:
                    for j in range(len(secondary_player.cards_in_play[chosen_planet + 1])):
                        if secondary_player.get_ability_given_pos(chosen_planet, j) == "Genestealer Hybrids" and i != j:
                            genestealer_hybrids_relevant = True
                if not genestealer_hybrids_relevant:
                    secondary_player.set_aiming_reticle_in_play(chosen_planet, i, "blue")

    async def update_game_event_action(self, name, game_update_string):
        if name == self.player_with_action:
            if name == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
                if self.p1.force_due_to_dark_possession:
                    game_update_string = ["HAND", "1", str(self.p1.pos_card_dark_possession)]
            else:
                primary_player = self.p2
                secondary_player = self.p1
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
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                    elif self.action_chosen == "Seer's Exodus":
                        await self.send_update_message("Stopping Seer's Exodus")
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Rapid Evolution":
                        await self.send_update_message("Stopping Rapid Evolution")
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Despise":
                        await self.send_update_message(
                            self.player_with_action + " does not sacrifice a card for Despise."
                        )
                        if self.player_with_action == self.name_1:
                            self.player_with_action = self.name_2
                            self.p1.sacced_card_for_despise = True
                        else:
                            self.player_with_action = self.name_1
                            self.p2.sacced_card_for_despise = True
                        if self.p1.sacced_card_for_despise and self.p2.sacced_card_for_despise:
                            primary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                            await secondary_player.dark_eldar_event_played()
                    elif self.action_chosen == "Preemptive Barrage":
                        await self.send_update_message("Stopping Preemptive Barrage early")
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Rapid Assault":
                        if self.chosen_second_card:
                            await self.send_update_message("Rapid Assault ended early")
                            secondary_player.create_enemy_played_event_reactions()
                            await primary_player.dark_eldar_event_played()
                            self.action_cleanup()
                    elif self.action_chosen == "Inevitable Betrayal":
                        await self.send_update_message("Finished resolving Inevitable Betrayal")
                        self.p1.reset_all_aiming_reticles_play_hq()
                        self.p2.reset_all_aiming_reticles_play_hq()
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                        await primary_player.dark_eldar_event_played()
                    elif self.action_chosen == "Cathedral of Saint Camila" or self.action_chosen == "Eldritch Storm":
                        await self.send_update_message("Finished " + self.action_chosen)
                        self.misc_counter = 0
                        self.action_cleanup()
                    elif self.action_chosen == "Daring Assault" and not self.chosen_first_card:
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Pattern IX Immolator":
                        if not self.chosen_first_card:
                            self.chosen_first_card = True
                            self.misc_counter = secondary_player.command_struggles_won_this_phase - 1
                            await self.send_update_message("Now place " + str(self.misc_counter) + " faith.")
                        else:
                            self.action_cleanup()
                    elif self.action_chosen == "Indiscriminate Bombing":
                        if not self.chosen_second_card:
                            self.chosen_second_card = True
                            self.player_with_action = secondary_player.name_player
                            await self.send_update_message("Indiscriminate Bombing passed.")
                        else:
                            primary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                            await self.send_update_message("Indiscriminate Bombing passed.")
                    elif self.action_chosen == "Biomass Sacrifice":
                        await self.send_update_message("Finished " + self.action_chosen)
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Crown of Control":
                        await self.send_update_message("Finished " + self.action_chosen)
                        self.action_cleanup()
                    elif self.action_chosen == "Piercing Wail":
                        await self.send_update_message("Finished " + self.action_chosen)
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Know No Fear":
                        await self.send_update_message("Stopping Know No Fear early")
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Soot-Blackened Axe":
                        self.action_cleanup()
                    elif self.action_chosen == "Guerrilla Tactics Move":
                        self.action_cleanup()
                    elif self.action_chosen == "Iridescent Wand":
                        self.action_cleanup()
                    elif self.action_chosen == "Unshrouded Truth":
                        num_revealed = len(self.misc_misc)
                        num_cards = len(primary_player.cards)
                        resources = num_cards - num_revealed
                        secondary_player.add_resources(resources)
                        await self.send_update_message("Gained " + str(resources) + " resources for unrevealed cards.")
                        self.misc_misc = None
                        primary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Attuned Gyrinx":
                        await self.send_update_message("Stopping Attuned Gyrinx early")
                        self.action_cleanup()
                    elif self.action_chosen == "Biomass Extraction":
                        self.action_cleanup()
                    elif self.action_chosen == "Whirling Death":
                        await self.send_update_message("Stopping Whirling Death")
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Force Reallocation":
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "Boast of Strength":
                        if not self.chosen_first_card:
                            secondary_player.create_enemy_played_event_reactions()
                        else:
                            secondary_player.draw_card()
                            secondary_player.add_resources(2)
                            primary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.action_chosen == "The Wolf Within":
                        await self.send_update_message("Stopping The Wolf Within early")
                        self.action_cleanup()
                    elif self.action_chosen == "Memories of Fallen Comrades":
                        await self.send_update_message("Stopping Memories of Fallen Comrades early")
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
                elif game_update_string[0] == "REMOVED":
                    chosen_removed = int(game_update_string[1])
                    pos_removed = int(game_update_string[2])
                    if self.player_with_action == self.name_1:
                        primary_player = self.p1
                        secondary_player = self.p2
                    else:
                        primary_player = self.p2
                        secondary_player = self.p1
                    if not self.action_chosen:
                        if chosen_removed == int(primary_player.number):
                            ability = primary_player.cards_removed_from_game[pos_removed]
                            if ability == "The Orgiastic Feast":
                                if self.phase == "COMMAND":
                                    vael_relevant = False
                                    vael_bloodied = False
                                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                                    if primary_player.get_ability_given_pos(
                                            warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                                            primary_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                                        vael_relevant = True
                                    elif primary_player.get_ability_given_pos(
                                            warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                                            and not primary_player.get_once_per_game_used_given_pos(warlord_pla,
                                                                                                    warlord_pos):
                                        vael_relevant = True
                                        vael_bloodied = True
                                    if vael_relevant:
                                        if primary_player.spend_resources(4):
                                            primary_player.add_card_to_discard(ability)
                                            primary_player.cards_removed_from_game.remove(ability)
                                            del primary_player.cards_removed_from_game_hidden[0]
                                            if vael_bloodied:
                                                primary_player.set_once_per_game_used_given_pos(warlord_pla,
                                                                                                warlord_pos, True)
                                            else:
                                                primary_player.set_once_per_round_used_given_pos(warlord_pla,
                                                                                                 warlord_pos, True)
                                            primary_player.number_cards_to_search = 12
                                            if primary_player.number_cards_to_search > len(primary_player.deck):
                                                primary_player.number_cards_to_search = len(primary_player.deck)
                                            self.choices_available = \
                                                primary_player.deck[:primary_player.number_cards_to_search]
                                            if self.choices_available:
                                                self.choice_context = "The Orgiastic Feast Rally 1"
                                                self.misc_target_choice = ""
                                                self.name_player_making_choices = primary_player.name_player
                                                self.resolving_search_box = True
                                                self.action_chosen = ability
                            elif ability == "Test of Faith":
                                vael_relevant = False
                                vael_bloodied = False
                                warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                                if primary_player.get_ability_given_pos(
                                        warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                                        primary_player.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                                    vael_relevant = True
                                elif primary_player.get_ability_given_pos(
                                        warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                                        and not primary_player.get_once_per_game_used_given_pos(warlord_pla,
                                                                                                warlord_pos):
                                    vael_relevant = True
                                    vael_bloodied = True
                                if vael_relevant:
                                    if primary_player.spend_resources(1):
                                        primary_player.add_card_to_discard(ability)
                                        primary_player.cards_removed_from_game.remove(ability)
                                        if vael_bloodied:
                                            primary_player.set_once_per_game_used_given_pos(warlord_pla,
                                                                                            warlord_pos, True)
                                        else:
                                            primary_player.set_once_per_round_used_given_pos(warlord_pla,
                                                                                             warlord_pos, True)
                                        self.action_chosen = ability
                    elif self.action_chosen == "Reveal The Blade":
                        if not self.chosen_first_card:
                            if chosen_removed == int(primary_player.number):
                                if primary_player.cards_removed_from_game_hidden[pos_removed] == "H":
                                    card_name = primary_player.cards_removed_from_game[pos_removed]
                                    card = self.preloaded_find_card(card_name)
                                    if card.get_shields() == 0:
                                        self.chosen_first_card = True
                                        primary_player.cards_removed_from_game_hidden[pos_removed] = "N"
                                        if card_name == "Connoisseur of Terror":
                                            self.create_reaction("Connoisseur of Terror", primary_player.name_player,
                                                                 (int(primary_player.number), -1, -1))
                                        if card_name == "Liatha's Retinue":
                                            self.create_reaction("Liatha's Retinue", primary_player.name_player,
                                                                 (int(primary_player.number), -1, -1))
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    await InPlayActions.update_game_event_action_in_play(self, name, game_update_string)
                elif game_update_string[0] == "RESERVE":
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    if not self.action_chosen:
                        if game_update_string[1] == primary_player.number:
                            if primary_player.cards_in_reserve[planet_pos][unit_pos].get_ability() \
                                    == "XV25 Stealth Squad" and self.phase == "COMBAT":
                                cost = primary_player.get_deepstrike_value_given_pos(planet_pos, unit_pos)
                                if primary_player.spend_resources(cost):
                                    primary_player.deepstrike_unit(planet_pos, unit_pos)
                                    self.action_cleanup()
                            elif primary_player.cards_in_reserve[planet_pos][unit_pos].get_ability() \
                                    == "Patient Infiltrator" and self.phase == "COMBAT":
                                cost = primary_player.get_deepstrike_value_given_pos(planet_pos, unit_pos)
                                if primary_player.spend_resources(cost):
                                    primary_player.deepstrike_unit(planet_pos, unit_pos)
                                    self.action_cleanup()
                            elif primary_player.cards_in_reserve[planet_pos][unit_pos].get_ability() \
                                    == "Deathleaper" and self.phase == "COMBAT":
                                cost = primary_player.get_deepstrike_value_given_pos(planet_pos, unit_pos)
                                if primary_player.spend_resources(cost):
                                    primary_player.deepstrike_unit(planet_pos, unit_pos)
                                    self.action_cleanup()
                    elif self.action_chosen == "Korporal Snagbrat":
                        if not self.chosen_first_card:
                            if game_update_string[1] == primary_player.get_number():
                                self.chosen_first_card = True
                                primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = "blue"
                                self.misc_target_choice = "RESERVE"
                                self.misc_target_unit = (planet_pos, unit_pos)
                    elif self.action_chosen == "Daring Assault":
                        if not self.chosen_first_card:
                            if game_update_string[1] == primary_player.get_number():
                                self.chosen_first_card = True
                                primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = "blue"
                                self.misc_target_unit = (planet_pos, unit_pos)
                    elif self.action_chosen == "The Dawn Blade":
                        if self.misc_target_choice == "Move":
                            if not self.chosen_first_card:
                                if game_update_string[1] == primary_player.get_number():
                                    self.chosen_first_card = True
                                    primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = "blue"
                                    self.misc_target_unit = (planet_pos, unit_pos)
                        else:
                            if primary_player.get_number() == game_update_string[1]:
                                actual_card = primary_player.cards_in_reserve[planet_pos][unit_pos]
                                if actual_card.get_card_type() == "Attachment":
                                    ds_value = primary_player.get_deepstrike_value_given_pos(planet_pos, unit_pos)
                                    if primary_player.spend_resources(ds_value):
                                        if primary_player.cards_in_reserve[planet_pos][unit_pos].planet_attachment:
                                            primary_player.add_attachment_to_planet(
                                                planet_pos, primary_player.cards_in_reserve[planet_pos][unit_pos])
                                            del primary_player.cards_in_reserve[planet_pos][unit_pos]
                                            primary_player.deepstrike_attachment_extras(planet_pos)
                                            self.action_cleanup()
                                        else:
                                            self.chosen_first_card = True
                                            primary_player.cards_in_reserve[planet_pos][
                                                unit_pos].aiming_reticle_color = "blue"
                                            self.misc_target_unit = (planet_pos, unit_pos)
                                            self.misc_target_choice = "RESERVE"
                    elif self.action_chosen == "Kommando Cunning":
                        if not self.chosen_first_card:
                            if primary_player.get_number() == game_update_string[1]:
                                actual_card = primary_player.cards_in_reserve[planet_pos][unit_pos]
                                if actual_card.get_card_type() == "Army":
                                    primary_player.deepstrike_unit(planet_pos, unit_pos)
                                    secondary_player.create_enemy_played_event_reactions()
                                    self.action_cleanup()
                                elif actual_card.get_card_type() == "Event":
                                    primary_player.deepstrike_event(planet_pos, unit_pos)
                                    secondary_player.create_enemy_played_event_reactions()
                                    self.action_cleanup()
                                elif actual_card.get_card_type() == "Attachment":
                                    if primary_player.cards_in_reserve[planet_pos][unit_pos].planet_attachment:
                                        primary_player.add_attachment_to_planet(
                                            planet_pos, primary_player.cards_in_reserve[planet_pos][unit_pos])
                                        del primary_player.cards_in_reserve[planet_pos][unit_pos]
                                        primary_player.deepstrike_attachment_extras(planet_pos)
                                        secondary_player.create_enemy_played_event_reactions()
                                        self.action_cleanup()
                                    else:
                                        self.chosen_first_card = True
                                        primary_player.cards_in_reserve[planet_pos][
                                            unit_pos].aiming_reticle_color = "blue"
                                        self.misc_target_unit = (planet_pos, unit_pos)
                                        self.misc_target_choice = "RESERVE"
                    elif self.action_chosen == "Vanguarding Horror":
                        if not self.chosen_first_card:
                            if primary_player.get_number() == game_update_string[1]:
                                if planet_pos == self.misc_target_planet:
                                    primary_player.cards_in_reserve[planet_pos][unit_pos].aiming_reticle_color = "blue"
                                    self.chosen_first_card = True
                                    self.misc_target_unit = (planet_pos, unit_pos)
                                elif abs(planet_pos - self.misc_target_planet) == 1:
                                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                                self.position_of_actioned_card[1])
                                    primary_player.cards_in_reserve[self.misc_target_planet].append(
                                        primary_player.cards_in_reserve[planet_pos][unit_pos]
                                    )
                                    del primary_player.cards_in_reserve[planet_pos][unit_pos]
                                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                                    self.action_cleanup()
                    elif self.action_chosen == "No Surprises":
                        if game_update_string[1] == "1":
                            target = self.p1
                        else:
                            target = self.p2
                        target.discard.append(
                            target.cards_in_reserve[planet_pos][unit_pos].get_name())
                        del target.cards_in_reserve[planet_pos][unit_pos]
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
            elif len(game_update_string) == 5:
                if game_update_string[0] == "ATTACHMENT" and game_update_string[1] == "HQ":
                    await AttachmentHQActions.update_game_event_action_attachment_hq(self, name, game_update_string)
                elif game_update_string[1] == "PLANETS":
                    player_num = int(game_update_string[2])
                    pos_planet = int(game_update_string[3])
                    pos_attachment = int(game_update_string[4])
                    if player_num == 1:
                        player_with_attach = self.p1
                    else:
                        player_with_attach = self.p2
                    if not self.action_chosen:
                        if player_with_attach.attachments_at_planet[pos_planet][
                            pos_attachment].get_ability() == "Rain of Mycetic Spores":
                            if primary_player.number == game_update_string[2]:
                                if player_with_attach.attachments_at_planet[pos_planet][
                                    pos_attachment].get_ready():
                                    player_with_attach.attachments_at_planet[pos_planet][
                                        pos_attachment].exhaust_card()
                                    if not self.infested_planets[pos_planet]:
                                        await self.send_update_message("Infested planet")
                                        self.infest_planet(pos_planet, player_with_attach)
                                        self.action_cleanup()
                                    else:
                                        previous_planet_infested = True
                                        next_planet_infested = True
                                        if pos_planet != 0:
                                            if self.planets_in_play_array[pos_planet - 1]:
                                                previous_planet_infested = self.infested_planets[pos_planet - 1]
                                        if pos_planet != 6:
                                            if self.planets_in_play_array[pos_planet + 1]:
                                                next_planet_infested = self.infested_planets[pos_planet + 1]
                                        if previous_planet_infested and next_planet_infested:
                                            await self.send_update_message("Gained 2 resources")
                                            player_with_attach.add_resources(2)
                                            self.action_cleanup()
                                        else:
                                            await self.send_update_message("Infest adjacent planet")
                                            self.action_chosen = "Rain of Mycetic Spores"
                                            self.misc_target_planet = pos_planet
                        elif player_with_attach.attachments_at_planet[pos_planet][
                            pos_attachment].get_ability() == "Call The Storm":
                            if primary_player.number == game_update_string[2]:
                                if player_with_attach.attachments_at_planet[pos_planet][
                                    pos_attachment].get_ready():
                                    if not secondary_player.check_for_warlord(pos_planet, True,
                                                                              primary_player.name_player):
                                        player_with_attach.attachments_at_planet[pos_planet][
                                            pos_attachment].exhaust_card()
                                        self.action_chosen = "Call The Storm"
                                        self.chosen_first_card = False
                                        self.misc_target_planet = pos_planet
                    elif self.action_chosen == "Subdual":
                        player_with_attach.deck.insert(
                            0, player_with_attach.attachments_at_planet[pos_planet][pos_attachment].get_name())
                        del player_with_attach.attachments_at_planet[pos_planet][pos_attachment]
                        if self.player_with_action == self.name_1:
                            primary_player = self.p1
                        else:
                            primary_player = self.p2
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
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

    async def send_victory_proper(self, winner_name, reason):
        victory_string = "GAME_INFO/VICTORY_MESSAGE/" + winner_name + "/" + reason
        await self.send_update_message(victory_string)

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
                if self.planets_in_play_array[int(game_update_string[1])]:
                    return True
            if game_update_string[0] == "CHOICE":
                if len(self.choices_available) > int(game_update_string[1]):
                    return True
                elif len(self.deck_part_being_rearranged) > int(game_update_string[1]):
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
            elif game_update_string[0] == "REMOVED":
                if game_update_string[1] == "1":
                    if len(self.p1.cards_removed_from_game) > int(game_update_string[2]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.cards_removed_from_game) > int(game_update_string[2]):
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
            elif game_update_string[0] == "RESERVE":
                if game_update_string[1] == "1":
                    if len(self.p1.cards_in_reserve[int(game_update_string[2])]) > int(game_update_string[3]):
                        return True
                elif game_update_string[1] == "2":
                    if len(self.p2.cards_in_reserve[int(game_update_string[2])]) > int(game_update_string[3]):
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

    def start_mulligan(self):
        self.choices_available = ["Yes", "No"]
        self.choice_context = "Mulligan Opening Hand?"
        self.name_player_making_choices = self.name_1
        self.resolving_search_box = True

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
                        if self.action_chosen == "Drop Pod Assault":
                            self.p2.create_enemy_played_event_reactions()
                            self.action_cleanup()
                        if self.faction_of_searched_card == "Necrons":
                            if self.reactions_needing_resolving:
                                if self.reactions_needing_resolving[0] == "Endless Legions":
                                    if self.p1.search_card_in_hq("Endless Legions", ready_relevant=True):
                                        self.create_reaction("Endless Legions", self.name_1, (1, -1, -1))
                                    self.delete_reaction()
                    else:
                        self.p2.bottom_remaining_cards()
                        if self.action_chosen == "Drop Pod Assault":
                            self.p1.create_enemy_played_event_reactions()
                            self.action_cleanup()
                        if self.faction_of_searched_card == "Necrons":
                            if self.reactions_needing_resolving:
                                if self.reactions_needing_resolving[0] == "Endless Legions":
                                    if self.p2.search_card_in_hq("Endless Legions", ready_relevant=True):
                                        self.create_reaction("Endless Legions", self.name_2, (1, -1, -1))
                                    self.delete_reaction()
                    self.cards_in_search_box = []
                    if self.resolving_search_box:
                        self.resolving_search_box = False
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    if self.number_who_is_searching == game_update_string[1]:
                        unit_pos = int(game_update_string[2])
                        if self.number_who_is_searching == "1":
                            player = self.p1
                        else:
                            player = self.p2
                        if player.get_ability_given_pos(-2, unit_pos) == "Dome of Crystal Seers":
                            if player.get_ready_given_pos(-2, unit_pos):
                                if not self.searching_enemy_deck:
                                    player.exhaust_given_pos(-2, unit_pos)
                                    player.number_cards_to_search += 3
                                    if len(player.deck) >= player.number_cards_to_search:
                                        self.cards_in_search_box = player.deck[:player.number_cards_to_search]
                                    else:
                                        self.cards_in_search_box = player.deck[:player.deck]
                        if self.choice_context == "Tower of Despair":
                            if player.check_is_unit_at_pos(-2, unit_pos):
                                if player.check_for_trait_given_pos(-2, unit_pos, "Haemonculus"):
                                    if player.get_ready_given_pos(-2, unit_pos):
                                        player.exhaust_given_pos(-2, unit_pos)
                                        self.misc_counter += 1
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if self.number_who_is_searching == game_update_string[1]:
                        planet_pos = int(game_update_string[2])
                        unit_pos = int(game_update_string[3])
                        if self.number_who_is_searching == "1":
                            player = self.p1
                        else:
                            player = self.p2
                        if self.choice_context == "Tower of Despair":
                            if player.check_is_unit_at_pos(planet_pos, unit_pos):
                                if player.check_for_trait_given_pos(planet_pos, unit_pos, "Haemonculus"):
                                    if player.get_ready_given_pos(planet_pos, unit_pos):
                                        player.exhaust_given_pos(planet_pos, unit_pos)
                                        self.misc_counter += 1
            elif len(game_update_string) == 2:
                if game_update_string[0] == "SEARCH":
                    if self.number_who_is_searching == "1":
                        primary_player = self.p1
                        secondary_player = self.p2
                    else:
                        primary_player = self.p2
                        secondary_player = self.p1
                    valid_card = True
                    if not self.no_restrictions_on_chosen_card:
                        card_chosen = FindCard.find_card(primary_player.deck[int(game_update_string[1])],
                                                         self.card_array, self.cards_dict,
                                                         self.apoka_errata_cards, self.cards_that_have_errata)
                        valid_card = self.check_if_card_searched_satisfies_conditions(card_chosen)
                    if valid_card:
                        if self.what_to_do_with_searched_card == "DRAW":
                            primary_player.draw_card_at_location_deck(int(game_update_string[1]))
                        elif self.what_to_do_with_searched_card == "PLAY TO HQ" and card_chosen is not None:
                            primary_player.add_to_hq(card_chosen)
                            del primary_player.deck[int(game_update_string[1])]
                            if self.resolving_search_box:
                                self.resolving_search_box = False
                        elif self.what_to_do_with_searched_card == "PLAY TO BATTLE" and card_chosen is not None:
                            primary_player.play_card_to_battle_at_location_deck(self.last_planet_checked_for_battle,
                                                                                int(game_update_string[1]), card_chosen)
                            if self.action_chosen == "Drop Pod Assault":
                                secondary_player.create_enemy_played_event_reactions()
                                self.action_cleanup()
                        elif self.what_to_do_with_searched_card == "STORE":
                            self.misc_target_choice = primary_player.deck[int(game_update_string[1])]
                            del primary_player.deck[int(game_update_string[1])]
                        elif self.what_to_do_with_searched_card == "Hybrid Metamorph":
                            pla, pos = self.misc_target_unit
                            card_name = primary_player.deck[int(game_update_string[1])]
                            card = self.preloaded_find_card(card_name)
                            self.misc_target_choice = ""
                            if primary_player.deploy_attachment(card, pla, pos, extra_discounts=1):
                                del primary_player.deck[int(game_update_string[1])]
                            else:
                                primary_player.number_cards_to_search += 1
                        elif self.what_to_do_with_searched_card == "DISCARD":
                            if self.searching_enemy_deck:
                                secondary_player.discard_card_from_deck(int(game_update_string[1]))
                            else:
                                primary_player.discard_card_from_deck(int(game_update_string[1]))
                        primary_player.number_cards_to_search -= 1
                        if self.choice_context == "Tower of Despair" and \
                                self.what_to_do_with_searched_card == "DRAW" and \
                                self.misc_counter > 0:
                            del self.cards_in_search_box[int(game_update_string[1])]
                            self.misc_counter = self.misc_counter - 1
                        else:
                            if self.choice_context == "Tower of Despair":
                                self.choice_context = ""
                            primary_player.bottom_remaining_cards()
                            self.reset_search_values()
                            if self.resolving_search_box:
                                self.resolving_search_box = False
                            if self.shuffle_after:
                                primary_player.shuffle_deck()
                                self.shuffle_after = False
                            if self.battle_ability_to_resolve == "Elouith" or \
                                    self.battle_ability_to_resolve == "Anshan":
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
        self.battle_in_progress = False
        self.p1.foretell_permitted = True
        self.p2.foretell_permitted = True
        self.ranged_skirmish_active = False
        self.cult_duplicity_available = True
        self.p1.rok_bombardment_active = []
        self.p2.rok_bombardment_active = []
        self.nectavus_active = False
        self.nectavus_target = -1
        self.resolving_search_box = False
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.p1.cegorach_jesters_active = False
        self.p1.cegorach_jesters_permitted = []
        self.p2.cegorach_jesters_active = False
        self.p2.cegorach_jesters_permitted = []
        self.different_atrox_origin = -1
        if self.nectavus_actual_current_planet != -1:
            self.last_planet_checked_command_struggle = self.nectavus_actual_current_planet
        self.nectavus_actual_current_planet = -1
        winner = self.p2
        loser = self.p1
        if self.player_resolving_battle_ability == self.name_1:
            winner = self.p1
            loser = self.p2
        for i in range(7):
            if self.planet_array[i] == self.battle_ability_to_resolve:
                for j in range(len(winner.cards_in_play[i + 1])):
                    if winner.get_ability_given_pos(i, j) == "Pathfinder Team":
                        if winner.get_ready_given_pos(i, j):
                            self.create_reaction("Pathfinder Team", winner.name_player,
                                                 (int(winner.number), i, j))
        if not self.tense_negotiations_active:
            self.p1.senatorum_directives_used = False
            self.p2.senatorum_directives_used = False
            winner = None
            if self.player_resolving_battle_ability == self.name_2:
                winner = self.p2
            elif self.player_resolving_battle_ability == self.name_1:
                winner = self.p1
            if winner is not None:
                i = 0
                j = 0
                while j < len(self.p1.attachments_at_planet[self.last_planet_checked_for_battle]):
                    if self.p1.attachments_at_planet[self.last_planet_checked_for_battle][j]. \
                            get_ability() == "Slaanesh's Temptation":
                        del self.p1.attachments_at_planet[self.last_planet_checked_for_battle][j]
                        j = j - 1
                        self.p1.add_card_to_discard("Slaanesh's Temptation")
                    j = j + 1
                j = 0
                while j < len(self.p2.attachments_at_planet[self.last_planet_checked_for_battle]):
                    if self.p2.attachments_at_planet[self.last_planet_checked_for_battle][j]. \
                            get_ability() == "Slaanesh's Temptation":
                        del self.p2.attachments_at_planet[self.last_planet_checked_for_battle][j]
                        j = j - 1
                        self.p2.add_card_to_discard("Slaanesh's Temptation")
                    j = j + 1
                while i < len(winner.cards_in_play[self.last_planet_checked_for_battle + 1]):
                    if winner.get_ability_given_pos(self.last_planet_checked_for_battle, i) == "Mystic Warden":
                        if winner.sacrifice_card_in_play(self.last_planet_checked_for_battle, i):
                            i = i - 1
                    i = i + 1
                if self.round_number == self.last_planet_checked_for_battle and not self.herald_of_the_waagh_active:
                    winner.move_all_at_planet_to_hq(self.last_planet_checked_for_battle)
                    winner.capture_planet(self.last_planet_checked_for_battle,
                                          self.planet_cards_array)
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                    self.p1.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                    self.p2.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                    await winner.send_victory_display()
                elif self.round_number != self.last_planet_checked_for_battle and not self.herald_of_the_waagh_active:
                    if winner.check_for_warlord(self.last_planet_checked_for_battle):
                        winner.retreat_warlord()
                self.planet_aiming_reticle_active = False
            self.planet_aiming_reticle_position = -1
            self.p1.reset_extra_attack_eob()
            self.p2.reset_extra_attack_eob()
            self.p1.reset_extra_health_eob()
            self.p2.reset_extra_health_eob()
            self.additional_icons_planets_eob = [[], [], [], [], [], [], []]
            if self.active_jaricho_battle:
                self.last_planet_checked_for_battle = self.jaricho_actual_triggered_planet
                self.active_jaricho_battle = False
                self.jaricho_actual_triggered_planet = -1
            self.mode = "Normal"
            if self.kaerux_erameas_active:
                self.kaerux_erameas_active = False
                self.actions_between_battle = True
                self.last_planet_checked_for_battle = -1
            elif self.herald_of_the_waagh_active:
                self.p1.has_passed = False
                self.p2.has_passed = False
                self.herald_of_the_waagh_active = False
                self.last_planet_checked_for_battle = -1
            else:
                self.actions_between_battle = True
                await self.send_update_message("Window allowed for actions between battles.")
        self.tense_negotiations_active = False
        if self.theater_of_war_active:
            self.theater_of_war_active = False
            self.forbidden_theater_of_war = self.battle_ability_to_resolve
            self.create_reaction("Theater of War Response", loser.name_player, (int(loser.number), -1, -1))
        self.damage_from_atrox = False
        self.reset_battle_resolve_attributes()

    async def complete_nullify(self):
        self.choosing_unit_for_nullify = False
        resolve_nullify_discard = True
        if self.first_player_nullified == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if self.nullifying_backlash or self.nullifying_storm_of_silence:
            if self.name_player_using_backlash == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
        if self.nullify_count % 2 == 0:
            if self.nullify_count > 0:
                primary_player.resolve_reactions_on_cancelling_enemy_effect()
            if self.nullifying_storm_of_silence:
                self.nullifying_storm_of_silence = False
                await self.complete_storm_of_silence(primary_player, secondary_player)
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
            elif self.nullify_context == "Indomitable":
                await self.resolve_indomitable(primary_player, secondary_player)
            elif self.nullify_context == "I Do Not Serve":
                await self.resolve_i_do_not_serve(primary_player, secondary_player)
            elif self.nullify_context == "Back to the Shadows":
                await self.resolve_back_to_the_shadows(primary_player, secondary_player)
            elif self.nullify_context == "Foretell":
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Use Foretell?"
                self.name_player_making_choices = primary_player.name_player
                self.nullify_enabled = False
                await self.update_game_event(primary_player.name_player, ["CHOICE", "0"], same_thread=True)
                self.nullify_enabled = True
            elif self.nullify_context == "Glorious Intervention":
                primary_player.aiming_reticle_coords_hand = self.pos_shield_card
                primary_player.aiming_reticle_color = "blue"
                self.alt_shield_name = self.nullify_context
                self.alt_shield_mode_active = True
            elif self.nullify_context == "Faith Denies Death":
                primary_player.aiming_reticle_coords_hand = self.pos_shield_card
                primary_player.aiming_reticle_color = "blue"
                self.alt_shield_name = self.nullify_context
                self.alt_shield_mode_active = True
            elif self.nullify_context == "Bigga Is Betta" or self.nullify_context == "Optimized Landing":
                self.nullify_enabled = False
                new_string_list = self.nullify_string.split(sep="/")
                await DeployPhase.update_game_event_deploy_section(self, self.first_player_nullified,
                                                                   new_string_list)
                self.nullify_enabled = True
            elif self.nullify_context == "Foresight" or self.nullify_context == "Superiority" or \
                    self.nullify_context == "Blackmane's Hunt" or self.nullify_context == "War of Ideas":
                self.nullify_enabled = False
                new_string_list = self.nullify_string.split(sep="/")
                await CommandPhase.update_game_event_command_section(self, self.first_player_nullified,
                                                                     new_string_list)
                self.nullify_enabled = True
            elif self.nullify_context == "Reaction Event":
                self.nullify_enabled = False
                await StartReaction.start_resolving_reaction(self, "", [])
                self.nullify_enabled = True
            elif self.nullify_context == "Win Battle Reaction Event":
                self.nullify_enabled = False
                await StartReaction.start_resolving_reaction(self, "", [])
                self.nullify_enabled = True
            elif self.nullify_context == "Interrupt Event":
                self.nullify_enabled = False
                await StartInterrupt.start_resolving_interrupt(self, "", [])
                self.nullify_enabled = False
            elif self.nullify_context == "Interrupt":
                self.nullify_enabled = False
                await StartInterrupt.start_resolving_interrupt(self, "", [])
                self.nullify_enabled = False
            elif self.nullify_context == "Reaction":
                self.nullify_enabled = False
                await StartReaction.start_resolving_reaction(self, "", [])
                self.nullify_enabled = True
            elif self.nullify_context == "Primal Howl":
                primary_player.discard_card_name_from_hand("Primal Howl")
                for _ in range(3):
                    primary_player.draw_card()
            elif self.nullify_context == "No Mercy":
                self.reset_choices_available()
                await self.send_update_message("No Mercy window offered")
                self.create_interrupt("No Mercy", self.first_player_nullified,
                                      (-1, -1, -1))
            elif self.nullify_context == "Fall Back":
                self.choices_available = []
                self.name_player_making_choices = self.first_player_nullified
                self.choice_context = "Target Fall Back:"
                for i in range(len(primary_player.stored_cards_recently_destroyed)):
                    card = FindCard.find_card(primary_player.stored_cards_recently_destroyed[i],
                                              self.card_array, self.cards_dict,
                                              self.apoka_errata_cards, self.cards_that_have_errata
                                              )
                    if card.check_for_a_trait("Elite") and card.get_is_unit():
                        self.choices_available.append(card.get_name())
            elif self.nullify_context == "The Emperor Protects":
                self.name_player_making_choices = self.first_player_nullified
                self.choice_context = "Target The Emperor Protects:"
                self.choices_available = primary_player.stored_targets_the_emperor_protects
            elif self.nullify_context == "Made Ta Fight":
                self.name_player_making_choices = self.first_player_nullified
                self.choice_context = "Target Made Ta Fight:"
                self.choices_available = primary_player.stored_targets_the_emperor_protects
            elif self.nullify_context == "Launch da Snots":
                primary_player.spend_resources(1)
                extra_attack = primary_player.count_copies_at_planet(self.attacker_planet,
                                                                     "Snotlings")
                primary_player.increase_attack_of_unit_at_pos(self.attacker_planet,
                                                              self.attacker_position,
                                                              extra_attack, expiration="NEXT")
                attack_name = primary_player.get_name_given_pos(self.attacker_planet,
                                                                self.attacker_position)
                await self.send_update_message(
                    attack_name + " gained " + str(extra_attack)
                    + " ATK from Launch Da Snots!"
                )
                primary_player.discard_card_name_from_hand("Launch da Snots")
        else:
            secondary_player.resolve_reactions_on_cancelling_enemy_effect()
            if self.nullifying_storm_of_silence:
                print("got to correct SoS Nullify")
                primary_player.discard_card_name_from_hand("Storm of Silence")
                primary_player.spend_resources(2)
                self.reset_choices_available()
                self.nullifying_storm_of_silence = False
                new_string_list = self.nullify_string.split(sep="/")
                print("String used:", new_string_list)
                resolve_nullify_discard = False
                await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
                while self.nullify_count > 0:
                    card_name_p1 = "Nullify"
                    if self.p1.castellan_crowe_relevant:
                        card_name_p1 = "Psychic Ward"
                    card_name_p2 = "Nullify"
                    if self.p2.castellan_crowe_relevant:
                        card_name_p2 = "Psychic Ward"
                    if self.name_player_using_backlash == self.name_1:
                        card_pos_discard = self.p2.discard_card_name_from_hand(card_name_p2)
                        if self.p2.aiming_reticle_coords_hand is not None:
                            if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                                self.p2.aiming_reticle_coords_hand -= 1
                        self.nullify_count -= 1
                        if self.nullify_count > 0:
                            card_pos_discard = self.p1.discard_card_name_from_hand(card_name_p1)
                            if self.p1.aiming_reticle_coords_hand is not None:
                                if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                                    self.p1.aiming_reticle_coords_hand -= 1
                            self.nullify_count -= 1
                    else:
                        card_pos_discard = self.p1.discard_card_name_from_hand(card_name_p1)
                        if self.p1.aiming_reticle_coords_hand is not None:
                            if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                                self.p1.aiming_reticle_coords_hand -= 1
                        self.nullify_count -= 1
                        if self.nullify_count > 0:
                            card_pos_discard = self.p2.discard_card_name_from_hand(card_name_p2)
                            if self.p2.aiming_reticle_coords_hand is not None:
                                if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                                    self.p2.aiming_reticle_coords_hand -= 1
                            self.nullify_count -= 1
            elif self.nullifying_backlash:
                primary_player.discard_card_name_from_hand("Backlash")
                if primary_player.urien_relevant:
                    primary_player.spend_resources(1)
                primary_player.spend_resources(1)
                self.reset_choices_available()
                self.nullifying_backlash = False
                new_string_list = self.nullify_string.split(sep="/")
                print("String used:", new_string_list)
                resolve_nullify_discard = False
                await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
                while self.nullify_count > 0:
                    card_name_p1 = "Nullify"
                    if self.p1.castellan_crowe_relevant:
                        card_name_p1 = "Psychic Ward"
                    card_name_p2 = "Nullify"
                    if self.p2.castellan_crowe_relevant:
                        card_name_p2 = "Psychic Ward"
                    if self.name_player_using_backlash == self.name_1:
                        card_pos_discard = self.p2.discard_card_name_from_hand(card_name_p2)
                        if self.p2.aiming_reticle_coords_hand is not None:
                            if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                                self.p2.aiming_reticle_coords_hand -= 1
                        self.nullify_count -= 1
                        if self.nullify_count > 0:
                            card_pos_discard = self.p1.discard_card_name_from_hand(card_name_p1)
                            if self.p1.aiming_reticle_coords_hand is not None:
                                if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                                    self.p1.aiming_reticle_coords_hand -= 1
                            self.nullify_count -= 1
                    else:
                        card_pos_discard = self.p1.discard_card_name_from_hand(card_name_p1)
                        if self.p1.aiming_reticle_coords_hand is not None:
                            if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                                self.p1.aiming_reticle_coords_hand -= 1
                        self.nullify_count -= 1
                        if self.nullify_count > 0:
                            card_pos_discard = self.p2.discard_card_name_from_hand(card_name_p2)
                            if self.p2.aiming_reticle_coords_hand is not None:
                                if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                                    self.p2.aiming_reticle_coords_hand -= 1
                            self.nullify_count -= 1
            elif self.nullify_context == "Foretell":
                print("\n\n!!CALLING FORETELL SPECIAL!!\n\n")
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Use Foretell?"
                self.name_player_making_choices = secondary_player.name_player
                await self.resolve_choice(secondary_player.name_player, ["CHOICE", "1"])
            else:
                if self.nullified_card_pos != -1:
                    primary_player.discard_card_from_hand(self.nullified_card_pos)
                    if self.card_pos_to_deploy > self.nullified_card_pos:
                        self.card_pos_to_deploy -= 1
                elif self.nullified_card_name != "":
                    primary_player.discard_card_name_from_hand(self.nullified_card_name)
                primary_player.spend_resources(self.cost_card_nullified)
                if self.nullify_context in self.alternative_shields:
                    self.pos_shield_card = -1
                elif self.nullify_context == "Reaction Event":
                    if self.nullified_card_name == "Cry of the Wind":
                        if primary_player.search_hand_for_card("Cry of the Wind"):
                            self.create_reaction("Cry of the Wind", primary_player.name_player,
                                                 (int(primary_player.number), -1, -1))
                    self.delete_reaction()
                elif self.nullify_context == "Reaction":
                    self.delete_reaction()
                elif self.nullify_context == "Interrupt":
                    self.delete_interrupt()
                elif self.nullify_context == "Interrupt Event":
                    self.delete_interrupt()
                elif self.nullify_context == "Win Battle Reaction Event":
                    if self.nullified_card_name in self.list_reactions_on_winning_combat:
                        if primary_player.search_hand_for_card(self.nullified_card_name):
                            self.create_reaction(self.nullified_card_name, primary_player.name_player,
                                                 (int(primary_player.number), -1, -1))
                    self.delete_reaction()
                elif self.nullify_context == "Event Action":
                    secondary_player.create_enemy_played_event_reactions()
                    primary_player.create_enemy_played_event_reactions()
                    self.action_cleanup()
                elif self.nullify_context == "In Play Action":
                    self.action_cleanup()
                if self.nullified_card_name == "Overrun":
                    primary_player.draw_card()
                    primary_player.draw_card()
                if self.nullified_card_name == "Breach and Clear":
                    primary_player.add_resources(2)
                primary_player.aiming_reticle_coords_hand = None
                primary_player.aiming_reticle_coords_hand_2 = None
        if resolve_nullify_discard:
            while self.nullify_count > 0:
                card_name_p1 = "Nullify"
                if self.p1.castellan_crowe_relevant:
                    card_name_p1 = "Psychic Ward"
                card_name_p2 = "Nullify"
                if self.p2.castellan_crowe_relevant:
                    card_name_p2 = "Psychic Ward"
                if self.first_player_nullified == self.name_1:
                    card_pos_discard = self.p2.discard_card_name_from_hand(card_name_p2)
                    if self.p2.aiming_reticle_coords_hand is not None:
                        if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                            self.p2.aiming_reticle_coords_hand -= 1
                    self.nullify_count -= 1
                    if self.nullify_count > 0:
                        card_pos_discard = self.p1.discard_card_name_from_hand(card_name_p1)
                        if self.p1.aiming_reticle_coords_hand is not None:
                            if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                                self.p1.aiming_reticle_coords_hand -= 1
                        self.nullify_count -= 1
                else:
                    card_pos_discard = self.p1.discard_card_name_from_hand(card_name_p1)
                    if self.p1.aiming_reticle_coords_hand is not None:
                        if self.p1.aiming_reticle_coords_hand > card_pos_discard:
                            self.p1.aiming_reticle_coords_hand -= 1
                    self.nullify_count -= 1
                    if self.nullify_count > 0:
                        card_pos_discard = self.p2.discard_card_name_from_hand(card_name_p2)
                        if self.p2.aiming_reticle_coords_hand is not None:
                            if self.p2.aiming_reticle_coords_hand > card_pos_discard:
                                self.p2.aiming_reticle_coords_hand -= 1
                        self.nullify_count -= 1
                if self.card_pos_to_deploy != -1 and (self.nullify_context == "Bigga Is Betta" or
                                                      self.nullify_context == "Optimized Landing"):
                    primary_player.aiming_reticle_coords_hand = self.card_pos_to_deploy
        self.nullify_count = 0
        if self.choice_context != "Use Interrupt?" and self.nullify_context != "Foretell":
            self.nullify_context = ""
            self.nullify_string = ""
            self.nullified_card_pos = -1
            self.nullified_card_name = ""
            self.cost_card_nullified = 0
            self.first_player_nullified = ""
        self.p1.num_nullify_played = 0
        self.p2.num_nullify_played = 0

    async def resolve_back_to_the_shadows(self, primary_player, secondary_player):
        pos_holder = self.positions_of_units_to_take_damage[0]
        player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
        primary_player.discard_card_from_hand(self.pos_shield_card)
        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
        self.pos_shield_card = -1
        self.retaliate_used = True
        primary_player.return_card_to_hand(planet_pos, unit_pos, return_attachments=True)
        primary_player.draw_card()
        await self.shield_cleanup(primary_player, secondary_player, planet_pos)

    async def resolve_i_do_not_serve(self, primary_player, secondary_player):
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

    async def complete_storm_of_silence(self, primary_player, secondary_player):
        self.reset_choices_available()
        primary_player.spend_resources(2)
        primary_player.discard_card_name_from_hand("Storm of Silence")
        primary_player.resolve_reactions_on_cancelling_enemy_effect()
        if self.storm_of_silence_friendly_unit:
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            if not primary_player.get_ready_given_pos(warlord_pla, warlord_pos):
                primary_player.ready_given_pos(warlord_pla, warlord_pos)
        if self.nullify_context == "Event Action":
            secondary_player.aiming_reticle_coords_hand = None
            secondary_player.aiming_reticle_coords_hand_2 = None
            if self.nullified_card_name == "Overrun":
                secondary_player.draw_card()
                secondary_player.draw_card()
            if self.nullified_card_name == "Breach and Clear":
                secondary_player.add_resources(2)
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
            self.position_of_actioned_card = (-1, -1)
        elif self.nullify_context == "Reaction":
            self.delete_reaction()
        elif self.nullify_context == "Reaction Event":
            self.delete_reaction()
            secondary_player.discard_card_name_from_hand(self.nullified_card_name)
        elif self.nullify_context == "Ferrin" or self.nullify_context == "Iridial":
            await self.resolve_battle_conclusion(secondary_player, game_string="")

    async def complete_backlash(self, primary_player, secondary_player):
        self.reset_choices_available()
        primary_player.spend_resources(1)
        primary_player.discard_card_name_from_hand("Backlash")
        if primary_player.urien_relevant:
            primary_player.spend_resources(1)
        print(self.nullified_card_name)
        print(self.nullify_context)
        primary_player.resolve_reactions_on_cancelling_enemy_effect()
        if self.nullify_context == "Event Action":
            if self.nullified_card_name == "Overrun":
                secondary_player.draw_card()
                secondary_player.draw_card()
            if self.nullified_card_name == "Breach and Clear":
                secondary_player.add_resources(2)
            secondary_player.aiming_reticle_coords_hand = None
            secondary_player.aiming_reticle_coords_hand_2 = None
            secondary_player.discard_card_name_from_hand(self.nullified_card_name)
            primary_player.create_enemy_played_event_reactions()
            secondary_player.create_enemy_played_event_reactions()
            self.action_cleanup()
        elif self.nullify_context == "In Play Action":
            secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                          self.position_of_actioned_card[1])
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
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
            secondary_player.create_enemy_played_event_reactions()
            primary_player.create_enemy_played_event_reactions()
        elif self.nullify_context == "Ferrin" or self.nullify_context == "Iridial":
            await self.resolve_battle_conclusion(secondary_player, game_string="")

    def mask_jain_zar_check_actions(self, primary_player, secondary_player):
        planet_pos, unit_pos = self.position_of_actioned_card
        if planet_pos != -1 and planet_pos != -2 and unit_pos != -1:
            if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                     (int(primary_player.number), planet_pos, unit_pos))

    def mask_jain_zar_check_interrupts(self, primary_player, secondary_player):
        num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
        if planet_pos != -1 and planet_pos != -2 and unit_pos != -1:
            if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                     (int(primary_player.number), planet_pos, unit_pos))

    def mask_jain_zar_check_reactions(self, primary_player, secondary_player):
        num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
        if planet_pos != -1 and planet_pos != -2 and unit_pos != -1:
            if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                     (int(primary_player.number), planet_pos, unit_pos))

    async def resolve_storm_of_silence(self, name, game_update_string, primary_player,
                                       secondary_player, may_nullify=True):
        if game_update_string[1] == "0":
            if secondary_player.nullify_check() and may_nullify:
                self.nullifying_storm_of_silence = True
                self.name_player_using_backlash = primary_player.name_player
                await self.send_update_message(
                    primary_player.name_player + " wants to play Storm of Silence; "
                                                 "Nullify window offered.")
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Nullify?"
            else:
                await self.complete_storm_of_silence(primary_player, secondary_player)
        elif game_update_string[1] == "1":
            self.reset_choices_available()
            self.storm_of_silence_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.storm_of_silence_enabled = True

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
            self.backlash_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.backlash_enabled = True

    async def resolve_colony_shield_generator(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.reset_choices_available()
            new_pos = -1
            for i in range(len(primary_player.headquarters)):
                if primary_player.get_ability_given_pos(-2, i) == "Colony Shield Generator":
                    if primary_player.get_ready_given_pos(-2, i):
                        primary_player.exhaust_given_pos(-2, i)
                        new_pos = i
            self.colony_shield_generator_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            if len(new_string_list) == 3:
                if new_pos != -1:
                    new_string_list[2] = str(new_pos)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.colony_shield_generator_enabled = True
        elif game_update_string[1] == "1":
            self.reset_choices_available()
            self.colony_shield_generator_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.colony_shield_generator_enabled = True

    async def resolve_slumbering_gardens(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.reset_choices_available()
            primary_player.exhaust_card_in_hq_given_name("Slumbering Gardens")
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
                self.position_of_actioned_card = (-1, -1)
            elif self.nullify_context == "Reaction":
                self.delete_reaction()
            elif self.nullify_context == "Reaction Event":
                self.delete_reaction()
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
            elif self.nullify_context == "Ferrin" or self.nullify_context == "Iridial":
                await self.resolve_battle_conclusion(secondary_player, game_string="")
        elif game_update_string[1] == "1":
            self.reset_choices_available()
            self.slumbering_gardens_enabled = False
            new_string_list = self.nullify_string.split(sep="/")
            print("String used:", new_string_list)
            await self.update_game_event(secondary_player.name_player, new_string_list, same_thread=True)
            self.slumbering_gardens_enabled = True

    async def resolve_immortal_loyalist(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.reset_choices_available()
            if self.nullify_context == "Event Action":
                secondary_player.aiming_reticle_coords_hand = None
                secondary_player.aiming_reticle_coords_hand_2 = None
                if self.nullified_card_name == "Overrun":
                    secondary_player.draw_card()
                    secondary_player.draw_card()
                if self.nullified_card_name == "Breach and Clear":
                    secondary_player.add_resources(2)
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
                self.position_of_actioned_card = (-1, -1)
            elif self.nullify_context == "Reaction":
                self.delete_reaction()
            elif self.nullify_context == "Reaction Event":
                self.delete_reaction()
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
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

    async def resolve_jain_zar(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.reset_choices_available()
            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
            primary_player.resolve_reactions_on_cancelling_enemy_effect()
            if warlord_pla != -2:
                primary_player.cards_in_play[warlord_pla + 1][warlord_pos].once_per_round_used = True
            if self.nullify_context == "Event Action":
                secondary_player.aiming_reticle_coords_hand = None
                secondary_player.aiming_reticle_coords_hand_2 = None
                if self.nullified_card_name == "Overrun":
                    secondary_player.draw_card()
                    secondary_player.draw_card()
                if self.nullified_card_name == "Breach and Clear":
                    secondary_player.add_resources(2)
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
                self.position_of_actioned_card = (-1, -1)
            elif self.nullify_context == "Reaction":
                self.delete_reaction()
            elif self.nullify_context == "Reaction Event":
                self.delete_reaction()
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
            elif self.nullify_context == "Interrupt":
                self.delete_interrupt()
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

    async def resolve_communications_relay(self, name, game_update_string, primary_player, secondary_player):
        if game_update_string[1] == "0":
            self.choices_available = []
            self.choice_context = ""
            self.name_player_making_choices = ""
            primary_player.exhaust_card_in_hq_given_name("Communications Relay")
            if self.nullify_context == "Event Action":
                secondary_player.aiming_reticle_coords_hand = None
                secondary_player.aiming_reticle_coords_hand_2 = None
                if self.nullified_card_name == "Overrun":
                    secondary_player.draw_card()
                    secondary_player.draw_card()
                if self.nullified_card_name == "Breach and Clear":
                    secondary_player.add_resources(2)
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
                self.position_of_actioned_card = (-1, -1)
            elif self.nullify_context == "Reaction":
                self.delete_reaction()
            elif self.nullify_context == "Reaction Event":
                self.delete_reaction()
                secondary_player.discard_card_name_from_hand(self.nullified_card_name)
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
        self.position_of_actioned_card = (-1, -1)
        self.omega_ambush_active = False
        self.sanguinary_ambush_active = False
        self.p1.harbinger_of_eternity_active = False
        self.p2.harbinger_of_eternity_active = False
        self.p1.waaagh_arbuttz_active = False
        self.p2.waaagh_arbuttz_active = False
        if self.phase == "DEPLOY":
            if self.number_with_deploy_turn == "1":
                self.player_with_deploy_turn = self.name_2
                self.number_with_deploy_turn = "2"
                self.p1.can_play_pledge = False
            elif self.number_with_deploy_turn == "2":
                self.player_with_deploy_turn = self.name_1
                self.number_with_deploy_turn = "1"
                self.p2.can_play_pledge = False

    def move_interrupt_to_front(self, interrupt_pos):
        if self.interrupts_waiting_on_resolution[interrupt_pos] == "Magus Harid":
            count_harid = -1
            i = 0
            while i < interrupt_pos:
                if self.interrupts_waiting_on_resolution[i] == "Magus Harid" \
                        and self.player_resolving_interrupts[0] == self.player_resolving_interrupts[i]:
                    count_harid += 1
                i += 1
            if count_harid < 0:
                count_harid = 0
            player = self.p1
            if self.player_resolving_interrupts[0] == self.name_2:
                player = self.p2
            player.magus_harid_waiting_cards.insert(0, player.magus_harid_waiting_cards.pop(count_harid))
        self.interrupts_waiting_on_resolution.insert(
            0, self.interrupts_waiting_on_resolution.pop(interrupt_pos)
        )
        self.player_resolving_interrupts.insert(
            0, self.player_resolving_interrupts.pop(interrupt_pos)
        )
        self.positions_of_units_interrupting.insert(
            0, self.positions_of_units_interrupting.pop(interrupt_pos)
        )
        self.extra_interrupt_info.insert(
            0, self.extra_interrupt_info.pop(interrupt_pos)
        )
        self.asking_if_interrupt = True

    def move_reaction_to_front(self, reaction_pos):
        if self.reactions_needing_resolving[reaction_pos] == "Ba'ar Zul the Hate-Bound":
            count_baar = 0
            i = 0
            while i < reaction_pos:
                if self.reactions_needing_resolving[i] == "Ba'ar Zul the Hate-Bound":
                    count_baar += 1
                i = i + 1
            self.damage_amounts_baarzul.insert(0, self.damage_amounts_baarzul.pop(count_baar))
        self.reactions_needing_resolving.insert(
            0, self.reactions_needing_resolving.pop(reaction_pos)
        )
        self.player_who_resolves_reaction.insert(
            0, self.player_who_resolves_reaction.pop(reaction_pos)
        )
        self.positions_of_unit_triggering_reaction.insert(
            0, self.positions_of_unit_triggering_reaction.pop(reaction_pos)
        )
        self.additional_reactions_info.insert(
            0, self.additional_reactions_info.pop(reaction_pos)
        )

        print(self.reactions_needing_resolving)
        self.asking_if_reaction = True

    async def create_necrons_wheel_choice(self, player):
        self.resolving_search_box = True
        self.choices_available = ["Space Marines", "Tau", "Eldar", "Dark Eldar",
                                  "Chaos", "Orks", "Astra Militarum"]
        self.name_player_making_choices = player.name_player
        self.choice_context = "Choose Enslaved Faction:"

    async def quick_battle_ability_resolution(self, name, game_update_string, winner, loser):
        self.reset_choices_available()
        if self.battle_ability_to_resolve == "Osus IV":
            if loser.spend_resources(1):
                winner.add_resources(1)
            await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Wounded Scream":
            if not self.wounded_scream_blanked:
                winner.add_resources(2)
                winner.draw_card()
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Blank Wounded Scream?"
                self.name_player_making_choices = winner.name_player
                self.resolving_search_box = True
            else:
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Jaricho":
            if self.phase != "COMBAT":
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Atrox Prime":
            self.atrox_origin = self.last_planet_checked_for_battle
            if self.different_atrox_origin != -1:
                self.atrox_origin = self.different_atrox_origin
        elif self.battle_ability_to_resolve == "Immortal Sorrows":
            self.choices_available = ["Brutal", "Armorbane"]
            self.choice_context = "Immortal Sorrows Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Hell's Theet":
            self.choices_available = ["Health", "Faith"]
            self.choice_context = "Hell's Theet Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Erekiel":
            self.choices_available = ["This Turn", "Next Turn"]
            self.choice_context = "Erekiel Choice"
            self.name_player_making_choices = loser.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Diamat":
            winner.total_indirect_damage = 2
            winner.indirect_damage_applied = 0
            self.location_of_indirect = "ALL"
            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
        elif self.battle_ability_to_resolve == "Gareth Prime":
            self.misc_target_unit = (-1, -1)
            self.player_resolving_battle_ability = loser.name_player
        elif self.battle_ability_to_resolve == "Selphini VII":
            self.chosen_first_card = False
            self.chosen_second_card = False
            self.player_resolving_battle_ability = loser.name_player
            self.misc_target_unit = (-1, -1)
            self.misc_target_player = ""
        elif self.battle_ability_to_resolve == "Chiros The Great Bazaar":
            self.choices_available = self.planets_removed_from_game
            self.choice_context = "Chiros The Great Bazaar Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "New Vulcan":
            warlord_pla, warlord_pos = winner.get_location_of_warlord()
            last_planet = self.determine_last_planet()
            if warlord_pla != last_planet:
                winner.move_unit_to_planet(warlord_pla, warlord_pos, last_planet)
            last_el_index = len(winner.cards_in_play[last_planet + 1]) - 1
            if last_el_index != -1:
                winner.exhaust_given_pos(last_planet, last_el_index)
            await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Hissan XI":
            self.player_resolving_battle_ability = loser.name_player
        elif self.battle_ability_to_resolve == "Josoon":
            self.chosen_first_card = False
        elif self.battle_ability_to_resolve == "Fenos":
            self.misc_target_unit = (-1, -1)
            self.chosen_first_card = False
        elif self.battle_ability_to_resolve == "Fortress World Garid":
            for _ in range(3):
                winner.draw_card()
        elif self.battle_ability_to_resolve == "Essio":
            self.misc_counter = 0
        elif self.battle_ability_to_resolve == "Heletine":
            num_cards = 4
            winner.add_resources(1)
            if num_cards > len(winner.deck):
                num_cards = len(winner.deck)
            if num_cards == 0:
                await self.resolve_battle_conclusion(name, game_update_string)
            else:
                self.choices_available = winner.deck[:num_cards]
                self.choices_available.append("Stop")
                self.choice_context = "Heletine Move"
                self.name_player_making_choices = winner.name_player
                self.resolving_search_box = True
                await self.send_update_message("Please choose which cards to put on the bottom of your deck.")
        elif self.battle_ability_to_resolve == "Ice World Hydras IV":
            found_card = False
            i = 0
            card_name = ""
            while i < len(winner.deck) and not found_card:
                card = self.preloaded_find_card(winner.deck[i])
                if card.get_card_type() == "Army":
                    found_card = True
                    card_name = card.get_name()
                i = i + 1
            if not card_name:
                await self.send_update_message("Did not find a valid card.")
                winner.shuffle_deck()
                await self.resolve_battle_conclusion(name, game_update_string)
            else:
                self.misc_target_choice = card_name
                card = self.preloaded_find_card(card_name)
                if card.get_cost() - 1 > winner.resources:
                    await self.send_update_message("Revealed a " + card_name + ". The card is too expensive!")
                    winner.shuffle_deck()
                    await self.resolve_battle_conclusion(name, game_update_string)
                else:
                    await self.send_update_message("Revealed a " + card_name + ". You may deploy this card.")
        elif self.battle_ability_to_resolve == "Agerath Minor":
            loser.add_resources(1)
            loser.draw_card()
            await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Tool of Abolition":
            self.choices_available = ["Exhaust", "Ready"]
            self.choice_context = "Tool of Abolition Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Petrified Desolations":
            self.choices_available = ["Heal", "Damage"]
            self.choice_context = "Petrified Desolations Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Barlus":
            interrupts = loser.search_triggered_interrupts_enemy_discard()
            if interrupts:
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = loser.name_player
                self.choice_context = "Interrupt Enemy Discard Effect?"
                self.resolving_search_box = True
                self.stored_discard_and_target.append(("Barlus", winner.number))
            else:
                loser.discard_card_at_random()
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Mangeras":
            self.misc_counter = 4
        elif self.battle_ability_to_resolve == "Contaminated World Adracan":
            self.misc_counter = 5
            self.misc_misc = []
            self.misc_target_planet = -1
            self.chosen_first_card = False
        elif self.battle_ability_to_resolve == "Craftworld Lugath":
            self.choices_available = ["Copy Adjacent", "Switch"]
            if self.last_planet_checked_for_battle == self.round_number:
                self.choices_available.remove("Switch")
            self.choice_context = "Craftworld Lugath Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Ironforge":
            self.chosen_first_card = False
            await self.send_update_message("You may move a unit to your HQ.")
        elif self.battle_ability_to_resolve == "Kunarog The Slave Market":
            self.choices_available = ["Cultist", "Guardsman", "Khymera", "Snotlings", "Termagant"]
            self.choice_context = "Kunarog The Slave Market Token"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Xenos World Tallin":
            self.chosen_first_card = False
            self.chosen_second_card = False
            self.misc_target_planet = -1
        elif self.battle_ability_to_resolve == "Frontier World Jaris":
            if len(winner.cards) < len(loser.cards):
                for _ in range(3):
                    winner.draw_card()
            await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Zarvoss Foundry":
            winner.number_cards_to_search = 8
            for i in range(len(winner.headquarters)):
                if winner.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                    if winner.headquarters[i].counter > 0:
                        winner.number_cards_to_search += 2
            if len(winner.deck) < winner.number_cards_to_search:
                winner.number_cards_to_search = len(winner.deck)
            self.choices_available = winner.deck[:winner.number_cards_to_search]
            if self.choices_available:
                self.choice_context = "Zarvoss Foundry Rally"
                self.name_player_making_choices = winner.name_player
                self.resolving_search_box = True
            else:
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Elouith":
            if len(winner.deck) > 2:
                winner.number_cards_to_search = 3
                for i in range(len(winner.headquarters)):
                    if winner.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                        if winner.headquarters[i].counter > 0:
                            winner.number_cards_to_search += 2
                self.cards_in_search_box = winner.deck[:winner.number_cards_to_search]
                self.name_player_who_is_searching = winner.name_player
                self.number_who_is_searching = str(winner.number)
                self.what_to_do_with_searched_card = "DRAW"
                self.traits_of_searched_card = None
                self.card_type_of_searched_card = None
                self.faction_of_searched_card = None
                self.max_cost_of_searched_card = None
                self.all_conditions_searched_card_required = False
                self.no_restrictions_on_chosen_card = True
            else:
                await self.send_update_message("Too few cards in deck for search")
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Clipped Wings":
            self.choices_available = ["Draw 1", "Discard to Draw 4"]
            self.choice_context = "Clipped Wings Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Beheaded Hope":
            self.choices_available = ["Return", "Deploy"]
            self.choice_context = "Beheaded Hope Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Freezing Tower":
            self.choices_available = ["Move", "Rout"]
            self.choice_context = "Freezing Tower Choice"
            self.name_player_making_choices = winner.name_player
            self.resolving_search_box = True
        elif self.battle_ability_to_resolve == "Navida Prime":
            self.choices_available = []
            for i in range(len(self.p1.victory_display)):
                self.choices_available.append(self.p1.victory_display[i].get_name())
            for i in range(len(self.p2.victory_display)):
                self.choices_available.append(self.p2.victory_display[i].get_name())
            if not self.choices_available:
                await self.resolve_battle_conclusion(name, game_update_string)
            else:
                self.choice_context = "Navida Prime Target"
                self.name_player_making_choices = winner.name_player
        elif self.battle_ability_to_resolve == "The Frozen Heart":
            self.choices_available = []
            for i in range(len(self.p1.victory_display)):
                self.choices_available.append(self.p1.victory_display[i].get_name())
            for i in range(len(self.p2.victory_display)):
                self.choices_available.append(self.p2.victory_display[i].get_name())
            if not self.choices_available:
                await self.resolve_battle_conclusion(name, game_update_string)
            else:
                self.choice_context = "The Frozen Heart Target"
                self.name_player_making_choices = winner.name_player
        elif self.battle_ability_to_resolve == "Anshan":
            winner.number_cards_to_search = len(winner.deck)
            if len(winner.deck) > 5:
                winner.number_cards_to_search = 6
                if len(winner.deck) > 7:
                    for i in range(len(winner.headquarters)):
                        if winner.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                            if winner.headquarters[i].counter > 0:
                                winner.number_cards_to_search += 2
            if winner.number_cards_to_search:
                self.cards_in_search_box = winner.deck[:winner.number_cards_to_search]
                self.name_player_who_is_searching = winner.name_player
                self.number_who_is_searching = str(winner.number)
                self.what_to_do_with_searched_card = "PLAY TO BATTLE"
                self.traits_of_searched_card = None
                self.card_type_of_searched_card = "Army"
                self.faction_of_searched_card = None
                self.max_cost_of_searched_card = 3
                self.no_restrictions_on_chosen_card = False
                self.all_conditions_searched_card_required = True
            else:
                await self.send_update_message("Too few cards in deck for search")
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Tarrus":
            winner_count = winner.count_units_in_play_all()
            loser_count = loser.count_units_in_play_all()
            if winner_count < loser_count:
                self.choices_available = ["Cards", "Resources"]
                self.choice_context = "Gains from Tarrus"
                self.name_player_making_choices = winner.name_player
            else:
                await self.resolve_battle_conclusion(name, game_update_string)
        elif self.battle_ability_to_resolve == "Beckel":
            await self.send_update_message("Please say your card name in the chat.")
            self.choices_available = ["Look At Hand."]
            self.choice_context = "Beckel Pause"
            self.name_player_making_choices = winner.name_player
        elif self.battle_ability_to_resolve == "Y'varn":
            self.yvarn_active = True
            self.p1_triggered_yvarn = False
            self.p2_triggered_yvarn = False
            self.reset_choices_available()
        elif self.battle_ability_to_resolve == "Excellor":
            self.misc_target_unit = (-1, -1)
            self.misc_target_player = ""
        elif self.battle_ability_to_resolve == "Vargus":
            self.misc_target_unit = (-1, -1)
            self.misc_target_player = ""
        elif self.battle_ability_to_resolve == "Jalayerid":
            self.misc_misc = []
            if self.last_planet_checked_for_battle != 0:
                if self.planets_in_play_array[self.last_planet_checked_for_battle - 1]:
                    self.misc_misc.append(self.last_planet_checked_for_battle - 1)
            if self.last_planet_checked_for_battle != 6:
                if self.planets_in_play_array[self.last_planet_checked_for_battle + 1]:
                    self.misc_misc.append(self.last_planet_checked_for_battle + 1)
            self.misc_misc.append(-2)
            self.misc_misc_2 = []

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
                        if not primary_player.harbinger_of_eternity_active:
                            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        primary_player.shuffle_deck()
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.choice_context == "Prototype Crisis Suit choices":
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.bottom_remaining_cards()
                    elif self.choice_context == "Agra's Preachings choices":
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.shuffle_deck()
                    elif self.choice_context == "Dark Allegiance Rally":
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.shuffle_deck()
                    elif self.choice_context == "Bork'an Sept Rally":
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.shuffle_deck()
                    elif self.choice_context == "Scheming Warlock Rally":
                        primary_player.bottom_remaining_cards()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        self.delete_reaction()
                    elif self.choice_context == "Support Fleet Rally":
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.shuffle_deck()
                    elif self.choice_context == "Prophetic Farseer Discard":
                        self.choice_context = "Prophetic Farseer Rearrange"
                    elif self.choice_context == "Prophetic Farseer Rearrange":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Morkanaut Rekuperator Rally":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.bottom_remaining_cards()
                        self.delete_reaction()
                    elif self.choice_context == "Krieg Armoured Regiment result:":
                        self.reset_choices_available()
                        self.delete_reaction()
                        self.resolving_search_box = False
                        primary_player.bottom_remaining_cards()
            if len(game_update_string) == 2:
                if game_update_string[0] == "CHOICE":
                    chosen_choice = self.choices_available[int(game_update_string[1])]
                    if self.choice_context == "Choose Which Interrupt":
                        print("\nGot to asking which interrupt\n")
                        self.asking_which_interrupt = False
                        interrupt_pos = int(game_update_string[1])
                        interrupt_pos = self.stored_interrupt_indexes[interrupt_pos]
                        self.move_interrupt_to_front(interrupt_pos)
                        self.has_chosen_to_resolve = False
                    elif self.choice_context == "Choose Which Reaction":
                        print("\nGot to asking which reaction\n")
                        self.asking_which_reaction = False
                        reaction_pos = int(game_update_string[1])
                        reaction_pos = self.stored_reaction_indexes[reaction_pos]
                        self.move_reaction_to_front(reaction_pos)
                        self.has_chosen_to_resolve = False
                    elif self.choice_context == "Increase or Decrease (WEB)?":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        await self.send_update_message("Select unit for World Engine Beam")
                    elif self.choice_context == "Amount of damage (WEB)":
                        amount_damage = int(self.choices_available[int(game_update_string[1])])
                        planet_pos, unit_pos = self.misc_target_unit
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, amount_damage, preventable=False,
                                                            by_enemy_unit=False)
                        player_with_web = self.misc_target_player
                        og_pla, og_pos = self.position_of_actioned_card
                        target_player = self.p2
                        if player_with_web == self.name_1:
                            target_player = self.p1
                        if self.misc_target_choice == "Increase":
                            target_player.headquarters[og_pos].counter += amount_damage
                        else:
                            target_player.headquarters[og_pos].counter = \
                                target_player.headquarters[og_pos].counter - amount_damage
                            if target_player.headquarters[og_pos].counter < 0:
                                target_player.headquarters[og_pos].counter = 0
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.action_cleanup()
                    elif self.choice_context == "Gauntlet of Fire":
                        if chosen_choice == "Change Enslavement":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.create_necrons_wheel_choice(primary_player)
                            self.action_cleanup()
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Beckel Gain":
                        if chosen_choice == "Yes":
                            primary_player.add_resources(1)
                        self.reset_choices_available()
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Beckel Pause":
                        message_to_send = "Cards in " + secondary_player.name_player + "'s hand: "
                        for i in range(len(secondary_player.cards)):
                            message_to_send += secondary_player.cards[i]
                            if i != len(secondary_player.cards) - 1:
                                message_to_send += ", "
                        message_to_send += ". Was the card you named in the hand?"
                        await self.send_update_message(message_to_send)
                        self.choice_context = "Beckel Gain"
                        self.choices_available = ["Yes", "No"]
                        self.name_player_making_choices = primary_player.name_player
                    elif self.choice_context == "Support Fleet Rally":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Attachment":
                            _, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                            primary_player.headquarters[unit_pos].attachments.append(card)
                            del primary_player.deck[int(game_update_string[1])]
                            primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                            self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
                            self.misc_counter = self.misc_counter - 1
                            if self.misc_counter < 1:
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                self.delete_reaction()
                                primary_player.bottom_remaining_cards()
                                primary_player.shuffle_deck()
                    elif self.choice_context == "The Dawn Blade Choice":
                        self.misc_target_choice = chosen_choice
                        self.reset_choices_available()
                    elif self.choice_context == "Support Fleet Transfer Target":
                        primary_player.cards.append(chosen_choice)
                        _, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                        del primary_player.headquarters[unit_pos].attachments[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Use which effect? (shield-likes)":
                        if chosen_choice == "Faith":
                            self.may_use_retaliate = False
                        if chosen_choice == "Retaliate":
                            self.may_use_faith = False
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        await self.better_shield_card_resolution(
                            primary_player.name_player, self.last_shield_string)
                        self.may_use_faith = True
                        self.may_use_retaliate = True
                    elif self.choice_context == "Nurgling Bomb Choice:":
                        planet, unit = self.misc_target_unit
                        primary_player.reset_aiming_reticle_in_play(planet, unit)
                        if game_update_string[1] == "0":
                            primary_player.cards_in_play[planet + 1][unit].need_to_resolve_nurgling_bomb = False
                            primary_player.cards_in_play[planet + 1][unit].choice_nurgling_bomb = "Rout"
                            await self.send_update_message(
                                "Will rout unit."
                            )
                        else:
                            primary_player.cards_in_play[planet + 1][unit].need_to_resolve_nurgling_bomb = False
                            primary_player.cards_in_play[planet + 1][unit].choice_nurgling_bomb = "Damage"
                            await self.send_update_message(
                                "Will damage unit."
                            )
                        self.reset_choices_available()
                        if not self.scan_planet_for_nurgling_bomb(primary_player, secondary_player, planet):
                            self.complete_nurgling_bomb(planet)
                    elif self.choice_context == "Prevent Psychic Ward?":
                        if game_update_string[1] == "0":
                            self.reset_choices_available()
                            pla, pos = primary_player.get_location_of_warlord()
                            primary_player.exhaust_given_pos(pla, pos)
                            pla, pos = secondary_player.get_location_of_warlord()
                            secondary_player.increase_faith_given_pos(pla, pos, 1)
                            secondary_player.discard_card_name_from_hand("Psychic Ward")
                            await self.complete_nullify()
                            self.nullify_count = 0
                        elif game_update_string[1] == "1":
                            self.reset_choices_available()
                            secondary_player.num_nullify_played += 1
                            self.nullify_count += 1
                            await self.complete_nullify()
                            self.nullify_count = 0
                    elif self.choice_context == "Use Psychic Ward?":
                        if game_update_string[1] == "0":
                            self.reset_choices_available()
                            pla, pos = secondary_player.get_location_of_warlord()
                            if secondary_player.get_ready_given_pos(pla, pos):
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Prevent Psychic Ward?"
                                self.choices_available = ["Yes", "No"]
                            else:
                                primary_player.num_nullify_played += 1
                                self.nullify_count += 1
                                await self.complete_nullify()
                                self.nullify_count = 0
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.complete_nullify()
                            self.nullify_count = 0
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
                    elif self.choice_context == "Quartermasters to HQ?":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if chosen_choice == "HQ":
                            self.card_to_deploy = self.preloaded_find_card("Quartermasters")
                            await DeployPhase.deploy_card_routine(self, name, -2, discounts=1)
                    elif self.choice_context == "The Orgiastic Feast Rally 2":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Army":
                            if card.get_cost() < 5:
                                self.misc_target_choice += "/" + card.get_name()
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                                del primary_player.deck[int(game_update_string[1])]
                                primary_player.bottom_remaining_cards()
                    elif self.choice_context == "The Orgiastic Feast Rally 1":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Army":
                            if card.get_cost() < 5:
                                self.choice_context = "The Orgiastic Feast Rally 2"
                                self.misc_target_choice = card.get_name()
                                primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                                del primary_player.deck[int(game_update_string[1])]
                                self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
                                if not self.choices_available:
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                    elif self.choice_context == "Putrescent Corpulence 1":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Attachment":
                            if card.check_for_a_trait("Blessing") or card.check_for_a_trait("Curse"):
                                self.choice_context = "Putrescent Corpulence 2"
                                self.misc_target_choice = card.get_name()
                                primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                                del primary_player.deck[int(game_update_string[1])]
                                primary_player.cards.append(card.get_name())
                                self.choices_available = primary_player.deck[:primary_player.number_cards_to_search]
                                if not self.choices_available:
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                    elif self.choice_context == "Putrescent Corpulence 2":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Attachment":
                            if card.check_for_a_trait("Blessing") or card.check_for_a_trait("Curse"):
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                                del primary_player.deck[int(game_update_string[1])]
                                primary_player.cards.append(card.get_name())
                                primary_player.bottom_remaining_cards()
                                secondary_player.create_enemy_played_event_reactions()
                                self.action_cleanup()
                    elif self.choice_context == "Garden of Solitude":
                        choice_pos = int(game_update_string[1])
                        if choice_pos == 0:
                            pass
                        else:
                            card_name = primary_player.deck[0]
                            primary_player.deck.append(card_name)
                            del primary_player.deck[0]
                        self.reset_choices_available()
                        self.action_cleanup()
                    elif self.choice_context == "Eldritch Council: Choose Card":
                        choice_pos = int(game_update_string[1])
                        if choice_pos == 0:
                            pass
                        else:
                            del self.choices_available[choice_pos]
                            choice_pos = choice_pos - 1
                            card_name = primary_player.deck[choice_pos]
                            primary_player.deck.append(card_name)
                            del primary_player.deck[choice_pos]
                        self.rearranging_deck = True
                        self.name_player_rearranging_deck = primary_player.name_player
                        self.deck_part_being_rearranged = primary_player.deck[:len(self.choices_available) - 1]
                        self.deck_part_being_rearranged.append("FINISH")
                        self.number_cards_to_rearrange = len(self.choices_available) - 1
                        self.choice_context = "Eldritch Council: Complete"
                        self.choices_available = ["Click to complete."]
                    elif self.choice_context == "Eldritch Council: Complete":
                        if len(primary_player.cards) < len(secondary_player.cards):
                            primary_player.draw_card()
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Choice Sacaellum Infestors":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                        planet_name = self.planet_array[planet_pos]
                        if chosen_choice == "Cards":
                            planet_card = FindCard.find_planet_card(planet_name, self.planet_cards_array)
                            for _ in range(planet_card.get_cards()):
                                primary_player.draw_card()
                        elif chosen_choice == "Resources":
                            planet_card = FindCard.find_planet_card(planet_name, self.planet_cards_array)
                            primary_player.add_resources(planet_card.get_resources())
                        self.resolving_search_box = False
                        self.reset_choices_available()
                        self.delete_reaction()
                    elif self.choice_context == "Raving Cryptek: Choose first card":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        del self.choices_available[int(game_update_string[1])]
                        self.choice_context = "Raving Cryptek: Choose second card"
                    elif self.choice_context == "Raving Cryptek: Choose second card":
                        second_choice = self.choices_available[int(game_update_string[1])]
                        self.choices_available = [second_choice, self.misc_target_choice]
                        await self.send_update_message(primary_player.name_player + " reveals " +
                                                       self.misc_target_choice + " and " + second_choice +
                                                       ". Please choose one to give +2 cost.")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Raving Cryptek: Increase cost"
                    elif self.choice_context == "Sacrifice Vamii Industrial Complex?":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        if chosen_choice == "No":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.delete_reaction()
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                            self.vamii_complex_discount = primary_player.headquarters[pos].counter
                            primary_player.sacrifice_card_in_hq(pos)
                    elif self.choice_context == "Raving Cryptek: Increase cost":
                        self.misc_target_choice = game_update_string[1]
                        if game_update_string[1] == "0":
                            await self.send_update_message(
                                "The first choice's (" + self.choices_available[int(game_update_string[1])] +
                                ") cost has been increased by two. Please choose which card to deploy."
                            )
                        elif game_update_string[1] == "1":
                            await self.send_update_message(
                                "The second choice's (" + self.choices_available[int(game_update_string[1])] +
                                ") cost has been increased by two. Please choose which card to deploy."
                            )
                        self.choice_context = "Raving Cryptek: Deploy choice"
                        self.name_player_making_choices = secondary_player.name_player
                    elif self.choice_context == "Scheming Warlock Rally":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_has_deepstrike():
                            primary_player.cards.append(card.get_name())
                            del primary_player.deck[int(game_update_string[1])]
                            primary_player.number_cards_to_search += -1
                            primary_player.bottom_remaining_cards()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                            self.delete_reaction()
                    elif self.choice_context == "The Broken Sigil Effect":
                        primary_player.broken_sigil_effect = chosen_choice
                        await self.send_update_message("The Broken Sigil effect selected. Try not to forget it!")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Raving Cryptek: Deploy choice":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        self.card_to_deploy = self.preloaded_find_card(target_choice)
                        card = self.card_to_deploy
                        self.discounts_applied = 0
                        if game_update_string[1] == self.misc_target_choice:
                            self.discounts_applied = -2
                        await self.calculate_available_discounts_unit(self.misc_target_planet, card, primary_player)
                        await self.calculate_automatic_discounts_unit(self.misc_target_planet, card, primary_player)
                        self.reset_choices_available()
                        if card.check_for_a_trait("Elite"):
                            primary_player.master_warpsmith_count = 0
                        if self.available_discounts > (self.discounts_applied + 2):
                            self.stored_mode = self.mode
                            self.mode = "DISCOUNT"
                            self.planet_aiming_reticle_position = self.misc_target_planet
                            self.planet_aiming_reticle_active = True
                        else:
                            await DeployPhase.deploy_card_routine(self, name, self.misc_target_planet,
                                                                  discounts=self.discounts_applied)
                    elif self.choice_context == "Radex Gain":
                        planet_pos, unit_pos = self.misc_target_unit
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        if planet_pos == -2:
                            if chosen_choice == "Armorbane":
                                primary_player.headquarters[unit_pos].armorbane_eog = True
                            elif chosen_choice == "Flying":
                                primary_player.headquarters[unit_pos].flying_eog = True
                            elif chosen_choice == "Mobile":
                                primary_player.headquarters[unit_pos].mobile_eog = True
                            elif chosen_choice == "Sweep (3)":
                                primary_player.headquarters[unit_pos].sweep_eog += 3
                            elif chosen_choice == "Retaliate (4)":
                                primary_player.headquarters[unit_pos].retaliate_eog += 4
                        else:
                            if chosen_choice == "Armorbane":
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].armorbane_eog = True
                            elif chosen_choice == "Flying":
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].flying_eog = True
                            elif chosen_choice == "Mobile":
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].mobile_eog = True
                            elif chosen_choice == "Sweep (3)":
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].sweep_eog += 3
                            elif chosen_choice == "Retaliate (4)":
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].retaliate_eog += 4
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Thundering Wraith Choice":
                        pla, pos = self.misc_target_unit
                        primary_player.reset_aiming_reticle_in_play(pla, pos)
                        if chosen_choice == "Rout Unit":
                            primary_player.rout_unit(pla, pos)
                        else:
                            primary_player.assign_damage_to_pos(pla, pos, 4)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
                        self.delete_reaction()
                    elif self.choice_context == "Mephiston Gains":
                        if chosen_choice == "Draw Card":
                            primary_player.draw_card()
                        else:
                            primary_player.add_resources(1)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.mask_jain_zar_check_interrupts(primary_player, secondary_player)
                        self.delete_interrupt()
                    elif self.choice_context == "Ready Vengeful Seraphim?":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        if chosen_choice == "Yes":
                            pass
                        else:
                            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                            self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Use WAAAGH! Arbuttz?":
                        if chosen_choice == "Yes":
                            primary_player.exhaust_card_in_hq_given_name("WAAAGH! Arbuttz")
                            primary_player.waaagh_arbuttz_active = True
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Interrupt Enemy Movement Effect?":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        num, og_pla, og_pos, dest = self.queued_moves[0]
                        del self.queued_moves[0]
                        if chosen_choice == "No Interrupt":
                            relevant_player = self.p1
                            if num == 2:
                                relevant_player = self.p2
                            relevant_player.move_unit_to_planet(og_pla, og_pos, dest, force=True, card_effect=False)
                        elif chosen_choice == "Strangleweb Termagant":
                            found_strangleweb = False
                            for i in range(len(primary_player.cards_in_play[og_pla + 1])):
                                if primary_player.get_ability_given_pos(og_pla, i) == "Strangleweb Termagant":
                                    if not found_strangleweb:
                                        found_strangleweb = True
                                        primary_player.exhaust_given_pos(og_pla, i)
                            if not found_strangleweb:
                                relevant_player = self.p1
                                if num == 2:
                                    relevant_player = self.p2
                                relevant_player.move_unit_to_planet(og_pla, og_pos, dest, force=True, card_effect=False)
                        if not self.queued_moves:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Interrupt Enemy Discard Effect?":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        if chosen_choice == "No Interrupt":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.interrupts_discard_enemy_allowed = False
                            await self.complete_enemy_discard(primary_player, secondary_player)
                            self.interrupts_discard_enemy_allowed = True
                        elif chosen_choice == "Scrying Pool":
                            primary_player.discard_card_name_from_hand("Scrying Pool")
                            primary_player.draw_card()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.name_player_making_choices = primary_player.name_player
                            self.interrupting_discard_effect_active = "Scrying Pool"
                            await self.send_update_message("Choose target for Scrying Pool.")
                        elif chosen_choice == "Hjorvath Coldstorm":
                            self.interrupting_discard_effect_active = "Hjorvath Coldstorm"
                            self.chosen_first_card = False
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.name_player_making_choices = primary_player.name_player
                        elif chosen_choice == "Shas'el Lyst":
                            self.choices_available = []
                            self.choice_context = "Target Planet Shas'el Lyst"
                            for i in range(len(self.planets_in_play_array)):
                                if self.planets_in_play_array[i]:
                                    self.choices_available.append(self.planet_array[i])
                            if not self.choices_available:
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                self.interrupts_discard_enemy_allowed = False
                                await self.complete_enemy_discard(primary_player, secondary_player)
                                self.interrupts_discard_enemy_allowed = True
                        elif chosen_choice == "Vale Tenndrac":
                            self.choices_available = []
                            self.choice_context = "Target Planet Vale Tenndrac"
                            for i in range(len(self.planets_in_play_array)):
                                if self.planets_in_play_array[i]:
                                    self.choices_available.append(self.planet_array[i])
                            if not self.choices_available:
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                self.interrupts_discard_enemy_allowed = False
                                await self.complete_enemy_discard(primary_player, secondary_player)
                                self.interrupts_discard_enemy_allowed = True
                        elif chosen_choice == "Blade of the Crimson Oath":
                            self.interrupting_discard_effect_active = "BCO"
                            self.chosen_first_card = False
                            await self.send_update_message("Please place 2 Guardsmen")
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.name_player_making_choices = primary_player.name_player
                    elif self.choice_context == "Target Planet Shas'el Lyst":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        i = 0
                        found_planet = False
                        while i < 7 and not found_planet:
                            if primary_player.cards_in_play[0][i] == chosen_choice:
                                found_planet = True
                                card = self.preloaded_find_card("Shas'el Lyst")
                                primary_player.add_card_to_planet(card, i)
                                primary_player.remove_card_name_from_hand("Shas'el Lyst")
                            i += 1
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.interrupts_discard_enemy_allowed = False
                        await self.complete_enemy_discard(primary_player, secondary_player)
                        self.interrupts_discard_enemy_allowed = True
                    elif self.choice_context == "Essio Spoils":
                        if chosen_choice == "Gain 2 Resources":
                            primary_player.add_resources(2)
                        else:
                            primary_player.draw_card()
                            primary_player.draw_card()
                        self.misc_counter = self.misc_counter - 1
                        if self.misc_counter < 1:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Daemon World Ivandis Healing":
                        amount_removed = int(chosen_choice)
                        target_player = self.p1
                        if self.misc_target_player == self.name_2:
                            target_player = self.p2
                        planet_pos, unit_pos = self.misc_target_unit
                        target_player.remove_damage_from_pos(planet_pos, unit_pos, amount_removed, healing=True)
                        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_bloodied_given_pos(warlord_pla, warlord_pos):
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "DWI: Make Warlord Hale?"
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "DWI: Make Warlord Hale?":
                        if chosen_choice == "Yes":
                            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                            primary_player.make_warlord_hale_given_pos(warlord_pla, warlord_pos)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Tras Replacement":
                        self.most_recently_revealed_planet = self.misc_target_planet
                        for i in range(len(primary_player.headquarters)):
                            if primary_player.get_ability_given_pos(-2, i) == "War Cabal":
                                self.create_reaction("War Cabal", primary_player.name_player,
                                                     (int(primary_player.number), -2, i))
                        for i in range(7):
                            if i != self.misc_target_planet:
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.get_ability_given_pos(i, j) == "War Cabal":
                                        self.create_reaction("War Cabal", primary_player.name_player,
                                                             (int(primary_player.number), i, j))
                        self.replaced_planets[self.misc_target_planet] = True
                        self.planet_array[self.misc_target_planet] = chosen_choice
                        self.available_breach_planets.remove(chosen_choice)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Mobilize the Chapter Reward:":
                        if chosen_choice == "Gain 1 Resource":
                            primary_player.add_resources(1)
                        else:
                            primary_player.draw_card()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "BaC: Sacrifice Attachment?":
                        if chosen_choice == "Sacrifice":
                            pass
                        else:
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "MtC Choose Trait:":
                        num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                        primary_player.headquarters[pos].misc_string = chosen_choice
                        await self.send_update_message("Mobilize the Chapter: Chose " + chosen_choice + " trait.")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "DA Choose Trait:":
                        num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                        primary_player.headquarters[pos].misc_string = chosen_choice
                        await self.send_update_message("Dark Allegiance: Chose " + chosen_choice + " trait.")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Big Mek Kagdrak Keyword":
                        primary_player.last_kagrak_trait = chosen_choice
                        target_player = primary_player
                        if self.misc_target_player != target_player.name_player:
                            target_player = secondary_player
                        planet_pos, unit_pos = self.misc_target_unit
                        if planet_pos == -2:
                            if chosen_choice == "Area Effect (1)":
                                target_player.headquarters[unit_pos].area_effect_eor += 1
                            elif chosen_choice == "Armorbane":
                                target_player.headquarters[unit_pos].armorbane_eor = True
                            elif chosen_choice == "Brutal":
                                target_player.headquarters[unit_pos].brutal_eor = True
                            elif chosen_choice == "Flying":
                                target_player.headquarters[unit_pos].flying_eor = True
                            elif chosen_choice == "Sweep (2)":
                                target_player.headquarters[unit_pos].sweep_eor += 2
                            elif chosen_choice == "Retaliate (3)":
                                target_player.headquarters[unit_pos].retaliate_eor += 3
                        else:
                            if chosen_choice == "Area Effect (1)":
                                target_player.cards_in_play[planet_pos + 1][unit_pos].area_effect_eor += 1
                            elif chosen_choice == "Armorbane":
                                target_player.cards_in_play[planet_pos + 1][unit_pos].armorbane_eor = True
                            elif chosen_choice == "Brutal":
                                target_player.cards_in_play[planet_pos + 1][unit_pos].brutal_eor = True
                            elif chosen_choice == "Flying":
                                target_player.cards_in_play[planet_pos + 1][unit_pos].flying_eor = True
                            elif chosen_choice == "Sweep (2)":
                                target_player.cards_in_play[planet_pos + 1][unit_pos].sweep_eor += 2
                            elif chosen_choice == "Retaliate (3)":
                                target_player.cards_in_play[planet_pos + 1][unit_pos].retaliate_eor += 3
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        og_pla, og_pos = self.position_of_actioned_card
                        primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
                    elif self.choice_context == "Vanguard Pack Payment":
                        if chosen_choice == "Give 1 resource":
                            primary_player.spend_resources(1)
                            secondary_player.add_resources(1)
                            target_planet = self.positions_of_unit_triggering_reaction[0][1]
                            i = 0
                            while i < len(secondary_player.attachments_at_planet[target_planet]):
                                if secondary_player.attachments_at_planet[target_planet][i].get_ability() == \
                                        "Vanguard Pack":
                                    secondary_player.cards.append("Vanguard Pack")
                                    del secondary_player.attachments_at_planet[target_planet][i]
                                    i = i - 1
                                i = i + 1
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Shaper Agnok Gains":
                        if chosen_choice == "Card":
                            primary_player.draw_card()
                        else:
                            primary_player.add_resources(1)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_interrupt()
                    elif self.choice_context == "Target Planet Vale Tenndrac":
                        i = 0
                        found_planet = False
                        while i < 7 and not found_planet:
                            if self.planet_array[i] == chosen_choice:
                                found_planet = True
                                card = self.preloaded_find_card("Vale Tenndrac")
                                primary_player.add_card_to_planet(card, i)
                                primary_player.draw_card()
                                primary_player.draw_card()
                                primary_player.remove_card_name_from_hand("Vale Tenndrac")
                            i += 1
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.interrupts_discard_enemy_allowed = False
                        await self.complete_enemy_discard(primary_player, secondary_player)
                        self.interrupts_discard_enemy_allowed = True
                    elif self.choice_context == "Interrupt Effect?":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        print("Choice chosen:", chosen_choice)
                        if chosen_choice == "No Interrupt":
                            self.reset_choices_available()
                            self.communications_relay_enabled = False
                            self.backlash_enabled = False
                            self.searing_brand_cancel_enabled = False
                            self.slumbering_gardens_enabled = False
                            self.colony_shield_generator_enabled = False
                            self.intercept_enabled = False
                            self.storm_of_silence_enabled = False
                            new_string_list = self.nullify_string.split(sep="/")
                            await self.update_game_event(secondary_player.name_player, new_string_list,
                                                         same_thread=True)
                            self.communications_relay_enabled = True
                            self.storm_of_silence_enabled = True
                            self.searing_brand_cancel_enabled = True
                            self.slumbering_gardens_enabled = True
                            self.colony_shield_generator_enabled = True
                            self.backlash_enabled = True
                            self.intercept_enabled = True
                        elif chosen_choice == "Communications Relay":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Communications Relay?"
                        elif chosen_choice == "Intercept":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Intercept?"
                        elif chosen_choice == "Jain Zar":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Jain Zar?"
                        elif chosen_choice == "Colony Shield Generator":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Colony Shield Generator?"
                        elif chosen_choice == "Slumbering Gardens":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Slumbering Gardens?"
                        elif chosen_choice == "Searing Brand":
                            self.choice_context = "Discard 2 Cards for Searing Brand?"
                            self.choices_available = ["Yes", "No"]
                        elif chosen_choice == "Backlash":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Backlash?"
                        elif chosen_choice == "Storm of Silence":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Storm of Silence?"
                        elif chosen_choice == "Immortal Loyalist":
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = "Use Immortal Loyalist?"
                    elif self.asking_if_interrupt and self.interrupts_waiting_on_resolution \
                            and not self.resolving_search_box:
                        print("Asking if interrupt")
                        self.asking_if_interrupt = False
                        if game_update_string[1] == "0":
                            self.has_chosen_to_resolve = True
                        elif game_update_string[1] == "1":
                            if self.interrupts_waiting_on_resolution[0] == "Ulthwe Spirit Stone":
                                num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
                                primary_player.discard_attachment_name_from_card(planet_pos, unit_pos,
                                                                                 "Ulthwe Spirit Stone")
                            elif self.interrupts_waiting_on_resolution[0] == "Slumbering Gardens Special":
                                num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
                                primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                            elif self.interrupts_waiting_on_resolution[0] == "Trazyn the Infinite":
                                num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
                                if planet_pos == -2:
                                    primary_player.headquarters[unit_pos].misc_ability_used = True
                                else:
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
                            elif self.interrupts_waiting_on_resolution[0] == "Catachan Devils Patrol" or \
                                    self.interrupts_waiting_on_resolution[0] == "Dodging Land Speeder":
                                self.shadow_thorns_body_allowed = False
                                _, current_planet, current_unit = self.last_defender_position
                                last_game_update_string = ["IN_PLAY", primary_player.get_number(),
                                                           str(current_planet),
                                                           str(current_unit)]
                                await CombatPhase.update_game_event_combat_section(
                                    self, secondary_player.name_player, last_game_update_string)
                            elif self.interrupts_waiting_on_resolution[0] == "Counterblow" or \
                                    self.interrupts_waiting_on_resolution[0] == "Trap Laying Hunter":
                                self.allow_damage_abilities_defender = False
                                self.shadow_thorns_body_allowed = False
                                _, current_planet, current_unit = self.last_defender_position
                                last_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                                           str(current_unit)]
                                await CombatPhase.update_game_event_combat_section(
                                    self, secondary_player.name_player, last_game_update_string)
                            self.resolving_search_box = False
                            self.delete_interrupt()
                        self.reset_choices_available()
                    elif self.choice_context == "Use Jain Zar?":
                        await self.resolve_jain_zar(name, game_update_string, primary_player, secondary_player)
                    elif self.choice_context == "Use Colony Shield Generator?":
                        await self.resolve_colony_shield_generator(name, game_update_string, primary_player,
                                                                   secondary_player)
                    elif self.choice_context == "Use Immortal Loyalist?":
                        await self.resolve_immortal_loyalist(name, game_update_string, primary_player, secondary_player)
                    elif self.choice_context == "Use Intercept?":
                        if game_update_string[1] == "0":
                            self.reset_choices_available()
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.get_ability_given_pos(-2, i) == "Intercept":
                                    if primary_player.get_ready_given_pos(-2, i):
                                        primary_player.exhaust_given_pos(-2, i)
                                        new_pos = i
                            self.intercept_active = True
                            self.name_player_intercept = primary_player.name_player
                        elif game_update_string[1] == "1":
                            self.reset_choices_available()
                            self.intercept_enabled = False
                            new_string_list = self.nullify_string.split(sep="/")
                            print("String used:", new_string_list)
                            await self.update_game_event(secondary_player.name_player, new_string_list,
                                                         same_thread=True)
                            self.intercept_enabled = True
                    elif self.choice_context == "Dark Lance Raider Damage":
                        self.misc_target_choice = chosen_choice
                        self.misc_misc = []
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Urien's Oubliette":
                        if game_update_string[1] == "0":
                            primary_player.discard_top_card_deck()
                            secondary_player.discard_top_card_deck()
                        else:
                            primary_player.draw_card()
                            secondary_player.draw_card()
                        self.action_cleanup()
                        self.reset_choices_available()
                    elif self.choice_context == "Anxious Infantry Platoon Payment":
                        if self.choices_available[int(game_update_string[1])] == "Pay resource":
                            if primary_player.spend_resources(1):
                                self.delete_reaction()
                                self.reset_choices_available()
                        else:
                            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                            primary_player.retreat_unit(planet_pos, unit_pos)
                            self.reset_choices_available()
                            self.delete_reaction()
                    elif self.choice_context == "Kunarog The Slave Market Token":
                        self.misc_target_choice = chosen_choice
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Rakarth's Experimentations card type":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        self.choices_available = ["Damage Warlord"]
                        for i in range(len(secondary_player.cards)):
                            card = FindCard.find_card(secondary_player.cards[i], self.card_array, self.cards_dict,
                                                      self.apoka_errata_cards, self.cards_that_have_errata)
                            if card.get_card_type() == self.misc_target_choice:
                                if card.get_name() not in self.choices_available:
                                    self.choices_available.append(card.get_name())
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Suffer Rakarth's Experimentations"
                    elif self.choice_context == "Chiros The Great Bazaar Choice":
                        self.battle_ability_to_resolve = chosen_choice
                        await self.send_update_message("Revealed " + chosen_choice)
                        self.choices_available = ["Yes", "No"]
                        self.choice_context = "Resolve Battle Ability?"
                        self.name_player_making_choices = name
                    elif self.choice_context == "Anshan own gains":
                        if chosen_choice == "Draw 1 card":
                            primary_player.draw_card()
                        else:
                            primary_player.add_resources(1)
                        self.choice_context = "Anshan opponent gains"
                    elif self.choice_context == "Cult of Duplicity":
                        if chosen_choice == "Duplicate":
                            if primary_player.spend_resources(1):
                                self.cult_duplicity_available = False
                                if self.misc_target_choice == "Health":
                                    self.misc_target_choice = "Faith"
                                    self.misc_counter = 5
                                elif self.misc_target_choice == "Faith":
                                    self.misc_target_choice = "Health"
                                elif self.misc_target_choice == "Ready":
                                    self.misc_target_choice = "Exhaust"
                                elif self.misc_target_choice == "Exhaust":
                                    self.misc_target_choice = "Ready"
                                elif self.misc_target_choice == "Return":
                                    self.misc_target_choice = "Deploy"
                                elif self.misc_target_choice == "Deploy":
                                    self.misc_target_choice = "Return"
                                elif self.misc_target_choice == "Heal":
                                    self.misc_target_choice = "Damage"
                                    self.misc_counter = 2
                                elif self.misc_target_choice == "Damage":
                                    self.misc_target_choice = "Heal"
                                    self.misc_counter = 3
                                elif self.misc_target_choice == "Rout":
                                    self.misc_target_choice = "Move"
                                elif self.misc_target_choice == "Move":
                                    self.misc_target_choice = "Rout"
                                elif self.misc_target_choice == "Draw 1":
                                    while primary_player.cards:
                                        primary_player.discard_card_from_hand(0)
                                    for _ in range(4):
                                        primary_player.draw_card()
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    await self.resolve_battle_conclusion(name, game_update_string)
                                elif self.misc_target_choice == "Discard to Draw 4":
                                    primary_player.draw_card()
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    await self.resolve_battle_conclusion(name, game_update_string)
                                elif self.misc_target_choice == "Brutal":
                                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                                    if warlord_pla == -2:
                                        primary_player.headquarters[warlord_pos].armorbane_eog = True
                                    else:
                                        primary_player.cards_in_play[warlord_pla + 1][warlord_pos].armorbane_eog = True
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    await self.resolve_battle_conclusion(name, game_update_string)
                                elif self.misc_target_choice == "Armorbane":
                                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                                    if warlord_pla == -2:
                                        primary_player.headquarters[warlord_pos].brutal_eog = True
                                    else:
                                        primary_player.cards_in_play[warlord_pla + 1][warlord_pos].brutal_eog = True
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    await self.resolve_battle_conclusion(name, game_update_string)
                                else:
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    await self.resolve_battle_conclusion(name, game_update_string)
                            else:
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                await self.resolve_battle_conclusion(name, game_update_string)
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Cajivak the Hateful Choice":
                        if chosen_choice == "Draw 2":
                            primary_player.discard_card_name_from_hand("Cajivak the Hateful")
                            primary_player.draw_card()
                            primary_player.draw_card()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            if primary_player.search_hand_for_card("Cajivak the Hateful"):
                                self.create_interrupt("Cajivak the Hateful", primary_player.name_player,
                                                      (int(primary_player.number), -1, -1))
                            self.delete_interrupt()
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Heletine Move":
                        if chosen_choice == "Stop":
                            await self.send_update_message(
                                "Stopping; Please use the rearrange deck command to rearrange the deck.")
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.resolve_battle_conclusion(name, game_update_string)
                        else:
                            primary_player.deck.append(primary_player.deck[int(game_update_string[1])])
                            del primary_player.deck[int(game_update_string[1])]
                            del self.choices_available[int(game_update_string[1])]
                    elif self.choice_context == "Munitorum Support Take":
                        planet_pos, unit_pos = self.position_of_actioned_card
                        primary_player.return_attachment_to_hand(-2, unit_pos, int(game_update_string[1]))
                        self.player_with_action = ""
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Senatorum Directives Reassign":
                        planet_pos, unit_pos = self.misc_target_unit
                        if chosen_choice == "Reassign":
                            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, is_reassign=True,
                                                                by_enemy_unit=False)
                            _, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
                            primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                            self.amount_that_can_be_removed_by_shield[0] += -1
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if self.amount_that_can_be_removed_by_shield[0] < 1:
                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                            await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                    elif self.choice_context == "Access to the Black Library":
                        if not self.chosen_first_card:
                            self.misc_target_choice = chosen_choice
                            self.chosen_first_card = True
                            self.chosen_second_card = False
                            self.choices_available.remove(chosen_choice)
                        elif not self.chosen_second_card:
                            await self.send_update_message("Please decide which card to give your opponent.")
                            self.choices_available = [chosen_choice, self.misc_target_choice]
                            self.name_player_making_choices = secondary_player.name_player
                            self.chosen_second_card = True
                        else:
                            secondary_player.cards.append(chosen_choice)
                            secondary_player.deck.remove(chosen_choice)
                            secondary_player.shuffle_deck()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                    elif self.choice_context == "BTD: Last Planet or HQ?":
                        if primary_player.aiming_reticle_coords_hand is not None:
                            card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
                            if chosen_choice == "HQ":
                                if primary_player.add_to_hq(card):
                                    del primary_player.cards[primary_player.aiming_reticle_coords_hand]
                            else:
                                last_planet = -1
                                for i in range(7):
                                    if self.planets_in_play_array[i]:
                                        last_planet = i
                                if last_planet != -1:
                                    if primary_player.add_card_to_planet(card, last_planet):
                                        del primary_player.cards[primary_player.aiming_reticle_coords_hand]
                        elif primary_player.aiming_reticle_coords_discard is not None:
                            card = primary_player.get_card_in_discard(primary_player.aiming_reticle_coords_discard)
                            if chosen_choice == "HQ":
                                if primary_player.add_to_hq(card):
                                    del primary_player.discard[primary_player.aiming_reticle_coords_discard]
                            else:
                                last_planet = -1
                                for i in range(7):
                                    if self.planets_in_play_array[i]:
                                        last_planet = i
                                if last_planet != -1:
                                    if primary_player.add_card_to_planet(card, last_planet) != -1:
                                        del primary_player.discard[primary_player.aiming_reticle_coords_discard]
                        self.reset_choices_available()
                        primary_player.aiming_reticle_coords_hand = None
                        primary_player.aiming_reticle_coords_discard = None
                        self.resolving_search_box = False
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Munos Topdeck":
                        if chosen_choice == "Do Nothing":
                            pass
                        else:
                            primary_player.deck.append(primary_player.deck[0])
                            del primary_player.deck[0]
                        self.resolving_search_box = False
                        self.reset_choices_available()
                        self.delete_reaction()
                    elif self.choice_context == "Everlasting Rage: Amount":
                        self.misc_target_choice = chosen_choice
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Anshan opponent gains":
                        if chosen_choice == "Draw 1 card":
                            secondary_player.draw_card()
                        else:
                            secondary_player.add_resources(1)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Catachan Devils Patrol: make a choice":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        if chosen_choice == "Take Damage":
                            primary_player.assign_damage_to_pos(self.attacker_planet,
                                                                self.attacker_position, 2,
                                                                shadow_field_possible=True,
                                                                rickety_warbuggy=True)
                        else:
                            primary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
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
                        self.reset_choices_available()
                    elif self.choice_context == "CWA: Infest Planet?":
                        if chosen_choice == "Yes":
                            self.infest_planet(self.misc_target_planet, primary_player)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        for i in range(len(self.misc_misc)):
                            num, pla, pos = self.misc_misc[i]
                            if num == 1:
                                self.p1.assign_damage_to_pos(pla, pos, 1)
                            else:
                                self.p2.assign_damage_to_pos(pla, pos, 1)
                            self.damage_from_atrox = True
                        if not self.damage_from_atrox:
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Trap Laying Hunter Trap":
                        if chosen_choice == "3 Damage":
                            for i in range(7):
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.cards_in_play[i + 1][j].resolving_attack:
                                        primary_player.assign_damage_to_pos(i, j, 3, rickety_warbuggy=True)
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.delete_interrupt()
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.player_resolving_interrupts[0] = primary_player.name_player
                    elif self.choice_context == "SD: Change Enslavement?":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if chosen_choice == "Yes":
                            for i in range(len(primary_player.headquarters)):
                                if primary_player.get_ability_given_pos(-2, i) == "Sautekh Dynasty":
                                    primary_player.headquarters[i].cannot_ready_hq_phase = True
                            await self.create_necrons_wheel_choice(primary_player)
                        self.delete_reaction()
                    elif self.choice_context == "Pulsating Carapace choice":
                        if chosen_choice == "Infest planet":
                            self.infest_planet(self.misc_target_planet, primary_player)
                        else:
                            target_player = self.p1
                            if self.misc_target_player == 2:
                                target_player = self.p2
                            planet_pos, unit_pos = self.misc_target_unit
                            target_player.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                        self.resolving_search_box = False
                        self.reset_choices_available()
                    elif self.choice_context == "Discard card (CotS)":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        primary_player.add_card_to_discard(chosen_choice)
                        del primary_player.deck[int(game_update_string[1])]
                        del self.choices_available[int(game_update_string[1])]
                        self.choice_context = "Bottom card (CotS)"
                    elif self.choice_context == "Rout or Exhaust (SS)":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        planet_pos, unit_pos = self.misc_target_unit
                        if chosen_choice == "Rout":
                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                            primary_player.rout_unit(planet_pos, unit_pos)
                            if len(primary_player.cards_in_play[planet_pos + 1]) > unit_pos:
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                            elif not self.chosen_first_card:
                                if secondary_player.cards_in_play[planet_pos + 1]:
                                    secondary_player.set_aiming_reticle_in_play(planet_pos, 0, "red")
                                    self.chosen_first_card = True
                                    self.misc_target_unit = (planet_pos, 0)
                                    self.choices_available = ["Exhaust", "Rout"]
                                    self.choice_context = "Rout or Exhaust (SS)"
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.resolving_search_box = True
                                else:
                                    i = 0
                                    while i < len(primary_player.attachments_at_planet[planet_pos]):
                                        if primary_player.attachments_at_planet[planet_pos][
                                            i].get_ability() == "Supreme Strategist":
                                            primary_player.add_card_to_discard("Supreme Strategist")
                                            del primary_player.attachments_at_planet[planet_pos][i]
                                            i = i - 1
                                        i = i + 1
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    self.delete_reaction()
                            else:
                                i = 0
                                while i < len(secondary_player.attachments_at_planet[planet_pos]):
                                    if secondary_player.attachments_at_planet[planet_pos][i].get_ability() == \
                                            "Supreme Strategist":
                                        secondary_player.add_card_to_discard("Supreme Strategist")
                                        del secondary_player.attachments_at_planet[planet_pos][i]
                                        i = i - 1
                                    i = i + 1
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                self.delete_reaction()
                        elif chosen_choice == "Exhaust":
                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                            primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                            if len(primary_player.cards_in_play[planet_pos + 1]) > unit_pos + 1:
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos + 1, "red")
                                self.misc_target_unit = (planet_pos, unit_pos + 1)
                            elif not self.chosen_first_card:
                                if secondary_player.cards_in_play[planet_pos + 1]:
                                    secondary_player.set_aiming_reticle_in_play(planet_pos, 0, "red")
                                    self.chosen_first_card = True
                                    self.misc_target_unit = (planet_pos, 0)
                                    self.choices_available = ["Exhaust", "Rout"]
                                    self.choice_context = "Rout or Exhaust (SS)"
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.resolving_search_box = True
                                else:
                                    i = 0
                                    while i < len(primary_player.attachments_at_planet[planet_pos]):
                                        if primary_player.attachments_at_planet[planet_pos][
                                            i].get_ability() == "Supreme Strategist":
                                            primary_player.add_card_to_discard("Supreme Strategist")
                                            del primary_player.attachments_at_planet[planet_pos][i]
                                            i = i - 1
                                        i = i + 1
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    self.delete_reaction()
                            else:
                                i = 0
                                while i < len(secondary_player.attachments_at_planet[planet_pos]):
                                    if secondary_player.attachments_at_planet[planet_pos][i].get_ability() == \
                                            "Supreme Strategist":
                                        secondary_player.add_card_to_discard("Supreme Strategist")
                                        del secondary_player.attachments_at_planet[planet_pos][i]
                                        i = i - 1
                                    i = i + 1
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                self.delete_reaction()
                    elif self.choice_context == "Bottom card (CotS)":
                        primary_player.deck.append(chosen_choice)
                        del primary_player.deck[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.resolving_search_box = True
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        self.delete_reaction()
                    elif self.choice_context == "The Dawnsinger Choice":
                        if chosen_choice == "Lose 2 cards":
                            pass
                        else:
                            secondary_player.draw_card()
                            secondary_player.draw_card()
                            self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Lost in the Webway":
                        if chosen_choice == "Harlequin":
                            await self.send_update_message("Swapping Harlequins")
                            self.action_chosen = "Lost in the Webway Harlequin"
                        else:
                            await self.send_update_message("Opponent must swap two army units.")
                            self.action_chosen = "Lost in the Webway Opponent"
                            self.player_with_action = secondary_player.name_player
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Select new synapse (RSN):":
                        card = self.preloaded_find_card(chosen_choice)
                        primary_player.add_to_hq(card)
                        last_element_index = len(primary_player.headquarters) - 1
                        primary_player.allowed_units_rsn.remove(chosen_choice)
                        primary_player.headquarters[last_element_index].from_deck = False
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Deepstrike cards?":
                        if self.choices_available[int(game_update_string[1])] == "Yes":
                            await self.send_update_message("Please choose cards to deepstrike")
                            self.resolving_search_box = False
                            self.num_player_deepstriking = primary_player.number
                            self.name_player_deepstriking = primary_player.name_player
                            self.reset_choices_available()
                        else:
                            primary_player.has_passed = True
                            if not secondary_player.has_passed:
                                self.name_player_making_choices = secondary_player.name_player
                                await self.send_update_message(secondary_player.name_player + " can deepstrike")
                            if primary_player.has_passed and secondary_player.has_passed:
                                self.end_start_battle_deepstrike()
                                self.resolving_search_box = False
                                self.reset_choices_available()
                                primary_player.has_passed = False
                                secondary_player.has_passed = False
                                await self.send_update_message("Deepstrike is complete")
                                self.start_ranged_skirmish(self.last_planet_checked_for_battle)
                    elif self.choice_context == "Choose trait: (EtA)":
                        primary_player.etekh_trait = self.choices_available[int(game_update_string[1])]
                        await self.send_update_message("Granted the " + primary_player.etekh_trait + " trait.")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.action_cleanup()
                    elif self.choice_context == "Optimized Protocol from discard or hand?":
                        if chosen_choice == "Discard":
                            primary_player.remove_card_name_from_discard("Optimized Protocol")
                            primary_player.remove_card_from_game("Optimized Protocol")
                        else:
                            primary_player.remove_card_name_from_hand("Optimized Protocol")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Necrodermis from discard or hand?":
                        if chosen_choice == "Discard":
                            primary_player.remove_card_name_from_discard("Necrodermis")
                            primary_player.remove_card_from_game("Necrodermis")
                        else:
                            primary_player.remove_card_name_from_hand("Necrodermis")
                        num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                        if primary_player.played_necrodermis:
                            await self.send_update_message(
                                "----GAME END----"
                                "Victory for " + secondary_player.name_player + "; "
                                + primary_player.name_player + " played a second Necrodermis whilst "
                                + primary_player.name_player + "already has one active."
                                                               "----GAME END----"
                            )
                            await self.send_victory_proper(secondary_player.name_player, "Necrodermis")
                        elif secondary_player.played_necrodermis:
                            await self.send_update_message(
                                "----GAME END----"
                                "Victory for " + primary_player.name_player + "; "
                                + primary_player.name_player + " played a second Necrodermis whilst "
                                + secondary_player.name_player + "already has one active."
                                                                 "----GAME END----"
                            )
                            await self.send_victory_proper(primary_player.name_player, "Necrodermis")
                        primary_player.played_necrodermis = True
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_interrupt()
                    elif self.choice_context == "Surrogate Host from discard or hand?":
                        if chosen_choice == "Discard":
                            primary_player.remove_card_name_from_discard("Surrogate Host")
                            primary_player.remove_card_from_game("Surrogate Host")
                        else:
                            primary_player.remove_card_name_from_hand("Surrogate Host")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Tempting Ceasefire Number":
                        if not self.chosen_first_card:
                            self.chosen_first_card = True
                            self.misc_target_choice = chosen_choice
                            self.name_player_making_choices = secondary_player.name_player
                        else:
                            owner_value = int(self.misc_target_choice)
                            enemy_value = int(chosen_choice)
                            diff = owner_value - enemy_value
                            for i in range(owner_value):
                                secondary_player.draw_card()
                            for i in range(enemy_value):
                                primary_player.draw_card()
                            if diff == 0:
                                secondary_player.draw_card()
                            elif diff < 0:
                                if primary_player.spend_resources(-diff):
                                    secondary_player.add_resources(-diff)
                            elif diff > 0:
                                primary_player.add_resources(diff)
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                    elif self.choice_context == "Eldritch Reaping: Enemy Announce":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        await self.send_update_message(primary_player.name_player + " selected " +
                                                       self.misc_target_choice + ".")
                        self.choice_context = "Eldritch Reaping: Own Announce"
                        self.name_player_making_choices = secondary_player.name_player
                        self.choices_available.remove(self.misc_target_choice)
                    elif self.choice_context == "Eldritch Reaping: Own Announce":
                        own_choice = self.choices_available[int(game_update_string[1])]
                        enemy_choice = self.misc_target_choice
                        if int(own_choice) > int(enemy_choice):
                            primary_player.draw_card()
                            primary_player.draw_card()
                            primary_player.add_resources(2)
                            primary_player.total_indirect_damage = int(own_choice)
                            primary_player.indirect_damage_applied = 0
                            self.valid_targets_for_indirect = ["Army", "Synapse", "Warlord", "Token"]
                            self.location_of_indirect = "ALL"
                        else:
                            secondary_player.total_indirect_damage = int(own_choice)
                            secondary_player.indirect_damage_applied = 0
                            self.valid_targets_for_indirect = ["Army", "Synapse", "Warlord", "Token"]
                            self.location_of_indirect = "ALL"
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                    elif self.choice_context == "WillSub: Draw Card for Damage?":
                        if chosen_choice == "Yes":
                            self.chosen_first_card = False
                            self.player_who_resolves_reaction[0] = primary_player.name_player
                        else:
                            self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Morkanaut Rekuperator Rally":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Attachment":
                            if not card.planet_attachment:
                                _, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                                if primary_player.attach_card(card, planet_pos, unit_pos):
                                    del primary_player.deck[int(game_update_string[1])]
                                    primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                                    primary_player.bottom_remaining_cards()
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    self.delete_reaction()
                    elif self.choice_context == "Immortal Sorrows Choice":
                        self.misc_target_choice = chosen_choice
                        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                        if warlord_pla == -2:
                            if chosen_choice == "Armorbane":
                                primary_player.headquarters[warlord_pos].armorbane_eog = True
                            else:
                                primary_player.headquarters[warlord_pos].brutal_eog = True
                        else:
                            if chosen_choice == "Armorbane":
                                primary_player.cards_in_play[warlord_pla + 1][warlord_pos].armorbane_eog = True
                            else:
                                primary_player.cards_in_play[warlord_pla + 1][warlord_pos].brutal_eog = True
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Hell's Theet Choice":
                        self.misc_target_choice = chosen_choice
                        if chosen_choice == "Faith":
                            self.misc_counter = 5
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Erekiel Choice":
                        self.misc_target_choice = chosen_choice
                        if chosen_choice == "This Turn":
                            self.misc_counter = 4
                            self.player_resolving_battle_ability = primary_player.name_player
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if chosen_choice == "Next Turn":
                            primary_player.erekiels_queued += 1
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Blank Wounded Scream?":
                        if chosen_choice == "Yes":
                            self.wounded_scream_blanked = True
                            await self.send_update_message("Wounded Scream was blanked.")
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Tool of Abolition Choice":
                        self.misc_target_choice = chosen_choice
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Petrified Desolations Choice":
                        self.misc_target_choice = chosen_choice
                        if chosen_choice == "Heal":
                            self.misc_counter = 3
                        else:
                            self.misc_counter = 2
                        self.misc_misc = []
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Clipped Wings Choice":
                        self.misc_target_choice = chosen_choice
                        if chosen_choice == "Draw 1":
                            primary_player.draw_card()
                        else:
                            while primary_player.cards:
                                primary_player.discard_card_from_hand(0)
                            for _ in range(4):
                                primary_player.draw_card()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        another_trigger = False
                        if primary_player.resources > 0 and self.cult_duplicity_available:
                            if self.replaced_planets[self.last_planet_checked_for_battle]:
                                if primary_player.search_card_in_hq("Cult of Duplicity"):
                                    another_trigger = True
                        if another_trigger:
                            self.choices_available = ["Duplicate", "Pass"]
                            self.choice_context = "Cult of Duplicity"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                        else:
                            await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Freezing Tower Choice":
                        self.misc_target_choice = chosen_choice
                        self.chosen_first_card = False
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Beheaded Hope Choice":
                        self.misc_target_choice = chosen_choice
                        self.chosen_first_card = False
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Krieg Armoured Regiment result:":
                        card_name = self.choices_available[int(game_update_string[1])]
                        card = self.preloaded_find_card(card_name)
                        if card.get_is_unit():
                            if card.check_for_a_trait("Tank") or card.check_for_a_trait("Vehicle") or \
                                    card.check_for_a_trait("Krieg"):
                                if card_name != "Krieg Armoured Regiment":
                                    num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                                    primary_player.add_card_to_planet(card, planet_pos)
                                    del primary_player.deck[int(game_update_string[1])]
                                    self.reset_choices_available()
                                    self.resolving_search_box = False
                                    primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                                    primary_player.bottom_remaining_cards()
                                    self.delete_reaction()
                    elif self.choice_context == "Zarvoss Foundry Rally":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Support":
                            primary_player.add_to_hq(card)
                            del primary_player.deck[int(game_update_string[1])]
                            primary_player.bottom_remaining_cards()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.resolve_battle_conclusion(name, game_update_string)
                        elif card.get_card_type() == "Attachment":
                            self.misc_player_storage = chosen_choice
                            del primary_player.deck[int(game_update_string[1])]
                            primary_player.bottom_remaining_cards()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Sacrifice Convent Prioris Advisor?":
                        if self.choices_available[int(game_update_string[1])] == "Yes":
                            i = 0
                            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                            while i < len(self.reactions_needing_resolving):
                                if i != 0:
                                    if self.reactions_needing_resolving[i] == "Convent Prioris Advisor":
                                        if self.player_who_resolves_reaction[i] == primary_player.name_player:
                                            del self.reactions_needing_resolving[i]
                                            del self.player_who_resolves_reaction[i]
                                            del self.positions_of_unit_triggering_reaction[i]
                                            del self.additional_reactions_info[i]
                                            i = i - 1
                                i = i + 1
                            primary_player.sacrifice_card_in_hq_given_name("Convent Prioris Advisor")
                            self.reset_choices_available()
                            self.delete_reaction()
                            self.resolving_search_box = True
                            primary_player.number_cards_to_search = 6
                            if len(primary_player.deck) > 5:
                                self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                            else:
                                self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = primary_player.number
                            self.what_to_do_with_searched_card = "DRAW"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = "Support"
                            self.faction_of_searched_card = None
                            self.no_restrictions_on_chosen_card = False
                            self.all_conditions_searched_card_required = True
                        else:
                            self.delete_reaction()
                            self.resolving_search_box = False
                            self.reset_choices_available()
                    elif self.choice_context == "Ymgarl Factor gains:":
                        planet_pos, unit_pos = self.misc_target_unit
                        if self.choices_available[int(game_update_string[1])] == "+2 ATK":
                            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, expiration="EOP")
                            if planet_pos == -2:
                                current_attack = primary_player.headquarters[unit_pos].extra_attack_until_end_of_phase
                            else:
                                current_attack = primary_player.cards_in_play[planet_pos + 1][unit_pos] \
                                    .extra_attack_until_end_of_phase
                            await self.send_update_message("Gained +2 ATK! Now has +" + str(current_attack) + " ATK.")
                        elif self.choices_available[int(game_update_string[1])] == "+2 HP":
                            if planet_pos == -2:
                                primary_player.headquarters[unit_pos].positive_hp_until_eop += 2
                                current_health = primary_player.headquarters[unit_pos].positive_hp_until_eop
                            else:
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].positive_hp_until_eop += 2
                                current_health = primary_player.cards_in_play[planet_pos + 1][unit_pos]. \
                                    positive_hp_until_eop
                            await self.send_update_message("Gained +2 HP! Now has +" + str(current_health) + " HP.")
                        self.action_cleanup()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Suffer Rakarth's Experimentations":
                        if game_update_string[1] == "0":
                            warlord_planet, warlord_pos = primary_player.get_location_of_warlord()
                            primary_player.assign_damage_to_pos(warlord_planet, warlord_pos, 1, by_enemy_unit=False)
                        else:
                            card_name = self.choices_available[int(game_update_string[1])]
                            primary_player.discard_card_name_from_hand(card_name)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                        await secondary_player.dark_eldar_event_played()
                        secondary_player.torture_event_played("Rakarth's Experimentations")
                    elif self.choice_context == "Which planet to add (DtC)":
                        self.misc_target_choice = self.choices_available[int(game_update_string[1])]
                        self.resolving_search_box = False
                        self.reset_choices_available()
                        await self.send_update_message("Choose planet to remove from play")
                    elif self.choice_context == "Sacrifice Hive Ship Tendrils?":
                        self.reset_choices_available()
                        self.chosen_first_card = False
                        if game_update_string[1] == "0":
                            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                            self.misc_counter = primary_player.headquarters[unit_pos].counter
                            primary_player.sacrifice_card_in_hq(unit_pos)
                        else:
                            self.delete_reaction()
                        self.resolving_search_box = False
                    elif self.choice_context == "Craftworld Lugath Choice":
                        self.misc_target_choice = chosen_choice
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Bork'an Sept Rally":
                        primary_player.cards.append(chosen_choice)
                        primary_player.deck.remove(chosen_choice)
                        await self.send_update_message("A " + chosen_choice + " was revealed.")
                        self.delete_reaction()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        primary_player.shuffle_deck()
                    elif self.choice_context == "Sweep Attack: Search which area?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Attachment from Deck: (Sweep Attack)"
                            for i in range(len(primary_player.deck)):
                                card_name = primary_player.deck[i]
                                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if card.get_card_type() == "Attachment" and card.check_for_a_trait("Condition"):
                                    if card_name not in self.choices_available:
                                        self.choices_available.append(card_name)
                            if not self.choices_available:
                                self.choices_available = ["Deck", "Discard"]
                                self.choice_context = "Sweep Attack: Search which area?"
                                await self.send_update_message("No cards in your deck are a valid target for "
                                                               "Sweep Attack. Please choose the discard.")
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Parasite of Mortrex: Search which area?":
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = "Attachment from Deck: (PoM)"
                            for i in range(len(primary_player.deck)):
                                card_name = primary_player.deck[i]
                                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if card.get_card_type() == "Attachment" and card.check_for_a_trait("Condition"):
                                    if card_name not in self.choices_available:
                                        self.choices_available.append(card_name)
                            if not self.choices_available:
                                self.choices_available = ["Deck", "Discard"]
                                self.choice_context = "Parasite of Mortrex: Search which area?"
                                await self.send_update_message("No cards in your deck are a valid target for "
                                                               "Parasite of Mortrex. Please choose the discard.")
                        else:
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Attachment from Deck: (Sweep Attack)":
                        self.misc_player_storage = self.choices_available[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.chosen_first_card = True
                        self.resolving_search_box = False
                        self.misc_counter = 0
                        await self.send_update_message("Attaching a " + self.misc_player_storage + ".")
                    elif self.choice_context == "Attachment from Deck: (PoM)":
                        self.misc_player_storage = self.choices_available[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.chosen_first_card = True
                        self.resolving_search_box = False
                        self.misc_counter = 0
                        await self.send_update_message("Attaching a " + self.misc_player_storage + ".")
                    elif self.choice_context == "Choose a new Synapse: (PotW)":
                        chosen_synapse = self.choices_available[int(game_update_string[1])]
                        card = FindCard.find_card(chosen_synapse, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
                        primary_player.add_to_hq(card)
                        og_pla, og_pos = self.position_of_actioned_card
                        primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                        self.action_cleanup()
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "Choose card to discard for Searing Brand":
                        primary_player.discard_card_from_hand(int(game_update_string[1]))
                        self.misc_counter += 1
                        self.choices_available = primary_player.cards
                        if self.misc_counter > 1:
                            secondary_player.discard_card_from_hand(secondary_player.aiming_reticle_coords_hand)
                            secondary_player.aiming_reticle_coords_hand = None
                            primary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                            self.reset_choices_available()
                    elif self.choice_context == "Searing Brand":
                        if game_update_string[1] == "0":
                            self.choices_available = primary_player.cards
                            self.misc_counter = 0
                            self.choice_context = "Choose card to discard for Searing Brand"
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.searing_brand_cancel_enabled = False
                            new_string_list = self.nullify_string.split(sep="/")
                            print("String used:", new_string_list)
                            await self.update_game_event(secondary_player.name_player, new_string_list,
                                                         same_thread=True)
                            self.searing_brand_cancel_enabled = True
                    elif self.choice_context == "Navida Prime Target":
                        self.battle_ability_to_resolve = chosen_choice
                        self.choices_available = ["Yes", "No"]
                        self.choice_context = "Resolve Battle Ability?"
                        self.name_player_making_choices = name
                    elif self.choice_context == "The Frozen Heart Target":
                        self.battle_ability_to_resolve = chosen_choice
                        self.choices_available = ["Yes", "No"]
                        self.choice_context = "Resolve Battle Ability?"
                        self.name_player_making_choices = name
                    elif self.choice_context == "Which Player? (Slake the Thirst):":
                        self.misc_target_choice = game_update_string[1]
                        self.choices_available = []
                        for i in range(len(self.p1.cards)):
                            if len(self.choices_available) < 4:
                                self.choices_available.append(str(i + 1))
                        self.choice_context = "How Many Cards? (Slake the Thirst):"
                    elif self.choice_context == "Overrun: Followup Rout?":
                        self.reset_choices_available()
                        if game_update_string[1] == "1":
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                    elif self.choice_context == "How Many Cards? (Slake the Thirst):":
                        num_cards = int(game_update_string[1]) + 1
                        if self.misc_target_choice == "0":
                            for _ in range(num_cards):
                                primary_player.discard_card_at_random()
                            for _ in range(num_cards):
                                primary_player.draw_card()
                        else:
                            for _ in range(num_cards):
                                secondary_player.discard_card_at_random()
                            for _ in range(num_cards):
                                secondary_player.draw_card()
                        await primary_player.dark_eldar_event_played()
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                        self.reset_choices_available()
                    elif self.choice_context == "Use Backlash?":
                        await self.resolve_backlash(name, game_update_string, primary_player, secondary_player)
                    elif self.choice_context == "Use Storm of Silence?":
                        await self.resolve_storm_of_silence(name, game_update_string, primary_player, secondary_player)
                    elif self.choice_context == "Use Communications Relay?":
                        await self.resolve_communications_relay(name, game_update_string,
                                                                primary_player, secondary_player)
                    elif self.choice_context == "Use Slumbering Gardens?":
                        await self.resolve_slumbering_gardens(name, game_update_string, primary_player,
                                                              secondary_player)
                    elif self.asking_if_reaction and self.reactions_needing_resolving \
                            and not self.resolving_search_box:
                        print("Asking if reaction")
                        self.asking_if_reaction = False
                        if game_update_string[1] == "0":
                            self.has_chosen_to_resolve = True
                        elif game_update_string[1] == "1":
                            if self.reactions_needing_resolving[0] == "Shadowed Thorns Bodysuit" or \
                                    self.reactions_needing_resolving[0] == "War Walker Squadron" or \
                                    self.reactions_needing_resolving[0] == "Fake Ooman Base" or \
                                    self.reactions_needing_resolving[0] == "Kaptin's Hook" or \
                                    self.reactions_needing_resolving[0] == "Dripping Scythes":
                                self.shadow_thorns_body_allowed = False
                                _, current_planet, current_unit = self.last_defender_position
                                last_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                                           str(current_unit)]
                                await CombatPhase.update_game_event_combat_section(
                                    self, secondary_player.name_player, last_game_update_string)
                            elif self.reactions_needing_resolving[0] == "Firedrake Terminators" or \
                                    self.reactions_needing_resolving[0] == "Rampaging Knarloc" or \
                                    self.reactions_needing_resolving[0] == "Neurotic Obliterator":
                                self.allow_damage_abilities_defender = False
                                self.shadow_thorns_body_allowed = False
                                _, current_planet, current_unit = self.last_defender_position
                                last_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                                           str(current_unit)]
                                await CombatPhase.update_game_event_combat_section(
                                    self, secondary_player.name_player, last_game_update_string)
                            self.resolving_search_box = False
                            self.delete_reaction()
                        self.reset_choices_available()
                    elif self.asking_if_remove_infested_planet:
                        if game_update_string[1] == "0":
                            self.infested_planets[self.last_planet_checked_for_battle] = False
                        self.asking_if_remove_infested_planet = False
                        self.already_asked_remove_infestation = True
                        await self.resolve_winning_combat(primary_player, secondary_player)
                    elif self.choice_context == "Use Foretell?":
                        if self.choices_available[int(game_update_string[1])] == "Yes":
                            primary_player.spend_foretell()
                            self.reset_choices_available()
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
                                    primary_player.name_player + " wants to play Foretell; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = -1
                                self.nullified_card_name = "Foretell"
                                self.cost_card_nullified = 0
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "Foretell"
                            else:
                                primary_player.draw_card()
                                await self.resolve_battle_conclusion(name, game_update_string)
                        else:
                            primary_player.foretell_permitted = False
                            self.choice_context = "Resolve Battle Ability?"
                            self.choices_available = ["Yes", "No"]
                            self.name_player_making_choices = self.player_using_battle_ability
                            await self.update_game_event(self.player_using_battle_ability, ["CHOICE", "0"], True)
                    elif self.choice_context == "Resolve Battle Ability?":
                        forced = False
                        if self.battle_ability_to_resolve in self.forced_battle_abilities:
                            forced = True
                        if self.choices_available[int(game_update_string[1])] == "Yes" or forced:
                            if self.choices_available[int(game_update_string[1])] != "Yes":
                                await self.send_update_message("The battle ability is forced.")
                            print("Wants to resolve battle ability")
                            if name == self.name_2:
                                winner = self.p2
                                loser = self.p1
                            else:
                                winner = self.p1
                                loser = self.p2
                            self.unit_to_move_position = (-1, -1)
                            self.player_using_battle_ability = winner.name_player
                            if winner.foretell_check():
                                self.choices_available = ["Yes", "No"]
                                self.choice_context = "Use Foretell?"
                                self.name_player_making_choices = winner.name_player
                                await self.send_update_message("Foretell window offered")
                            elif loser.foretell_check():
                                self.choices_available = ["Yes", "No"]
                                self.choice_context = "Use Foretell?"
                                self.name_player_making_choices = loser.name_player
                                await self.send_update_message("Foretell window offered")
                            else:
                                await self.quick_battle_ability_resolution(name, game_update_string, winner, loser)
                        else:
                            self.reset_choices_available()
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
                        self.reset_choices_available()
                        await self.resolve_battle_conclusion(name, game_update_string)
                    elif self.choice_context == "Amount to spend for Tzeentch's Firestorm:":
                        print(self.choices_available[int(game_update_string[1])])
                        if primary_player.spend_resources(int(game_update_string[1])):
                            self.amount_spend_for_tzeentch_firestorm = int(game_update_string[1])
                            self.reset_choices_available()
                    elif self.choice_context == "RT: Amount to Remove":
                        damage = int(chosen_choice)
                        _, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage, healing=True)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
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
                            self.resolving_search_box = False
                            await self.send_update_message(
                                "Both players setup, good luck and have fun!")
                            if self.p1.search_hand_for_card("Adaptative Thorax Swarm"):
                                self.create_reaction("Adaptative Thorax Swarm", self.name_1, (1, -1, -1))
                            if self.p2.search_hand_for_card("Adaptative Thorax Swarm"):
                                self.create_reaction("Adaptative Thorax Swarm", self.name_2, (2, -1, -1))
                            if self.p1.warlord_faction == "Necrons":
                                await self.create_necrons_wheel_choice(self.p1)
                            elif self.p2.warlord_faction == "Necrons":
                                await self.create_necrons_wheel_choice(self.p2)
                            await self.change_phase("DEPLOY")
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
                    elif self.choice_context == "Blood Axe Strategist Destination":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if game_update_string[1] == "0":
                            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                            primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                            self.delete_reaction()
                    elif self.choice_context == "Use Reanimating Warriors?":
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        if game_update_string[1] == "0":
                            self.chosen_first_card = False
                            self.asked_if_resolve_effect = True
                            self.misc_target_unit = (-1, -1)
                        if game_update_string[1] == "1":
                            self.delete_interrupt()
                    elif self.choice_context == "Prophetic Farseer Discard":
                        card_name = secondary_player.deck[int(game_update_string[1])]
                        card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
                        if card.get_shields() > 0:
                            secondary_player.add_card_to_discard(card_name)
                            del secondary_player.deck[int(game_update_string[1])]
                            del self.choices_available[int(game_update_string[1])]
                        if not self.choices_available:
                            self.reset_choices_available()
                            self.delete_reaction()
                    elif self.choice_context == "Prophetic Farseer Rearrange":
                        secondary_player.deck.insert(0, secondary_player.deck.pop(int(game_update_string[1])))
                        self.choices_available.insert(0, self.choices_available.pop(int(game_update_string[1])))
                    elif self.choice_context == "Retreat Warlord?":
                        if game_update_string[1] == "0":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.attack_being_resolved = False
                            primary_player.cards_in_play[self.attacker_planet + 1][self.attacker_position]. \
                                resolving_attack = False
                            primary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
                            primary_player.retreat_unit(self.attacker_planet, self.attacker_position)
                            self.reset_combat_positions()
                            self.number_with_combat_turn = secondary_player.get_number()
                            self.player_with_combat_turn = secondary_player.get_name_player()
                        elif game_update_string[1] == "1":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Absorb a planet:":
                        chosen_choice = self.choices_available[int(game_update_string[1])]
                        self.planets_removed_from_game.append(chosen_choice)
                        position_planet = -1
                        for i in range(len(primary_player.victory_display)):
                            if primary_player.victory_display[i].get_name() == chosen_choice:
                                position_planet = i
                        del primary_player.victory_display[position_planet]
                        self.resolving_search_box = False
                        await primary_player.send_victory_display()
                        self.reset_choices_available()
                    elif self.choice_context == "Target Dark Possession:":
                        primary_player.force_due_to_dark_possession = True
                        primary_player.cards.append(self.choices_available[int(game_update_string[1])])
                        primary_player.pos_card_dark_possession = len(primary_player.cards) - 1
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        await self.update_game_event_action(name, game_update_string)
                    elif self.choice_context == "Kabalite Blackguard Amount":
                        if game_update_string[1] == "0":
                            pass
                        elif game_update_string[1] == "1":
                            if secondary_player.spend_resources(1):
                                primary_player.add_resources(1)
                        elif game_update_string[1] == "2":
                            if secondary_player.spend_resources(2):
                                primary_player.add_resources(2)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        self.delete_reaction()
                    elif self.choice_context == "Deploy into reserve?":
                        if self.choices_available[int(game_update_string[1])] == "Normal Deploy":
                            self.deepstrike_allowed = False
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await DeployPhase.update_game_event_deploy_section(self, name, self.stored_deploy_string)
                            self.deepstrike_allowed = True
                            self.stored_deploy_string = []
                        else:
                            self.deepstrike_deployment_active = True
                            self.reset_choices_available()
                            self.resolving_search_box = False
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
                    elif self.choice_context == "Agra's Preachings choices":
                        card_name = primary_player.deck[int(game_update_string[1])]
                        card = self.preloaded_find_card(card_name)
                        if card.get_card_type() == "Army" and card.get_faction() == "Astra Militarum" and not \
                                card.check_for_a_trait("Elite"):
                            card_at_planet = CardClasses.AttachmentCard(
                                card_name, "", "", -1, "", "", -1, False, planet_attachment=True
                            )
                            primary_player.add_attachment_to_planet(self.misc_target_planet, card_at_planet)
                            del primary_player.deck[int(game_update_string[1])]
                            primary_player.number_cards_to_search = primary_player.number_cards_to_search - 1
                            primary_player.bottom_remaining_cards()
                            self.delete_reaction()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Prototype Crisis Suit choices":
                        num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                        card_name = primary_player.deck[int(game_update_string[1])]
                        card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
                        if card.get_card_type() == "Attachment" and card.get_faction() == "Tau":
                            if card.get_cost() < 3:
                                if primary_player.attach_card(card, planet_pos, unit_pos):
                                    del primary_player.deck[int(game_update_string[1])]
                                    self.misc_counter += 1
                                    if self.misc_counter == 1:
                                        self.choices_available = primary_player.deck[:8]
                                    else:
                                        self.delete_reaction()
                                        self.reset_choices_available()
                                        self.resolving_search_box = False
                                        primary_player.shuffle_deck()
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
                    elif self.choice_context == "Wisdom of the Serpent trait":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.resolving_search_box = True
                        self.what_to_do_with_searched_card = "DRAW"
                        self.traits_of_searched_card = target_choice
                        self.card_type_of_searched_card = "Army"
                        self.faction_of_searched_card = None
                        self.max_cost_of_searched_card = 99
                        self.all_conditions_searched_card_required = True
                        self.no_restrictions_on_chosen_card = False
                        primary_player.number_cards_to_search = 3
                        if len(primary_player.deck) > 2:
                            self.cards_in_search_box = \
                                primary_player.deck[:primary_player.number_cards_to_search]
                        else:
                            self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
                        self.name_player_who_is_searching = primary_player.name_player
                        self.number_who_is_searching = primary_player.number
                        self.action_cleanup()
                    elif self.choice_context == "Path of the Leader choice":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        self.resolving_search_box = False
                        self.reset_choices_available()
                        if target_choice == "Gain 1 Resource":
                            primary_player.add_resources(1)
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                        else:
                            self.chosen_first_card = False
                            self.action_chosen = target_choice
                    elif self.choice_context == "ND: Faction":
                        self.misc_misc.remove(chosen_choice)
                        self.choices_available = []
                        self.choice_context = "ND: Unit"
                        for i in range(len(self.card_array)):
                            if self.card_array[i].get_faction() == chosen_choice:
                                if self.card_array[i].get_loyalty() == "Common":
                                    if not self.card_array[i].get_has_deepstrike():
                                        if self.card_array[i].get_card_type() == "Army":
                                            self.choices_available.append(self.card_array[i].get_name())
                    elif self.choice_context == "ND: Unit":
                        self.misc_target_choice = chosen_choice
                        self.resolving_search_box = False
                        self.reset_choices_available()
                    elif self.choice_context == "Target Doom Scythe Invader:":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                        self.resolving_search_box = False
                        card = FindCard.find_card(target_choice, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
                        if primary_player.add_card_to_planet(card, pla) != -1:
                            position_of_unit = len(primary_player.cards_in_play[pla + 1]) - 1
                            primary_player.cards_in_play[pla + 1][position_of_unit]. \
                                valid_target_dynastic_weaponry = True
                            if "Dynastic Weaponry" in primary_player.discard:
                                if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                                    self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                                         (int(primary_player.get_number()), pla, position_of_unit))
                            if primary_player.optimized_protocol_check():
                                self.create_reaction("Optimized Protocol", primary_player.name_player,
                                                     (int(primary_player.get_number()), pla, position_of_unit))
                            primary_player.discard.remove(target_choice)
                        self.delete_reaction()
                        self.reset_choices_available()
                    elif self.choice_context == "Target Dread Monolith:":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        planet, pos = self.position_of_actioned_card
                        primary_player.reset_aiming_reticle_in_play(planet, pos)
                        card = FindCard.find_card(target_choice, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
                        if primary_player.add_card_to_planet(card, planet) != -1:
                            position_of_unit = len(primary_player.cards_in_play[planet + 1]) - 1
                            primary_player.cards_in_play[planet + 1][position_of_unit]. \
                                valid_target_dynastic_weaponry = True
                            if "Dynastic Weaponry" in primary_player.discard:
                                if not primary_player.check_if_already_have_reaction("Dynastic Weaponry"):
                                    self.create_reaction("Dynastic Weaponry", primary_player.name_player,
                                                         (int(primary_player.get_number()), planet, position_of_unit))
                            if primary_player.optimized_protocol_check():
                                self.create_reaction("Optimized Protocol", primary_player.name_player,
                                                     (int(primary_player.get_number()), planet, position_of_unit))
                            primary_player.discard.remove(target_choice)
                        self.reset_choices_available()
                        self.mask_jain_zar_check_actions(primary_player, secondary_player)
                        self.action_cleanup()
                    elif self.choice_context == "Visions of Agony Discard:":
                        secondary_player.discard_card_from_hand(int(game_update_string[1]))
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        secondary_player.create_enemy_played_event_reactions()
                        self.action_cleanup()
                        await primary_player.dark_eldar_event_played()
                        primary_player.torture_event_played("Visions of Agony")
                    elif self.choice_context == "War Walker Attach Exhaust":
                        target_attachment_name = self.choices_available[int(game_update_string[1])]
                        num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                        primary_player.exhaust_attachment_name_pos(planet_pos, unit_pos, target_attachment_name)
                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                        secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
                        self.reset_combat_positions()
                        self.shining_blade_active = False
                        self.number_with_combat_turn = primary_player.get_number()
                        self.player_with_combat_turn = primary_player.get_name_player()
                        self.attack_being_resolved = False
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
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
                                self.create_interrupt("No Mercy", name, (-1, -1, -1))
                                self.already_resolving_interrupt = True
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            await self.better_shield_card_resolution(
                                secondary_player.name_player, self.last_shield_string, alt_shields=False,
                                can_no_mercy=False)
                    elif self.choice_context == "First Line Rhinos Rally":
                        _, pla, pos = self.positions_of_unit_triggering_reaction[0]
                        card_name = self.choices_available[int(game_update_string[1])]
                        card = self.preloaded_find_card(card_name)
                        if card.get_faction() == "Space Marines" and card.get_card_type() == "Army" and not \
                                card.check_for_a_trait("Vehicle") and card.get_cost() < 4:
                            attachment_card = CardClasses.AttachmentCard(
                                card_name, "", "", 0, "Space Marines", "Common", 0, False)
                            attachment_card.from_front_line_rhinos = True
                            primary_player.attach_card(attachment_card, pla, pos)
                            del primary_player.deck[int(game_update_string[1])]
                            primary_player.bottom_remaining_cards()
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            self.delete_reaction()
                    elif self.choice_context == "Use Woken Machine Spirit?":
                        self.woken_machine_spirit_enabled = False
                        if game_update_string[1] == "0":
                            self.woken_machine_spirit_active = True
                            pos_holder = self.positions_of_units_to_take_damage[0]
                            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
                            primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                        else:
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                    elif self.choice_context == "Use Distorted Talos?":
                        self.distorted_talos_enabled = False
                        if game_update_string[1] == "0":
                            self.distorted_talos_active = True
                            pos_holder = self.positions_of_units_to_take_damage[0]
                            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
                            damage_total = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                            damage_removed = damage_total - self.amount_that_can_be_removed_by_shield[0]
                            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                            primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage_removed, healing=True)
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                        else:
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                    elif self.choice_context == "Use Maksim's Squadron?":
                        self.maksim_squadron_enabled = False
                        if game_update_string[1] == "0":
                            self.maksim_squadron_active = True
                            if self.apoka:
                                pos_holder = self.positions_of_units_to_take_damage[0]
                                player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
                                primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                                primary_player.draw_card()
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                        else:
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                    elif self.choice_context == "Use Guardian Mesh Armor?":
                        self.guardian_mesh_armor_enabled = False
                        num, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
                        primary_player.exhaust_attachment_name_pos(planet_pos, unit_pos, "Guardian Mesh Armor")
                        if game_update_string[1] == "0":
                            self.guardian_mesh_armor_active = True
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
                        else:
                            self.reset_choices_available()
                            await self.better_shield_card_resolution(
                                primary_player.name_player, self.last_shield_string, alt_shields=False)
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
                                                          self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
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
                                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
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
                                card = FindCard.find_card(secondary_player.discard[i], self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
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
                            card = FindCard.find_card(self.misc_target_choice, self.card_array, self.cards_dict,
                                                      self.apoka_errata_cards, self.cards_that_have_errata)
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
                    elif self.choice_context == "Target Made Ta Fight:":
                        target = self.choices_available[int(game_update_string[1])]
                        card = FindCard.find_card(target, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
                        self.misc_counter = card.attack
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    elif self.choice_context == "The Flayed Mask Choice:":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if chosen_choice == "Forgo Capture":
                            primary_player.flayed_mask_active = True
                            self.delete_reaction()
                        elif chosen_choice == "Sacrifice Unit":
                            self.player_who_resolves_reaction[0] = primary_player.name_player
                        else:
                            self.delete_reaction()
                            self.location_of_indirect = "ALL"
                            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
                            primary_player.indirect_damage_applied = 0
                            primary_player.total_indirect_damage = 5
                    elif self.choice_context == "Target The Emperor Protects:":
                        target = self.choices_available[int(game_update_string[1])]
                        primary_player.discard_card_name_from_hand("The Emperor Protects")
                        primary_player.cards.append(target)
                        try:
                            primary_player.stored_targets_the_emperor_protects.remove(target)
                            primary_player.discard.remove(target)
                            primary_player.stored_cards_recently_discarded.remove(target)
                            primary_player.stored_cards_recently_destroyed.remove(target)
                        except ValueError:
                            pass
                        self.choices_available = primary_player.stored_targets_the_emperor_protects
                        self.emp_protecc()
                        self.resolving_search_box = False
                        self.reset_choices_available()
                        self.delete_reaction()
                    elif self.choice_context == "Target Fall Back:":
                        primary_player.spend_resources(1)
                        if primary_player.urien_relevant:
                            primary_player.spend_resources(1)
                        target = self.choices_available[int(game_update_string[1])]
                        card = FindCard.find_card(target, self.card_array, self.cards_dict,
                                                  self.apoka_errata_cards, self.cards_that_have_errata)
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
                                                          self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if card.check_for_a_trait("Elite") and card.get_is_unit():
                                    self.choices_available.append(card.get_name())
                        if not self.choices_available:
                            self.resolving_search_box = False
                            self.reset_choices_available()
                            self.delete_reaction()
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
                    elif self.choice_context == "Keyword copied from Brood Chamber" or \
                            self.choice_context == "Evolutionary Adaptation":
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
                            if secondary_player.search_card_at_planet(hurt_planet, "The Mask of Jain Zar"):
                                self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                     (int(primary_player.number), hurt_planet, hurt_pos))
                            self.amount_that_can_be_removed_by_shield[0] -= 1
                        elif game_update_string[1] == "2":
                            self.damage_moved_to_old_one_eye += 2
                            primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 2)
                            primary_player.assign_damage_to_pos(old_one_planet, old_one_pos, 2,
                                                                can_shield=False, is_reassign=True)
                            if secondary_player.search_card_at_planet(hurt_planet, "The Mask of Jain Zar"):
                                self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                     (int(primary_player.number), hurt_planet, hurt_pos))
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
                                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if card.check_for_a_trait("Tzeentch", primary_player.etekh_trait):
                                    self.choices_available.append(card.get_name())
                            if not self.choices_available:
                                await self.send_update_message(
                                    "No valid targets for Shrine of Warpflame")
                                self.resolving_search_box = False
                        elif game_update_string[1] == "1":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                    elif self.choice_context == "Dark Allegiance Rally":
                        card = self.preloaded_find_card(chosen_choice)
                        if card.get_card_type() == "Attachment" or card.get_card_type() == "Army":
                            if card.check_for_a_trait(self.misc_target_choice):
                                self.card_to_deploy = card
                                del primary_player.deck[int(game_update_string[1])]
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                primary_player.number_cards_to_search += -1
                                primary_player.bottom_remaining_cards()
                    elif self.choice_context == "Myriad Excesses Correct":
                        planet_pos, unit_pos = self.misc_target_unit
                        if chosen_choice == "Take Control":
                            self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
                        elif chosen_choice == "Destroy":
                            secondary_player.destroy_card_in_play(planet_pos, unit_pos)
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        self.delete_reaction()
                    elif self.choice_context == "Damage Drifting Spore Mines?":
                        planet_pos, unit_pos = self.misc_target_unit
                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                        self.chosen_first_card = True
                        self.resolving_search_box = False
                        self.reset_choices_available()
                        if game_update_string[1] == "0":
                            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                        else:
                            self.delete_reaction()
                    elif self.choice_context == "Heavy Venom Cannon":
                        planet, unit, att = self.misc_target_attachment
                        self.choice_context = ""
                        self.choices_available = []
                        self.name_player_making_choices = ""
                        target_player = primary_player
                        if self.misc_target_player == secondary_player.name_player:
                            target_player = secondary_player
                        if game_update_string[1] == "0":
                            if planet == -2:
                                target_player.headquarters[unit].armorbane_eop = True
                                target_player.headquarters[unit].get_attachments()[att].set_once_per_phase_used(True)
                                name = target_player.headquarters[unit].get_name()
                                await self.send_update_message(
                                    name + " gained armorbane from Heavy Venom Cannon!"
                                )
                            else:
                                target_player.cards_in_play[planet + 1][unit].armorbane_eop = True
                                target_player.cards_in_play[planet + 1][unit].get_attachments()[
                                    att].set_once_per_phase_used(True)
                                name = target_player.cards_in_play[planet + 1][unit].get_name()
                                await self.send_update_message(
                                    name + " gained armorbane from Heavy Venom Cannon!"
                                )
                        elif game_update_string[1] == "1":
                            if planet == -2:
                                target_player.headquarters[unit].area_effect_eop += 2
                                target_player.headquarters[unit].get_attachments()[att].set_once_per_phase_used(True)
                                name = target_player.headquarters[unit].get_name()
                                await self.send_update_message(
                                    name + " gained area effect (2) from Heavy Venom Cannon!"
                                )
                            else:
                                target_player.cards_in_play[planet + 1][unit].area_effect_eop += 2
                                target_player.cards_in_play[planet + 1][unit].get_attachments()[att]. \
                                    set_once_per_phase_used(True)
                                name = target_player.cards_in_play[planet + 1][unit].get_name()
                                await self.send_update_message(
                                    name + " gained area effect (2) from Heavy Venom Cannon!"
                                )
                        self.action_cleanup()
                    elif self.choice_context == "Use Made Ta Fight?":
                        if game_update_string[1] == "0":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
                                    primary_player.name_player + " wants to play Made Ta Fight; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = -1
                                self.nullified_card_name = "Made Ta Fight"
                                self.cost_card_nullified = 2
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "Made Ta Fight"
                            else:
                                self.choices_available = primary_player.stored_targets_the_emperor_protects
                                self.choice_context = "Target Made Ta Fight:"
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            self.delete_reaction()
                    elif self.choice_context == "Use The Emperor Protects?":
                        if game_update_string[1] == "0":
                            if secondary_player.nullify_check() and self.nullify_enabled:
                                await self.send_update_message(
                                    primary_player.name_player + " wants to play The Emperor Protects; "
                                                                 "Nullify window offered.")
                                self.choices_available = ["Yes", "No"]
                                self.name_player_making_choices = secondary_player.name_player
                                self.choice_context = "Use Nullify?"
                                self.nullified_card_pos = -1
                                self.nullified_card_name = "The Emperor Protects"
                                self.cost_card_nullified = 0
                                self.nullify_string = "/".join(game_update_string)
                                self.first_player_nullified = primary_player.name_player
                                self.nullify_context = "The Emperor Protects"
                            else:
                                self.choices_available = primary_player.stored_targets_the_emperor_protects
                                self.choice_context = "Target The Emperor Protects:"
                        elif game_update_string[1] == "1":
                            primary_player.stored_targets_the_emperor_protects = []
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
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
                                                              self.card_array, self.cards_dict,
                                                              self.apoka_errata_cards, self.cards_that_have_errata)
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
                                                          self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
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
                                                          self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
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
                        elif self.choices_available[int(game_update_string[1])] == "Crushing Blow":
                            self.choice_context = "Use Crushing Blow?"
                            self.choices_available = ["Yes", "No"]
                        else:
                            self.auto_card_destruction = True
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                    elif self.choice_context == "Use Crushing Blow?":
                        planet_pos, unit_pos = self.furiable_unit_position
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.auto_card_destruction = True
                    elif self.choice_context == "Brutal Cunning: amount of damage":
                        if game_update_string[1] == "0":
                            self.misc_counter = 1
                        elif game_update_string[1] == "1":
                            self.misc_counter = 2
                        self.reset_choices_available()
                    elif self.choice_context == "Use The Fury of Sicarius?":
                        planet_pos, unit_pos = self.furiable_unit_position
                        if game_update_string[1] == "0":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                        elif game_update_string[1] == "1":
                            self.choices_available = []
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.auto_card_destruction = True
                    elif self.choice_context == "Use Liatha?":
                        if game_update_string[1] == "0":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.better_shield_card_resolution(name, self.last_shield_string, alt_shields=False)
                        else:
                            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                            current_val = primary_player.get_once_per_phase_used_given_pos(warlord_pla, warlord_pos)
                            if not current_val:
                                current_val = 0
                            primary_player.set_once_per_phase_used_given_pos(warlord_pla, warlord_pos, current_val + 1)
                            await self.send_update_message("Liatha is being used. The card may be flipped.")
                            self.choice_context = "Flip Liatha?"
                            self.choices_available = ["Pass", "Flip"]
                            self.name_player_making_choices = secondary_player.name_player
                            self.liatha_active = True
                    elif self.choice_context == "Flip Liatha?":
                        if game_update_string[1] == "0":
                            self.reset_choices_available()
                            self.resolving_search_box = False
                            await self.better_shield_card_resolution(
                                secondary_player.name_player, self.last_shield_string, alt_shields=False)
                        else:
                            card_name = secondary_player.cards[int(self.last_shield_string[2])]
                            card = self.preloaded_find_card(card_name)
                            if card_name == "Connoisseur of Terror":
                                self.create_reaction("Connoisseur of Terror", secondary_player.name_player,
                                                     (int(secondary_player.number), -1, -1))
                            if card_name == "Liatha's Retinue":
                                self.create_reaction("Liatha's Retinue", secondary_player.name_player,
                                                     (int(secondary_player.number), -1, -1))
                            if card.get_shields() == 2:
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                await self.better_shield_card_resolution(
                                    secondary_player.name_player, self.last_shield_string,
                                    alt_shields=False, liatha_called=True)
                                self.create_interrupt("Liatha Punishment", secondary_player.name_player,
                                                      (int(primary_player.number), -1, -1))
                            else:
                                self.reset_choices_available()
                                self.resolving_search_box = False
                                secondary_player.remove_card_from_game(card_name)
                                del secondary_player.cards[int(self.last_shield_string[2])]
                                self.last_shield_string = ["pass-P1"]
                                await self.better_shield_card_resolution(
                                    secondary_player.name_player, self.last_shield_string, alt_shields=False)
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
                            elif primary_player.cards[self.pos_shield_card] == "I Do Not Serve":
                                if secondary_player.nullify_check():
                                    await self.send_update_message(
                                        primary_player.name_player + " wants to play I Do Not Serve; "
                                                                     "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = self.pos_shield_card
                                    self.nullified_card_name = "I Do Not Serve"
                                    self.cost_card_nullified = 1
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "I Do Not Serve"
                                else:
                                    await self.resolve_i_do_not_serve(primary_player, secondary_player)
                            elif primary_player.cards[self.pos_shield_card] == "Back to the Shadows":
                                if secondary_player.nullify_check():
                                    await self.send_update_message(
                                        primary_player.name_player + " wants to play Back to the Shadows; "
                                                                     "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = self.pos_shield_card
                                    self.nullified_card_name = "Back to the Shadows"
                                    self.cost_card_nullified = 0
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Back to the Shadows"
                                else:
                                    await self.resolve_back_to_the_shadows(primary_player, secondary_player)
                            elif primary_player.cards[self.pos_shield_card] == "Uphold His Honor":
                                pos_holder = self.positions_of_units_to_take_damage[0]
                                player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
                                primary_player.discard_card_from_hand(self.pos_shield_card)
                                self.pos_shield_card = -1
                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - 1
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Righteous Initiate":
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos]. \
                                        extra_attack_until_end_of_phase += 2
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Dutiful Castellan":
                                    if planet_pos != -2:
                                        self.create_reaction("Dutiful Castellan", primary_player.name_player,
                                                             (int(primary_player.number), planet_pos, unit_pos))
                                if primary_player.get_ability_given_pos(planet_pos,
                                                                        unit_pos) == "Sword Brethren Dreadnought":
                                    if planet_pos != -2:
                                        self.create_reaction("Sword Brethren Dreadnought", primary_player.name_player,
                                                             (int(primary_player.number), planet_pos, unit_pos))
                                if primary_player.get_ability_given_pos(planet_pos,
                                                                        unit_pos) == "Steadfast Sword Brethren":
                                    self.create_reaction("Steadfast Sword Brethren", primary_player.name_player,
                                                         (int(primary_player.number), planet_pos, unit_pos))
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Wrathful Dreadnought":
                                    self.create_reaction("Wrathful Dreadnought", primary_player.name_player,
                                                         (int(primary_player.number), planet_pos, unit_pos))
                                if primary_player.get_ability_given_pos(planet_pos,
                                                                        unit_pos) == "Fighting Company Daras":
                                    primary_player.increase_retaliate_given_pos_eop(planet_pos, unit_pos, 2)
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Reclusiam Templars":
                                    primary_player.ready_given_pos(planet_pos, unit_pos)
                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Brotherhood Justicar":
                                    primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                                if self.amount_that_can_be_removed_by_shield[0] < 1:
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
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
                                    self.alt_shield_name = "Glorious Intervention"
                                    self.alt_shield_mode_active = True
                            elif primary_player.cards[self.pos_shield_card] == "Faith Denies Death":
                                if secondary_player.nullify_check():
                                    await self.send_update_message(
                                        primary_player.name_player + " wants to play Faith Denies Death; "
                                                                     "Nullify window offered.")
                                    self.choices_available = ["Yes", "No"]
                                    self.name_player_making_choices = secondary_player.name_player
                                    self.choice_context = "Use Nullify?"
                                    self.nullified_card_pos = self.pos_shield_card
                                    self.nullified_card_name = "Faith Denies Death"
                                    self.cost_card_nullified = 0
                                    self.first_player_nullified = primary_player.name_player
                                    self.nullify_context = "Faith Denies Death"
                                else:
                                    primary_player.aiming_reticle_coords_hand = self.pos_shield_card
                                    primary_player.aiming_reticle_color = "blue"
                                    self.alt_shield_name = "Faith Denies Death"
                                    self.alt_shield_mode_active = True
                    elif self.choice_context == "Faith Denies Death: Amount Blocked":
                        amount = int(self.choices_available[int(game_update_string[1])])
                        num, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, amount)
                        self.amount_that_can_be_removed_by_shield[0] = \
                            self.amount_that_can_be_removed_by_shield[0] - amount
                        primary_player.discard_card_from_hand(self.pos_shield_card)
                        primary_player.aiming_reticle_coords_hand = None
                        self.alt_shield_name = ""
                        self.alt_shield_mode_active = False
                        self.reset_choices_available()
                        if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Sororitas Command Squad":
                            if self.positions_attackers_of_units_to_take_damage[0]:
                                if not primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos):
                                    self.sororitas_command_squad_value = amount
                                    primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
                                    self.create_reaction("Sororitas Command Squad", primary_player.name_player,
                                                         self.positions_attackers_of_units_to_take_damage[0])
                        if self.amount_that_can_be_removed_by_shield[0] < 1:
                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                            await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                    elif self.choice_context == "Awake the Sleepers":
                        target_name = self.choices_available[int(game_update_string[1])]
                        primary_player.deck.append(target_name)
                        primary_player.discard.remove(target_name)
                        del self.choices_available[int(game_update_string[1])]
                        if not self.choices_available:
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            if not primary_player.harbinger_of_eternity_active:
                                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                            primary_player.aiming_reticle_coords_hand = None
                            await self.send_update_message(
                                "No valid targets for Awake the Sleepers"
                            )
                            primary_player.shuffle_deck()
                            secondary_player.create_enemy_played_event_reactions()
                            self.action_cleanup()
                    elif self.choice_context == "Toxic Venomthrope: Gain Card or Resource?" or \
                            self.choice_context == "Homing Beacon: Gain Card or Resource?":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if game_update_string[1] == "0":
                            primary_player.draw_card()
                        elif game_update_string[1] == "1":
                            primary_player.add_resources(1)
                        self.delete_reaction()
                    elif self.choice_context == "Flayed Ones Revenants additional costs":
                        target_choice = self.choices_available[int(game_update_string[1])]
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        if target_choice == "Discard Cards":
                            pass
                        else:
                            if primary_player.spend_resources(2):
                                for _ in range(8):
                                    primary_player.discard_top_card_deck()
                                self.delete_interrupt()
                            else:
                                await self.send_update_message("Not enough resources. Discard cards instead.")
                    elif self.choice_context == "Warlock Destructor: pay fee or discard?":
                        self.reset_choices_available()
                        self.resolving_search_box = False
                        num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
                        if game_update_string[1] == "0":
                            primary_player.add_card_in_play_to_discard(planet_pos, unit_pos)
                        else:
                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                            primary_player.spend_resources(1)
                        self.delete_reaction()
                    elif self.choice_context == "Sautekh Complex: Gain Card or Resource?":
                        self.reset_choices_available()
                        self.resolving_search_box = False
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
                            self.reactions_needing_resolving[0] = "Commander Shadowsun hand"
                            self.location_hand_attachment_shadowsun = -1
                            await self.send_update_message("Choose card in hand")
                        else:
                            self.shadowsun_chose_hand = False
                            self.name_attachment_discard_shadowsun = ""
                            self.choice_context = "Shadowsun attachment from discard:"
                            self.name_player_making_choices = name
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if (card.get_card_type() == "Attachment" and card.get_faction() == "Tau" and
                                    card.get_cost() < 3) or card.get_name() == "Shadowsun's Stealth Cadre":
                                    if card.get_name() not in self.choices_available:
                                        self.choices_available.append(card.get_name())
                            if not self.choices_available:
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                await self.send_update_message("No valid cards in discard")
                                self.resolving_search_box = False
                                self.delete_reaction()
                            else:
                                await self.send_update_message("Choose card in discard")
                    elif self.choice_context == "Shadowsun attachment from discard:":
                        self.name_attachment_discard_shadowsun = self.choices_available[int(game_update_string[1])]
                        await self.send_update_message(
                            "Selected a " + self.name_attachment_discard_shadowsun)
                        self.choices_available = []
                        self.choice_context = ""
                        self.name_player_making_choices = ""
                        self.reactions_needing_resolving[0] = "Commander Shadowsun discard"
                    elif self.choice_context == "Which deck to use Crucible of Malediction:":
                        self.reset_choices_available()
                        if game_update_string[1] == "0":
                            player = primary_player
                            self.searching_enemy_deck = False
                        else:
                            player = secondary_player
                            self.searching_enemy_deck = True
                        if len(player.deck) > 2:
                            player.number_cards_to_search = 3
                            self.bottom_cards_after_search = False
                            self.cards_in_search_box = player.deck[:player.number_cards_to_search]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = str(primary_player.number)
                            self.what_to_do_with_searched_card = "DISCARD"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = None
                            self.faction_of_searched_card = None
                            self.max_cost_of_searched_card = None
                            self.no_restrictions_on_chosen_card = True
                            self.all_conditions_searched_card_required = False
                        else:
                            await self.send_update_message("Too few cards in deck")
                    elif self.choice_context == "Which deck to use Biel-Tan Warp Spiders:":
                        self.reset_choices_available()
                        if game_update_string[1] == "0":
                            player = primary_player
                            self.searching_enemy_deck = False
                        else:
                            player = secondary_player
                            self.searching_enemy_deck = True
                        if len(player.deck) > 1:
                            player.number_cards_to_search = 2
                            self.bottom_cards_after_search = False
                            self.cards_in_search_box = player.deck[:player.number_cards_to_search]
                            self.name_player_who_is_searching = primary_player.name_player
                            self.number_who_is_searching = str(primary_player.number)
                            self.what_to_do_with_searched_card = "DISCARD"
                            self.traits_of_searched_card = None
                            self.card_type_of_searched_card = None
                            self.faction_of_searched_card = None
                            self.max_cost_of_searched_card = None
                            self.no_restrictions_on_chosen_card = True
                            self.all_conditions_searched_card_required = False
                        else:
                            await self.send_update_message("Too few cards in deck")

    async def complete_enemy_discard(self, secondary_player, primary_player):
        effect, number = self.stored_discard_and_target[0]
        if effect == "Barlus":
            if not self.discard_fully_prevented:
                secondary_player.discard_card_at_random()
            await self.resolve_battle_conclusion("", [])
        elif effect == "Murder of Razorwings":
            if not self.discard_fully_prevented:
                secondary_player.discard_card_at_random()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif effect == "Mandrake Fearmonger":
            if not self.discard_fully_prevented:
                secondary_player.discard_card_at_random()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif effect == "The Price of Success":
            if not self.discard_fully_prevented:
                secondary_player.discard_card_at_random()
                secondary_player.discard_card_at_random()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif effect == "Unconquerable Fear":
            if not self.discard_fully_prevented:
                secondary_player.discard_card_at_random()
                secondary_player.discard_card_at_random()
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
        elif effect == "Pact of the Haemonculi":
            if not self.discard_fully_prevented:
                secondary_player.discard_card_at_random()
            primary_player.draw_card()
            primary_player.draw_card()
            self.card_pos_to_deploy = -1
            secondary_player.create_enemy_played_event_reactions()
            self.action_cleanup()
            await primary_player.dark_eldar_event_played()
        elif effect == "Visions of Agony":
            if not self.discard_fully_prevented:
                self.choices_available = secondary_player.cards
                self.choice_context = "Visions of Agony Discard:"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
            else:
                secondary_player.create_enemy_played_event_reactions()
                self.action_cleanup()
                await primary_player.dark_eldar_event_played()
        del self.stored_discard_and_target[0]

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
        elif self.nectavus_active:
            await CommandPhase.update_game_event_command_section(self, name, game_update_string)
            if not self.nectavus_active:
                await self.resolve_battle_conclusion(self.player_resolving_battle_ability, game_update_string)
        elif name != self.player_resolving_battle_ability:
            primary_player = self.p1
            secondary_player = self.p2
            if name == secondary_player.name_player:
                secondary_player = self.p1
                primary_player = self.p2
            if name == self.name_1 or name == self.name_2:
                if self.battle_ability_to_resolve == "Xenos World Tallin":
                    if self.chosen_first_card and not self.chosen_second_card:
                        if len(game_update_string) == 1:
                            if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                                self.chosen_second_card = True
                                await self.send_update_message("The mandatory move was not performed.")
                        if len(game_update_string) == 3:
                            if game_update_string[0] == "HQ":
                                if game_update_string[1] == primary_player.get_number():
                                    if primary_player.get_card_type_given_pos(-2, int(game_update_string[2])) == "Army":
                                        primary_player.move_unit_to_planet(
                                            -2, int(game_update_string[2]),
                                            self.misc_target_planet)
                                        self.chosen_second_card = True
                                        await self.send_update_message(secondary_player.name_player +
                                                                       " may move an army unit to the same planet.")
                        if len(game_update_string) == 4:
                            if game_update_string[0] == "IN_PLAY":
                                if game_update_string[1] == primary_player.get_number():
                                    if primary_player.get_card_type_given_pos(int(game_update_string[2]),
                                                                              int(game_update_string[3])) == "Army":
                                        if int(game_update_string[2]) != self.misc_target_planet:
                                            primary_player.move_unit_to_planet(
                                                int(game_update_string[2]),
                                                int(game_update_string[3]), self.misc_target_planet)
                                            self.chosen_second_card = True
                                            await self.send_update_message(secondary_player.name_player +
                                                                           " may move an army unit to the same planet.")
        elif name == self.player_resolving_battle_ability:
            primary_player = self.p1
            secondary_player = self.p2
            if name == secondary_player.name_player:
                secondary_player = self.p1
                primary_player = self.p2
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    if self.battle_ability_to_resolve in ["Selphini VII", "Hissan XI", "Gareth Prime",
                                                          "Erekiel"]:
                        self.player_resolving_battle_ability = secondary_player.name_player
                    if self.battle_ability_to_resolve == "Ice World Hydras IV":
                        primary_player.shuffle_deck()
                    if self.battle_ability_to_resolve == "Jalayerid" and self.misc_misc_2 is not None:
                        for i in range(len(self.misc_misc_2)):
                            og_pla, og_pos = self.misc_misc_2[i]
                            secondary_player.assign_damage_to_pos(og_pla, og_pos, 1)
                        self.misc_misc = None
                        self.misc_misc_2 = None
                        self.damage_from_atrox = True
                    elif self.battle_ability_to_resolve == "Ironforge" and not self.chosen_first_card:
                        self.chosen_first_card = True
                        await self.send_update_message("Passed on moving a unit to the HQ. "
                                                       "You may still increase the stats of a unit.")
                    elif self.battle_ability_to_resolve == "Essio" and self.misc_counter > 0:
                        self.choices_available = ["Gain 2 Resources", "Draw 2 Cards"]
                        self.choice_context = "Essio Spoils"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                    elif self.battle_ability_to_resolve == "Contaminated World Adracan" and not self.chosen_first_card:
                        self.chosen_first_card = True
                        self.choices_available = ["Yes", "No"]
                        self.choice_context = "CWA: Infest Planet?"
                        self.name_player_making_choices = primary_player.name_player
                        self.resolving_search_box = True
                        await self.send_update_message("Infest the planet?")
                    else:
                        await self.resolve_battle_conclusion(self.player_resolving_battle_ability, game_update_string)
            if self.battle_ability_to_resolve == "Ferrin":
                await PlanetBattleAbilities.manual_ferrin_ability(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Carnath":
                await PlanetBattleAbilities.manual_carnath_ability(self, name, game_update_string,
                                                                   primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Hissan XI":
                await PlanetBattleAbilities.manual_hissan_xi_ability(self, name, game_update_string,
                                                                     primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Ice World Hydras IV":
                await PlanetBattleAbilities.manual_ice_world_hydras_iv_ability(self, name, game_update_string,
                                                                               primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Fenos":
                await PlanetBattleAbilities.manual_fenos_ability(self, name, game_update_string,
                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Josoon":
                await PlanetBattleAbilities.manual_josoon_ability(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Xorlom":
                await PlanetBattleAbilities.manual_xorlom_ability(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Langeran":
                await PlanetBattleAbilities.manual_langeran_ability(self, name, game_update_string,
                                                                    primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Radex":
                await PlanetBattleAbilities.manual_radex_ability(self, name, game_update_string,
                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Coradim":
                await PlanetBattleAbilities.manual_coradim_ability(self, name, game_update_string,
                                                                   primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Belis":
                await PlanetBattleAbilities.manual_belis_ability(self, name, game_update_string,
                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Essio":
                await PlanetBattleAbilities.manual_essio_ability(self, name, game_update_string,
                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Erekiel":
                await PlanetBattleAbilities.manual_erekiel_ability(self, name, game_update_string,
                                                                   primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Hell's Theet":
                await PlanetBattleAbilities.manual_hells_theet_ability(self, name, game_update_string,
                                                                       primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Tool of Abolition":
                await PlanetBattleAbilities.manual_tool_of_abolition_ability(self, name, game_update_string,
                                                                             primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Kunarog The Slave Market":
                await PlanetBattleAbilities.manual_kunarog_the_slave_market_ability(self, name, game_update_string,
                                                                                    primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Baneful Veil":
                await PlanetBattleAbilities.manual_baneful_veil_ability(self, name, game_update_string,
                                                                        primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Craftworld Lugath":
                await PlanetBattleAbilities.manual_craftworld_lugath_ability(self, name, game_update_string,
                                                                             primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Ironforge":
                await PlanetBattleAbilities.manual_ironforge_ability(self, name, game_update_string,
                                                                     primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Daprian's Gate":
                await PlanetBattleAbilities.manual_daprians_gate_ability(self, name, game_update_string,
                                                                         primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Bhorsapolis The Decadent":
                await PlanetBattleAbilities.manual_bhorsapolis_the_decadent_ability(self, name, game_update_string,
                                                                                    primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Beheaded Hope":
                await PlanetBattleAbilities.manual_beheaded_hope_ability(self, name, game_update_string,
                                                                         primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Contaminated World Adracan":
                await PlanetBattleAbilities.manual_contaminated_world_adracan_ability(self, name, game_update_string,
                                                                                      primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Petrified Desolations":
                await PlanetBattleAbilities.manual_petrified_desolations_ability(self, name, game_update_string,
                                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Mangeras":
                await PlanetBattleAbilities.manual_mangeras_ability(self, name, game_update_string,
                                                                    primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Freezing Tower":
                await PlanetBattleAbilities.manual_freezing_tower_ability(self, name, game_update_string,
                                                                          primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Xenos World Tallin":
                await PlanetBattleAbilities.manual_xenos_world_talling_ability(self, name, game_update_string,
                                                                               primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Fortress World Garid":
                await PlanetBattleAbilities.manual_fortress_world_garid_ability(self, name, game_update_string,
                                                                                primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Zarvoss Foundry":
                await PlanetBattleAbilities.manual_zarvoss_foundry_ability(self, name, game_update_string,
                                                                           primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Nectavus XI":
                await PlanetBattleAbilities.manual_nectavus_xi_ability(self, name, game_update_string,
                                                                       primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Jaricho":
                await PlanetBattleAbilities.manual_jaricho_ability(self, name, game_update_string,
                                                                   primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Munos":
                await PlanetBattleAbilities.manual_munos_ability(self, name, game_update_string,
                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Daemon World Ivandis":
                await PlanetBattleAbilities.manual_daemon_world_ivandis_ability(self, name, game_update_string,
                                                                                primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Erida":
                await PlanetBattleAbilities.manual_erida_ability(self, name, game_update_string,
                                                                 primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Jalayerid":
                await PlanetBattleAbilities.manual_jalayerid_ability(self, name, game_update_string,
                                                                     primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Vargus":
                await PlanetBattleAbilities.manual_vargus_ability(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Selphini VII":
                await PlanetBattleAbilities.manual_selphini_vii_ability(self, name, game_update_string,
                                                                        primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Excellor":
                await PlanetBattleAbilities.manual_excellor_ability(self, name, game_update_string,
                                                                    primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Iridial":
                await PlanetBattleAbilities.manual_iridial_ability(self, name, game_update_string,
                                                                   primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Gareth Prime":
                await PlanetBattleAbilities.manual_gareth_prime_ability(self, name, game_update_string,
                                                                        primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Plannum":
                await PlanetBattleAbilities.manual_plannum_ability(self, name, game_update_string,
                                                                   primary_player, secondary_player)
            elif self.battle_ability_to_resolve == "Atrox Prime":
                await PlanetBattleAbilities.manual_atrox_prime_ability(self, name, game_update_string,
                                                                       primary_player, secondary_player)

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

    def preloaded_find_card(self, card_name):
        return FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                  self.apoka_errata_cards, self.cards_that_have_errata)

    async def resolve_on_kill_effects(self, i):
        print("--------\nON KILL EFFECTS\n--------")
        num, planet, pos = self.recently_damaged_units[i]
        if num == 1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if planet != -1 and pos != -1:
            if primary_player.check_if_card_is_destroyed(planet, pos):
                if self.on_kill_effects_of_attacker[i]:
                    for j in range(len(self.on_kill_effects_of_attacker[i])):
                        self.create_reaction(self.on_kill_effects_of_attacker[i][j], secondary_player.name_player,
                                             (int(secondary_player.number), planet, pos))
                        self.name_of_attacked_unit = primary_player.get_name_given_pos(planet, pos)

                if self.positions_of_attacker_of_unit_that_took_damage[i] is not None:
                    if (primary_player.check_for_trait_given_pos(planet, pos, "Warrior") or
                        primary_player.check_for_trait_given_pos(planet, pos, "Soldier")) and \
                            primary_player.get_faction_given_pos(planet, pos) == "Necrons":
                        if primary_player.search_card_at_planet(planet, "Ghost Ark of Orikan"):
                            if primary_player.get_cost_given_pos(planet, pos) > 0:
                                self.create_reaction("Ghost Ark of Orikan", primary_player.name_player,
                                                     (int(primary_player.number), planet, -1))
                                self.ghost_ark_of_orikan = primary_player.get_cost_given_pos(planet, pos)

                    if primary_player.search_hand_for_card("Vengeance!"):
                        self.create_reaction("Vengeance!", primary_player.name_player,
                                             (int(primary_player.number), planet, -1))

    def toggle_combat_turn_values(self):
        if self.player_with_combat_turn == self.name_1:
            self.player_with_combat_turn = self.name_2
            self.number_with_combat_turn = "2"
        else:
            self.player_with_combat_turn = self.name_1
            self.number_with_combat_turn = "1"

    async def destroy_check_cards_at_planet(self, player, planet_num):
        i = 0
        destroyed_something = False
        while i < len(player.cards_in_play[planet_num + 1]):
            if self.attacker_planet == planet_num and self.attacker_position == i:
                if self.player_with_combat_turn == player.name_player:
                    player.set_aiming_reticle_in_play(planet_num, i, "blue")
            if player.check_if_card_is_destroyed(planet_num, i):
                if self.player_with_combat_turn == player.name_player:
                    if self.attacker_planet == planet_num:
                        if self.attacker_position == i:
                            self.attacker_planet = -1
                            self.attacker_position = -1
                            if self.attack_being_resolved:
                                self.attack_resolution_cleanup = True
                                self.attack_being_resolved = False
                                self.reset_combat_positions()
                                self.toggle_combat_turn_values()
                        elif self.attacker_position > i:
                            self.attacker_position = self.attacker_position - 1
                player.destroy_card_in_play(planet_num, i)
                destroyed_something = True
                i = i - 1
            i = i + 1
        if destroyed_something:
            self.bloodthirst_active[planet_num] = True

    def holy_sepulchre_check(self, player):
        if player.search_card_in_hq("Holy Sepulchre", ready_relevant=True):
            for card_name in player.stored_cards_recently_discarded:
                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_faction() == "Space Marines" and card.get_is_unit():
                    return True
        return False

    def leviathan_hive_ship_check(self, player):
        if player.search_card_in_hq("Leviathan Hive Ship", ready_relevant=True):
            for card_name in player.stored_cards_recently_destroyed:
                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_is_unit():
                    if card.has_hive_mind and card.get_cost() < 4:
                        return True
        return False

    def fall_back_check(self, player):
        if player.search_hand_for_card("Fall Back!"):
            for card_name in player.stored_cards_recently_discarded:
                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.check_for_a_trait("Elite"):
                    return True
        return False

    async def complete_destruction_checks(self):
        if not self.reactions_needing_resolving and not self.interrupts_waiting_on_resolution \
                and not self.cards_in_search_box and not self.choices_available:
            self.p1.stored_cards_recently_discarded = copy.deepcopy(self.p1.cards_recently_discarded)
            self.p2.stored_cards_recently_discarded = copy.deepcopy(self.p2.cards_recently_discarded)
            self.p1.stored_cards_recently_destroyed = copy.deepcopy(self.p1.cards_recently_destroyed)
            self.p2.stored_cards_recently_destroyed = copy.deepcopy(self.p2.cards_recently_destroyed)
        else:
            self.p1.stored_cards_recently_discarded += copy.deepcopy(self.p1.cards_recently_discarded)
            self.p2.stored_cards_recently_discarded += copy.deepcopy(self.p2.cards_recently_discarded)
            self.p1.stored_cards_recently_destroyed += copy.deepcopy(self.p1.cards_recently_destroyed)
            self.p2.stored_cards_recently_destroyed += copy.deepcopy(self.p2.cards_recently_destroyed)
        if self.reactions_on_destruction_permitted:
            self.reactions_on_destruction_permitted = False
            if self.fall_back_check(self.p1):
                already_fall_back = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Fall Back!":
                        if self.player_who_resolves_reaction[i] == self.name_1:
                            already_fall_back = True
                if not already_fall_back:
                    self.create_reaction("Fall Back!", self.name_1, (1, -1, -1))
            if self.fall_back_check(self.p2):
                already_fall_back = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Fall Back!":
                        if self.player_who_resolves_reaction[i] == self.name_2:
                            already_fall_back = True
                if not already_fall_back:
                    self.create_reaction("Fall Back!", self.name_2, (2, -1, -1))
            if self.leviathan_hive_ship_check(self.p1):
                already_hive_ship = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Leviathan Hive Ship":
                        if self.player_who_resolves_reaction[i] == self.name_1:
                            already_hive_ship = True
                if not already_hive_ship:
                    self.create_reaction("Leviathan Hive Ship", self.name_1, (1, -1, -1))
            if self.leviathan_hive_ship_check(self.p2):
                already_hive_ship = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Leviathan Hive Ship":
                        if self.player_who_resolves_reaction[i] == self.name_2:
                            already_hive_ship = True
                if not already_hive_ship:
                    self.create_reaction("Leviathan Hive Ship", self.name_2, (2, -1, -1))
            if self.holy_sepulchre_check(self.p1):
                already_sepulchre = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Holy Sepulchre":
                        if self.player_who_resolves_reaction[i] == self.name_1:
                            already_sepulchre = True
                if not already_sepulchre:
                    self.create_reaction("Holy Sepulchre", self.name_1, (1, -1, -1))
            if self.holy_sepulchre_check(self.p2):
                already_sepulchre = False
                for i in range(len(self.reactions_needing_resolving)):
                    if self.reactions_needing_resolving[i] == "Holy Sepulchre":
                        if self.player_who_resolves_reaction[i] == self.name_2:
                            already_sepulchre = True
                if not already_sepulchre:
                    self.create_reaction("Holy Sepulchre", self.name_2, (2, -1, -1))
            if self.p2.stored_cards_recently_destroyed:
                if self.p1.search_card_in_hq("Shrine of Warpflame", ready_relevant=True):
                    already_warp_flame = False
                    for i in range(len(self.reactions_needing_resolving)):
                        if self.reactions_needing_resolving[i] == "Shrine of Warpflame":
                            if self.player_who_resolves_reaction[i] == self.name_1:
                                already_warp_flame = True
                    if not already_warp_flame:
                        self.create_reaction("Shrine of Warpflame", self.name_1, (1, -1, -1))
            if self.p1.stored_cards_recently_destroyed:
                if self.p2.search_card_in_hq("Shrine of Warpflame", ready_relevant=True):
                    already_warp_flame = False
                    for i in range(len(self.reactions_needing_resolving)):
                        if self.reactions_needing_resolving[i] == "Shrine of Warpflame":
                            if self.player_who_resolves_reaction[i] == self.name_2:
                                already_warp_flame = True
                    if not already_warp_flame:
                        self.create_reaction("Shrine of Warpflame", self.name_2, (2, -1, -1))
            self.emp_protecc()
            self.made_ta_fight()
        if self.p1.warlord_just_got_destroyed and not self.p2.warlord_just_got_destroyed:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_2 + "; " + self.name_1 + "'s warlord was destroyed."
                                                                    "----GAME END----"
            )
            await self.send_victory_proper(self.name_2, "warlord destruction")
        elif not self.p1.warlord_just_got_destroyed and self.p2.warlord_just_got_destroyed:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_1 + "; " + self.name_2 + "'s warlord was destroyed."
                                                                    "----GAME END----"
            )
            await self.send_victory_proper(self.name_1, "warlord destruction")
        elif self.p1.warlord_just_got_destroyed and self.p2.warlord_just_got_destroyed:
            await self.send_update_message(
                "----GAME END----"
                "Both warlords just died. I guess it is a draw?"
                "----GAME END----"
            )
            await self.send_victory_proper("Who knows who", "warlord destruction")
        self.p1.warlord_just_got_destroyed = False
        self.p2.warlord_just_got_destroyed = False
        self.reset_resolving_attack_on_units = True
        if self.resolving_kugath_nurglings:
            self.set_targeting_icons_kugath_nurglings()

    async def destroy_check_all_cards(self):
        if not self.interrupts_waiting_on_resolution:
            self.p1.search_for_preemptive_destroy_interrupts()
            self.p2.search_for_preemptive_destroy_interrupts()
        if not self.reactions_needing_resolving and not self.interrupts_waiting_on_resolution:
            print("\n\nABOUT TO EXECUTE:", self.on_kill_effects_of_attacker)
            for i in range(len(self.recently_damaged_units)):
                await self.resolve_on_kill_effects(i)
            self.recently_damaged_units = []
            self.damage_taken_was_from_attack = []
            self.positions_of_attacker_of_unit_that_took_damage = []
            self.faction_of_attacker = []
            self.card_names_that_caused_damage = []
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

    def advance_damage_aiming_reticle(self):
        if self.positions_of_units_to_take_damage:
            pos_holder = self.positions_of_units_to_take_damage[0]
            player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
            if player_num == 1:
                self.p1.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
            elif player_num == 2:
                self.p2.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")

    def determine_leftmost_planet(self):
        if self.player_with_initiative == self.name_1:
            for i in range(7):
                if self.planets_in_play_array[i]:
                    return i
        else:
            last_planet = -1
            for i in range(7):
                if self.planets_in_play_array[i]:
                    last_planet = i
            return last_planet
        return -1

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
        last_phase = self.phase
        self.phase = new_val
        if self.p1.command_struggles_won_this_phase < self.p2.command_struggles_won_this_phase:
            pla, pos = self.p1.get_location_of_warlord()
            if self.p1.get_ability_given_pos(pla, pos, bloodied_relevant=True) == "Mephiston" \
                    and last_phase == "COMMAND":
                self.create_interrupt("Mephiston", self.name_1, (1, pla, pos))
        elif self.p2.command_struggles_won_this_phase < self.p1.command_struggles_won_this_phase \
                and last_phase == "COMMAND":
            pla, pos = self.p2.get_location_of_warlord()
            if self.p2.get_ability_given_pos(pla, pos, bloodied_relevant=True) == "Mephiston":
                self.create_interrupt("Mephiston", self.name_2, (2, pla, pos))
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.last_planet_checked_for_battle = -1
        self.p1.muster_the_guard_count = 0
        self.p2.muster_the_guard_count = 0
        self.p1.master_warpsmith_count = 0
        self.p2.master_warpsmith_count = 0
        self.p1.contaminated_convoys = False
        self.p2.contaminated_convoys = False
        self.bloodrain_tempest_active = False
        i = 0
        while i < len(self.p1.headquarters):
            if self.p1.check_is_unit_at_pos(-2, i):
                if self.p1.headquarters[i].move_to_planet_end_of_phase_planet != -1:
                    if self.p1.headquarters[i].move_to_planet_end_of_phase_phase == last_phase:
                        if self.planets_in_play_array[self.p1.headquarters[i].move_to_planet_end_of_phase_planet]:
                            stored_val_dest = self.p1.headquarters[i].move_to_planet_end_of_phase_planet
                            self.p1.headquarters[i].move_to_planet_end_of_phase_planet = -1
                            self.p1.move_unit_to_planet(
                                -2, i, stored_val_dest, force=True
                            )
                            i = i - 1
            i = i + 1
        for i in range(7):
            j = 0
            while j < len(self.p1.cards_in_play[i + 1]):
                if self.p1.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet != -1:
                    if self.p1.cards_in_play[i + 1][j].move_to_planet_end_of_phase_phase == last_phase:
                        if self.planets_in_play_array[
                            self.p1.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet]:
                            stored_val_dest = self.p1.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet
                            self.p1.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet = -1
                            self.p1.move_unit_to_planet(
                                i, j, stored_val_dest, force=True
                            )
                            j = j - 1
                j = j + 1
        i = 0
        while i < len(self.p2.headquarters):
            if self.p2.check_is_unit_at_pos(-2, i):
                if self.p2.headquarters[i].move_to_planet_end_of_phase_planet != -1:
                    if self.p2.headquarters[i].move_to_planet_end_of_phase_phase == last_phase:
                        if self.planets_in_play_array[
                            self.p2.headquarters[i].move_to_planet_end_of_phase_planet]:
                            stored_val_dest = self.p2.headquarters[i].move_to_planet_end_of_phase_planet
                            self.p2.headquarters[i].move_to_planet_end_of_phase_planet = -1
                            self.p2.move_unit_to_planet(
                                -2, i, stored_val_dest, force=True
                            )
                            i = i - 1
            i = i + 1
        for i in range(7):
            j = 0
            while j < len(self.p2.cards_in_play[i + 1]):
                if self.p2.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet != -1:
                    if self.p2.cards_in_play[i + 1][j].move_to_planet_end_of_phase_phase == last_phase:
                        if self.planets_in_play_array[
                            self.p2.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet]:
                            stored_val_dest = self.p2.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet
                            self.p2.cards_in_play[i + 1][j].move_to_planet_end_of_phase_planet = -1
                            self.p2.move_unit_to_planet(
                                i, j, stored_val_dest, force=True
                            )
                            j = j - 1
                j = j + 1
        if self.phase == "COMMAND":
            self.committing_warlords = True
        if self.phase == "COMBAT":
            if self.p1.search_card_in_hq("'idden Base"):
                self.p1.idden_base_transform()
                self.p1.idden_base_active = True
            if self.p2.search_card_in_hq("idden Base"):
                self.p2.idden_base_transform()
                self.p2.idden_base_active = True
        if self.phase == "HEADQUARTERS":
            self.p1.idden_base_detransform(force=True)
            self.p1.idden_base_active = False
            self.p2.idden_base_detransform(force=True)
            self.p2.idden_base_active = False
        sacrifice_locations = self.p1.sacrifice_check_eop()
        sacrifice_locations = self.p2.sacrifice_check_eop()
        self.conclude_mind_shackle_scarab()
        if last_phase == "COMBAT":
            self.p1.start_agras_preachings_deployment()
            self.p2.start_agras_preachings_deployment()
        print("Phase change called")
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
            if "Undying Saint" in self.p1.discard:
                self.create_reaction("Undying Saint", self.p1.name_player, (1, -1, -1))
            if "Undying Saint" in self.p2.discard:
                self.create_reaction("Undying Saint", self.p2.name_player, (2, -1, -1))
            print("resetting necrons enslaved factions")
            self.p1.chosen_enslaved_faction = False
            self.p2.chosen_enslaved_faction = False
            self.p1.remove_all_faith_in_play()
            self.p2.remove_all_faith_in_play()
            if self.p1.warlord_faction == "Necrons":
                await self.create_necrons_wheel_choice(self.p1)
            elif self.p2.warlord_faction == "Necrons":
                await self.create_necrons_wheel_choice(self.p2)
        if self.p1.played_necrodermis:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_2 + "; "
                + self.name_1 + " played a Necrodermis this phase."
                                "----GAME END----"
            )
            await self.send_victory_proper(self.name_2, "Necrodermis")
        if self.p2.played_necrodermis:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_1 + "; "
                + self.name_2 + " played a Necrodermis this phase."
                                "----GAME END----"
            )
            await self.send_victory_proper(self.name_1, "Necrodermis")
        self.create_reactions_phase_begins()

    async def calculate_automatic_discounts_unit(self, planet_chosen, card, player):
        other_player = self.p1
        if player.name_player == self.name_1:
            other_player = self.p2
        if card.check_for_a_trait("Haemonculus"):
            for i in range(len(player.cards_in_play[planet_chosen + 1])):
                if player.get_ability_given_pos(planet_chosen, i) == "Arrogant Haemonculus":
                    self.discounts_applied = self.discounts_applied - 1
            for i in range(len(other_player.cards_in_play[planet_chosen + 1])):
                if other_player.get_ability_given_pos(planet_chosen, i) == "Arrogant Haemonculus":
                    self.discounts_applied = self.discounts_applied - 1
        if card.get_faction() == "Astra Militarum":
            for i in range(len(player.attachments_at_planet[planet_chosen])):
                if player.attachments_at_planet[planet_chosen][i].get_ability() == "Imperial Rally Point":
                    if card.get_cost() - self.discounts_applied > 1:
                        self.discounts_applied += 1
        if card.get_ability() == "Burrowing Trygon":
            num_termagants = player.get_most_termagants_at_single_planet()
            self.discounts_applied += num_termagants
        if card.get_faction() == "Astra Militarum":
            self.discounts_applied += player.muster_the_guard_count
        slaanesh_temptation = False
        if card.get_ability() == "Dutiful Castellan":
            if player.check_if_control_trait("Ecclesiarchy"):
                self.discounts_applied += 1
        if card.check_for_a_trait("Elite"):
            self.discounts_applied += player.master_warpsmith_count
            if self.planet_array[planet_chosen] == "Essio":
                self.discounts_applied = self.discounts_applied - 2
        else:
            for i in range(len(other_player.cards_in_play[planet_chosen + 1])):
                if other_player.get_ability_given_pos(planet_chosen, i) == "Purveyor of Hubris":
                    self.discounts_applied = self.discounts_applied - 2
        for i in range(7):
            for j in range(len(player.cards_in_play[i + 1])):
                if player.get_ability_given_pos(i, j) == "Uncontrollable Rioters":
                    self.discounts_applied = self.discounts_applied - 1
        if player.name_player == self.name_1:
            for i in range(len(self.p2.attachments_at_planet)):
                if i != planet_chosen:
                    for j in range(len(self.p2.attachments_at_planet[i])):
                        if self.p2.attachments_at_planet[i][j].get_ability() == "Slaanesh's Temptation":
                            slaanesh_temptation = True
        else:
            for i in range(len(self.p1.attachments_at_planet)):
                if i != planet_chosen:
                    for j in range(len(self.p1.attachments_at_planet[i])):
                        if self.p1.attachments_at_planet[i][j].get_ability() == "Slaanesh's Temptation":
                            slaanesh_temptation = True
        if slaanesh_temptation:
            self.discounts_applied -= 1
        self.discounts_applied += self.vamii_complex_discount

    async def calculate_available_discounts_unit(self, planet_chosen, card, player):
        other_player = self.p1
        if player.name_player == self.name_1:
            other_player = self.p2
        self.available_discounts = player.search_hq_for_discounts(card.get_faction(),
                                                                  card.get_traits(),
                                                                  planet_chosen=planet_chosen,
                                                                  name_of_card=card.get_name())
        if card.check_for_a_trait("Haemonculus"):
            for i in range(len(player.cards_in_play[planet_chosen + 1])):
                if player.get_ability_given_pos(planet_chosen, i) == "Arrogant Haemonculus":
                    self.available_discounts = self.available_discounts - 1
            for i in range(len(other_player.cards_in_play[planet_chosen + 1])):
                if other_player.get_ability_given_pos(planet_chosen, i) == "Arrogant Haemonculus":
                    self.available_discounts = self.available_discounts - 1
        if card.get_faction() == "Astra Militarum":
            for i in range(len(player.attachments_at_planet[planet_chosen])):
                if player.attachments_at_planet[planet_chosen][i].get_ability() == "Imperial Rally Point":
                    if card.get_cost() - self.available_discounts > 1:
                        self.available_discounts += 1
        hand_disc = player.search_hand_for_discounts(card.get_faction(), card.get_traits())
        self.available_discounts += hand_disc
        if hand_disc > 0:
            if card.get_faction() == "Orks":
                await self.send_update_message(
                    "Bigga Is Betta detected, may be used as a discount."
                )
            else:
                await self.send_update_message(
                    "Optimized Landing detected, may be used as a discount."
                )
        temp_av_disc, _ = player. \
            search_same_planet_for_discounts(self.faction_of_card_to_play, planet_pos=planet_chosen)
        if player.gorzod_relevant:
            if card.get_faction() == "Astra Militarum" or card.get_faction() == "Space Marines":
                if card.get_cost() > 1:
                    warlord_planet, warlord_pos = player.get_location_of_warlord()
                    player.set_aiming_reticle_in_play(warlord_planet, warlord_pos, "green")
                    self.available_discounts += 1
        if card.get_ability() == "Burrowing Trygon":
            num_termagants = player.get_most_termagants_at_single_planet()
            self.available_discounts += num_termagants
        if card.get_faction() == "Astra Militarum":
            self.available_discounts += player.muster_the_guard_count
        if card.get_ability() == "Dutiful Castellan":
            if player.check_if_control_trait("Ecclesiarchy"):
                self.available_discounts += 1
        for i in range(7):
            for j in range(len(player.cards_in_play[i + 1])):
                if player.get_ability_given_pos(i, j) == "Uncontrollable Rioters":
                    self.available_discounts = self.available_discounts - 1
        if card.check_for_a_trait("Elite"):
            self.available_discounts += player.master_warpsmith_count
            if self.planet_array[planet_chosen] == "Essio":
                self.available_discounts = self.available_discounts - 2
        else:
            for i in range(len(other_player.cards_in_play[planet_chosen + 1])):
                if other_player.get_ability_given_pos(planet_chosen, i) == "Purveyor of Hubris":
                    self.available_discounts = self.available_discounts - 2
        slaanesh_temptation = False
        if player.name_player == self.name_1:
            for i in range(len(self.p2.attachments_at_planet)):
                if i != planet_chosen:
                    for j in range(len(self.p2.attachments_at_planet[i])):
                        if self.p2.attachments_at_planet[i][j].get_ability() == "Slaanesh's Temptation":
                            slaanesh_temptation = True
        else:
            for i in range(len(self.p1.attachments_at_planet)):
                if i != planet_chosen:
                    for j in range(len(self.p1.attachments_at_planet[i])):
                        if self.p1.attachments_at_planet[i][j].get_ability() == "Slaanesh's Temptation":
                            slaanesh_temptation = True
        if slaanesh_temptation:
            self.available_discounts -= 1
        self.available_discounts += player.search_all_planets_for_discounts(self.traits_of_card_to_play,
                                                                            card.get_faction(),
                                                                            name_of_card=card.get_name())
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

    def checks_on_damage(self, primary_player, secondary_player, planet_pos, unit_pos):
        if primary_player.search_attachments_at_pos(planet_pos, unit_pos, "Armour of Saint Katherine"):
            self.create_reaction("Armour of Saint Katherine", primary_player.name_player,
                                 (int(primary_player.number), planet_pos, unit_pos))

    def checks_on_damage_from_attack(self, primary_player, secondary_player, planet_pos, unit_pos):
        att_num, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
        if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and \
                secondary_player.get_card_type_given_pos(att_pla, att_pos) == "Army":
            if secondary_player.castellan_crowe_2_relevant:
                self.create_reaction("Castellan Crowe", secondary_player.name_player,
                                     (int(primary_player.number), planet_pos, unit_pos))
        if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Neophyte Apprentice":
            self.create_reaction("Neophyte Apprentice", secondary_player.name_player,
                                 (int(secondary_player.number), att_pla, att_pos))
        if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Corrupted Clawed Fiend":
            if secondary_player.get_card_type_given_pos(att_pla, att_pos) == "Army":
                if secondary_player.get_cost_given_pos(att_pla, att_pos) < 3:
                    self.create_reaction("Corrupted Clawed Fiend", primary_player.name_player,
                                         (int(secondary_player.number), att_pla, att_pos))
        if secondary_player.search_attachments_at_pos(att_pla, att_pos, "Electrocorrosive Whip"):
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    primary_player.resolve_electro_whip(planet_pos, unit_pos)
        if primary_player.search_attachments_at_pos(planet_pos, unit_pos, "Repulsor Impact Field",
                                                    must_match_name=True):
            self.create_reaction("Repulsor Impact Field", primary_player.name_player,
                                 (int(secondary_player.number), att_pla, att_pos))
        if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Mandrake Fearmonger":
            self.create_reaction("Mandrake Fearmonger", secondary_player.name_player,
                                 (int(secondary_player.number), -1, -1))
        if secondary_player.check_for_trait_given_pos(att_pla, att_pos, "Kroot"):
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if secondary_player.get_ability_given_pos(planet_pos, i) == "Kroot Hounds":
                    if secondary_player.get_ready_given_pos(planet_pos, i):
                        self.create_reaction("Kroot Hounds", secondary_player.name_player,
                                             (int(primary_player.number), planet_pos, unit_pos))
        if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Solarite Avetys":
            if not secondary_player.get_flying_given_pos(att_pla, att_pos):
                self.create_reaction("Solarite Avetys", primary_player.name_player,
                                     (int(secondary_player.number), att_pla, att_pos))
        cost_diff = secondary_player.get_cost_given_pos(att_pla, att_pos) - \
                    primary_player.get_cost_given_pos(planet_pos, unit_pos)
        if cost_diff > 0:
            for k in range(len(primary_player.cards_in_play[planet_pos + 1][unit_pos].attachments)):
                if primary_player.cards_in_play[planet_pos + 1][unit_pos].attachments[k].get_ability() == \
                        "Seal of the Ebon Chalice":
                    self.ebon_chalice_value = cost_diff
                    self.create_interrupt("Seal of the Ebon Chalice", primary_player.name_player,
                                          (int(secondary_player.number), att_pla, att_pos))
        if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
            if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Volatile Pyrovore":
                self.create_reaction("Volatile Pyrovore", primary_player.name_player,
                                     (int(secondary_player.number), att_pla, att_pos))
        if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
            if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Phantasmatic Masque":
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    if not primary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos):
                        self.create_reaction("Phantasmatic Masque", primary_player.name_player,
                                             (int(primary_player.number), planet_pos, unit_pos))
        if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Deathskull Lootas":
            self.create_reaction("Deathskull Lootas", secondary_player.name_player,
                                 (int(secondary_player.number), att_pla, att_pos))
        if secondary_player.search_hand_for_card("Sneaky Lootin'"):
            if secondary_player.resources > 0:
                if secondary_player.get_faction_given_pos(att_pla, att_pos) == "Orks":
                    if secondary_player.check_for_trait_given_pos(att_pla, att_pos, "Soldier"):
                        self.create_reaction("Sneaky Lootin'", secondary_player.name_player,
                                             (int(secondary_player.number), att_pla, att_pos))
        if secondary_player.search_attachments_at_pos(att_pla, att_pos, "Searing Burst Cannon"):
            damage = self.amount_that_can_be_removed_by_shield[0]
            primary_player.cards_in_play[planet_pos + 1][unit_pos].damage += damage
        if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Shrieking Basilisk":
            self.create_reaction("Shrieking Basilisk", secondary_player.name_player,
                                 (int(secondary_player.number), planet_pos, unit_pos))
        for i in range(len(secondary_player.cards_in_play[att_pla + 1][att_pos].get_attachments())):
            if secondary_player.cards_in_play[att_pla + 1][att_pos].get_attachments()[i].get_ability() \
                    == "Nocturne-Ultima Storm Bolter" and secondary_player. \
                    cards_in_play[att_pla + 1][att_pos].get_attachments()[i].name_owner \
                    == secondary_player.name_player:
                self.create_reaction("Nocturne-Ultima Storm Bolter", secondary_player.name_player,
                                     (int(secondary_player.number), att_pla, att_pos))
        if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Vehicle"):
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    if secondary_player.get_card_type_given_pos(att_pla, att_pos) == "Warlord":
                        if secondary_player.resources > 0:
                            if secondary_player.search_hand_for_card("Hostile Acquisition"):
                                self.create_reaction("Hostile Acquisition", secondary_player.name_player,
                                                     (int(primary_player.number), planet_pos, unit_pos))
            if primary_player.cards_in_play[planet_pos + 1][unit_pos].get_card_type() != "Warlord":
                if secondary_player.get_ability_given_pos(att_pla, att_pos) == "Black Heart Ravager":
                    self.create_reaction("Black Heart Ravager", secondary_player.name_player,
                                         (int(primary_player.number), planet_pos, unit_pos))
                if secondary_player.search_attachments_at_pos(att_pla, att_pos, "Pincer Tail"):
                    self.create_reaction("Pincer Tail", secondary_player.name_player, pos_holder)
            if primary_player.get_card_type_given_pos(
                    planet_pos, unit_pos) == "Army":
                if secondary_player.search_attachments_at_pos(
                        att_pla, att_pos, "Last Breath"):
                    self.create_reaction(
                        "Last Breath", secondary_player.name_player,
                        (int(primary_player.number), planet_pos, unit_pos)
                    )

    def create_interrupt(self, name_interrupt, name_player, pos_interrupter, extra_info=None):
        if name_player == self.name_1:
            player = self.p1
        else:
            player = self.p2
        if not player.hit_by_gorgul:
            self.interrupts_waiting_on_resolution.append(name_interrupt)
            self.player_resolving_interrupts.append(name_player)
            self.positions_of_units_interrupting.append(pos_interrupter)
            self.extra_interrupt_info.append(extra_info)

    async def better_shield_card_resolution(self, name, game_update_string,
                                            alt_shields=True, can_no_mercy=True, liatha_called=False):
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
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                        if primary_player.defensive_protocols_active:
                            amount_to_remove = self.amount_that_can_be_removed_by_shield[0] - 1
                            if amount_to_remove > 0:
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - amount_to_remove
                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, amount_to_remove)
                    self.recently_damaged_units.append(self.positions_of_units_to_take_damage[0])
                    self.queued_sound = "damage"
                    if planet_pos != -2:
                        if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                            if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Reanimating Warriors" \
                                    and not primary_player.cards_in_play[planet_pos + 1][unit_pos].once_per_phase_used:
                                self.create_interrupt("Reanimating Warriors", primary_player.name_player,
                                                      (int(primary_player.number), planet_pos, unit_pos))
                            if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Treacherous Lhamaean":
                                self.create_reaction("Treacherous Lhamaean", primary_player.name_player,
                                                     (int(primary_player.number), planet_pos, unit_pos))
                            if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                    == "Swarmling Termagants":
                                self.create_reaction("Swarmling Termagants", primary_player.name_player,
                                                     (int(primary_player.number), planet_pos, unit_pos))
                            if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                    == "Prudent Fire Warriors":
                                self.create_interrupt("Prudent Fire Warriors", primary_player.name_player,
                                                      (int(primary_player.number), planet_pos, unit_pos))
                    if self.flamers_damage_active:
                        primary_player.cards_in_play[planet_pos + 1][unit_pos].hit_by_which_salamanders.append(
                            self.id_of_the_active_flamer)
                    self.checks_on_damage(primary_player, secondary_player, planet_pos, unit_pos)
                    if self.positions_attackers_of_units_to_take_damage[0] is not None:
                        att_num, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
                        self.damage_taken_was_from_attack.append(True)
                        self.positions_of_attacker_of_unit_that_took_damage.append(
                            self.positions_attackers_of_units_to_take_damage[0])
                        self.faction_of_attacker.append(secondary_player.get_faction_given_pos(att_pla, att_pos))
                        self.card_names_that_caused_damage.append(self.card_names_triggering_damage[0])
                        self.on_kill_effects_of_attacker.append([])
                        print("\n\nSAVED ON KILL EFFECTS\n\n", self.on_kill_effects_of_attacker)
                        self.checks_on_damage_from_attack(primary_player, secondary_player, planet_pos, unit_pos)
                    else:
                        self.damage_taken_was_from_attack.append(False)
                        self.positions_of_attacker_of_unit_that_took_damage.append(None)
                        self.faction_of_attacker.append("")
                        self.card_names_that_caused_damage.append(self.card_names_triggering_damage[0])
                        self.on_kill_effects_of_attacker.append([])
                    if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Zogwort's Runtherders":
                        self.create_reaction("Zogwort's Runtherders", primary_player.name_player,
                                             (int(primary_player.number), planet_pos, unit_pos))
                    if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                        if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                            primary_player.set_vow_of_honor(planet_pos, unit_pos, True)
                            if primary_player.resources > 0:
                                if primary_player.search_hand_for_card("Vow of Honor"):
                                    if not primary_player.check_if_already_have_reaction("Vow of Honor"):
                                        self.create_reaction("Vow of Honor", primary_player.name_player,
                                                             (int(primary_player.number), -1, -1))
                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
            elif not self.damage_is_preventable[0]:
                await self.send_update_message("Damage is not preventable; you must pass")
            elif len(game_update_string) == 3:
                if game_update_string[0] == "HAND":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        hand_pos = int(game_update_string[2])
                        tank = primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Tank")
                        shields = primary_player.get_shields_given_pos(hand_pos, planet_pos=planet_pos, tank=tank)
                        if self.liatha_active:
                            shields = 2
                        card_name = primary_player.cards[hand_pos]
                        alt_shield_check = False
                        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                        liatha = False
                        if self.liatha_available and alt_shields and not self.liatha_active:
                            print("Liatha checking")
                            if primary_player.get_ability_given_pos(warlord_pla, warlord_pos) == "Liatha":
                                print("is liatha")
                                uses = primary_player.get_once_per_phase_used_given_pos(warlord_pla, warlord_pos)
                                print(uses)
                                if not uses:
                                    liatha = True
                                elif uses < 3:
                                    liatha = True
                        self.pos_shield_card = hand_pos
                        if alt_shields and not primary_player.hit_by_gorgul:
                            if primary_player.cards[hand_pos] in self.alternative_shields:
                                if primary_player.cards[hand_pos] == "Indomitable":
                                    if primary_player.resources > 0:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            if primary_player.get_faction_given_pos(
                                                    planet_pos, unit_pos) == "Space Marines":
                                                alt_shield_check = True
                                                self.choices_available = ["Shield", "Effect"]
                                                self.name_player_making_choices = name
                                                self.choice_context = "Use alternative shield effect?"
                                                self.last_shield_string = game_update_string
                                elif primary_player.cards[hand_pos] == "I Do Not Serve":
                                    if primary_player.resources > 0:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            _, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
                                            if secondary_player.get_faction_given_pos(att_pla, att_pos) == \
                                                    primary_player.enslaved_faction:
                                                if primary_player.check_for_trait_given_pos(att_pla, att_pos,
                                                                                            "Sautekh") or \
                                                        primary_player.check_for_trait_given_pos(att_pla, att_pos,
                                                                                                 "Novokh"):
                                                    alt_shield_check = True
                                                    self.choices_available = ["Shield", "Effect"]
                                                    self.name_player_making_choices = name
                                                    self.choice_context = "Use alternative shield effect?"
                                                    self.last_shield_string = game_update_string
                                elif primary_player.cards[hand_pos] == "Back to the Shadows":
                                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                                        alt_shield_check = True
                                        self.choices_available = ["Shield", "Effect"]
                                        self.name_player_making_choices = name
                                        self.choice_context = "Use alternative shield effect?"
                                        self.last_shield_string = game_update_string
                                elif primary_player.cards[hand_pos] == "Glorious Intervention":
                                    if primary_player.resources > 0:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            alt_shield_check = True
                                            self.choices_available = ["Shield", "Effect"]
                                            self.name_player_making_choices = name
                                            self.choice_context = "Use alternative shield effect?"
                                            self.last_shield_string = game_update_string
                                elif primary_player.cards[hand_pos] == "Faith Denies Death":
                                    if primary_player.get_has_faith_given_pos(planet_pos, unit_pos) > 0:
                                        alt_shield_check = True
                                        self.choices_available = ["Shield", "Effect"]
                                        self.name_player_making_choices = name
                                        self.choice_context = "Use alternative shield effect?"
                                        self.last_shield_string = game_update_string
                                elif primary_player.cards[hand_pos] == "Uphold His Honor":
                                    if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                        if primary_player.get_unstoppable_given_pos(planet_pos, unit_pos):
                                            alt_shield_check = True
                                            self.choices_available = ["Shield", "Effect"]
                                            self.name_player_making_choices = name
                                            self.choice_context = "Use alternative shield effect?"
                                            self.last_shield_string = game_update_string
                        if liatha and not alt_shield_check:
                            self.choices_available = ["Shield", "Liatha"]
                            self.name_player_making_choices = name
                            self.choice_context = "Use Liatha?"
                            self.resolving_search_box = True
                            self.last_shield_string = game_update_string
                            alt_shield_check = True
                        if shields > 0 and not alt_shield_check:
                            print("Just before can shield check")
                            cego_check = False
                            if primary_player.cegorach_jesters_active:
                                card = self.preloaded_find_card(card_name)
                                if card.get_card_type() == "Attachment" or card.get_card_type() == "Event":
                                    if card_name not in primary_player.cegorach_jesters_permitted:
                                        cego_check = True
                            if cego_check:
                                await self.send_update_message("That card was not revealed for Cegorach's Jesters!")
                            elif self.damage_can_be_shielded[0]:
                                can_continue = True
                                if primary_player.search_attachments_at_pos(planet_pos, unit_pos,
                                                                            "Guardian Mesh Armor",
                                                                            ready_relevant=True,
                                                                            must_match_name=True):
                                    if self.guardian_mesh_armor_enabled and not primary_player.hit_by_gorgul:
                                        self.last_shield_string = game_update_string
                                        self.choice_context = "Use Guardian Mesh Armor?"
                                        self.choices_available = ["Yes", "No"]
                                        self.name_player_making_choices = primary_player.name_player
                                        can_continue = False
                                if not self.choices_available:
                                    if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                            == "Maksim's Squadron":
                                        if not self.apoka or not primary_player.get_once_per_phase_used_given_pos(
                                                planet_pos, unit_pos):
                                            if self.maksim_squadron_enabled and not primary_player.hit_by_gorgul:
                                                self.last_shield_string = game_update_string
                                                self.choice_context = "Use Maksim's Squadron?"
                                                self.choices_available = ["Yes", "No"]
                                                self.name_player_making_choices = primary_player.name_player
                                                can_continue = False
                                if can_continue:
                                    if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                            == "Distorted Talos":
                                        if not primary_player.get_once_per_phase_used_given_pos(
                                                planet_pos, unit_pos):
                                            if self.distorted_talos_enabled and not primary_player.hit_by_gorgul:
                                                self.last_shield_string = game_update_string
                                                self.choice_context = "Use Distorted Talos?"
                                                self.choices_available = ["Yes", "No"]
                                                self.name_player_making_choices = primary_player.name_player
                                                can_continue = False
                                if can_continue:
                                    if primary_player.search_attachments_at_pos(planet_pos, unit_pos,
                                                                                "Woken Machine Spirit"):
                                        if self.woken_machine_spirit_enabled and not primary_player.hit_by_gorgul:
                                            self.last_shield_string = game_update_string
                                            self.choice_context = "Use Woken Machine Spirit?"
                                            self.choices_available = ["Yes", "No"]
                                            self.name_player_making_choices = primary_player.name_player
                                            can_continue = False
                                if can_continue:
                                    no_mercy_possible = False
                                    if can_no_mercy:
                                        for i in range(len(secondary_player.cards)):
                                            if secondary_player.cards[i] == "No Mercy":
                                                no_mercy_possible = True
                                                if secondary_player.urien_relevant:
                                                    if secondary_player.resources < 1:
                                                        no_mercy_possible = False
                                    if no_mercy_possible:
                                        no_mercy_possible = secondary_player.search_ready_unique_unit()
                                    if no_mercy_possible:
                                        self.last_shield_string = game_update_string
                                        self.choice_context = "Use No Mercy?"
                                        self.choices_available = ["Yes", "No"]
                                        self.name_player_making_choices = secondary_player.name_player
                                        shield_string = "No Mercy can be played. A " + str(shields) + \
                                                        "-shield card, " + card_name + ", is being played."
                                        if self.liatha_active:
                                            shield_string = "No Mercy can be played. A " + str(shields) + \
                                                            "-shield card, from Liatha's ability, is being played."
                                        await self.send_update_message(shield_string)
                                    else:
                                        if shields == 1:
                                            for i in range(len(primary_player.headquarters)):
                                                if primary_player.get_ability_given_pos(-2, i) == "Anvil Strike Force":
                                                    if primary_player.headquarters[i].counter > 0:
                                                        if not primary_player.get_once_per_round_used_given_pos(-2, i):
                                                            shields += 1
                                                            primary_player.set_once_per_round_used_given_pos(-2, i,
                                                                                                             True)
                                        if self.guardian_mesh_armor_active:
                                            shields = shields * 2
                                        if self.maksim_squadron_active:
                                            shields += 1
                                        if self.woken_machine_spirit_active:
                                            shields += 1
                                        if primary_player.search_attachments_at_pos(
                                                warlord_pla, warlord_pos, "Cloak of Shade", ready_relevant=True):
                                            primary_player.exhaust_attachment_name_pos(
                                                warlord_pla, warlord_pos, "Cloak of Shade")
                                            shields += 1
                                        if not primary_player.fortress_world_garid_used:
                                            for i in range(len(primary_player.victory_display)):
                                                if primary_player.victory_display[i].get_name() == \
                                                        "Fortress World Garid":
                                                    shields += 1
                                                    primary_player.fortress_world_garid_used = True
                                        self.maksim_squadron_enabled = True
                                        self.woken_machine_spirit_enabled = True
                                        self.guardian_mesh_armor_enabled = True
                                        self.distorted_talos_enabled = True
                                        shields = min(shields, self.amount_that_can_be_removed_by_shield[0])
                                        self.amount_that_can_be_removed_by_shield[0] = \
                                            self.amount_that_can_be_removed_by_shield[0] - shields
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, shields)
                                        took_damage = True
                                        if self.amount_that_can_be_removed_by_shield[0] == 0:
                                            took_damage = False
                                        if primary_player.get_ability_given_pos(
                                                planet_pos, unit_pos) == "Sororitas Command Squad":
                                            if self.positions_attackers_of_units_to_take_damage[0]:
                                                if not primary_player.get_once_per_phase_used_given_pos(planet_pos,
                                                                                                        unit_pos):
                                                    self.sororitas_command_squad_value = shields
                                                    primary_player.set_once_per_phase_used_given_pos(
                                                        planet_pos, unit_pos, True)
                                                    self.create_reaction(
                                                        "Sororitas Command Squad", primary_player.name_player,
                                                        self.positions_attackers_of_units_to_take_damage[0]
                                                    )
                                        if self.positions_attackers_of_units_to_take_damage[0]:
                                            num_atk, pla_atk, pos_atk = \
                                            self.positions_attackers_of_units_to_take_damage[0]
                                            for attach_pos in range(len(secondary_player.cards_in_play[pla_atk + 1
                                                                        ][pos_atk].get_attachments())):
                                                if secondary_player.cards_in_play[pla_atk + 1][
                                                    pos_atk].get_attachments()[attach_pos
                                                ].get_ability() == "Spray and Pray":
                                                    self.create_reaction(
                                                        "Spray and Pray", secondary_player.name_player,
                                                        (num_atk, pla_atk,
                                                         pos_atk))
                                                    self.spray_and_pray_amounts.append(shields)
                                        for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                                            for j in range(len(secondary_player.cards_in_play[
                                                                   planet_pos + 1][i].attachments)):
                                                if secondary_player.cards_in_play[planet_pos + 1][i].attachments[j]. \
                                                        get_ability() == "Revered Heavy Flamer":
                                                    self.create_reaction("Revered Heavy Flamer",
                                                                         secondary_player.name_player,
                                                                         (int(secondary_player.number), planet_pos, i))
                                        if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                                            if primary_player.defensive_protocols_active:
                                                amount_to_remove = self.amount_that_can_be_removed_by_shield[0] - 1
                                                if amount_to_remove > 0:
                                                    self.amount_that_can_be_removed_by_shield[0] = \
                                                        self.amount_that_can_be_removed_by_shield[0] - amount_to_remove
                                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos,
                                                                                          amount_to_remove)
                                            if card_name == "Quantum Shielding":
                                                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos,
                                                                                            "Vehicle"):
                                                    self.create_interrupt("Quantum Shielding",
                                                                          primary_player.name_player,
                                                                          (int(primary_player.number),
                                                                           planet_pos, unit_pos))
                                        if self.liatha_active:
                                            hidden = "H"
                                            if liatha_called:
                                                hidden = "N"
                                            primary_player.remove_card_from_game(primary_player.cards[hand_pos],
                                                                                 hidden=hidden)
                                            del primary_player.cards[hand_pos]
                                        else:
                                            primary_player.discard_card_from_hand(hand_pos)
                                        if not primary_player.cards:
                                            if primary_player.search_for_card_everywhere("Torturer's Masks",
                                                                                         ready_relevant=True):
                                                self.create_reaction("Torturer's Masks", primary_player.name_player,
                                                                     (int(primary_player.number), -1, -1))
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        self.queued_sound = "shield"
                                        if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                                            if primary_player.get_ability_given_pos(
                                                    planet_pos, unit_pos) == "Holy Battery":
                                                self.create_reaction("Holy Battery", primary_player.name_player,
                                                                     (int(primary_player.number),
                                                                      planet_pos, unit_pos))
                                        if took_damage:
                                            if self.flamers_damage_active:
                                                primary_player.cards_in_play[planet_pos + 1][
                                                    unit_pos].hit_by_which_salamanders.append(
                                                    self.id_of_the_active_flamer)
                                            self.queued_sound = "damage"
                                            self.recently_damaged_units.append(
                                                self.positions_of_units_to_take_damage[0])
                                            if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                                                if primary_player.get_ability_given_pos(
                                                        planet_pos, unit_pos) == "Reanimating Warriors" \
                                                        and not primary_player.cards_in_play[planet_pos + 1][
                                                    unit_pos].once_per_phase_used:
                                                    self.create_interrupt("Reanimating Warriors",
                                                                          primary_player.name_player,
                                                                          (int(primary_player.number), planet_pos,
                                                                           unit_pos))
                                                if primary_player.get_ability_given_pos(
                                                        planet_pos, unit_pos) == "Treacherous Lhamaean":
                                                    self.create_reaction(
                                                        "Treacherous Lhamaean", primary_player.name_player,
                                                        (int(primary_player.number), planet_pos, unit_pos)
                                                    )
                                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                                        == "Swarmling Termagants":
                                                    self.create_reaction("Swarmling Termagants",
                                                                         primary_player.name_player,
                                                                         (int(primary_player.number), planet_pos,
                                                                          unit_pos))
                                                if primary_player.get_ability_given_pos(planet_pos, unit_pos) \
                                                        == "Prudent Fire Warriors":
                                                    self.create_interrupt("Prudent Fire Warriors",
                                                                          primary_player.name_player,
                                                                          (int(primary_player.number), planet_pos,
                                                                           unit_pos))
                                            self.checks_on_damage(primary_player, secondary_player, planet_pos,
                                                                  unit_pos)
                                            if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                                att_num, att_pla, att_pos = \
                                                    self.positions_attackers_of_units_to_take_damage[0]
                                                self.damage_taken_was_from_attack.append(True)
                                                self.positions_of_attacker_of_unit_that_took_damage.append(
                                                    self.positions_attackers_of_units_to_take_damage[0])
                                                self.faction_of_attacker.append(
                                                    secondary_player.get_faction_given_pos(att_pla, att_pos))
                                                self.card_names_that_caused_damage.append(
                                                    self.card_names_triggering_damage[0])
                                                self.on_kill_effects_of_attacker.append([])
                                                print("\n\nSAVED ON KILL EFFECTS\n\n", self.on_kill_effects_of_attacker)
                                                self.checks_on_damage_from_attack(primary_player, secondary_player,
                                                                                  planet_pos, unit_pos)
                                            else:
                                                self.damage_taken_was_from_attack.append(False)
                                                self.positions_of_attacker_of_unit_that_took_damage.append(None)
                                                self.faction_of_attacker.append("")
                                                self.card_names_that_caused_damage.append(
                                                    self.card_names_triggering_damage[0])
                                                self.on_kill_effects_of_attacker.append([])
                                            if not primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                                                if primary_player.get_faction_given_pos(planet_pos,
                                                                                        unit_pos) == "Space Marines":
                                                    primary_player.set_vow_of_honor(planet_pos, unit_pos, True)
                                                    if primary_player.resources > 0:
                                                        if primary_player.search_hand_for_card("Vow of Honor"):
                                                            if not primary_player.check_if_already_have_reaction(
                                                                    "Vow of Honor"):
                                                                self.create_reaction("Vow of Honor",
                                                                                     primary_player.name_player,
                                                                                     (int(primary_player.number),
                                                                                      -1, -1))
                                            if primary_player.get_ability_given_pos(
                                                    planet_pos, unit_pos) == "Zogwort's Runtherders":
                                                self.create_reaction("Zogwort's Runtherders",
                                                                     primary_player.name_player,
                                                                     (int(primary_player.number), planet_pos, unit_pos))
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                            else:
                                await self.send_update_message("This damage can not be shielded!")
                elif primary_player.hit_by_gorgul:
                    await self.send_update_message("Gorgul da Slaya is in effect; "
                                                   "your only choices are shield or pass.")
                elif game_update_string[0] == "HQ":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        hq_pos = int(game_update_string[2])
                        hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                        if self.alt_shield_mode_active:
                            if self.alt_shield_name == "Faith Denies Death":
                                if primary_player.spend_faith_given_pos(-2, hq_pos, 1) > 0:
                                    self.choice_context = "Faith Denies Death: Amount Blocked"
                                    self.name_player_making_choices = primary_player.name_player
                                    self.choices_available = [0, 1, 2, 3, 4, 5]
                                    i = 0
                                    while i < len(self.choices_available):
                                        if self.choices_available[i] > self.amount_that_can_be_removed_by_shield[0]:
                                            del self.choices_available[i]
                                            i = i - 1
                                        self.choices_available[i] = str(self.choices_available[i])
                                        i = i + 1
                        elif primary_player.headquarters[hq_pos].get_ability() == "Ghosts of Cegorach":
                            if primary_player.get_ready_given_pos(-2, hq_pos):
                                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Harlequin"):
                                    if planet_pos != -2:
                                        if primary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                                            if primary_player.check_for_warlord(planet_pos):
                                                primary_player.exhaust_given_pos(-2, hq_pos)
                                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                                warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                                                primary_player.assign_damage_to_pos(
                                                    warlord_pla, warlord_pos, 1, is_reassign=True, by_enemy_unit=False)
                                                self.amount_that_can_be_removed_by_shield[0] += -1
                                                if self.amount_that_can_be_removed_by_shield[0] < 1:
                                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                                    await self.shield_cleanup(primary_player, secondary_player,
                                                                              planet_pos)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Unstoppable Tide":
                            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Warlord":
                                if primary_player.get_ready_given_pos(-2, hq_pos):
                                    primary_player.exhaust_given_pos(-2, hq_pos)
                                    primary_player.unstoppable_tide_value = self.amount_that_can_be_removed_by_shield[0]
                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos,
                                                                          self.amount_that_can_be_removed_by_shield[0])
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    self.amount_that_can_be_removed_by_shield[0] = 0
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Senatorum Directives":
                            if not primary_player.senatorum_directives_used:
                                if planet_pos != -2:
                                    if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Catachan"):
                                        primary_player.senatorum_directives_used = True
                                        primary_player.summon_token_at_planet("Guardsman", planet_pos)
                                        self.choices_available = ["Reassign", "Pass"]
                                        self.choice_context = "Senatorum Directives Reassign"
                                        self.name_player_making_choices = primary_player.name_player
                                        self.resolving_search_box = True
                                        last_el = len(primary_player.cards_in_play[planet_pos + 1]) - 1
                                        self.misc_target_unit = (planet_pos, last_el)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Extra Boomsticks":
                            if primary_player.headquarters[hq_pos].get_ready():
                                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                                    primary_player.exhaust_given_pos(-2, hq_pos)
                                    primary_player.increase_retaliate_given_pos_eop(planet_pos, unit_pos, 2)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Talon Strike Force":
                            if primary_player.headquarters[hq_pos].counter > 2:
                                self.alt_shield_mode_active = True
                                self.alt_shield_name = "Talon Strike Force"
                                await self.send_update_message("Talon Strike Force shielding effect activated!")
                        elif primary_player.headquarters[hq_pos].get_ability() == "Rockcrete Bunker":
                            print("is rockcrete bunker")
                            if primary_player.headquarters[hq_pos].get_ready():
                                print("is ready")
                                primary_player.exhaust_given_pos(-2, hq_pos)
                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - 1
                                primary_player.headquarters[hq_pos].increase_damage(1)
                                if primary_player.headquarters[hq_pos].damage > 3:
                                    primary_player.sacrifice_card_in_hq(hq_pos)
                                if self.amount_that_can_be_removed_by_shield[0] == 0:
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.get_ability_given_pos(-2, hq_pos) == "Humanity's Shield":
                            if self.damage_can_be_shielded[0]:
                                primary_player.cards.append("Humanity's Shield")
                                del primary_player.headquarters[hq_pos]
                        elif primary_player.get_ability_given_pos(-2, hq_pos) == "The Phalanx":
                            if self.damage_can_be_shielded[0]:
                                card_phalanx = primary_player.headquarters[hq_pos]
                                primary_player.phalanx_shield_value = card_phalanx.damage + card_phalanx.counter + 2
                                primary_player.cards.append("The Phalanx")
                                del primary_player.headquarters[hq_pos]
                        elif primary_player.get_ability_given_pos(-2, hq_pos) == "Dal'yth Sept":
                            if primary_player.dalyth_sept_active and self.damage_can_be_shielded[0]:
                                primary_player.cards.append("Dal'yth Sept")
                                del primary_player.headquarters[hq_pos]
                        elif primary_player.get_ability_given_pos(-2, hq_pos) == "Praetorian Shadow":
                            if primary_player.get_ready_given_pos(-2, hq_pos):
                                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Warlord":
                                    primary_player.exhaust_given_pos(-2, hq_pos)
                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                    self.amount_that_can_be_removed_by_shield[0] = \
                                        self.amount_that_can_be_removed_by_shield[0] - 1
                                    if self.amount_that_can_be_removed_by_shield[0] == 0:
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Faith and Hatred":
                            if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                if primary_player.headquarters[hq_pos].get_ready():
                                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                                        primary_player.exhaust_given_pos(-2, hq_pos)
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                        self.amount_that_can_be_removed_by_shield[0] = \
                                            self.amount_that_can_be_removed_by_shield[0] - 1
                                        if self.amount_that_can_be_removed_by_shield[0] == 0:
                                            primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                            await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.headquarters[hq_pos].get_ability() == "Null Shield Matrix":
                            if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                                if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                    if not primary_player.headquarters[hq_pos].misc_ability_used:
                                        primary_player.headquarters[hq_pos].misc_ability_used = True
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                        self.amount_that_can_be_removed_by_shield[0] = \
                                            self.amount_that_can_be_removed_by_shield[0] - 1
                                        if self.amount_that_can_be_removed_by_shield[0] == 0:
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
                        elif planet_pos == hurt_planet and hurt_pos == unit_pos:
                            if primary_player.our_last_stand_bonus_active and self.may_block_with_ols and \
                                    primary_player.get_card_type_given_pos(hurt_planet, hurt_pos) == "Warlord" and \
                                    self.amount_that_can_be_removed_by_shield[0] > 1:
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - 1
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                self.may_block_with_ols = False
                            elif primary_player.get_ability_given_pos(-2, hq_pos) == "Blood Angels Veterans" and \
                                    primary_player.get_ready_given_pos(hurt_planet, hurt_pos) and not \
                                    primary_player.headquarters[hurt_pos].misc_ability_used:
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                primary_player.headquarters[hurt_pos].misc_ability_used = True
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - 1
                                if self.amount_that_can_be_removed_by_shield[0] == 0:
                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                            elif primary_player.get_faith_given_pos(hurt_planet, hurt_pos) > 0:
                                amount_to_remove = primary_player.get_faith_given_pos(hurt_planet, hurt_pos)
                                if primary_player.get_ability_given_pos(
                                        hurt_planet, hurt_pos) == "Fanatical Sister Repentia":
                                    amount_to_remove = amount_to_remove * 2
                                if amount_to_remove > self.amount_that_can_be_removed_by_shield[0]:
                                    amount_to_remove = self.amount_that_can_be_removed_by_shield[0]
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, amount_to_remove)
                                self.queued_sound = "shield"
                                primary_player.remove_faith_given_pos(hurt_planet, hurt_pos)
                                await self.send_update_message("Faith is being used as a shield.\n" +
                                                               str(amount_to_remove) + " damage is being removed.")
                                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                await self.shield_cleanup(primary_player, secondary_player, planet_pos)
            elif primary_player.hit_by_gorgul:
                await self.send_update_message("Gorgul da Slaya is in effect; "
                                               "your only choices are shield or pass.")
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if game_update_string[1] == str(self.number_who_is_shielding):
                        planet_pos = int(game_update_string[2])
                        unit_pos = int(game_update_string[3])
                        hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                        if self.starmist_raiment:
                            if hurt_planet == planet_pos and hurt_pos != unit_pos:
                                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord":
                                    primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                    primary_player.resolve_moved_damage_to_pos(planet_pos, unit_pos, 1)
                                    self.amount_that_can_be_removed_by_shield[0] = \
                                        self.amount_that_can_be_removed_by_shield[0] - 1
                                    if self.amount_that_can_be_removed_by_shield[0] < 1:
                                        primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif self.alt_shield_mode_active:
                            if self.alt_shield_name == "Glorious Intervention":
                                if game_update_string[1] == primary_player.get_number():
                                    pos_holder = self.positions_of_units_to_take_damage[0]
                                    player_num, planet_pos, unit_pos = pos_holder[0], pos_holder[1], pos_holder[2]
                                    sac_planet_pos = int(game_update_string[2])
                                    sac_unit_pos = int(game_update_string[3])
                                    print("Reached new GI code")
                                    if sac_planet_pos == planet_pos:
                                        if sac_unit_pos != unit_pos:
                                            if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos]. \
                                                    get_card_type() != "Warlord":
                                                if primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos] \
                                                        .check_for_a_trait("Warrior", primary_player.etekh_trait) or \
                                                        primary_player.cards_in_play[sac_planet_pos + 1][sac_unit_pos] \
                                                                .check_for_a_trait("Soldier",
                                                                                   primary_player.etekh_trait):
                                                    primary_player.aiming_reticle_coords_hand = None
                                                    primary_player.discard_card_from_hand(self.pos_shield_card)
                                                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                                    self.pos_shield_card = -1
                                                    printed_atk = primary_player.cards_in_play[
                                                        sac_planet_pos + 1][sac_unit_pos].attack
                                                    primary_player.remove_damage_from_pos(
                                                        planet_pos, unit_pos,
                                                        self.amount_that_can_be_removed_by_shield[0])
                                                    primary_player.sacrifice_card_in_play(sac_planet_pos, sac_unit_pos)
                                                    att_num, att_pla, att_pos = \
                                                        self.positions_attackers_of_units_to_take_damage[0]
                                                    secondary_player.assign_damage_to_pos(att_pla, att_pos, printed_atk,
                                                                                          by_enemy_unit=False)
                                                    await self.shield_cleanup(primary_player, secondary_player,
                                                                              planet_pos)
                            elif self.alt_shield_name == "Data Analyzer":
                                if hurt_planet == planet_pos and unit_pos != hurt_pos:
                                    primary_player.resolve_moved_damage_to_pos(planet_pos, unit_pos, 1)
                                    primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                    self.amount_that_can_be_removed_by_shield[0] = \
                                        self.amount_that_can_be_removed_by_shield[0] - 1
                                    self.alt_shield_mode_active = False
                                    self.alt_shield_name = ""
                                    if self.amount_that_can_be_removed_by_shield[0] < 1:
                                        primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                        await self.shield_cleanup(primary_player, secondary_player,
                                                                  planet_pos)
                            elif self.alt_shield_name == "Faith Denies Death":
                                if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1) > 0:
                                    self.choice_context = "Faith Denies Death: Amount Blocked"
                                    self.name_player_making_choices = primary_player.name_player
                                    self.choices_available = [0, 1, 2, 3, 4, 5]
                                    i = 0
                                    while i < len(self.choices_available):
                                        if self.choices_available[i] > self.amount_that_can_be_removed_by_shield[0]:
                                            del self.choices_available[i]
                                            i = i - 1
                                        self.choices_available[i] = str(self.choices_available[i])
                                        i = i + 1
                        elif primary_player.cards_in_play[planet_pos + 1][unit_pos].get_name() == "Old One Eye":
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
                        elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Expendable Pawn":
                            if planet_pos != hurt_planet or unit_pos != hurt_pos:
                                if planet_pos == hurt_planet or abs(planet_pos - hurt_planet) == 1:
                                    damage_to_remove = 2
                                    if self.amount_that_can_be_removed_by_shield[0] < 2:
                                        damage_to_remove = self.amount_that_can_be_removed_by_shield[0]
                                    self.amount_that_can_be_removed_by_shield[0] = \
                                        self.amount_that_can_be_removed_by_shield[0] - damage_to_remove
                                    primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage_to_remove)
                                    primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                                    if planet_pos == hurt_planet and unit_pos < hurt_pos:
                                        hurt_pos = hurt_pos - 1
                                    if self.amount_that_can_be_removed_by_shield[0] < 1:
                                        primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Praetorian Shadow":
                            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                if primary_player.get_card_type_given_pos(hurt_planet, hurt_pos) == "Warlord":
                                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                    primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                    self.amount_that_can_be_removed_by_shield[0] = \
                                        self.amount_that_can_be_removed_by_shield[0] - 1
                                    if self.amount_that_can_be_removed_by_shield[0] == 0:
                                        primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Noble Shining Spears":
                            if not primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used:
                                if primary_player.get_mobile_given_pos(hurt_planet, hurt_pos):
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
                                    primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                    damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                                    primary_player.set_damage_given_pos(planet_pos, unit_pos, damage + 1)
                                    self.amount_that_can_be_removed_by_shield[0] = \
                                        self.amount_that_can_be_removed_by_shield[0] - 1
                                    if self.amount_that_can_be_removed_by_shield[0] == 0:
                                        primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif planet_pos == hurt_planet and hurt_pos == unit_pos:
                            can_faith = False
                            if primary_player.get_faith_given_pos(hurt_planet, hurt_pos) > 0 and self.may_use_faith:
                                can_faith = True
                            can_retaliate = False
                            att_num, att_pla, att_pos = self.attacker_location
                            if primary_player.get_retaliate_given_pos(planet_pos, unit_pos) > 0 and \
                                    primary_player.get_card_type_given_pos(planet_pos, unit_pos) != "Warlord" and \
                                    self.may_use_retaliate:
                                if (att_pla != -1 and att_pos != -1) or \
                                        self.positions_attackers_of_units_to_take_damage[0] is not None:
                                    can_retaliate = True
                            if primary_player.our_last_stand_bonus_active and self.may_block_with_ols and \
                                    primary_player.get_card_type_given_pos(hurt_planet, hurt_pos) == "Warlord" and \
                                    self.amount_that_can_be_removed_by_shield[0] > 1:
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - 1
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                self.may_block_with_ols = False
                            elif primary_player.get_ability_given_pos(planet_pos,
                                                                      unit_pos) == "Blood Angels Veterans" and \
                                    primary_player.get_ready_given_pos(planet_pos, unit_pos) and not \
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used:
                                primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1)
                                primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
                                if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                                    self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                         (int(primary_player.number), planet_pos, unit_pos))
                                self.amount_that_can_be_removed_by_shield[0] = \
                                    self.amount_that_can_be_removed_by_shield[0] - 1
                                if self.amount_that_can_be_removed_by_shield[0] == 0:
                                    primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                    await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
                            elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Deff Dread" and not \
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used:
                                if self.positions_attackers_of_units_to_take_damage[0]:
                                    primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, preventable=False,
                                                                        by_enemy_unit=False)
                                    primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used = True
                                    if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                                        self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                             (int(primary_player.number), planet_pos, unit_pos))
                                    _, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
                                    secondary_player.assign_damage_to_pos(att_pla, att_pos, 3, rickety_warbuggy=True)
                            elif primary_player.get_ability_given_pos(
                                    hurt_planet, hurt_pos) == "Evanescent Players" and not \
                                    primary_player.get_once_per_phase_used_given_pos(hurt_planet, hurt_pos) and \
                                    self.amount_that_can_be_removed_by_shield[0] > 2 and \
                                    self.positions_attackers_of_units_to_take_damage[0]:
                                if secondary_player.special_get_card_type_given_pos(
                                        self.positions_attackers_of_units_to_take_damage[0]
                                ) == "Army":
                                    damage_prevented = self.amount_that_can_be_removed_by_shield[0] - 2
                                    self.amount_that_can_be_removed_by_shield[0] = 2
                                    primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage_prevented)
                                    _, att_pla, att_pos = self.positions_attackers_of_units_to_take_damage[0]
                                    secondary_player.assign_damage_to_pos(att_pla, att_pos, damage_prevented,
                                                                          rickety_warbuggy=True,
                                                                          shadow_field_possible=True)
                                    primary_player.set_once_per_phase_used_given_pos(hurt_planet, hurt_pos, True)
                            elif can_faith and can_retaliate:
                                self.choices_available = ["Faith", "Retaliate"]
                                self.choice_context = "Use which effect? (shield-likes)"
                                self.name_player_making_choices = primary_player.name_player
                                self.resolving_search_box = True
                                self.last_shield_string = game_update_string
                            elif can_faith:
                                amount_to_remove = primary_player.get_faith_given_pos(hurt_planet, hurt_pos)
                                if primary_player.get_ability_given_pos(
                                        hurt_planet, hurt_pos) == "Fanatical Sister Repentia":
                                    amount_to_remove = amount_to_remove * 2
                                if amount_to_remove > self.amount_that_can_be_removed_by_shield[0]:
                                    amount_to_remove = self.amount_that_can_be_removed_by_shield[0]
                                if primary_player.get_ability_given_pos(
                                        hurt_planet, hurt_pos) == "Sororitas Command Squad":
                                    if self.positions_attackers_of_units_to_take_damage[0]:
                                        if not primary_player.get_once_per_phase_used_given_pos(hurt_planet, hurt_pos):
                                            primary_player.set_once_per_phase_used_given_pos(hurt_planet,
                                                                                             hurt_pos, True)
                                            self.sororitas_command_squad_value = amount_to_remove
                                            self.create_reaction("Sororitas Command Squad", primary_player.name_player,
                                                                 self.positions_attackers_of_units_to_take_damage[0])
                                print("pre-spray")
                                if self.positions_attackers_of_units_to_take_damage[0]:
                                    print("Spray check")
                                    num_atk, pla_atk, pos_atk = self.positions_attackers_of_units_to_take_damage[0]
                                    for attach_pos in range(len(secondary_player.cards_in_play[pla_atk + 1
                                                                ][pos_atk].get_attachments())):
                                        if secondary_player.cards_in_play[pla_atk + 1][
                                            pos_atk].get_attachments()[attach_pos
                                        ].get_ability() == "Spray and Pray":
                                            self.create_reaction(
                                                "Spray and Pray", secondary_player.name_player,
                                                (num_atk, pla_atk,
                                                 pos_atk))
                                            self.spray_and_pray_amounts.append(amount_to_remove)
                                primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, amount_to_remove)
                                self.queued_sound = "shield"
                                primary_player.remove_faith_given_pos(hurt_planet, hurt_pos)
                                await self.send_update_message("Faith is being used as a shield.\n" +
                                                               str(amount_to_remove) + " damage is being removed.")
                                primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                            elif can_retaliate:
                                self.retaliate_used = True
                                retaliate_value = primary_player.get_retaliate_given_pos(planet_pos, unit_pos)
                                shadow_field = False
                                if primary_player.get_cost_given_pos(planet_pos, unit_pos) < 3:
                                    shadow_field = True
                                att_num, att_pla, att_pos = self.attacker_location
                                self.positions_attackers_of_units_to_take_damage[0] = self.attacker_location
                                secondary_player.assign_damage_to_pos(att_pla, att_pos, retaliate_value,
                                                                      rickety_warbuggy=True,
                                                                      shadow_field_possible=shadow_field)
                                primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                                await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                        elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Follower of Gork":
                            hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                            if planet_pos == hurt_planet:
                                if primary_player.cards_in_play[hurt_planet + 1][hurt_pos].check_for_a_trait("Elite"):
                                    if primary_player.cards_in_play[hurt_planet + 1][
                                        hurt_pos].follower_of_gork_available:
                                        primary_player.cards_in_play[hurt_planet + 1][
                                            hurt_pos].follower_of_gork_available = False
                                        damage_to_remove = 2
                                        if self.amount_that_can_be_removed_by_shield == 1:
                                            damage_to_remove = 1
                                        primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage_to_remove)
                                        if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                                            self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                                 (int(primary_player.number), hurt_planet, hurt_pos))
                                        self.amount_that_can_be_removed_by_shield[0] = \
                                            self.amount_that_can_be_removed_by_shield[0] - damage_to_remove
                                        if self.amount_that_can_be_removed_by_shield[0] < 1:
                                            primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                            await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
                        elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Enginseer Mechanic":
                            hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                            if planet_pos == hurt_planet:
                                if primary_player.cards_in_play[hurt_planet + 1][hurt_pos].check_for_a_trait(
                                        "Vehicle", primary_player.etekh_trait):
                                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                        damage_to_remove = 2
                                        if self.amount_that_can_be_removed_by_shield == 1:
                                            damage_to_remove = 1
                                        primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, damage_to_remove)
                                        if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                                            self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                                 (int(primary_player.number), planet_pos, unit_pos))
                                        self.amount_that_can_be_removed_by_shield[0] = \
                                            self.amount_that_can_be_removed_by_shield[0] - damage_to_remove
                                        if self.amount_that_can_be_removed_by_shield[0] < 1:
                                            primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                            await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
                        elif primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Steel Legion Chimera":
                            if self.positions_attackers_of_units_to_take_damage[0]:
                                hurt_num, hurt_planet, hurt_pos = self.positions_of_units_to_take_damage[0]
                                if planet_pos == hurt_planet:
                                    if not primary_player.cards_in_play[hurt_planet + 1][hurt_pos] \
                                            .check_for_a_trait("Vehicle", primary_player.etekh_trait):
                                        if not primary_player.cards_in_play[planet_pos + 1][unit_pos].misc_ability_used:
                                            primary_player.remove_damage_from_pos(hurt_planet, hurt_pos, 1)
                                            primary_player.cards_in_play[planet_pos + 1][unit_pos]. \
                                                misc_ability_used = True
                                            if secondary_player.search_card_at_planet(planet_pos,
                                                                                      "The Mask of Jain Zar"):
                                                self.create_reaction("The Mask of Jain Zar",
                                                                     secondary_player.name_player,
                                                                     (int(primary_player.number), planet_pos, unit_pos))
                                            self.amount_that_can_be_removed_by_shield[0] = \
                                                self.amount_that_can_be_removed_by_shield[0] - 1
                                            if self.amount_that_can_be_removed_by_shield[0] < 1:
                                                primary_player.reset_aiming_reticle_in_play(hurt_planet, hurt_pos)
                                                await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
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
                                if secondary_player.search_card_at_planet(planet_pos, "The Mask of Jain Zar"):
                                    self.create_reaction("The Mask of Jain Zar", secondary_player.name_player,
                                                         (int(primary_player.number), planet_pos, unit_pos))
                                await self.shield_cleanup(primary_player, secondary_player, hurt_planet)
            elif len(game_update_string) == 5:
                if planet_pos == -2:
                    if game_update_string[0] == "ATTACHMENT":
                        if game_update_string[1] == "HQ":
                            if game_update_string[2] == self.number_who_is_shielding:
                                if int(game_update_string[3]) == unit_pos:
                                    attachment_pos = int(game_update_string[4])
                                    attachment = primary_player.headquarters[unit_pos].get_attachments()[attachment_pos]
                                    if self.alt_shield_mode_active:
                                        if self.alt_shield_name == "Talon Strike Force":
                                            if attachment.name_owner == primary_player.name_player:
                                                primary_player.return_attachment_to_hand(-2, unit_pos, attachment_pos)
                                                last_card_in_hand = len(primary_player.cards) - 1
                                                if last_card_in_hand != -1:
                                                    self.alt_shield_name = ""
                                                    self.alt_shield_mode_active = False
                                                    new_game_update_string = ["HAND", primary_player.number,
                                                                              str(last_card_in_hand)]
                                                    await self.better_shield_card_resolution(
                                                        name, new_game_update_string, alt_shields=False)
                                    elif attachment.get_ability() == "Iron Halo" and attachment.get_ready() and \
                                            attachment.name_owner == primary_player.name_player:
                                        attachment.exhaust_card()
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        self.pos_shield_card = -1
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                                        if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                                self.damage_on_units_list_before_new_damage[0]:
                                            primary_player.set_damage_given_pos(
                                                planet_pos, unit_pos, self.damage_on_units_list_before_new_damage[0])
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                                    elif attachment.get_ability() == "Warhost Helmet" and attachment.get_ready() and \
                                            attachment.name_owner == primary_player.name_player and \
                                            primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                        attachment.exhaust_card()
                                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        damage = self.amount_that_can_be_removed_by_shield[0]
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage)
                                        self.amount_that_can_be_removed_by_shield[0] = 0
                                        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1,
                                                                                      expiration="NEXT")
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
            elif len(game_update_string) == 6:
                if game_update_string[0] == "ATTACHMENT":
                    if game_update_string[1] == "IN_PLAY":
                        if game_update_string[2] == self.number_who_is_shielding:
                            if int(game_update_string[3]) == planet_pos:
                                attachment_pos = int(game_update_string[5])
                                attachment = primary_player.cards_in_play[planet_pos + 1][int(game_update_string[4])] \
                                    .get_attachments()[attachment_pos]
                                if self.alt_shield_mode_active:
                                    if self.alt_shield_name == "Talon Strike Force":
                                        if attachment.name_owner == primary_player.name_player:
                                            primary_player.return_attachment_to_hand(planet_pos, unit_pos,
                                                                                     attachment_pos)
                                            last_card_in_hand = len(primary_player.cards) - 1
                                            if last_card_in_hand != -1:
                                                self.alt_shield_name = ""
                                                self.alt_shield_mode_active = False
                                                new_game_update_string = ["HAND", primary_player.number,
                                                                          str(last_card_in_hand)]
                                                await self.better_shield_card_resolution(
                                                    name, new_game_update_string, alt_shields=False)
                                elif attachment.get_ability() == "Starmist Raiment" and attachment.get_ready():
                                    if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Harlequin"):
                                        attachment.exhaust_card()
                                        self.starmist_raiment = True
                                elif attachment.get_ability() == "Data Analyzer" and not attachment.misc_ability_used:
                                    if self.positions_attackers_of_units_to_take_damage[0]:
                                        if len(primary_player.cards_in_play[planet_pos + 1]) > 1:
                                            self.alt_shield_mode_active = True
                                            attachment.misc_ability_used = True
                                            self.alt_shield_name = "Data Analyzer"
                                            await self.send_update_message("Data Analyzer activated!")
                                elif int(game_update_string[4]) == unit_pos:
                                    attachment_pos = int(game_update_string[5])
                                    attachment = primary_player.cards_in_play[planet_pos + 1][unit_pos] \
                                        .get_attachments()[attachment_pos]
                                    if attachment.get_ability() == "Iron Halo" and attachment.get_ready() and \
                                            attachment.name_owner == primary_player.name_player:
                                        attachment.exhaust_card()
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        self.pos_shield_card = -1
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                                        if primary_player.get_damage_given_pos(planet_pos, unit_pos) <= \
                                                self.damage_on_units_list_before_new_damage[0]:
                                            primary_player.set_damage_given_pos(
                                                planet_pos, unit_pos, self.damage_on_units_list_before_new_damage[0])
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                                    elif attachment.get_ability() == "Warhost Helmet" and attachment.get_ready() and \
                                            attachment.name_owner == primary_player.name_player and \
                                            primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                        attachment.exhaust_card()
                                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                        damage = self.amount_that_can_be_removed_by_shield[0]
                                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage)
                                        self.amount_that_can_be_removed_by_shield[0] = 0
                                        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1,
                                                                                      expiration="NEXT")
                                        await self.shield_cleanup(primary_player, secondary_player, planet_pos)
                                    elif attachment.get_ability() == "Armored Shell" and \
                                            attachment.name_owner == primary_player.name_player and \
                                            not attachment.from_magus_harid:
                                        if self.positions_attackers_of_units_to_take_damage[0] is not None:
                                            damage_to_remove = 0
                                            if self.amount_that_can_be_removed_by_shield[0] > 2:
                                                damage_to_remove = self.amount_that_can_be_removed_by_shield[0] - 2
                                            if damage_to_remove > 0:
                                                self.amount_that_can_be_removed_by_shield[0] = 2
                                                primary_player.remove_damage_from_pos(planet_pos, unit_pos,
                                                                                      damage_to_remove)

    def combat_reset_eocr_values(self):
        self.jungle_trench_count = 0
        self.p1.reset_eocr_values()
        self.p2.reset_eocr_values()

    async def resolve_reaction(self, name, game_update_string):
        if name == self.player_who_resolves_reaction[0]:
            print("player reacting:", name)
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
                    if self.reactions_needing_resolving[0] == "The Blood Pits":
                        if self.misc_misc:
                            for i in range(len(self.misc_misc)):
                                pla, pos = self.misc_misc[i]
                                secondary_player.assign_damage_to_pos(pla, pos, 2)
                        self.misc_misc = None
                        primary_player.drammask_nane_check()
                    if self.reactions_needing_resolving[0] == "The Inevitable Decay":
                        primary_player.drammask_nane_check()
                    if self.reactions_needing_resolving[0] == "Drammask Nane":
                        primary_player.reset_all_aiming_reticles_play_hq()
                    if self.reactions_needing_resolving[0] == "Castellan Crowe":
                        num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                        if self.misc_counter > 0:
                            secondary_player.assign_damage_to_pos(pla, pos, self.misc_counter)
                    if self.reactions_needing_resolving[0] == "Fire Warrior Elite" or \
                            self.reactions_needing_resolving[0] == "Deathwing Interceders" or \
                            self.reactions_needing_resolving[0] == "Runts to the Front":
                        self.may_move_defender = False
                        self.additional_attack_effects_allowed = False
                        _, current_planet, current_unit = self.last_defender_position
                        last_game_update_string = ["IN_PLAY", primary_player.get_number(), str(current_planet),
                                                   str(current_unit)]
                        await CombatPhase.update_game_event_combat_section(
                            self, secondary_player.name_player, last_game_update_string)
                    if self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
                        planet_pos, unit_pos = self.misc_target_unit
                        primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    if self.reactions_needing_resolving[0] == "Adaptative Thorax Swarm":
                        i = 0
                        names_list = []
                        while i < len(self.misc_player_storage):
                            names_list.append(primary_player.cards[self.misc_player_storage[i]])
                            primary_player.remove_card_from_hand(self.misc_player_storage[i])
                            primary_player.deck.append(names_list[i])
                            j = i + 1
                            while j < len(self.misc_player_storage):
                                if self.misc_player_storage[j] > self.misc_player_storage[i]:
                                    self.misc_player_storage[j] = self.misc_player_storage[j] - 1
                                j = j + 1
                            i = i + 1
                        cards_removed = ", ".join(names_list)
                        await self.send_update_message("Cards put on bottom of deck: " + cards_removed)
                        for _ in range(len(self.misc_player_storage)):
                            primary_player.draw_card()
                        primary_player.aiming_reticle_coords_hand = None
                        primary_player.aiming_reticle_coords_hand_2 = None
                        if primary_player.search_hand_for_card("Adaptative Thorax Swarm"):
                            self.create_reaction("Adaptative Thorax Swarm", primary_player.name_player,
                                                 (int(primary_player.number), -1, -1))
                    if self.reactions_needing_resolving[0] == "Commander Shadowsun hand":
                        primary_player.aiming_reticle_coords_hand = None
                        self.reset_choices_available()
                        self.resolving_search_box = False
                    if self.reactions_needing_resolving[0] == "Willing Submission":
                        primary_player.reset_all_aiming_reticles_play_hq()
                        secondary_player.reset_all_aiming_reticles_play_hq()
                    if self.reactions_needing_resolving[0] == "Cegorach's Jesters":
                        primary_player.cegorach_jesters_permitted = []
                        for i in range(len(self.misc_misc)):
                            primary_player.cegorach_jesters_permitted.append(primary_player.cards[self.misc_misc[i]])
                        self.misc_misc = []
                        total_string = "Cards Revealed: "
                        for i in range(len(primary_player.cegorach_jesters_permitted)):
                            total_string += primary_player.cegorach_jesters_permitted[i] + ", "
                        total_string += "."
                        await self.send_update_message(total_string)
                        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
                    if self.reactions_needing_resolving[0] == "Soul Grinder":
                        planet_pos = self.positions_of_unit_triggering_reaction[0][1]
                        unit_pos = self.positions_of_unit_triggering_reaction[0][2]
                        secondary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    if self.reactions_needing_resolving[0] == "Tunneling Mawloc":
                        self.infest_planet(self.misc_target_planet, primary_player)
                    if self.reactions_needing_resolving[0] == "Awakened Geomancer":
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    if self.reactions_needing_resolving[0] == "Dark Lance Raider":
                        if self.misc_misc is not None:
                            for i in range(len(self.misc_misc)):
                                og_pla, og_pos = self.misc_misc[i]
                                secondary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                                secondary_player.assign_damage_to_pos(og_pla, og_pos, 1, rickety_warbuggy=True)
                            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    if self.reactions_needing_resolving[0] == "Sautekh Royal Crypt Damage":
                        for i in range(len(self.misc_misc_2)):
                            planet_pos, unit_pos = self.misc_misc_2[i]
                            secondary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                        self.misc_misc = None
                        self.misc_misc_2 = None
                    if self.reactions_needing_resolving[0] == "Sacred Rose Immolator":
                        if self.misc_misc is not None:
                            for i in range(len(self.misc_misc)):
                                current_pla, current_pos = self.misc_misc[i]
                                secondary_player.assign_damage_to_pos(current_pla, current_pos, 1,
                                                                      rickety_warbuggy=True)
                        self.misc_misc = None
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        primary_player.reset_all_aiming_reticles_play_hq()
                    if self.reactions_needing_resolving[0] == "Fierce Purgator":
                        if self.misc_misc_2 is not None:
                            for i in range(len(self.misc_misc_2)):
                                current_num, current_pla, current_pos = self.misc_misc_2[i]
                                if current_num == 1:
                                    self.p1.assign_damage_to_pos(current_pla, current_pos, 1, context="Fierce Purgator",
                                                                 rickety_warbuggy=True)
                                else:
                                    self.p2.assign_damage_to_pos(current_pla, current_pos, 1, context="Fierce Purgator",
                                                                 rickety_warbuggy=True)
                        self.misc_misc = None
                        self.misc_misc_2 = None
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        primary_player.reset_all_aiming_reticles_play_hq()
                    if self.reactions_needing_resolving[0] == "Heavy Flamer Retributor":
                        for i in range(len(self.misc_misc)):
                            current_pla, current_pos = self.misc_misc[i]
                            secondary_player.assign_damage_to_pos(current_pla, current_pos, 1,
                                                                  rickety_warbuggy=True)
                        self.misc_misc = None
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    if self.reactions_needing_resolving[0] == "Howling Exarch":
                        primary_player.reset_all_aiming_reticles_play_hq()
                        if self.misc_misc is not None:
                            for i in range(len(self.misc_misc)):
                                num, planet_pos, unit_pos = self.misc_misc[i]
                                if num == 1:
                                    self.p1.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    self.p1.assign_damage_to_pos(planet_pos, unit_pos, 1)
                                else:
                                    self.p2.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                                    self.p2.assign_damage_to_pos(planet_pos, unit_pos, 1)
                    if self.reactions_needing_resolving[0] == "Nullify":
                        await self.complete_nullify()

                    # Decide whether to delete the reaction.
                    if self.reactions_needing_resolving[0] == "Patron Saint" and not self.chosen_first_card:
                        self.chosen_first_card = True
                        self.misc_counter = 3 - self.misc_counter
                        if self.misc_counter < 1:
                            self.delete_reaction()
                        else:
                            await self.send_update_message("Now place " + str(self.misc_counter) + " faith.")
                    elif self.reactions_needing_resolving[0] == "Scavenging Kroot Rider":
                        if not self.chosen_first_card:
                            self.chosen_first_card = True
                            await self.send_update_message("Skipping enemy support exhaustion.")
                        else:
                            self.delete_reaction()
                    elif self.reactions_needing_resolving[0] != "Warlock Destructor":
                        self.delete_reaction()
            elif len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    await PlanetsReaction.resolve_planet_reaction(self, name, game_update_string,
                                                                  primary_player, secondary_player)
            elif len(game_update_string) == 3:
                print("len is 3")
                if game_update_string[0] == "HAND":
                    print("hand reaction")
                    await HandReaction.resolve_hand_reaction(self, name, game_update_string,
                                                             primary_player, secondary_player)
                elif game_update_string[0] == "HQ":
                    await HQReaction.resolve_hq_reaction(self, name, game_update_string,
                                                         primary_player, secondary_player)
                elif game_update_string[0] == "IN_DISCARD":
                    await DiscardReaction.resolve_discard_reaction(self, name, game_update_string,
                                                                   primary_player, secondary_player)
                elif game_update_string[0] == "REMOVED":
                    chosen_removed = int(game_update_string[1])
                    pos_removed = int(game_update_string[2])
                    print("Check what player")
                    print(self.player_who_resolves_reaction)
                    current_reaction = self.reactions_needing_resolving[0]
                    if current_reaction == "Shadow Hunt":
                        if not self.chosen_first_card:
                            if chosen_removed == int(primary_player.get_number()):
                                card_name = primary_player.cards_removed_from_game[pos_removed]
                                if primary_player.cards_removed_from_game_hidden[pos_removed] == "H":
                                    card = self.preloaded_find_card(card_name)
                                    if card.get_card_type() == "Army" and card.get_faction() == "Dark Eldar":
                                        if not card.check_for_a_trait("Elite"):
                                            primary_player.cards_removed_from_game_hidden[pos_removed] = "N"
                                            if card_name == "Connoisseur of Terror":
                                                self.create_reaction(
                                                    "Connoisseur of Terror", primary_player.name_player,
                                                    (int(primary_player.number), -1, -1)
                                                )
                                            self.chosen_first_card = True
                                            self.misc_counter = pos_removed
                    elif current_reaction == "Liatha's Loyal Hound":
                        if chosen_removed == int(primary_player.get_number()):
                            if primary_player.cards_removed_from_game_hidden[pos_removed] == "H":
                                card_name = primary_player.cards_removed_from_game[pos_removed]
                                card = self.preloaded_find_card(card_name)
                                if card.get_shields() == 0:
                                    primary_player.cards_removed_from_game_hidden[pos_removed] = "N"
                                    last_planet = 0
                                    for i in range(7):
                                        if self.planets_in_play_array[i]:
                                            last_planet = i
                                    primary_player.add_card_to_planet(self.preloaded_find_card("Liatha's Loyal Hound"),
                                                                      last_planet)
                                    del primary_player.cards_removed_from_game[-1]
                                    del primary_player.cards_removed_from_game_hidden[-1]
                                    if card_name == "Liatha's Retinue" or card_name == "Connoisseur of Terror":
                                        self.create_reaction(card_name, primary_player.name_player,
                                                             (int(primary_player.number), -1, -1))
                                    self.delete_reaction()
            elif len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    await InPlayReaction.resolve_in_play_reaction(self, name, game_update_string,
                                                                  primary_player, secondary_player)
                elif game_update_string[0] == "RESERVE":
                    if self.reactions_needing_resolving[0] == "Seer Adept":
                        if game_update_string[1] == secondary_player.number:
                            name_card = secondary_player.cards_in_reserve[
                                int(game_update_string[2])][int(game_update_string[3])].get_name()
                            await self.send_update_message(secondary_player.name_player + " has a " + name_card +
                                                           " at that position")
                            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                            self.delete_reaction()
                    elif self.reactions_needing_resolving[0] == "Snagbrat's Scouts":
                        if game_update_string[1] == primary_player.number:
                            if primary_player.cards_in_reserve[
                                int(game_update_string[2])][
                                int(game_update_string[3])].get_ability() == "Snagbrat's Scouts":
                                ds_value = primary_player.get_deepstrike_value_given_pos(int(game_update_string[2]),
                                                                                         int(game_update_string[3]))
                                if primary_player.spend_resources(ds_value):
                                    last_el_index = primary_player.deepstrike_unit(int(game_update_string[2]),
                                                                                   int(game_update_string[3]))
                                    if last_el_index != -1:
                                        primary_player.cards_in_play[int(game_update_string[2]) + 1][
                                            last_el_index].extra_command_eop += 2
                                    found_one = False
                                    for i in range(7):
                                        for j in range(len(primary_player.cards_in_reserve[i])):
                                            if primary_player.cards_in_reserve[
                                                i][j].get_ability() == "Snagbrat's Scouts":
                                                if primary_player.resources > 0:
                                                    if not found_one:
                                                        found_one = True
                                                        self.create_reaction("Snagbrat's Scouts",
                                                                             primary_player.name_player,
                                                                             (int(primary_player.number), -1, -1))
                                    self.delete_reaction()
                    elif self.reactions_needing_resolving[0] == "Kamouflage Expert":
                        if game_update_string[1] == primary_player.number:
                            og_pla = self.positions_of_unit_triggering_reaction[0][1]
                            planet_pos = int(game_update_string[2])
                            unit_pos = int(game_update_string[3])
                            if og_pla == planet_pos or (og_pla - unit_pos) == 1:
                                card = CardClasses.ArmyCard("Cardback", "I am a Deepstriked Card.", "",
                                                            0, "Orks", "Common", 3, 3, 0, False)
                                card.actually_a_deepstrike = True
                                card.not_idden_base_src = True
                                card.deepstrike_card_name = primary_player.cards_in_reserve[planet_pos][
                                    unit_pos].get_name()
                                card.name_owner = primary_player.name_player
                                primary_player.cards_in_play[planet_pos + 1].append(card)
                                del primary_player.cards_in_reserve[planet_pos][unit_pos]
                                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                                self.delete_reaction()
                    elif self.reactions_needing_resolving[0] == "Impulsive Loota Reserve":
                        if not self.chosen_first_card:
                            if game_update_string[1] == primary_player.number:
                                if primary_player.cards_in_reserve[int(game_update_string[2])][
                                    int(game_update_string[3])].get_ability() == "Impulsive Loota":
                                    cost = primary_player.get_deepstrike_value_given_pos(int(game_update_string[2]),
                                                                                         int(game_update_string[3]))
                                    if primary_player.spend_resources(cost):
                                        last_el_index = primary_player.deepstrike_unit(int(game_update_string[2]),
                                                                                       int(game_update_string[3]))
                                        if last_el_index == -1:
                                            await self.send_update_message(
                                                "Could not Deep Strike the Impulsive Loota! Cancelling...")
                                            self.delete_reaction()
                                        else:
                                            self.chosen_first_card = True
                                            self.misc_target_unit = (int(game_update_string[2]), last_el_index)
                                            await self.send_update_message("Please choose the card to attach.")
                                    else:
                                        await self.send_update_message(
                                            "Could not pay the cost for the Impulsive Loota! Cancelling...")
                                        self.delete_reaction()
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
                    elif game_update_string[1] == "HQ":
                        await AttachmentHQReaction.resolve_attachment_hq_reaction(
                            self, name, game_update_string, primary_player, secondary_player
                        )
            elif len(game_update_string) == 6:
                if game_update_string[0] == "ATTACHMENT":
                    if game_update_string[1] == "IN_PLAY":
                        await AttachmentInPlayReaction.resolve_attachment_in_play_reaction(
                            self, name, game_update_string, primary_player, secondary_player
                        )

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
                                                                   self.unit_to_move_position[1],
                                                                   planet_pos, card_effect=False)
                                if not primary_player.search_cards_for_available_mobile():
                                    primary_player.mobile_resolved = True
                                self.unit_to_move_position = [-1, -1]
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if int(game_update_string[1]) == int(primary_player.number):
                            self.unit_to_move_position = (int(game_update_string[2]), int(game_update_string[3]))
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
                                                                     self.unit_to_move_position[1],
                                                                     planet_pos, card_effect=False)
                                if not secondary_player.search_cards_for_available_mobile():
                                    secondary_player.mobile_resolved = True
                                self.unit_to_move_position = [-1, -1]
                elif len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        if int(game_update_string[1]) == int(secondary_player.number):
                            self.unit_to_move_position = (int(game_update_string[2]), int(game_update_string[3]))
                            secondary_player.set_aiming_reticle_in_play(self.unit_to_move_position[0],
                                                                        self.unit_to_move_position[1], "blue")
        if primary_player.mobile_resolved and secondary_player.mobile_resolved:
            await self.send_update_message("mobile complete")
            await self.send_update_message("Window granted for players to use "
                                           "reactions/actions before the battle begins.")
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
                if self.location_of_indirect == "PLANET" or self.location_of_indirect == "ALL":
                    if len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            if self.planet_of_indirect == int(game_update_string[2]) \
                                    or self.location_of_indirect == "ALL":
                                if game_update_string[1] == player.get_number():
                                    if player.get_card_type_given_pos(
                                            int(game_update_string[2]), int(game_update_string[3])) \
                                            in self.valid_targets_for_indirect and \
                                            (not self.indirect_exhaust_only or not player.get_ready_given_pos(
                                                int(game_update_string[2]), int(game_update_string[3]))) and \
                                            (self.forbidden_traits_indirect == ""
                                             or not player.check_for_trait_given_pos(
                                                        int(game_update_string[2]), int(game_update_string[3]),
                                                        self.forbidden_traits_indirect)):
                                        if player.get_faction_given_pos(
                                                int(game_update_string[2]), int(game_update_string[3])) == \
                                                self.faction_of_cards_for_indirect or not \
                                                self.faction_of_cards_for_indirect:
                                            player.increase_indirect_damage_at_pos(int(game_update_string[2]),
                                                                                   int(game_update_string[3]), 1)
        if self.p1.indirect_damage_applied >= self.p1.total_indirect_damage and \
                self.p2.indirect_damage_applied >= self.p2.total_indirect_damage:
            await self.resolve_indirect_damage_applied()
            if self.battle_ability_to_resolve == "Diamat":
                self.damage_from_atrox = True
            self.indirect_exhaust_only = False
            self.forbidden_traits_indirect = ""
            self.p1.total_indirect_damage = 0
            self.p2.total_indirect_damage = 0

    async def resolve_indirect_damage_applied(self):
        self.first_card_damaged = True
        await self.p1.transform_indirect_into_damage()
        await self.p2.transform_indirect_into_damage()
        self.first_card_damaged = True

    async def resolve_interrupts(self, name, game_update_string):
        if name == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        print("Resolving effect")
        if name == self.player_resolving_interrupts[0]:
            print("name check ok")
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    current_interrupt = self.interrupts_waiting_on_resolution[0]
                    if current_interrupt == "Flayed Ones Revenants":
                        num, planet_pos, unit_pos = self.positions_of_units_interrupting[0]
                        primary_player.add_card_in_play_to_discard(planet_pos, unit_pos)
                        await self.send_update_message("Did not pay the additional cost; "
                                                       "card added to discard.")
                    if current_interrupt == "The Shadow Suit":
                        if self.chosen_first_card:
                            card = self.preloaded_find_card("The Shadow Suit")
                            if "The Shadow Suit" in secondary_player.discard:
                                secondary_player.discard.remove("The Shadow Suit")
                            secondary_player.put_card_into_reserve(card, chosen_planet, payment=False)
                    if current_interrupt == "Blood of Martyrs":
                        if not self.chosen_first_card:
                            self.delete_interrupt()
                        elif not self.chosen_second_card:
                            self.chosen_second_card = True
                            await self.send_update_message("Targeted less than the maximum number of units.")
                            if primary_player.get_faith_given_pos(self.misc_target_unit[0],
                                                                  self.misc_target_unit[1]) < 1:
                                await self.send_update_message("No faith to move; skipping directly to "
                                                               "increasing the attack of the units step.")
                                for i in range(len(self.misc_misc)):
                                    primary_player.increase_attack_of_unit_at_pos(self.misc_misc[i][0],
                                                                                  self.misc_misc[i][1], 1,
                                                                                  expiration="NEXT")
                                if primary_player.check_for_trait_given_pos(
                                        self.misc_target_unit[0], self.misc_target_unit[1], "Martyr"):
                                    primary_player.draw_card()
                                self.delete_interrupt()
                                primary_player.reset_all_aiming_reticles_play_hq()
                        else:
                            await self.send_update_message("Increasing the attack of the units.")
                            for i in range(len(self.misc_misc)):
                                primary_player.increase_attack_of_unit_at_pos(self.misc_misc[i][0],
                                                                              self.misc_misc[i][1], 1,
                                                                              expiration="NEXT")
                            if primary_player.check_for_trait_given_pos(
                                    self.misc_target_unit[0], self.misc_target_unit[1], "Martyr"):
                                primary_player.draw_card()
                            self.delete_interrupt()
                            primary_player.reset_all_aiming_reticles_play_hq()
                    elif current_interrupt == "Zen Xi Aonia":
                        await self.send_update_message("You cannot stop Zen Xi Aonia.")
                    else:
                        self.delete_interrupt()
            if len(game_update_string) == 2:
                if game_update_string[0] == "PLANETS":
                    await PlanetInterrupts.resolve_planet_interrupt(self, name, game_update_string,
                                                                    primary_player, secondary_player)
            if len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    await InPlayInterrupts.resolve_in_play_interrupt(self, name, game_update_string,
                                                                     primary_player, secondary_player)
                elif game_update_string[0] == "RESERVE":
                    planet_pos = int(game_update_string[2])
                    unit_pos = int(game_update_string[3])
                    if game_update_string[1] == primary_player.number:
                        player_owning_card = primary_player
                    else:
                        player_owning_card = secondary_player
                    current_interrupt = self.interrupts_waiting_on_resolution[0]
                    if current_interrupt == "Dark Angels Purifier":
                        if self.positions_of_units_interrupting[0][1] == planet_pos:
                            if game_update_string[1] == primary_player.number:
                                card_in_reserve = primary_player.cards_in_reserve[planet_pos][unit_pos]
                                if card_in_reserve.check_for_a_trait(
                                        "Dark Angels") and card_in_reserve.get_card_type() == "Army":
                                    if primary_player.spend_resources(card_in_reserve.get_deepstrike_value()):
                                        primary_player.deepstrike_unit(planet_pos, unit_pos)
                                        self.delete_interrupt()
            if len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    await HQInterrupts.resolve_hq_interrupt(self, name, game_update_string,
                                                            primary_player, secondary_player)
                elif game_update_string[0] == "HAND":
                    if game_update_string[1] == primary_player.number:
                        await HandInterrupts.resolve_hand_interrupt(self, name, game_update_string,
                                                                    primary_player, secondary_player)
            if len(game_update_string) == 5:
                if game_update_string[0] == "ATTACHMENT":
                    if game_update_string[1] == "HQ":
                        await AttachmentHQInterrupts.resolve_hq_attachment_interrupt(self, name, game_update_string,
                                                                                     primary_player, secondary_player)
                    if game_update_string[1] == "PLANETS":
                        player_num = int(game_update_string[2])
                        planet_pos = int(game_update_string[3])
                        attachment_pos = int(game_update_string[4])
                        current_interrupt = self.interrupts_waiting_on_resolution[0]
                        if player_num == 1:
                            player_with_attach = self.p1
                        else:
                            player_with_attach = self.p2
                        if current_interrupt == "World Engine Beam":
                            player_with_attach.add_card_to_discard(
                                player_with_attach.attachments_at_planet[planet_pos][attachment_pos].get_name())
                            del player_with_attach.attachments_at_planet[planet_pos][attachment_pos]
                            self.delete_interrupt()

            if len(game_update_string) == 6:
                if game_update_string[0] == "ATTACHMENT":
                    if game_update_string[1] == "IN_PLAY":
                        await AttachmentInPlayInterrupts.resolve_in_play_attachment_interrupt(
                            self, name, game_update_string, primary_player, secondary_player
                        )

    def delete_reaction(self):
        if self.reactions_needing_resolving:
            if self.reactions_needing_resolving[0] == "Ba'ar Zul the Hate-Bound":
                if self.damage_amounts_baarzul:
                    del self.damage_amounts_baarzul[0]
            if self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
                self.need_to_reset_tomb_blade_squadron = True
            if self.reactions_needing_resolving[0] == "Dynastic Weaponry":
                self.need_to_reset_tomb_blade_squadron = True
            if self.reactions_needing_resolving[0] == "Wrathful Retribution":
                if self.player_who_resolves_reaction[0] == self.name_1:
                    self.p1.wrathful_retribution_value = 0
                else:
                    self.p2.wrathful_retribution_value = 0
            if self.reactions_needing_resolving[0] == "Storming Librarian":
                player = self.p1
                if self.player_who_resolves_reaction[0] == self.name_2:
                    player = self.p2
                num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                id_storm_lib = -1
                if pla == -2:
                    id_storm_lib = player.headquarters[pos].card_id
                else:
                    id_storm_lib = player.cards_in_play[pla + 1][pos].card_id
                for i in range(7):
                    for j in range(len(self.p1.cards_in_play[i + 1])):
                        while id_storm_lib in self.p1.cards_in_play[i + 1][j].hit_by_which_storming_librarians:
                            self.p1.cards_in_play[i + 1][j].hit_by_which_storming_librarians.remove(id_storm_lib)
                    for j in range(len(self.p2.cards_in_play[i + 1])):
                        while id_storm_lib in self.p2.cards_in_play[i + 1][j].hit_by_which_storming_librarians:
                            self.p2.cards_in_play[i + 1][j].hit_by_which_storming_librarians.remove(id_storm_lib)
                for i in range(len(self.p1.headquarters)):
                    while id_storm_lib in self.p1.headquarters[i].hit_by_which_storming_librarians:
                        self.p1.headquarters[i].hit_by_which_storming_librarians.remove(id_storm_lib)
                for i in range(len(self.p2.headquarters)):
                    while id_storm_lib in self.p2.headquarters[i].hit_by_which_storming_librarians:
                        self.p2.headquarters[i].hit_by_which_storming_librarians.remove(id_storm_lib)
            self.asking_which_reaction = True
            self.already_resolving_reaction = False
            self.last_player_who_resolved_reaction = self.player_who_resolves_reaction[0]
            del self.reactions_needing_resolving[0]
            del self.player_who_resolves_reaction[0]
            del self.positions_of_unit_triggering_reaction[0]
            del self.additional_reactions_info[0]
        if not self.reactions_needing_resolving:
            for i in range(len(self.p1.headquarters)):
                if self.p1.check_is_unit_at_pos(-2, i):
                    self.p1.headquarters[i].valid_target_magus_harid = False
            for i in range(len(self.p2.headquarters)):
                if self.p2.check_is_unit_at_pos(-2, i):
                    self.p2.headquarters[i].valid_target_magus_harid = False
            for i in range(7):
                for j in range(len(self.p1.cards_in_play[i + 1])):
                    self.p1.cards_in_play[i + 1][j].valid_target_ashen_banner = False
                    self.p1.cards_in_play[i + 1][j].valid_target_magus_harid = False
            for i in range(7):
                for j in range(len(self.p2.cards_in_play[i + 1])):
                    self.p2.cards_in_play[i + 1][j].valid_target_ashen_banner = False
                    self.p2.cards_in_play[i + 1][j].valid_target_magus_harid = False
            self.p1.reset_movement_trackers()
            self.p2.reset_movement_trackers()

    def delete_interrupt(self):
        if self.interrupts_waiting_on_resolution:
            if self.interrupts_waiting_on_resolution[0] == "Magus Harid":
                player = self.p1
                if self.player_resolving_interrupts[0] == self.name_2:
                    player = self.p2
                if player.magus_harid_waiting_cards:
                    del player.magus_harid_waiting_cards[0]
            if self.interrupts_waiting_on_resolution[0] == "Magus Harid: Final Form" or \
                    self.interrupts_waiting_on_resolution[0] == "Grand Master Belial":
                player = self.p1
                if self.player_resolving_interrupts[0] == self.name_2:
                    player = self.p2
                warlord_pla, warlord_pos = player.get_location_of_warlord()
                if warlord_pla == -1 or warlord_pos == -1:
                    player.warlord_just_got_destroyed = True
            if self.interrupts_waiting_on_resolution[0] == "Saint Celestine: Rebirth":
                player = self.p1
                if self.player_resolving_interrupts[0] == self.name_2:
                    player = self.p2
                warlord_pla, warlord_pos = player.get_location_of_warlord()
                if warlord_pla == -1 or warlord_pos == -1:
                    player.warlord_just_got_destroyed = True
                else:
                    player.set_once_per_game_used_given_pos(warlord_pla, warlord_pos, True)
            self.asking_which_interrupt = True
            self.last_player_who_resolved_interrupt = self.player_resolving_interrupts[0]
            del self.interrupts_waiting_on_resolution[0]
            del self.player_resolving_interrupts[0]
            del self.positions_of_units_interrupting[0]
            del self.extra_interrupt_info[0]
        self.already_resolving_interrupt = False

    def start_ranged_skirmish(self, planet_pos):
        self.ranged_skirmish_active = True
        for i in range(len(self.p1.cards_in_play[planet_pos + 1])):
            for j in range(len(self.p1.cards_in_play[planet_pos + 1][i].attachments)):
                if self.p1.cards_in_play[planet_pos + 1][i].attachments[j].get_ability() == "Sanctified Bolter":
                    self.create_reaction("Sanctified Bolter", self.name_1, (1, planet_pos, i))
        for i in range(len(self.p2.cards_in_play[planet_pos + 1])):
            for j in range(len(self.p2.cards_in_play[planet_pos + 1][i].attachments)):
                if self.p2.cards_in_play[planet_pos + 1][i].attachments[j].get_ability() == "Sanctified Bolter":
                    self.create_reaction("Sanctified Bolter", self.name_2, (2, planet_pos, i))

    async def shield_cleanup(self, primary_player, secondary_player, planet_pos):
        self.guardian_mesh_armor_active = False
        self.liatha_active = False
        self.liatha_available = True
        self.maksim_squadron_active = False
        self.maksim_squadron_enabled = True
        self.distorted_talos_enabled = True
        self.woken_machine_spirit_enabled = True
        self.guardian_mesh_armor_enabled = True
        self.alt_shield_mode_active = False
        self.may_block_with_ols = True
        self.alt_shield_name = ""
        self.starmist_raiment = False
        primary_player.reset_card_name_misc_ability("Data Analyzer")
        secondary_player.reset_card_name_misc_ability("Data Analyzer")
        primary_player.reset_card_name_misc_ability("Steel Legion Chimera")
        primary_player.reset_card_name_misc_ability("Blood Angels Veterans")
        secondary_player.reset_card_name_misc_ability("Steel Legion Chimera")
        secondary_player.reset_card_name_misc_ability("Blood Angels Veterans")
        primary_player.reset_card_name_misc_ability("Follower of Gork")
        secondary_player.reset_card_name_misc_ability("Follower of Gork")
        primary_player.reset_card_name_misc_ability("Noble Shining Spears")
        secondary_player.reset_card_name_misc_ability("Noble Shining Spears")
        primary_player.reset_card_name_misc_ability("Deff Dread")
        secondary_player.reset_card_name_misc_ability("Deff Dread")
        primary_player.reset_card_name_misc_ability("Null Shield Matrix")
        secondary_player.reset_card_name_misc_ability("Null Shield Matrix")
        primary_player.phalanx_shield_value = 0
        secondary_player.phalanx_shield_value = 0
        if not self.retaliate_used:
            if self.amount_that_can_be_removed_by_shield[0] > 2:
                player_num, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
                if primary_player.search_attachments_at_pos(planet_pos, unit_pos, "Pulsating Carapace"):
                    damage_to_remove = self.amount_that_can_be_removed_by_shield[0] - 2
                    self.amount_that_can_be_removed_by_shield[0] = 2
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage_to_remove)
            if self.amount_that_can_be_removed_by_shield[0] > 3:
                player_num, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
                if primary_player.get_ability_given_pos(planet_pos, unit_pos) == "Rampaging Knarloc":
                    if primary_player.resources > 3:
                        damage_to_remove = self.amount_that_can_be_removed_by_shield[0] - 3
                        self.amount_that_can_be_removed_by_shield[0] = 3
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage_to_remove)
            if self.amount_that_can_be_removed_by_shield[0] > 1:
                player_num, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
                if primary_player.celestian_amelia_active \
                        and primary_player.get_ability_given_pos(planet_pos, unit_pos) != "Celesitan Amelia":
                    if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum":
                        damage_to_remove = self.amount_that_can_be_removed_by_shield[0] - 1
                        self.amount_that_can_be_removed_by_shield[0] = 1
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage_to_remove)
            if self.amount_that_can_be_removed_by_shield[0] > 0:
                num, def_pla, def_pos = self.positions_of_units_to_take_damage[0]
                if primary_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                    if primary_player.get_ability_given_pos(warlord_pla, warlord_pos,
                                                            bloodied_relevant=True) == "Chapter Champion Varn":
                        if primary_player.check_if_support_exists():
                            health = primary_player.get_health_given_pos(def_pla, def_pos)
                            damage = primary_player.get_damage_given_pos(def_pla, def_pos)
                            if health >= damage:
                                primary_player.remove_damage_from_pos(def_pla, def_pos, 1)
                                self.create_interrupt("Chapter Champion Varn", primary_player.name_player,
                                                      (int(primary_player.number), -1, -1))
                if not primary_player.check_if_card_is_destroyed(def_pla, def_pos):
                    if primary_player.get_ability_given_pos(def_pla, def_pos) != "Ba'ar Zul the Hate-Bound":
                        if primary_player.search_card_at_planet(def_pla, "Ba'ar Zul the Hate-Bound",
                                                                bloodied_relevant=True):
                            if not primary_player.hit_by_gorgul:
                                self.create_reaction("Ba'ar Zul the Hate-Bound", primary_player.name_player,
                                                     (int(primary_player.number), def_pla, def_pos))
                                self.damage_amounts_baarzul.append(self.amount_that_can_be_removed_by_shield[0])
                    if primary_player.check_for_trait_given_pos(def_pla, def_pos, "Slaanesh"):
                        for i in range(7):
                            if i != def_pla:
                                for j in range(len(primary_player.cards_in_play[i + 1])):
                                    if primary_player.get_ability_given_pos(i, j) == "Seekers of Pleasure":
                                        self.create_reaction("Seekers of Pleasure", primary_player.name_player,
                                                             (int(primary_player.number), i, j),
                                                             additional_info=def_pla)
                    if self.card_names_triggering_damage[0] in self.valid_crushing_blow_triggers:
                        if not secondary_player.check_if_already_have_reaction("Crushing Blow"):
                            if secondary_player.search_hand_for_card("Crushing Blow"):
                                self.create_reaction("Crushing Blow", secondary_player.name_player,
                                                     (int(primary_player.number), -1, -1))
                                primary_player.set_valid_crushing_blow_given_pos(def_pla, def_pos, True)
                    if self.positions_attackers_of_units_to_take_damage[0] is not None:
                        player_num, planet_pos, unit_pos = self.positions_attackers_of_units_to_take_damage[0]
                        if not secondary_player.check_if_already_have_reaction("Crushing Blow"):
                            if secondary_player.search_hand_for_card("Crushing Blow"):
                                if secondary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                                    self.create_reaction("Crushing Blow", secondary_player.name_player,
                                                         (int(primary_player.number), -1, -1))
                                    primary_player.set_valid_crushing_blow_given_pos(def_pla, def_pos, True)
                        if not secondary_player.check_if_already_have_reaction("The Fury of Sicarius"):
                            if secondary_player.search_hand_for_card("The Fury of Sicarius"):
                                if primary_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
                                    if secondary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                                        self.create_reaction("The Fury of Sicarius", secondary_player.name_player,
                                                             (int(primary_player.number), def_pla, def_pos))

            if self.positions_attackers_of_units_to_take_damage[0] is not None:
                player_num, planet_pos, unit_pos = self.positions_attackers_of_units_to_take_damage[0]
                secondary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                num, def_pla, def_pos = self.positions_of_units_to_take_damage[0]
                if not primary_player.check_if_card_is_destroyed(def_pla, def_pos):
                    if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Shedding Hive Crone":
                        if primary_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
                            self.create_delayed_reaction("Shedding Hive Crone", secondary_player.name_player,
                                                         (int(secondary_player.number), planet_pos, unit_pos))
                    if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Bladeguard Veteran Squad":
                        if primary_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
                            if not secondary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos):
                                self.create_delayed_reaction("Bladeguard Veteran Squad", secondary_player.name_player,
                                                             (int(secondary_player.number), planet_pos, unit_pos))
                    for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                        if secondary_player.get_ability_given_pos(planet_pos, i) == "Penitent Engine":
                            self.create_delayed_reaction("Penitent Engine", secondary_player.name_player,
                                                         (int(secondary_player.number), planet_pos, i))
                    if self.amount_that_can_be_removed_by_shield[0] > 0:
                        if primary_player.search_hand_for_card("Righteous Reprisal") and \
                                primary_player.get_resources() > 0:
                            if primary_player.get_faction_given_pos(def_pla, def_pos) == "Space Marines" and \
                                    primary_player.get_ready_given_pos(def_pla, def_pos):
                                self.create_reaction("Righteous Reprisal", primary_player.name_player,
                                                     (num, def_pla, def_pos))
                        if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Chaos Maulerfiend":
                            self.create_reaction("Chaos Maulerfiend", secondary_player.name_player,
                                                 (int(secondary_player.number), planet_pos, unit_pos),
                                                 (def_pla, def_pos))
                else:
                    if primary_player.get_card_type_given_pos(def_pla, def_pos) != "Warlord":
                        if secondary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                            for _ in range(secondary_player.mork_blessings_count):
                                self.create_delayed_reaction("Blessing of Mork", secondary_player.name_player,
                                                             (int(secondary_player.number), planet_pos, unit_pos))
                        if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Patrolling Wraith":
                            self.create_delayed_reaction("Patrolling Wraith", secondary_player.name_player,
                                                         (int(secondary_player.number), planet_pos, unit_pos),
                                                         primary_player.get_name_given_pos(def_pla, def_pos))
                        if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Draining Cronos":
                            self.create_delayed_reaction("Draining Cronos", secondary_player.name_player,
                                                         (int(secondary_player.number), planet_pos, unit_pos))
                        if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Salvaged Battlewagon":
                            self.create_delayed_reaction("Salvaged Battlewagon", secondary_player.name_player,
                                                         (int(secondary_player.number), planet_pos, unit_pos))
                        if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Goliath Rockgrinder":
                            self.create_delayed_reaction("Goliath Rockgrinder", secondary_player.name_player,
                                                         (int(secondary_player.number), planet_pos, unit_pos))
                            self.goliath_rockgrinder_value = primary_player.cards_in_play[def_pla + 1][def_pos].health
                        if secondary_player.search_card_in_hq("Restorative Tunnels", ready_relevant=True):
                            if secondary_player.get_damage_given_pos(planet_pos, unit_pos) > 0:
                                self.create_delayed_reaction("Restorative Tunnels", secondary_player.name_player,
                                                             (int(secondary_player.number), planet_pos, unit_pos))
                        for i in range(len(secondary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments())):
                            if primary_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
                                if secondary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[
                                    i].get_ability() == "Bone Sabres":
                                    self.create_delayed_reaction("Bone Sabres", secondary_player.name_player,
                                                                 (int(secondary_player.number), planet_pos, unit_pos))
                                if secondary_player.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[
                                    i].get_ability() == "Kroot Hunting Rifle":
                                    self.create_delayed_reaction("Kroot Hunting Rifle", secondary_player.name_player,
                                                                 (int(secondary_player.number), planet_pos, unit_pos))
                        if primary_player.get_card_type_given_pos(def_pla, def_pos) == "Army":
                            if secondary_player.search_card_in_hq("Holding Cell"):
                                self.create_delayed_reaction("Holding Cell", secondary_player.name_player,
                                                             (int(secondary_player.number), -1, -1))
                                self.name_of_attacked_unit = primary_player.get_name_given_pos(def_pla, def_pos)
                            if secondary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Genestealer"):
                                if primary_player.get_cost_given_pos(def_pla, def_pos) < 4:
                                    if secondary_player.get_resources() > 0 and \
                                            secondary_player.search_hand_for_card("Gene Implantation"):
                                        self.create_delayed_reaction("Gene Implantation", secondary_player.name_player,
                                                                     (int(secondary_player.number), -1, -1), 
                                                                     primary_player.get_name_given_pos(
                                                                         def_pla, def_pos))
                            if secondary_player.get_ability_given_pos(
                                    planet_pos, unit_pos) == "Ravenous Haruspex":
                                if not secondary_player.get_once_per_phase_used_given_pos(planet_pos, unit_pos):
                                    self.create_delayed_reaction("Ravenous Haruspex", secondary_player.name_player,
                                                                 (int(secondary_player.number), planet_pos, unit_pos))
                                    self.ravenous_haruspex_gain = primary_player.get_cost_given_pos(
                                        def_pla, def_pos)
                            if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Striking Ravener":
                                self.create_delayed_reaction("Striking Ravener", secondary_player.name_player,
                                                             (int(secondary_player.number), planet_pos, unit_pos))
                            if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Fire Prism":
                                self.create_delayed_reaction("Fire Prism", secondary_player.name_player,
                                                             (int(secondary_player.number), planet_pos, unit_pos))
        else:
            player_num, planet_pos, unit_pos = self.positions_attackers_of_units_to_take_damage[0]
            if secondary_player.get_ability_given_pos(planet_pos, unit_pos) == "Shedding Hive Crone":
                self.create_delayed_reaction("Shedding Hive Crone", secondary_player.name_player,
                                             (int(secondary_player.number), planet_pos, unit_pos))
            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                if secondary_player.get_ability_given_pos(planet_pos, i) == "Penitent Engine":
                    self.create_delayed_reaction("Penitent Engine", secondary_player.name_player,
                                                 (int(secondary_player.number), planet_pos, i))
        if self.action_chosen == "Painboy Surjery":
            player_num, planet_pos, unit_pos = self.positions_of_units_to_take_damage[0]
            if primary_player.check_if_card_is_destroyed(planet_pos, unit_pos):
                secondary_player.create_enemy_played_event_reactions()
                self.action_cleanup()
        del self.damage_on_units_list_before_new_damage[0]
        del self.damage_is_preventable[0]
        del self.positions_of_units_to_take_damage[0]
        del self.damage_can_be_shielded[0]
        del self.positions_attackers_of_units_to_take_damage[0]
        del self.card_names_triggering_damage[0]
        del self.amount_that_can_be_removed_by_shield[0]
        self.damage_moved_to_old_one_eye = 0
        self.retaliate_used = False
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

    async def update_interrupts(self, name, game_update_string, count=0):
        print("updating")
        if self.interrupts_waiting_on_resolution and not self.already_resolving_interrupt \
                and not self.already_resolving_reaction and not self.resolving_search_box \
                and not self.queued_moves:
            print("not already resolving")
            if count < 10:
                p_one_count, p_two_count = self.count_number_interrupts_for_each_player()
                print("p_one count: ", p_one_count, "p_two count: ", p_two_count)
                if p_one_count > 0 and ((self.player_with_initiative == self.name_1 and
                                         self.last_player_who_resolved_interrupt != self.name_1)
                                        or (self.last_player_who_resolved_interrupt == self.name_2) or
                                        p_two_count == 0):
                    print("\n\nInterrupts update UPDATE P1\n\n")
                    self.stored_interrupt_indexes = self.get_positions_of_players_interrupts(self.name_1)
                    if p_one_count > 1:
                        if self.asking_which_interrupt:
                            self.choices_available = self.get_name_interrupts_of_players_interrupts(self.name_1)
                            self.choice_context = "Choose Which Interrupt"
                            self.name_player_making_choices = self.name_1
                        elif not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            if self.interrupts_waiting_on_resolution[0] in self.forced_interrupts:
                                self.choices_available = ["Yes"]
                            self.choice_context = self.interrupts_waiting_on_resolution[0]
                            self.name_player_making_choices = self.player_resolving_interrupts[0]
                            self.asking_if_interrupt = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_interrupt = True
                            self.reset_choices_available()
                            await StartInterrupt.start_resolving_interrupt(self, name, game_update_string)
                    else:
                        interrupt_pos = self.stored_interrupt_indexes[0]
                        self.move_interrupt_to_front(interrupt_pos)
                        self.asking_which_interrupt = False
                        if not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            if self.interrupts_waiting_on_resolution[0] in self.forced_interrupts:
                                self.choices_available = ["Yes"]
                            self.choice_context = self.interrupts_waiting_on_resolution[0]
                            self.name_player_making_choices = self.player_resolving_interrupts[0]
                            self.asking_if_interrupt = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_interrupt = True
                            self.reset_choices_available()
                            await StartInterrupt.start_resolving_interrupt(self, name, game_update_string)
                else:
                    self.stored_interrupt_indexes = self.get_positions_of_players_interrupts(self.name_2)
                    if p_two_count > 1:
                        if self.asking_which_interrupt:
                            self.choices_available = self.get_name_interrupts_of_players_interrupts(self.name_2)
                            self.choice_context = "Choose Which Interrupt"
                            self.name_player_making_choices = self.name_2
                        elif not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = self.interrupts_waiting_on_resolution[0]
                            self.name_player_making_choices = self.player_resolving_interrupts[0]
                            self.asking_if_interrupt = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_interrupt = True
                            self.reset_choices_available()
                            await StartInterrupt.start_resolving_interrupt(self, name, game_update_string)
                    else:
                        interrupt_pos = self.stored_interrupt_indexes[0]
                        self.move_interrupt_to_front(interrupt_pos)
                        self.asking_which_interrupt = False
                        if not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            self.choice_context = self.interrupts_waiting_on_resolution[0]
                            self.name_player_making_choices = self.player_resolving_interrupts[0]
                            self.asking_if_interrupt = True
                        elif self.has_chosen_to_resolve:
                            self.has_chosen_to_resolve = False
                            self.already_resolving_interrupt = True
                            self.reset_choices_available()
                            await StartInterrupt.start_resolving_interrupt(self, name, game_update_string)

    def convert_delayed(self):
        for i in range(len(self.delayed_reactions_needing_resolving)):
            self.reactions_needing_resolving.append(self.delayed_reactions_needing_resolving[i])
            self.player_who_resolves_reaction.append(self.delayed_player_who_resolves_reaction[i])
            self.positions_of_unit_triggering_reaction.append(self.delayed_positions_of_unit_triggering_reaction[i])
            self.additional_reactions_info.append(self.delayed_additional_reactions_info[i])
        self.delayed_player_who_resolves_reaction = []
        self.delayed_reactions_needing_resolving = []
        self.delayed_positions_of_unit_triggering_reaction = []
        self.delayed_additional_reactions_info = []

    async def update_reactions(self, name, game_update_string, count=0):
        if count < 10:
            if self.reactions_needing_resolving and not self.already_resolving_reaction and not \
                    self.resolving_search_box and not self.interrupts_waiting_on_resolution \
                    and not self.positions_of_units_to_take_damage and not self.queued_moves:
                p_one_count, p_two_count = self.count_number_reactions_for_each_player()
                print("p_one count: ", p_one_count, "p_two count: ", p_two_count)
                if p_one_count > 0 and ((self.player_with_initiative == self.name_1 and
                                         self.last_player_who_resolved_reaction != self.name_1)
                                        or (self.last_player_who_resolved_reaction == self.name_2) or
                                        p_two_count == 0):
                    print("\n\nREACTION UPDATE P1\n\n")
                    self.stored_reaction_indexes = self.get_positions_of_players_reactions(self.name_1)
                    if p_one_count > 1:
                        if self.asking_which_reaction:
                            self.choices_available = self.get_name_reactions_of_players_reactions(self.name_1)
                            self.choice_context = "Choose Which Reaction"
                            self.name_player_making_choices = self.name_1
                        elif not self.has_chosen_to_resolve:
                            self.choices_available = ["Yes", "No"]
                            if self.reactions_needing_resolving[0] in self.forced_reactions:
                                self.choices_available = ["Yes"]
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
                            if self.reactions_needing_resolving[0] in self.forced_reactions:
                                self.choices_available = ["Yes"]
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
                            if self.reactions_needing_resolving[0] in self.forced_reactions:
                                self.choices_available = ["Yes"]
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
                            if self.reactions_needing_resolving[0] in self.forced_reactions:
                                self.choices_available = ["Yes"]
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
                            if primary_player.urien_relevant:
                                primary_player.spend_resources(1)
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
                            if primary_player.urien_relevant:
                                primary_player.spend_resources(1)
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
                                self.p1.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True,
                                                             rickety_warbuggy=True)
                    else:
                        if self.p2.cards_in_play[planet_pos + 1][unit_pos].valid_kugath_nurgling_target:
                            if self.p2.cards_in_play[planet_pos + 1][unit_pos].damage_from_kugath_nurgling < \
                                    self.calc_kugath_nurgling_triggers_at_planet(planet_pos):
                                self.p2.cards_in_play[planet_pos + 1][unit_pos].damage_from_kugath_nurgling += 1
                                self.p2.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True,
                                                             rickety_warbuggy=True)

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

    async def nurgling_bomb_resolution(self, name, game_update_string):
        if self.player_resolving_nurgling_bomb == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if name == self.player_resolving_nurgling_bomb:
            if len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if game_update_string[1] == primary_player.get_number():
                        planet_pos = int(game_update_string[2])
                        unit_pos = int(game_update_string[3])
                        if primary_player.cards_in_play[planet_pos + 1][unit_pos].need_to_resolve_nurgling_bomb:
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.choices_available = ["Rout", "Damage"]
                            self.choice_context = "Nurgling Bomb Choice:"
                            self.name_player_making_choices = primary_player.name_player

    def complete_nurgling_bomb(self, planet_id):
        i = 0
        while i < len(self.p1.cards_in_play[planet_id + 1]):
            if self.p1.cards_in_play[planet_id + 1][i].choice_nurgling_bomb == "Rout":
                self.p1.cards_in_play[planet_id + 1][i].choice_nurgling_bomb = ""
                self.p1.rout_unit(planet_id, i)
                i = i - 1
            i += 1
        i = 0
        while i < len(self.p2.cards_in_play[planet_id + 1]):
            if self.p2.cards_in_play[planet_id + 1][i].choice_nurgling_bomb == "Rout":
                self.p2.cards_in_play[planet_id + 1][i].choice_nurgling_bomb = ""
                self.p2.rout_unit(planet_id, i)
                i = i - 1
            i += 1
        i = 0
        while i < len(self.p1.cards_in_play[planet_id + 1]):
            if self.p1.cards_in_play[planet_id + 1][i].choice_nurgling_bomb == "Damage":
                self.p1.cards_in_play[planet_id + 1][i].choice_nurgling_bomb = ""
                self.p1.assign_damage_to_pos(planet_id, i, 1, by_enemy_unit=False)
                i = i - 1
            i += 1
        i = 0
        while i < len(self.p2.cards_in_play[planet_id + 1]):
            if self.p2.cards_in_play[planet_id + 1][i].choice_nurgling_bomb == "Damage":
                self.p2.cards_in_play[planet_id + 1][i].choice_nurgling_bomb = ""
                self.p2.assign_damage_to_pos(planet_id, i, 1, by_enemy_unit=False)
                i = i - 1
            i += 1
        self.resolving_nurgling_bomb = False

    def scan_planet_for_nurgling_bomb(self, pri, sec, planet_id):
        for i in range(len(pri.cards_in_play[planet_id + 1])):
            if pri.cards_in_play[planet_id + 1][i].need_to_resolve_nurgling_bomb:
                self.player_resolving_nurgling_bomb = pri.name_player
                return True
        for i in range(len(sec.cards_in_play[planet_id + 1])):
            if sec.cards_in_play[planet_id + 1][i].need_to_resolve_nurgling_bomb:
                self.player_resolving_nurgling_bomb = sec.name_player
                return True
        return False

    def made_ta_fight(self):
        warlord_planet, warlord_pos = self.p1.get_location_of_warlord()
        print("made ta fight")
        if warlord_planet != -2:
            print("ok warlord")
            if self.p1.stored_targets_the_emperor_protects:
                print("units valid")
                if self.p1.search_hand_for_card("Made Ta Fight") and self.p1.resources > 1:
                    already_present = False
                    for i in range(len(self.reactions_needing_resolving)):
                        if self.reactions_needing_resolving[i] == "Made Ta Fight":
                            if self.player_who_resolves_reaction[i] == self.name_1:
                                already_present = True
                    if not already_present:
                        self.create_reaction("Made Ta Fight", self.name_1, (1, -1, -1))
        warlord_planet, warlord_pos = self.p2.get_location_of_warlord()
        if warlord_planet != -2:
            if self.p2.stored_targets_the_emperor_protects:
                if self.p2.search_hand_for_card("Made Ta Fight") and self.p2.resources > 1:
                    already_present = False
                    for i in range(len(self.reactions_needing_resolving)):
                        if self.reactions_needing_resolving[i] == "Made Ta Fight":
                            if self.player_who_resolves_reaction[i] == self.name_2:
                                already_present = True
                    if not already_present:
                        self.create_reaction("Made Ta Fight", self.name_2, (2, -1, -1))

    def emp_protecc(self):
        if self.p1.stored_targets_the_emperor_protects:
            if self.p1.search_hand_for_card("The Emperor Protects"):
                if not self.p1.check_if_already_have_reaction("The Emperor Protects"):
                    self.create_reaction("The Emperor Protects", self.name_1, (1, -1, -1))
        if self.p2.stored_targets_the_emperor_protects:
            if self.p2.search_hand_for_card("The Emperor Protects"):
                if not self.p2.check_if_already_have_reaction("The Emperor Protects"):
                    self.create_reaction("The Emperor Protects", self.name_2, (2, -1, -1))

    def change_to_reserve(self, game_update_string):
        if len(game_update_string) == 4:
            if game_update_string[0] == "IN_PLAY":
                if game_update_string[1] == "1":
                    if len(self.p1.cards_in_play[int(game_update_string[2]) + 1]) <= int(game_update_string[3]):
                        if self.p1.cards_in_reserve[int(game_update_string[2])]:
                            game_update_string[0] = "RESERVE"
                            print(game_update_string[3], len(self.p1.cards_in_play[int(game_update_string[2]) + 1]))
                            game_update_string[3] = str(int(game_update_string[3]) -
                                                        len(self.p1.cards_in_play[int(game_update_string[2]) + 1]))
                            return game_update_string
                elif game_update_string[1] == "2":
                    if len(self.p2.cards_in_play[int(game_update_string[2]) + 1]) <= int(game_update_string[3]):
                        if self.p2.cards_in_reserve[int(game_update_string[2])]:
                            game_update_string[0] = "RESERVE"
                            game_update_string[3] = str(int(game_update_string[3]) -
                                                        len(self.p2.cards_in_play[int(game_update_string[2]) + 1]))
                            return game_update_string
        return game_update_string

    async def resolve_xv805_enforcer(self, name, game_update_string):
        if name == self.player_using_xv805:
            if self.asking_if_use_xv805_enforcer:
                if game_update_string[0] == "CHOICE":
                    if game_update_string[1] == "0":
                        self.asking_amount_xv805_enforcer = True
                        self.asking_if_use_xv805_enforcer = False
                    else:
                        self.xv805_enforcer_active = False
                        self.asking_if_use_xv805_enforcer = False
                        self.asking_amount_xv805_enforcer = False
                        self.amount_xv805_enforcer = 0
                        self.damage_index_xv805 = -1
                        self.player_using_xv805 = ""
                        self.og_pos_xv805_target = (-1, -1)
                        self.resolving_search_box = False
                        self.reset_choices_available()
            elif self.asking_amount_xv805_enforcer:
                if game_update_string[0] == "CHOICE":
                    self.amount_xv805_enforcer = int(self.choices_available[int(game_update_string[1])])
                    self.asking_amount_xv805_enforcer = False
            else:
                if game_update_string[0] == "IN_PLAY":
                    new_pla = int(game_update_string[2])
                    new_pos = int(game_update_string[3])
                    if new_pla == self.last_planet_checked_for_battle:
                        primary_player = self.p1
                        enemy_player = self.p2
                        if primary_player.name_player != name:
                            primary_player = self.p2
                            enemy_player = self.p1
                        if game_update_string[1] == enemy_player.get_number():
                            og_pla, og_pos = self.og_pos_xv805_target
                            if og_pla != new_pla or og_pos != new_pos:
                                enemy_player.assign_damage_to_pos(new_pla, new_pos, self.amount_xv805_enforcer,
                                                                  rickety_warbuggy=True, is_reassign=True)
                                enemy_player.remove_damage_from_pos(og_pla, og_pos, self.amount_xv805_enforcer)
                                self.amount_that_can_be_removed_by_shield[self.damage_index_xv805] = \
                                    self.amount_that_can_be_removed_by_shield[self.damage_index_xv805] - \
                                    self.amount_xv805_enforcer
                                self.xv805_enforcer_active = False
                                self.asking_if_use_xv805_enforcer = False
                                self.asking_amount_xv805_enforcer = False
                                self.amount_xv805_enforcer = 0
                                self.damage_index_xv805 = -1
                                self.player_using_xv805 = ""
                                self.og_pos_xv805_target = (-1, -1)
                                self.resolving_search_box = False
                                self.reset_choices_available()

    def complete_intercept(self):
        self.p1.reset_all_aiming_reticles_play_hq()
        self.p2.reset_all_aiming_reticles_play_hq()
        self.intercept_active = False
        self.name_player_intercept = ""

    async def resolve_intercept(self, name, game_update_string):
        if name == self.name_player_intercept:
            if name == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
            if len(game_update_string) == 1:
                if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                    self.intercept_active = False
                    self.name_player_intercept = ""
                    self.intercept_enabled = False
                    new_string_list = self.nullify_string.split(sep="/")
                    print("String used:", new_string_list)
                    await self.update_game_event(secondary_player.name_player, new_string_list,
                                                 same_thread=True)
                    self.intercept_enabled = True
            if len(game_update_string) == 3:
                if game_update_string[0] == "HQ":
                    if game_update_string[1] == primary_player.number:
                        await HQIntercept.update_intercept_hq(self, primary_player, secondary_player,
                                                              name, game_update_string, self.nullified_card_name)
            if len(game_update_string) == 4:
                if game_update_string[0] == "IN_PLAY":
                    if game_update_string[1] == primary_player.number:
                        await InPlayIntercept.update_intercept_in_play(
                            self, primary_player, secondary_player,
                            name, game_update_string, self.nullified_card_name)

    async def resolve_discard_interrupt(self, name, game_update_string):
        if name == self.name_player_making_choices:
            if name == self.name_1:
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
            if self.interrupting_discard_effect_active == "BCO":
                if not self.chosen_first_card:
                    if len(game_update_string) == 2:
                        if game_update_string[0] == "PLANETS":
                            primary_player.summon_token_at_planet("Guardsman", int(game_update_string[1]))
                            primary_player.summon_token_at_planet("Guardsman", int(game_update_string[1]))
                            self.chosen_first_card = True
                            await self.send_update_message("Now attach the Blade of the Crimson Oath to a unit.")
                else:
                    if len(game_update_string) == 3:
                        if game_update_string[0] == "HQ":
                            if game_update_string[1] == primary_player.get_number():
                                card = self.preloaded_find_card("Blade of the Crimson Oath")
                                if primary_player.attach_card(card, -2, int(game_update_string[2])):
                                    self.interrupting_discard_effect_active = False
                                    self.interrupts_discard_enemy_allowed = False
                                    await self.complete_enemy_discard(primary_player, secondary_player)
                                    self.interrupts_discard_enemy_allowed = True
                    elif len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            if game_update_string[1] == primary_player.get_number():
                                card = self.preloaded_find_card("Blade of the Crimson Oath")
                                if primary_player.attach_card(card, int(game_update_string[2]),
                                                              int(game_update_string[3])):
                                    self.interrupting_discard_effect_active = False
                                    self.interrupts_discard_enemy_allowed = False
                                    await self.complete_enemy_discard(primary_player, secondary_player)
                                    self.interrupts_discard_enemy_allowed = True
            elif self.interrupting_discard_effect_active == "Scrying Pool":
                if len(game_update_string) == 1:
                    if game_update_string[0] == "pass-P1" or game_update_string[0] == "pass-P2":
                        self.interrupts_discard_enemy_allowed = False
                        self.discard_fully_prevented = True
                        await self.complete_enemy_discard(primary_player, secondary_player)
                        self.discard_fully_prevented = False
                        self.interrupts_discard_enemy_allowed = True
                if len(game_update_string) == 3:
                    if game_update_string[0] == "HQ":
                        player_owning_card = self.p1
                        if game_update_string[1] == "2":
                            player_owning_card = self.p2
                        card = self.preloaded_find_card("Scrying Pool")
                        if player_owning_card.attach_card(card, -2, int(game_update_string[2])):
                            primary_player.discard.remove("Scrying Pool")
                            self.interrupting_discard_effect_active = False
                            self.interrupts_discard_enemy_allowed = False
                            self.discard_fully_prevented = True
                            await self.complete_enemy_discard(primary_player, secondary_player)
                            self.discard_fully_prevented = False
                            self.interrupts_discard_enemy_allowed = True
                if len(game_update_string) == 4:
                    if game_update_string[0] == "IN_PLAY":
                        player_owning_card = self.p1
                        if game_update_string[1] == "2":
                            player_owning_card = self.p2
                        card = self.preloaded_find_card("Scrying Pool")
                        if player_owning_card.attach_card(card, int(game_update_string[2]), int(game_update_string[3])):
                            primary_player.discard.remove("Scrying Pool")
                            self.interrupting_discard_effect_active = False
                            self.interrupts_discard_enemy_allowed = False
                            self.discard_fully_prevented = True
                            await self.complete_enemy_discard(primary_player, secondary_player)
                            self.discard_fully_prevented = False
                            self.interrupts_discard_enemy_allowed = True
            elif self.interrupting_discard_effect_active == "Hjorvath Coldstorm":
                if not self.chosen_first_card:
                    if len(game_update_string) == 2:
                        if game_update_string[0] == "PLANETS":
                            card = self.preloaded_find_card("Hjorvath Coldstorm")
                            primary_player.add_card_to_planet(card, int(game_update_string[1]))
                            primary_player.remove_card_name_from_hand("Hjorvath Coldstorm")
                            self.chosen_first_card = True
                            self.misc_target_planet = int(game_update_string[1])
                else:
                    if len(game_update_string) == 4:
                        if game_update_string[0] == "IN_PLAY":
                            if game_update_string[1] == secondary_player.get_number():
                                secondary_player.assign_damage_to_pos(int(game_update_string[2]),
                                                                      int(game_update_string[3]), 1,
                                                                      shadow_field_possible=True,
                                                                      rickety_warbuggy=True,
                                                                      context="Hjorvath Coldstorm")
                                primary_player.draw_card()
                                self.interrupting_discard_effect_active = False
                                self.interrupts_discard_enemy_allowed = False
                                await self.complete_enemy_discard(primary_player, secondary_player)
                                self.interrupts_discard_enemy_allowed = True

    async def update_rearranging_deck(self, name, game_update_string):
        if name == self.name_player_rearranging_deck:
            if game_update_string[0] == "CHOICE":
                choice_index = int(game_update_string[1])
                if self.deck_part_being_rearranged[choice_index] == "FINISH":
                    del self.deck_part_being_rearranged[choice_index]
                    player = self.p1
                    if name == self.name_2:
                        player = self.p2
                    for i in range(len(self.deck_part_being_rearranged)):
                        player.deck[i] = self.deck_part_being_rearranged[i]
                    self.stop_rearranging_deck()
                else:
                    self.deck_part_being_rearranged.insert(
                        0, self.deck_part_being_rearranged.pop(choice_index)
                    )

    def stop_rearranging_deck(self):
        self.rearranging_deck = False
        self.name_player_rearranging_deck = ""
        self.deck_part_being_rearranged = []
        self.number_cards_to_rearrange = 0

    async def update_game_event(self, name, game_update_string, same_thread=False):
        if not same_thread:
            self.condition_main_game.acquire()
        resolved_subroutine = False
        game_update_string = self.change_to_reserve(game_update_string)
        print(game_update_string)
        if self.phase == "SETUP":
            await self.send_update_message("Buttons can't be pressed in setup")
        elif self.validate_received_game_string(game_update_string):
            print("String validated as ok")
            if self.choosing_unit_for_nullify:
                await self.nullification_unit(name, game_update_string)
            elif self.intercept_active:
                await self.resolve_intercept(name, game_update_string)
            elif self.xv805_enforcer_active:
                await self.resolve_xv805_enforcer(name, game_update_string)
            elif self.resolving_consumption:
                await self.consumption_resolution(name, game_update_string)
            elif self.manual_bodyguard_resolution:
                await self.resolve_manual_bodyguard(name, game_update_string)
            elif self.rearranging_deck:
                await self.update_rearranging_deck(name, game_update_string)
            elif self.cards_in_search_box:
                await self.resolve_card_in_search_box(name, game_update_string)
            elif self.p1.total_indirect_damage > 0 or self.p2.total_indirect_damage > 0:
                await self.apply_indirect_damage(name, game_update_string)
            elif self.mode == "DISCOUNT":
                await self.update_game_event_applying_discounts(name, game_update_string)
            elif self.choices_available:
                await self.resolve_choice(name, game_update_string)
            elif self.interrupting_discard_effect_active:
                await self.resolve_discard_interrupt(name, game_update_string)
            elif self.resolving_nurgling_bomb:
                await self.nurgling_bomb_resolution(name, game_update_string)
            elif self.interrupts_waiting_on_resolution:
                await self.resolve_interrupts(name, game_update_string)
            elif self.positions_of_units_to_take_damage:
                await self.better_shield_card_resolution(name, game_update_string)
            elif self.resolving_kugath_nurglings:
                await self.resolution_of_kugath_nurglings(name, game_update_string)
            elif self.reactions_needing_resolving:
                await self.resolve_reaction(name, game_update_string)
            elif not self.p1.mobile_resolved or not self.p2.mobile_resolved:
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
            if self.p1.has_passed and self.p2.has_passed and not self.reactions_needing_resolving:
                print("Both passed, move to warlord movement.")
                await self.change_phase("COMMAND")
        elif self.phase == "COMBAT":
            if not self.p1.idden_base_active:
                if self.p1.search_card_in_hq("'idden Base"):
                    self.p1.idden_base_transform()
                    self.p1.idden_base_active = True
            else:
                if not self.p1.search_card_in_hq("'idden Base"):
                    self.p1.idden_base_detransform()
                    self.p1.idden_base_active = False
            if not self.p2.idden_base_active:
                if self.p2.search_card_in_hq("idden Base"):
                    self.p2.idden_base_transform()
                    self.p2.idden_base_active = True
            else:
                if not self.p2.search_card_in_hq("'idden Base"):
                    self.p2.idden_base_detransform()
                    self.p2.idden_base_active = False
        if self.resolving_kugath_nurglings:
            if self.check_end_kugath_nurglings():
                await self.send_update_message("Leaving Ku'gath Nurglings")
        if self.xv805_enforcer_active:
            if self.asking_if_use_xv805_enforcer:
                self.choices_available = ["Yes", "No"]
                self.choice_context = "Use XV8-05 Enforcer to reassign?"
                self.name_player_making_choices = self.player_using_xv805
                self.resolving_search_box = True
            elif self.asking_amount_xv805_enforcer:
                self.choices_available = []
                for i in range(self.amount_xv805_enforcer):
                    self.choices_available.append(str(i + 1))
                self.choice_context = "Use XV8-05 Enforcer to reassign?"
                self.name_player_making_choices = self.player_using_xv805
                self.resolving_search_box = True
            else:
                self.reset_choices_available()
                self.resolving_search_box = False
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
        if self.p1.discard_inquis_caius_wroth or self.p2.discard_inquis_caius_wroth:
            if self.player_who_resolves_reaction[0] == self.name_1:
                if len(self.p1.cards) < 5:
                    self.p1.discard_inquis_caius_wroth = False
                    self.player_who_resolves_reaction[0] = self.name_2
            else:
                if len(self.p2.cards) < 5:
                    self.p2.discard_inquis_caius_wroth = False
                    self.player_who_resolves_reaction[0] = self.name_1
            if not self.p1.discard_inquis_caius_wroth and not self.p2.discard_inquis_caius_wroth:
                self.delete_reaction()
        await self.update_interrupts(name, game_update_string)
        await self.update_interrupts(name, game_update_string)
        await self.update_reactions(name, game_update_string)
        await self.update_reactions(name, game_update_string)
        if not self.reactions_needing_resolving and not self.queued_moves:
            self.last_player_who_resolved_reaction = ""
            if self.reactions_on_winning_combat_being_executed:
                if self.name_player_who_won_combat == self.name_1:
                    winner = self.p1
                    loser = self.p2
                else:
                    winner = self.p2
                    loser = self.p1
                await self.resolve_winning_combat(winner, loser)
            if self.resolve_remaining_cs_after_reactions and not self.positions_of_units_to_take_damage \
                    and not self.interrupts_waiting_on_resolution and not self.queued_moves:
                self.resolve_remaining_cs_after_reactions = False
                ret_val = CommandPhase.try_entire_command(self, self.last_planet_checked_command_struggle)
                await CommandPhase.interpret_command_state(self, ret_val)
        if not self.interrupts_waiting_on_resolution:
            self.p1.valid_prey_on_the_weak = [False, False, False, False, False, False, False]
            self.p2.valid_prey_on_the_weak = [False, False, False, False, False, False, False]
            self.p1.valid_surrogate_host = [False, False, False, False, False, False, False]
            self.p2.valid_surrogate_host = [False, False, False, False, False, False, False]
            self.last_player_who_resolved_interrupt = ""
            self.p1.highest_death_serves_value = 0
            self.p2.highest_death_serves_value = 0
            i = 0
            if not self.positions_of_units_to_take_damage:
                while i < len(self.p1.headquarters):
                    if self.p1.headquarters[i].get_ability() == "World Engine Beam":
                        if self.p1.headquarters[i].counter > 7:
                            self.create_interrupt("World Engine Beam", self.name_1, (1, -2, i))
                    i = i + 1
                i = 0
                while i < len(self.p2.headquarters):
                    if self.p2.headquarters[i].get_ability() == "World Engine Beam":
                        if self.p2.headquarters[i].counter > 7:
                            self.create_interrupt("World Engine Beam", self.name_2, (2, -2, i))
                    i = i + 1
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
            if not self.reactions_needing_resolving and not self.positions_of_units_to_take_damage \
                    and not self.xv805_enforcer_active:
                if self.auto_card_destruction:
                    self.resolve_destruction_checks_after_reactions = False
                    await self.destroy_check_all_cards()
        elif not self.positions_of_units_to_take_damage:
            if self.auto_card_destruction:
                self.resolve_destruction_checks_after_reactions = False
                await self.destroy_check_all_cards()
        if not self.positions_of_units_to_take_damage and not self.interrupts_waiting_on_resolution \
                and not self.choices_available and self.p1.mobile_resolved and self.p2.mobile_resolved and \
                self.mode == "Normal" and not self.xv805_enforcer_active and not self.queued_moves:
            if not self.reactions_needing_resolving and not self.resolving_search_box:
                if self.reactions_on_end_deploy_phase and \
                        not self.p1.extra_deploy_turn_active and not self.p2.extra_deploy_turn_active:
                    self.reactions_on_end_deploy_phase = False
                    await self.send_update_message("Both passed, move to warlord movement.")
                    await self.change_phase("COMMAND")
                self.convert_delayed()
                self.p1.highest_cost_invasion_site = 0
                self.p2.highest_cost_invasion_site = 0
                self.p1.stored_targets_the_emperor_protects = []
                self.p2.stored_targets_the_emperor_protects = []
                self.p1.valid_planets_berzerker_warriors = [False, False, False, False, False, False, False]
                self.p2.valid_planets_berzerker_warriors = [False, False, False, False, False, False, False]
                if self.need_to_reset_tomb_blade_squadron:
                    self.need_to_reset_tomb_blade_squadron = False
                    self.p1.reset_card_name_misc_ability("Tomb Blade Squadron")
                    self.p2.reset_card_name_misc_ability("Tomb Blade Squadron")
                for i in range(len(self.p1.headquarters)):
                    self.p1.headquarters[i].valid_target_dynastic_weaponry = False
                    self.p1.headquarters[i].just_entered_play = False
                for i in range(len(self.p2.headquarters)):
                    self.p2.headquarters[i].valid_target_dynastic_weaponry = False
                    self.p2.headquarters[i].just_entered_play = False
                for i in range(7):
                    for j in range(len(self.p1.cards_in_play[i + 1])):
                        self.p1.cards_in_play[i + 1][j].valid_target_dynastic_weaponry = False
                        self.p1.cards_in_play[i + 1][j].just_entered_play = False
                    for j in range(len(self.p2.cards_in_play[i + 1])):
                        self.p2.cards_in_play[i + 1][j].valid_target_dynastic_weaponry = False
                        self.p2.cards_in_play[i + 1][j].just_entered_play = False
            if self.attack_resolution_cleanup and not self.attack_being_resolved:
                self.attack_resolution_cleanup = False
                if self.damage_abilities_defender_active:
                    self.damage_abilities_defender_active = False
                    self.allow_damage_abilities_defender = True
                    self.p1.reset_all_aiming_reticles_play_hq()
                    self.p2.reset_all_aiming_reticles_play_hq()
            if self.attack_being_resolved and not self.reactions_needing_resolving:
                if self.damage_abilities_defender_active:
                    if self.attacker_position == -1:
                        self.damage_abilities_defender_active = False
                        self.allow_damage_abilities_defender = True
                        self.p1.reset_all_aiming_reticles_play_hq()
                        self.p2.reset_all_aiming_reticles_play_hq()
                    else:
                        primary_player = self.p1
                        secondary_player = self.p2
                        if self.number_with_combat_turn == "2":
                            primary_player = self.p2
                            secondary_player = self.p1
                        self.shadow_thorns_body_allowed = False
                        self.allow_damage_abilities_defender = False
                        def_num, current_planet, current_unit = self.last_defender_position
                        last_game_update_string = ["IN_PLAY", def_num, str(current_planet), str(current_unit)]
                        await CombatPhase.update_game_event_combat_section(
                            self, primary_player.name_player, last_game_update_string)
                        self.damage_abilities_defender_active = False
                        await self.update_game_event(name, [], same_thread=True)
            if self.attack_being_resolved and self.defender_position == -1 and self.attacker_position == -1:
                self.attack_being_resolved = False
                self.p1.celestian_amelia_active = False
                self.p2.celestian_amelia_active = False
                self.flamers_damage_active = False
                self.id_of_the_active_flamer = -1
                planet = self.last_planet_checked_for_battle
                name_player_who_resolved_attack = ""
                if planet > -1:
                    for i in range(len(self.p1.cards_in_play[planet + 1])):
                        if self.p1.cards_in_play[planet + 1][i].resolving_attack:
                            name_player_who_resolved_attack = self.name_1
                            for j in range(len(self.p1.cards_in_play[planet + 1])):
                                self.p1.cards_in_play[planet + 1][j].cannot_be_declared_as_attacker = False
                            if self.p1.get_card_type_given_pos(planet, i) == "Army":
                                for j in range(len(self.p2.cards_in_play[planet + 1])):
                                    if self.p2.get_ability_given_pos(planet, j) == "Tomb Blade Diversionist":
                                        if not self.p2.cards_in_play[planet + 1][j].misc_ability_used:
                                            self.create_reaction("Tomb Blade Diversionist", self.name_2,
                                                                 (1, planet, i))
                            if self.p1.get_card_type_given_pos(planet, i) == "Token":
                                for j in range(len(self.p1.cards_in_play[planet + 1])):
                                    if self.p1.get_ability_given_pos(planet, j) == "Grey Hunters":
                                        if not self.p1.does_own_reaction_exist("Grey Hunters"):
                                            self.create_reaction("Grey Hunters", self.name_1, (1, planet, i))
                                for j in range(len(self.p2.cards_in_play[planet + 1])):
                                    if self.p2.get_ability_given_pos(planet, j) == "Grey Hunters":
                                        if not self.p2.does_own_reaction_exist("Grey Hunters"):
                                            self.create_reaction("Grey Hunters", self.name_2, (1, planet, i))
                            sweep = self.p1.get_sweep_given_pos(planet, i)
                            if sweep > 0 and not self.sweep_active:
                                self.create_reaction("Sweep", self.name_1, (1, planet, i))
                                self.sweep_value = sweep
                            if self.p1.get_ability_given_pos(planet, i) == "Snakebite Thug":
                                self.p1.assign_damage_to_pos(planet, i, 1, shadow_field_possible=True,
                                                             by_enemy_unit=False)
                            if self.p1.get_ability_given_pos(planet, i) == "Shambling Revenant":
                                self.create_reaction("Shambling Revenant", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Explosive Scarabs":
                                self.create_reaction("Explosive Scarabs", self.name_1, (1, planet, i))
                            for j in range(len(self.p1.get_all_attachments_at_pos(planet, i))):
                                if self.p1.get_attachment_at_pos(planet, i, j).get_ability() == "Unstable Runtgun":
                                    self.p1.assign_damage_to_pos(planet, i, 1, by_enemy_unit=False)
                                if self.p1.get_attachment_at_pos(planet, i, j).get_ability() == "Flayer Affliction":
                                    self.create_reaction("Flayer Affliction", self.name_1, (1, planet, i))
                            if self.p1.search_attachments_at_pos(planet, i, "Rail Rifle"):
                                self.create_reaction("Rail Rifle", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Fierce Purgator":
                                self.create_reaction("Fierce Purgator", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Ravenwing Dark Talons":
                                if self.card_type_defender == "Warlord" or self.defender_is_also_warlord:
                                    self.create_reaction("Ravenwing Dark Talons", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Razorwing Jetfighter":
                                if self.defender_is_flying_or_mobile:
                                    if self.p1.get_once_per_phase_used_given_pos(planet, i) < 2:
                                        self.create_reaction("Razorwing Jetfighter", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Furious Wraithblade":
                                if not self.p1.get_once_per_phase_used_given_pos(planet, i):
                                    self.create_reaction("Furious Wraithblade", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Sacred Rose Immolator":
                                if not self.p1.get_once_per_round_used_given_pos(planet, i):
                                    self.create_reaction("Sacred Rose Immolator", self.name_1, (1, planet, i))
                                elif self.p1.get_once_per_round_used_given_pos(planet, i) < 2:
                                    self.create_reaction("Sacred Rose Immolator", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Swordwind Wave Serpent":
                                self.create_reaction("Swordwind Wave Serpent", self.name_1, (1, planet, i))
                            if self.p1.get_faction_given_pos(planet, i) == "Orks":
                                if self.p1.search_card_at_planet(planet, "Blood Axe Strategist"):
                                    self.create_reaction("Blood Axe Strategist", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Ravening Psychopath":
                                self.create_reaction("Ravening Psychopath", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Morkanaut Rekuperator":
                                self.create_reaction("Morkanaut Rekuperator", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Heavy Flamer Retributor":
                                self.create_reaction("Heavy Flamer Retributor", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "The Masque":
                                self.create_reaction("The Masque", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Junk Chucka Kommando":
                                self.create_reaction("Junk Chucka Kommando", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Prodigal Sons Disciple":
                                self.create_reaction("Prodigal Sons Disciple", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Leman Russ Conqueror":
                                self.create_reaction("Leman Russ Conqueror", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Inspiring Sergeant":
                                self.create_reaction("Inspiring Sergeant", self.name_1, (1, planet, i))
                            if self.p1.get_ability_given_pos(planet, i) == "Command Predator":
                                if not self.p1.get_once_per_phase_used_given_pos(planet, i):
                                    self.create_reaction("Command Predator", self.name_1, (1, planet, i))
                            for rok in self.p1.rok_bombardment_active:
                                if rok == "Own":
                                    self.p1.assign_damage_to_pos(planet, i, 1, by_enemy_unit=False)
                                elif not self.p1.get_immune_to_enemy_events(planet, i):
                                    self.p1.assign_damage_to_pos(planet, i, 1, by_enemy_unit=False)
                    for i in range(len(self.p2.cards_in_play[planet + 1])):
                        if self.p2.cards_in_play[planet + 1][i].resolving_attack:
                            name_player_who_resolved_attack = self.name_2
                            for j in range(len(self.p2.cards_in_play[planet + 1])):
                                self.p2.cards_in_play[planet + 1][j].cannot_be_declared_as_attacker = False
                            if self.p2.get_card_type_given_pos(planet, i) == "Army":
                                for j in range(len(self.p1.cards_in_play[planet + 1])):
                                    if self.p1.get_ability_given_pos(planet, j) == "Tomb Blade Diversionist":
                                        if not self.p1.cards_in_play[planet + 1][j].misc_ability_used:
                                            self.create_reaction("Tomb Blade Diversionist", self.name_1,
                                                                 (2, planet, i))
                            if self.p2.get_card_type_given_pos(planet, i) == "Token":
                                for j in range(len(self.p1.cards_in_play[planet + 1])):
                                    if self.p1.get_ability_given_pos(planet, j) == "Grey Hunters":
                                        if not self.p1.does_own_reaction_exist("Grey Hunters"):
                                            self.create_reaction("Grey Hunters", self.name_1, (2, planet, i))
                                for j in range(len(self.p2.cards_in_play[planet + 1])):
                                    if self.p2.get_ability_given_pos(planet, j) == "Grey Hunters":
                                        if not self.p2.does_own_reaction_exist("Grey Hunters"):
                                            self.create_reaction("Grey Hunters", self.name_2, (2, planet, i))
                            sweep = self.p2.get_sweep_given_pos(planet, i)
                            if sweep > 0 and not self.sweep_active:
                                self.create_reaction("Sweep", self.name_2, (2, planet, i))
                                self.sweep_value = sweep
                            if self.p2.get_ability_given_pos(planet, i) == "Snakebite Thug":
                                self.p2.assign_damage_to_pos(planet, i, 1, shadow_field_possible=True,
                                                             by_enemy_unit=False)
                            if self.p2.get_ability_given_pos(planet, i) == "Shambling Revenant":
                                self.create_reaction("Shambling Revenant", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Explosive Scarabs":
                                self.create_reaction("Explosive Scarabs", self.name_2, (2, planet, i))
                            for j in range(len(self.p2.get_all_attachments_at_pos(planet, i))):
                                if self.p2.get_attachment_at_pos(planet, i, j).get_ability() == "Unstable Runtgun":
                                    self.p2.assign_damage_to_pos(planet, i, 1, by_enemy_unit=False)
                                if self.p2.get_attachment_at_pos(planet, i, j).get_ability() == "Flayer Affliction":
                                    self.create_reaction("Flayer Affliction", self.name_2, (2, planet, i))
                            if self.p2.search_attachments_at_pos(planet, i, "Rail Rifle"):
                                self.create_reaction("Rail Rifle", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Fierce Purgator":
                                self.create_reaction("Fierce Purgator", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Furious Wraithblade":
                                if not self.p2.get_once_per_phase_used_given_pos(planet, i):
                                    self.create_reaction("Furious Wraithblade", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Sacred Rose Immolator":
                                if not self.p2.get_once_per_round_used_given_pos(planet, i):
                                    self.create_reaction("Sacred Rose Immolator", self.name_2, (2, planet, i))
                                elif self.p2.get_once_per_round_used_given_pos(planet, i) < 2:
                                    self.create_reaction("Sacred Rose Immolator", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Swordwind Wave Serpent":
                                self.create_reaction("Swordwind Wave Serpent", self.name_2, (2, planet, i))
                            if self.p2.get_faction_given_pos(planet, i) == "Orks":
                                if self.p2.search_card_at_planet(planet, "Blood Axe Strategist"):
                                    self.create_reaction("Blood Axe Strategist", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Ravening Psychopath":
                                self.create_reaction("Ravening Psychopath", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Heavy Flamer Retributor":
                                self.create_reaction("Heavy Flamer Retributor", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "The Masque":
                                self.create_reaction("The Masque", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Ravenwing Dark Talons":
                                if self.card_type_defender == "Warlord" or self.defender_is_also_warlord:
                                    self.create_reaction("Ravenwing Dark Talons", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Razorwing Jetfighter":
                                if self.defender_is_flying_or_mobile:
                                    if self.p2.get_once_per_phase_used_given_pos(planet, i) < 2:
                                        self.create_reaction("Razorwing Jetfighter", self.name_2, (1, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Junk Chucka Kommando":
                                self.create_reaction("Junk Chucka Kommando", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Morkanaut Rekuperator":
                                self.create_reaction("Morkanaut Rekuperator", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Prodigal Sons Disciple":
                                self.create_reaction("Prodigal Sons Disciple", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Leman Russ Conqueror":
                                self.create_reaction("Leman Russ Conqueror", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Inspiring Sergeant":
                                self.create_reaction("Inspiring Sergeant", self.name_2, (2, planet, i))
                            if self.p2.get_ability_given_pos(planet, i) == "Command Predator":
                                if not self.p2.get_once_per_phase_used_given_pos(planet, i):
                                    self.create_reaction("Command Predator", self.name_2, (2, planet, i))
                            for rok in self.p2.rok_bombardment_active:
                                if rok == "Own":
                                    self.p2.assign_damage_to_pos(planet, i, 1, by_enemy_unit=False)
                                elif not self.p2.get_immune_to_enemy_events(planet, i):
                                    self.p2.assign_damage_to_pos(planet, i, 1, by_enemy_unit=False)
                if name_player_who_resolved_attack == self.name_1:
                    if self.p1.resources > 1 and self.p1.search_hand_for_card("Outflank'em"):
                        self.create_reaction("Outflank'em", self.name_1, (1, -1, -1))
                if name_player_who_resolved_attack == self.name_2:
                    if self.p2.resources > 1 and self.p2.search_hand_for_card("Outflank'em"):
                        self.create_reaction("Outflank'em", self.name_2, (2, -1, -1))
                self.p1.ethereal_movement_resolution()
                self.p2.ethereal_movement_resolution()
                self.p1.hit_by_gorgul = False
                self.p2.hit_by_gorgul = False
                self.sweep_active = False
                self.p1.reset_resolving_attacks_everywhere()
                self.p2.reset_resolving_attacks_everywhere()
                self.card_type_defender = ""
                self.defender_is_flying_or_mobile = False
                self.defender_is_also_warlord = False
                self.need_to_move_to_hq = False
                self.unit_will_move_after_attack = False
            if not self.attack_being_resolved and not self.reactions_needing_resolving and not \
                    self.damage_abilities_defender_active and not self.positions_of_units_to_take_damage:
                for i in range(len(self.p1.headquarters)):
                    self.p1.headquarters[i].can_be_crushing_blowed = False
                    self.p1.headquarters[i].valid_target_vow_of_honor = False
                    self.p1.headquarters[i].valid_sweep_target = True
                    self.p1.headquarters[i].recently_assigned_damage = False
                for i in range(len(self.p2.headquarters)):
                    self.p2.headquarters[i].can_be_crushing_blowed = False
                    self.p2.headquarters[i].valid_target_vow_of_honor = False
                    self.p2.headquarters[i].valid_sweep_target = True
                    self.p2.headquarters[i].recently_assigned_damage = False
                for i in range(7):
                    for j in range(len(self.p1.cards_in_play[i + 1])):
                        self.p1.cards_in_play[i + 1][j].can_be_crushing_blowed = False
                        self.p1.cards_in_play[i + 1][j].valid_sweep_target = True
                        self.p1.cards_in_play[i + 1][j].recently_assigned_damage = False
                        self.p1.cards_in_play[i + 1][j].valid_target_vow_of_honor = False
                    for j in range(len(self.p2.cards_in_play[i + 1])):
                        self.p2.cards_in_play[i + 1][j].can_be_crushing_blowed = False
                        self.p2.cards_in_play[i + 1][j].valid_sweep_target = True
                        self.p2.cards_in_play[i + 1][j].recently_assigned_damage = False
                        self.p2.cards_in_play[i + 1][j].valid_target_vow_of_honor = False
        if self.reset_resolving_attack_on_units:
            self.reset_resolving_attack_on_units = False
        await self.update_interrupts(name, game_update_string)
        await self.update_interrupts(name, game_update_string)
        await self.update_reactions(name, game_update_string)
        await self.update_reactions(name, game_update_string)
        if not self.p1.deck and self.phase != "SETUP":
            self.p1.lost_due_to_deck = True
        if not self.p2.deck and self.phase != "SETUP":
            self.p2.lost_due_to_deck = True
        if self.p1.lost_due_to_deck and not self.p1.already_lost_due_to_deck:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_2 + "; " + self.name_1 + " was unable to draw a card from their deck."
                                                                    "----GAME END----"
            )
            await self.send_victory_proper(self.name_2, "deck out")
            self.p1.already_lost_due_to_deck = True
        if self.p2.lost_due_to_deck and not self.p2.already_lost_due_to_deck:
            await self.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_1 + "; " + self.name_2 + " was unable to draw a card from their deck."
                                                                    "----GAME END----"
            )
            await self.send_victory_proper(self.name_1, "deck out")
            self.p2.already_lost_due_to_deck = True
        print("---\nDEBUG INFO\n---")
        print(self.interrupts_waiting_on_resolution)
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
        if self.choice_context == "Use Nullify?":
            if self.name_player_making_choices == self.name_1:
                if self.p1.castellan_crowe_relevant:
                    self.choice_context = "Use Psychic Ward?"
                    await self.send_update_message("Switched to offering Psychic Ward")
            elif self.name_player_making_choices == self.name_2:
                if self.p2.castellan_crowe_relevant:
                    self.choice_context = "Use Psychic Ward?"
                    await self.send_update_message("Switched to offering Psychic Ward")
        await self.send_search()
        await self.send_info_box()
        await self.send_decks()
        await self.p1.send_units_at_all_planets()
        await self.p1.send_hq()
        await self.p1.send_hand()
        await self.p1.send_discard()
        await self.p1.send_removed_cards()
        await self.p1.send_resources()
        await self.p2.send_units_at_all_planets()
        await self.p2.send_hq()
        await self.p2.send_hand()
        await self.p2.send_discard()
        await self.p2.send_removed_cards()
        await self.p2.send_resources()
        await self.send_planet_array()
        await self.send_initiative()
        await self.send_queued_sound()
        await self.send_queued_message()
        if not same_thread:
            await self.update_game_event("", [], same_thread=True)
        if not same_thread:
            self.condition_main_game.notify_all()
            self.condition_main_game.release()

    def get_name_interrupts_of_players_interrupts(self, name):
        interrupts_positions_list = []
        for i in range(len(self.interrupts_waiting_on_resolution)):
            if self.player_resolving_interrupts[i] == name:
                interrupts_positions_list.append(self.interrupts_waiting_on_resolution[i])
        return interrupts_positions_list

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

    def get_positions_of_players_interrupts(self, name):
        interrupts_positions_list = []
        for i in range(len(self.interrupts_waiting_on_resolution)):
            if self.player_resolving_interrupts[i] == name:
                interrupts_positions_list.append(i)
        return interrupts_positions_list

    def count_number_reactions_for_each_player(self):
        count_1 = 0
        count_2 = 0
        for i in range(len(self.reactions_needing_resolving)):
            if self.player_who_resolves_reaction[i] == self.name_1:
                count_1 += 1
            else:
                count_2 += 1
        return count_1, count_2

    def count_number_interrupts_for_each_player(self):
        count_1 = 0
        count_2 = 0
        for i in range(len(self.interrupts_waiting_on_resolution)):
            if self.player_resolving_interrupts[i] == self.name_1:
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

    def check_reactions_from_losing_combat(self, winner, loser, planet_id):
        reactions = []
        if self.reactions_on_winning_combat_permitted:
            for i in range(len(loser.attachments_at_planet[planet_id])):
                if loser.attachments_at_planet[planet_id][i].get_ability() == "Close Quarters Doctrine":
                    reactions.append("Close Quarters Doctrine")
            for i in range(len(loser.cards_in_reserve[planet_id])):
                if loser.cards_in_reserve[planet_id][i].get_ability() == "The Price of Success":
                    if loser.get_resources() >= loser.get_deepstrike_value_given_pos(planet_id, i):
                        if "The Price of Success" not in reactions:
                            reactions.append("The Price of Success")
            if loser.search_card_in_hq("Agra's Preachings", ready_relevant=True):
                reactions.append("Agra's Preachings")
            if loser.search_card_in_hq("Order of the Crimson Oath"):
                reactions.append("Order of the Crimson Oath")
            if loser.search_card_in_hq("Host of the Emissary", ready_relevant=True):
                reactions.append("Host of the Emissary")
            if loser.the_flayed_mask_planet == planet_id:
                reactions.append("The Flayed Mask Surprise")
            if loser.resources > 0 and self.round_number == planet_id:
                if loser.search_hand_for_card("The Grand Plan"):
                    reactions.append("The Grand Plan")
                elif "The Grand Plan" in loser.cards_removed_from_game:
                    warlord_pla, warlord_pos = loser.get_location_of_warlord()
                    vael_relevant = False
                    if loser.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                            loser.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    elif loser.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                            and not loser.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    if vael_relevant:
                        reactions.append("The Grand Plan")
        return reactions

    def check_reactions_from_winning_combat(self, winner, planet_id):
        reactions_exist = False
        if self.reactions_on_winning_combat_permitted:
            if self.round_number > 0:
                if winner.search_card_in_hq("WAAAGH! Ungskar"):
                    for i in range(len(winner.cards_in_reserve[planet_id])):
                        if winner.cards_in_reserve[planet_id][i].get_ability() == "Squiggoth Brute":
                            self.create_reaction("WAAAGH! Ungskar Deepstrike", winner.name_player,
                                                 (int(winner.number), -1, -1))
                            reactions_exist = True
            if winner.search_card_in_hq("Novokh Dynasty"):
                for i in range(len(winner.cards_in_reserve[planet_id])):
                    if winner.get_deepstrike_value_given_pos(planet_id, i, in_play_card=False) > 50:
                        self.create_reaction("Novokh Dynasty Deepstrike", winner.name_player,
                                             (int(winner.number), -1, -1))
                        reactions_exist = True
            if winner.search_card_in_hq("Reclamation Pool", ready_relevant=True):
                self.create_reaction("Reclamation Pool", winner.name_player,
                                     (int(winner.number), planet_id, -1))
                reactions_exist = True
            for i in range(len(winner.attachments_at_planet[planet_id])):
                if winner.attachments_at_planet[planet_id][i].get_ability() == "Close Quarters Doctrine":
                    self.create_reaction("Close Quarters Doctrine", winner.name_player, (int(winner.number), -1, -1))
                    reactions_exist = True
            for i in range(len(winner.cards_in_play[planet_id + 1])):
                if winner.get_ability_given_pos(planet_id, i) == "Kabalite Blackguard":
                    self.create_reaction("Kabalite Blackguard", winner.name_player, (int(winner.number), planet_id, i))
                    reactions_exist = True
                if winner.get_ability_given_pos(planet_id, i) == "Khornate Heldrake":
                    self.create_reaction("Khornate Heldrake", winner.name_player, (int(winner.number), planet_id, i))
                    reactions_exist = True
                if winner.get_ability_given_pos(planet_id, i) == "Sanguinary Guard":
                    self.create_reaction("Sanguinary Guard", winner.name_player, (int(winner.number), planet_id, i))
                    reactions_exist = True
                if winner.get_ability_given_pos(planet_id, i) == "Raiding Kabal":
                    self.create_reaction("Raiding Kabal", winner.name_player, (int(winner.number), planet_id, i))
                    reactions_exist = True
            if winner.search_card_in_hq("Clearing the Path"):
                if winner.check_for_warlord(planet_id, True, winner.name_player):
                    self.create_reaction("Clearing the Path", winner.name_player, (int(winner.number), -1, -1))
                    reactions_exist = True
            if winner.search_card_in_hq("Anvil Strike Force"):
                if planet_id == self.round_number:
                    if winner.check_for_warlord(planet_id, True, winner.name_player):
                        self.create_reaction("Anvil Strike Force", winner.name_player, (int(winner.number), -1, -1))
                        reactions_exist = True
            if self.get_blue_icon(planet_id):
                if winner.resources > 0:
                    if not winner.accept_any_challenge_used:
                        if winner.search_hand_for_card("Accept Any Challenge"):
                            self.create_reaction("Accept Any Challenge", winner.name_player,
                                                 (int(winner.number), -1, -1))
                            reactions_exist = True
                if winner.resources > 1:
                    if winner.search_hand_for_card("Declare the Crusade"):
                        self.create_reaction("Declare the Crusade", winner.name_player, (int(winner.number), -1, -1))
                        reactions_exist = True
            if self.get_green_icon(planet_id):
                if winner.resources > 0:
                    if winner.search_hand_for_card("Inspirational Fervor"):
                        self.create_reaction("Inspirational Fervor", winner.name_player, (int(winner.number), -1, -1))
                        reactions_exist = True
                if planet_id != self.round_number and not self.sacaellums_finest_active:
                    if winner.search_hand_for_card("Sacaellum's Finest"):
                        self.create_reaction("Sacaellum's Finest", winner.name_player, (int(winner.number), -1, -1))
                        reactions_exist = True
            if self.get_red_icon(planet_id):
                cost = 0
                if winner.urien_relevant:
                    cost += 1
                if winner.resources >= cost:
                    if not winner.gut_and_pillage_used:
                        if winner.search_hand_for_card("Gut and Pillage"):
                            self.create_reaction("Gut and Pillage", winner.name_player, (int(winner.number), -1, -1))
                            reactions_exist = True
                if winner.search_hand_for_card("Scavenging Run"):
                    if winner.get_resources() > 0:
                        if winner.search_trait_at_planet(planet_id, "Kroot"):
                            self.create_reaction("Scavenging Run", winner.name_player, (int(winner.number), -1, -1))
                            reactions_exist = True
            if winner.resources > 0 and planet_id == self.round_number:
                if winner.search_hand_for_card("The Grand Plan"):
                    self.create_reaction("The Grand Plan", winner.name_player, (int(winner.number), -1, -1))
                    reactions_exist = True
                elif "The Grand Plan" in winner.cards_removed_from_game:
                    warlord_pla, warlord_pos = winner.get_location_of_warlord()
                    vael_relevant = False
                    if winner.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted" and not \
                            winner.get_once_per_round_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    elif winner.get_ability_given_pos(warlord_pla, warlord_pos) == "Vael the Gifted BLOODIED" \
                            and not winner.get_once_per_game_used_given_pos(warlord_pla, warlord_pos):
                        vael_relevant = True
                    if vael_relevant:
                        self.create_reaction("The Grand Plan", winner.name_player, (int(winner.number), -1, -1))
                        reactions_exist = True
        return reactions_exist

    def infest_planet(self, planet, player_doing_infesting):
        if not self.infested_planets[planet]:
            self.infested_planets[planet] = True
            if self.p1.search_card_in_hq("Sacaellum Infestors", ready_relevant=True):
                self.create_reaction("Sacaellum Infestors", self.name_1, (1, planet, -1))
            if self.p2.search_card_in_hq("Sacaellum Infestors", ready_relevant=True):
                self.create_reaction("Sacaellum Infestors", self.name_2, (2, planet, -1))
            if player_doing_infesting.search_for_card_everywhere("Ardaci-strain Broodlord", limit_phase_rel=True):
                if not player_doing_infesting.check_if_already_have_reaction("Ardaci-strain Broodlord"):
                    self.create_reaction("Ardaci-strain Broodlord", player_doing_infesting.name_player,
                                         (int(player_doing_infesting.number), planet, -1))

    async def resolve_winning_combat(self, winner, loser):
        self.name_player_who_won_combat = winner.name_player
        planet_name = self.planet_array[self.last_planet_checked_for_battle]
        reactions_lose = self.check_reactions_from_losing_combat(winner, loser, self.last_planet_checked_for_battle)
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
            reactions_win = self.check_reactions_from_winning_combat(winner, self.last_planet_checked_for_battle)
            if reactions_win or reactions_lose:
                await self.send_update_message("Reactions on winning combat detected.")
                self.reactions_on_winning_combat_being_executed = True
                self.reactions_on_winning_combat_permitted = False
                for i in range(len(reactions_lose)):
                    self.create_reaction(reactions_lose[i], loser.name_player, (int(loser.number), -1, -1))
            else:
                self.already_asked_remove_infestation = False
                print("Resolve battle ability of:", planet_name)
                self.need_to_resolve_battle_ability = True
                self.reactions_on_winning_combat_being_executed = False
                self.reactions_on_winning_combat_permitted = True
                self.battle_ability_to_resolve = planet_name
                self.player_resolving_battle_ability = winner.name_player
                self.number_resolving_battle_ability = str(winner.number)
                self.choices_available = ["Yes", "No"]
                if self.sacaellums_finest_active:
                    self.choices_available = ["No", "No"]
                    self.sacaellums_finest_active = False
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
                        self.p1.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                        self.p2.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                        await winner.send_victory_display()

    async def check_stalemate(self, name):
        p1_has_units = self.p1.check_if_units_present(self.last_planet_checked_for_battle)
        p2_has_units = self.p2.check_if_units_present(self.last_planet_checked_for_battle)
        if p1_has_units or p2_has_units:
            pass
        else:
            if not p1_has_units and not p2_has_units:
                if self.round_number == self.last_planet_checked_for_battle:
                    self.p1.discard_planet_attachments(self.last_planet_checked_for_battle)
                    self.p2.discard_planet_attachments(self.last_planet_checked_for_battle)
                    self.planets_in_play_array[self.last_planet_checked_for_battle] = False
                    self.p1.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                    self.p2.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                await self.resolve_battle_conclusion(name, ["", ""])

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
                    self.p1.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                    self.p2.discard_all_cards_in_reserve(self.last_planet_checked_for_battle)
                await self.resolve_battle_conclusion(name, ["", ""])

    def create_delayed_reaction(self, reaction_name, player_name, unit_tuple, additional_info=None):
        if player_name == self.name_1:
            player = self.p1
        else:
            player = self.p2
        if not player.hit_by_gorgul:
            self.delayed_reactions_needing_resolving.append(reaction_name)
            self.delayed_player_who_resolves_reaction.append(player_name)
            self.delayed_positions_of_unit_triggering_reaction.append(unit_tuple)
            self.delayed_additional_reactions_info.append(additional_info)

    def create_reaction(self, reaction_name, player_name, unit_tuple, additional_info=None):
        if player_name == self.name_1:
            player = self.p1
        else:
            player = self.p2
        if not player.hit_by_gorgul:
            self.reactions_needing_resolving.append(reaction_name)
            self.player_who_resolves_reaction.append(player_name)
            self.positions_of_unit_triggering_reaction.append(unit_tuple)
            self.additional_reactions_info.append(additional_info)

    def begin_combat_round(self):
        self.bloodthirst_active = [False, False, False, False, False, False, False]
        self.p1.resolve_combat_round_begins(self.last_planet_checked_for_battle)
        self.p2.resolve_combat_round_begins(self.last_planet_checked_for_battle)

    def take_control_of_card(self, primary_player, secondary_player, planet_pos, unit_pos):
        if planet_pos == -2:
            primary_player.headquarters.append(secondary_player.headquarters[unit_pos])
            secondary_player.remove_card_from_hq(unit_pos)
            return None
        primary_player.cards_in_play[planet_pos + 1].append(secondary_player.cards_in_play[planet_pos + 1][unit_pos])
        secondary_player.remove_card_from_play(planet_pos, unit_pos)
        return None

    async def reset_values_for_new_round(self):
        self.imperial_blockades_active = [0, 0, 0, 0, 0, 0, 0]
        self.p1.has_passed = False
        self.p2.has_passed = False
        self.p1.bluddflagg_used = False
        self.p2.bluddflagg_used = False
        self.masters_of_the_webway = False
        self.p1.command_struggles_won_this_phase = 0
        self.p2.command_struggles_won_this_phase = 0
        self.p1.sac_altar_rewards = [0, 0, 0, 0, 0, 0, 0]
        self.p2.sac_altar_rewards = [0, 0, 0, 0, 0, 0, 0]
        self.p1.won_command_struggles_planets_round = [False, False, False, False, False, False, False]
        self.p2.won_command_struggles_planets_round = [False, False, False, False, False, False, False]
        if self.p1.planet_absorption_played:
            await self.game.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_2 + "; "
                + self.name_1 + " lost from Planet Absorption."
                                "----GAME END----"
            )
            await self.send_victory_proper(self.name_2, "Planet Absorption")
        if self.p2.planet_absorption_played:
            await self.game.send_update_message(
                "----GAME END----"
                "Victory for " + self.name_1 + "; "
                + self.name_2 + " lost from Planet Absorption."
                                "----GAME END----"
            )
            await self.send_victory_proper(self.name_1, "Planet Absorption")
        if self.p1.reinforced_synaptic_network_played:
            i = 0
            while i < len(self.p1.headquarters):
                if self.p1.headquarters[i].get_card_type() == "Synapse" and not self.p1.headquarters[i].from_deck:
                    self.p1.add_card_in_hq_to_discard(i)
                    i = i - 1
                i = i + 1
            self.p1.reinforced_synaptic_network_played = False
        if self.p2.reinforced_synaptic_network_played:
            i = 0
            while i < len(self.p2.headquarters):
                if self.p2.headquarters[i].get_card_type() == "Synapse" and not self.p2.headquarters[i].from_deck:
                    self.p2.add_card_in_hq_to_discard(i)
                    i = i - 1
                i = i + 1
            self.p2.reinforced_synaptic_network_played = False
        self.p1.permitted_commit_locs_warlord = [True, True, True, True, True, True, True]
        self.p2.permitted_commit_locs_warlord = [True, True, True, True, True, True, True]
        self.p1.illegal_commits_warlord = 0
        self.p1.illegal_commits_synapse = 0
        self.p2.illegal_commits_warlord = 0
        self.p2.illegal_commits_synapse = 0
        self.p1.primal_howl_used = False
        self.p2.primal_howl_used = False
        self.p1.fortress_world_garid_used = False
        self.p2.fortress_world_garid_used = False
        self.p1.tempting_ceasefire_used = False
        self.p2.tempting_ceasefire_used = False
        self.p1.etekh_trait = ""
        self.p2.etekh_trait = ""
        self.p1.gut_and_pillage_used = False
        self.p2.gut_and_pillage_used = False
        self.p1.used_reanimation_protocol = False
        self.p2.used_reanimation_protocol = False
        self.p1.accept_any_challenge_used = False
        self.p2.accept_any_challenge_used = False
        self.p1.unconquerable_fear_used = False
        self.p2.unconquerable_fear_used = False
        self.p1.death_serves_used = False
        self.p2.death_serves_used = False
        self.p1.counterblow_used = False
        self.p2.counterblow_used = False
        self.p1.everlasting_rage_used = False
        self.p2.everlasting_rage_used = False
        self.p1.optimized_landing_used = False
        self.p2.optimized_landing_used = False
        self.p1.our_last_stand_used = False
        self.p2.our_last_stand_used = False
        self.p1.our_last_stand_bonus_active = False
        self.p2.our_last_stand_bonus_active = False
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

    async def automated_headquarters_phase(self):
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
        self.p1.return_cards_to_hand_eor()
        self.p2.return_cards_to_hand_eor()
        self.p1.ready_all_planet_attach()
        self.p2.ready_all_planet_attach()
        self.p1.set_can_play_limited(True)
        self.p2.set_can_play_limited(True)
        self.p1.refresh_all_once_per_round()
        self.p2.refresh_all_once_per_round()
        if self.round_number == 0:
            self.planets_in_play_array[5] = True
            self.most_recently_revealed_planet = 5
            for i in range(len(self.p1.headquarters)):
                if self.p1.get_ability_given_pos(-2, i) == "War Cabal":
                    self.create_reaction("War Cabal", self.p1.name_player,
                                         (int(self.p1.number), -2, i))
            for i in range(7):
                for j in range(len(self.p1.cards_in_play[i + 1])):
                    if self.p1.get_ability_given_pos(i, j) == "War Cabal":
                        self.create_reaction("War Cabal", self.p1.name_player,
                                             (int(self.p1.number), i, j))
            for i in range(len(self.p2.headquarters)):
                if self.p2.get_ability_given_pos(-2, i) == "War Cabal":
                    self.create_reaction("War Cabal", self.p2.name_player,
                                         (int(self.p2.number), -2, i))
            for i in range(7):
                for j in range(len(self.p2.cards_in_play[i + 1])):
                    if self.p2.get_ability_given_pos(i, j) == "War Cabal":
                        self.create_reaction("War Cabal", self.p2.name_player,
                                             (int(self.p2.number), i, j))
        elif self.round_number == 1:
            self.planets_in_play_array[6] = True
            self.most_recently_revealed_planet = 6
            for i in range(len(self.p1.headquarters)):
                if self.p1.get_ability_given_pos(-2, i) == "War Cabal":
                    self.create_reaction("War Cabal", self.p1.name_player,
                                         (int(self.p1.number), -2, i))
            for i in range(7):
                for j in range(len(self.p1.cards_in_play[i + 1])):
                    if self.p1.get_ability_given_pos(i, j) == "War Cabal":
                        self.create_reaction("War Cabal", self.p1.name_player,
                                             (int(self.p1.number), i, j))
            for i in range(len(self.p2.headquarters)):
                if self.p2.get_ability_given_pos(-2, i) == "War Cabal":
                    self.create_reaction("War Cabal", self.p2.name_player,
                                         (int(self.p2.number), -2, i))
            for i in range(7):
                for j in range(len(self.p2.cards_in_play[i + 1])):
                    if self.p2.get_ability_given_pos(i, j) == "War Cabal":
                        self.create_reaction("War Cabal", self.p2.name_player,
                                             (int(self.p2.number), i, j))
        self.round_number += 1
        i = 0
        while i < len(self.grand_plan_queued):
            planet_name, target_round, num_getting_planet, p1_planned, p2_planned = self.grand_plan_queued[i]
            if target_round == self.round_number:
                planet_card = FindCard.find_planet_card(planet_name, self.planet_cards_array)
                if planet_card.get_name() != "FINAL CARD":
                    if num_getting_planet == 1:
                        self.p1.victory_display.append(planet_card)
                        await self.send_update_message("The Grand Plan bears fruit.")
                        await self.p1.send_victory_display()
                    else:
                        self.p2.victory_display.append(planet_card)
                        await self.send_update_message("The Gran Plan bears fruit.")
                        await self.p2.send_victory_display()
                    if p1_planned:
                        for _ in range(4):
                            self.p1.draw_card()
                    if p2_planned:
                        for _ in range(4):
                            self.p2.draw_card()
                del self.grand_plan_queued[i]
                i = i - 1
            i = i + 1
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
        self.battle_in_progress = True
        self.combat_round_number = 1
        self.last_planet_checked_for_battle = planet_pos
        self.p1.resolve_battle_begins(planet_pos)
        self.p2.resolve_battle_begins(planet_pos)
        if self.p1.check_for_cards_in_reserve(planet_pos) or self.p2.check_for_cards_in_reserve(planet_pos):
            self.start_battle_deepstrike = True
            if self.p1.check_for_cards_in_reserve(planet_pos):
                self.p1.has_passed = False
            else:
                self.p1.has_passed = True
            if self.p2.check_for_cards_in_reserve(planet_pos):
                self.p2.has_passed = False
            else:
                self.p2.has_passed = True
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Deepstrike cards?"
            self.resolving_search_box = True
            if self.p1.check_for_cards_in_reserve(planet_pos) and self.p2.check_for_cards_in_reserve(planet_pos):
                if self.player_with_initiative == self.name_1:
                    self.name_player_making_choices = self.name_1
                else:
                    self.name_player_making_choices = self.name_2
            elif self.p1.check_for_cards_in_reserve(planet_pos):
                self.name_player_making_choices = self.name_1
            else:
                self.name_player_making_choices = self.name_2

    def find_next_planet_for_combat(self):
        if self.jaricho_target != -1:
            i = self.jaricho_target
            self.jaricho_target = -1
            self.begin_battle(i)
            if not self.start_battle_deepstrike:
                self.begin_combat_round()
                self.start_ranged_skirmish(i)
            return True
        elif not self.bloodrain_tempest_active:
            i = self.last_planet_checked_for_battle + 1
            while i < len(self.planet_array):
                if self.planets_in_play_array[i]:
                    p1_has_warlord = self.p1.check_for_warlord(i)
                    p2_has_warlord = self.p2.check_for_warlord(i)
                    if not p1_has_warlord and not p2_has_warlord:
                        p1_has_warlord = self.p1.check_savage_warrior_prime_present(i)
                        p2_has_warlord = self.p2.check_savage_warrior_prime_present(i)
                    if not p1_has_warlord and not p2_has_warlord:
                        p1_has_warlord = self.p1.check_yvraine_battle(i)
                        p2_has_warlord = self.p2.check_yvraine_battle(i)
                    if p1_has_warlord or p2_has_warlord or i == self.round_number:
                        self.begin_battle(i)
                        if not self.start_battle_deepstrike:
                            self.begin_combat_round()
                            self.start_ranged_skirmish(i)
                        return True
                i = i + 1
        else:
            i = self.last_planet_checked_for_battle - 1
            while i > -1:
                if self.planets_in_play_array[i]:
                    p1_has_warlord = self.p1.check_for_warlord(i)
                    p2_has_warlord = self.p2.check_for_warlord(i)
                    if not p1_has_warlord and not p2_has_warlord:
                        p1_has_warlord = self.p1.check_savage_warrior_prime_present(i)
                        p2_has_warlord = self.p2.check_savage_warrior_prime_present(i)
                    if not p1_has_warlord and not p2_has_warlord:
                        p1_has_warlord = self.p1.check_yvraine_battle(i)
                        p2_has_warlord = self.p2.check_yvraine_battle(i)
                    if p1_has_warlord or p2_has_warlord or i == self.round_number:
                        self.begin_battle(i)
                        if not self.start_battle_deepstrike:
                            self.begin_combat_round()
                            self.start_ranged_skirmish(i)
                        return True
                i = i - 1
        return False

    def end_start_battle_deepstrike(self):
        self.start_battle_deepstrike = False
        self.begin_combat_round()

    def reset_combat_turn(self):
        self.player_with_combat_turn = self.player_reset_combat_turn
        self.number_with_combat_turn = self.number_reset_combat_turn

    def force_set_battle_initiative(self, name, number):
        self.player_with_combat_turn = name
        self.player_reset_combat_turn = name
        self.number_with_combat_turn = number
        self.number_reset_combat_turn = number

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
        if self.number_with_combat_turn == "1":
            self.p1.has_initiative_for_battle = True
            self.p2.has_initiative_for_battle = False
        else:
            self.p2.has_initiative_for_battle = True
            self.p1.has_initiative_for_battle = False

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
