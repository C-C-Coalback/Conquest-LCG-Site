from .. import FindCard


async def update_game_event_action_hq(self, name, game_update_string):
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    unit_pos = int(game_update_string[2])
    if not self.action_chosen:
        self.position_of_actioned_card = (-2, int(game_update_string[2]))
        if int(game_update_string[1]) == int(primary_player.get_number()):
            card = primary_player.headquarters[self.position_of_actioned_card[1]]
            ability = card.get_ability()
            if card.get_has_action_while_in_play():
                if card.get_allowed_phases_while_in_play() == self.phase or \
                        card.get_allowed_phases_while_in_play() == "ALL":
                    print("trying to resolve combat special")
                    if card.get_ability() == "Catachan Outpost":
                        if card.get_ready():
                            self.action_chosen = "Catachan Outpost"
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Hunter Gargoyles":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                    elif ability == "Awakening Cavern":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Mekaniak Repair Krew":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(-2, uni)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                    elif ability == "Slumbering Tomb":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            primary_player.draw_card()
                            primary_player.draw_card()
                            self.misc_counter = 0
                    elif ability == "Mycetic Spores":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.unit_to_move_position = [-1, -1]
                    elif ability == "Twisted Laboratory":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Ork Kannon":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Smasha Gun Battery":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.action_cleanup()
                            self.location_of_indirect = "ALL"
                            self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
                            secondary_player.indirect_damage_applied = 0
                            secondary_player.total_indirect_damage = len(secondary_player.cards)
                            primary_player.indirect_damage_applied = 0
                            primary_player.total_indirect_damage = len(primary_player.cards)
                    elif ability == "Ambush Platform":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Corrupted Teleportarium":
                        if card.get_ready():
                            self.action_chosen = ability
                            self.first_card_chosen = False
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Anrakyr the Traveller":
                        if not card.get_once_per_phase_used():
                            self.action_chosen = ability
                            self.choices_available = ["Own Discard", "Enemy Discard"]
                            self.choice_context = "Anrakyr: Select which discard:"
                            self.name_player_making_choices = primary_player.name_player
                            self.anrakyr_unit_position = -1
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            card.set_once_per_phase_used(True)
                    elif ability == "Autarch Celachia":
                        if not card.once_per_round_used:
                            if primary_player.spend_resources(1):
                                self.choices_available = ["Area Effect (1)", "Armorbane", "Mobile"]
                                self.choice_context = "Autarch Celachia"
                                if self.phase == "DEPLOY":
                                    self.player_with_deploy_turn = secondary_player.name_player
                                    self.number_with_deploy_turn = secondary_player.number
                                self.name_player_making_choices = primary_player.name_player
                    elif ability == "Brood Chamber":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.misc_target_planet = -1
                            self.chosen_first_card = False
                    elif ability == "Vile Laboratory":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.misc_target_planet = -1
                            self.misc_target_unit = (-1, -1)
                            self.chosen_first_card = False
                            self.chosen_second_card = False
                    elif ability == "Eternity Gate":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Ruined Passages":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            primary_player.sacrifice_card_in_hq(unit_pos)
                            self.action_chosen = ability
                    elif ability == "Particle Whip":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.misc_counter = 0
                    elif ability == "Ork Landa":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            if primary_player.discard_top_card_deck():
                                card = primary_player.get_card_top_discard()
                                if card.get_faction() == "Orks" and card.get_cost() % 2 == 1:
                                    await self.send_update_message(
                                        "Ork Landa hit an odd Orks card!"
                                    )
                                    self.location_of_indirect = "ALL"
                                    self.valid_targets_for_indirect = ["Army", "Synapse", "Token", "Warlord"]
                                    secondary_player.indirect_damage_applied = 0
                                    secondary_player.total_indirect_damage = card.get_cost()
                                else:
                                    await self.send_update_message(
                                        "Ork Landa missed"
                                    )
                            self.action_cleanup()
                    elif ability == "Throne of Vainglory":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            if primary_player.discard_top_card_deck():
                                card = primary_player.get_card_top_discard()
                                if card.get_cost() > 2:
                                    primary_player.summon_token_at_hq("Cultist", 2)
                                self.action_cleanup()
                    elif ability == "Ba'ar Zul's Cleavers":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            primary_player.increase_attack_of_unit_at_pos(-2, unit_pos, 2, "NEXT")
                            primary_player.assign_damage_to_pos(-2, unit_pos, 2)
                            self.action_cleanup()
                    elif ability == "Wisdom of the Serpent":
                        if card.get_ready():
                            card.exhaust_card()
                            self.choices_available = ["Warrior", "Psyker"]
                            self.choice_context = "Wisdom of the Serpent trait"
                            self.resolving_search_box = True
                            self.name_player_making_choices = primary_player.name_player
                    elif ability == "Kaerux Erameas":
                        if card.get_ready():
                            if self.last_planet_checked_for_battle == -1:
                                primary_player.exhaust_given_pos(-2, unit_pos)
                                self.action_chosen = "Kaerux Erameas"
                    elif ability == "Chaplain Mavros":
                        if primary_player.headquarters[unit_pos].once_per_phase_used is False:
                            primary_player.headquarters[unit_pos].once_per_phase_used = 1
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                            self.position_of_actioned_card = (-2, unit_pos)
                        elif primary_player.headquarters[unit_pos].once_per_phase_used < 2:
                            primary_player.headquarters[unit_pos].once_per_phase_used += 1
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                            self.position_of_actioned_card = (-2, unit_pos)
                    elif ability == "Troop Transport":
                        self.action_chosen = ability
                        primary_player.sacrifice_card_in_hq(unit_pos)
                    elif ability == "The Nexus of Shadows":
                        if not card.get_once_per_phase_used():
                            if primary_player.spend_resources(2):
                                card.set_once_per_phase_used(True)
                                primary_player.draw_card()
                                self.action_cleanup()
                    elif ability == "Immortal Legion":
                        planet_pos = -2
                        unit_pos = int(game_update_string[2])
                        if card.get_ready():
                            if secondary_player.warlord_faction == primary_player.enslaved_faction:
                                target_planet = secondary_player.get_planet_of_warlord()
                                if target_planet != -2 and target_planet != -1:
                                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                    primary_player.move_unit_to_planet(planet_pos, unit_pos, target_planet)
                                    self.action_cleanup()
                    elif ability == "Lone Wolf":
                        planet_pos = -2
                        unit_pos = int(game_update_string[2])
                        if card.get_ready():
                            target_planet = secondary_player.get_planet_of_warlord()
                            if target_planet != -2 and target_planet != -1:
                                if not primary_player.cards_in_play[target_planet + 1]:
                                    primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                    primary_player.move_unit_to_planet(planet_pos, unit_pos, target_planet)
                                    self.action_cleanup()
                    elif ability == "Pathfinder Shi Or'es":
                        if not card.get_once_per_phase_used():
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            self.position_of_actioned_card = (-2, int(game_update_string[2]))
                            card_chosen.set_once_per_phase_used(True)
                    elif ability == "Hallow Librarium":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.action_chosen = ability
                    elif ability == "Urien's Oubliette":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.action_chosen = ability
                            self.position_of_actioned_card = (-2, int(game_update_string[2]))
                            self.choices_available = ["Discard", "Draw"]
                            self.choice_context = "Urien's Oubliette"
                            self.name_player_making_choices = primary_player.name_player
                    elif ability == "Twisted Wracks":
                        self.action_chosen = ability
                        player_owning_card.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                        self.position_of_actioned_card = (-2, unit_pos)
                    elif ability == "Ammo Depot":
                        if card.get_ready():
                            if len(primary_player.cards) < 4:
                                primary_player.exhaust_given_pos(-2, unit_pos)
                                primary_player.draw_card()
                                self.action_cleanup()
                    elif ability == "Staging Ground":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.action_chosen = ability
                            self.chosen_first_card = False
                    elif ability == "The Glovodan Eagle":
                        primary_player.return_card_to_hand(-2, unit_pos)
                        self.action_cleanup()
                    elif ability == "Repair Bay":
                        if card.get_ready():
                            card.exhaust_card()
                            self.choices_available = []
                            self.choice_context = "Repair Bay"
                            self.name_player_making_choices = primary_player.name_player
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict)
                                if card.check_for_a_trait("Drone") or card.check_for_a_trait("Pilot"):
                                    if card.get_name() not in self.choices_available:
                                        self.choices_available.append(card.get_name())
                            if not self.choices_available:
                                await self.send_update_message(
                                    "No valid target for Repair Bay."
                                )
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                            self.action_cleanup()
                    elif ability == "Starblaze's Outpost":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.misc_target_planet = -1
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.misc_counter = -1
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                    elif ability == "Kraktoof Hall":
                        if card.get_ready():
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.chosen_second_card = False
                            self.misc_target_planet = -1
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Killing Field":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
                    elif ability == "Cathedral of Saint Camila":
                        if card.get_ready():
                            if not card.get_once_per_phase_used():
                                card.set_once_per_phase_used(True)
                                self.action_chosen = ability
                                primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                                self.misc_counter = [False, False, False, False, False, False, False]
                                for i in range(7):
                                    if self.get_green_icon(i):
                                        self.misc_counter[i] = True
                    elif ability == "Vaulting Harlequin":
                        if primary_player.get_ready_given_pos(-2, int(game_update_string[2])):
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            primary_player.headquarters[int(game_update_string[2])].flying_eop = True
                            self.action_cleanup()
                    elif ability == "Ksi'm'yen Orbital City":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.chosen_first_card = False
                            self.misc_target_unit = (-1, -1)
                            self.action_chosen = ability
                    elif ability == "Inquisitorial Fortress":
                        if card.get_ready():
                            if primary_player.sacrifice_card_in_hq(int(game_update_string[2])):
                                self.action_chosen = ability
                    elif ability == "Aun'shi's Sanctum":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Master Program":
                        if card.get_ready():
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.misc_target_planet = -1
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Death Korps Engineers":
                        self.action_chosen = ability
                        player_owning_card.sacrifice_card_in_play(-2, unit_pos)
                    elif ability == "Teleportarium":
                        if card.get_ready():
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.misc_target_unit = (-1, -1)
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Craftworld Gate":
                        if card.get_ready():
                            self.action_chosen = "Craftworld Gate"
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Khymera Den":
                        if card.get_ready():
                            self.action_chosen = "Khymera Den"
                            self.khymera_to_move_positions = []
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Ravenous Flesh Hounds":
                        self.action_chosen = ability
                        primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                    elif ability == "Ancient Keeper of Secrets":
                        self.action_chosen = ability
                        primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                    elif card.get_ability() == "Tellyporta Pad":
                        if card.get_ready():
                            if self.planets_in_play_array[self.round_number]:
                                self.action_chosen = "Tellyporta Pad"
                                primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                                primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            else:
                                await self.send_update_message("First planet not in play")
    elif self.action_chosen == "Pact of the Haemonculi":
        if game_update_string[1] == self.number_with_deploy_turn:
            if self.number_with_deploy_turn == "1":
                primary_player = self.p1
                secondary_player = self.p2
            else:
                primary_player = self.p2
                secondary_player = self.p1
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
                await primary_player.dark_eldar_event_played()
    elif self.action_chosen == "Particle Whip":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
            if possible_interrupts:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = self.amount_spend_for_tzeentch_firestorm
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
        if can_continue:
            if player_being_hit.headquarters[unit_pos].get_card_type() == "Army":
                if player_being_hit.headquarters[unit_pos].check_for_a_trait("Elite"):
                    player_being_hit.assign_damage_to_pos(-2, unit_pos, self.misc_counter)
                    player_being_hit.set_aiming_reticle_in_play(-2, unit_pos, "red")
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.misc_counter = 0
                    self.action_cleanup()
    elif self.action_chosen == "Despise":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.headquarters[unit_pos].check_for_a_trait("Ally"):
                if primary_player.sacrifice_card_in_hq(unit_pos):
                    self.player_with_action = secondary_player.name_player
                    primary_player.sacced_card_for_despise = True
                    if primary_player.sacced_card_for_despise and secondary_player.sacced_card_for_despise:
                        self.action_cleanup()
                        await secondary_player.dark_eldar_event_played()
    elif self.action_chosen == "Fetid Haze":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.headquarters[unit_pos].get_is_unit():
                if primary_player.headquarters[unit_pos].check_for_a_trait("Nurgle"):
                    damage = primary_player.get_damage_given_pos(-2, unit_pos)
                    primary_player.remove_damage_from_pos(-2, unit_pos, 999)
                    self.action_cleanup()
    elif self.action_chosen == "Know No Fear":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
                    if primary_player.get_faction_given_pos(-2, unit_pos) == "Space Marines":
                        self.chosen_first_card = True
                        self.position_of_actioned_card = (-2, unit_pos)
                        primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
    elif self.action_chosen == "To Arms!":
        if game_update_string[1] == "1":
            target_player = self.p1
        else:
            target_player = self.p2
        if target_player.get_card_type_given_pos(-2, unit_pos) == "Support":
            if not target_player.get_ready_given_pos(-2, unit_pos):
                target_player.ready_given_pos(-2, unit_pos)
                self.action_cleanup()
    elif self.action_chosen == "Doombolt":
        if game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
                can_continue = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    damage = secondary_player.get_damage_given_pos(-2, unit_pos)
                    secondary_player.assign_damage_to_pos(-2, unit_pos, damage)
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.action_cleanup()
    elif self.action_chosen == "Tzeentch's Firestorm":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
            if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
            elif possible_interrupts:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = self.amount_spend_for_tzeentch_firestorm
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
        if can_continue:
            if player_being_hit.headquarters[unit_pos].get_card_type() != "Warlord":
                player_being_hit.assign_damage_to_pos(-2, unit_pos, self.amount_spend_for_tzeentch_firestorm)
                player_being_hit.set_aiming_reticle_in_play(-2, unit_pos, "red")
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.amount_spend_for_tzeentch_firestorm = -1
                self.action_cleanup()
    elif self.action_chosen == "Hate":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = False
        if primary_player.resources >= player_being_hit.get_cost_given_pos(-2, unit_pos) and \
                primary_player.enslaved_faction == player_being_hit.get_faction_given_pos(-2, unit_pos):
            can_continue = True
            if player_being_hit.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
                if possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Action"
        if can_continue:
            primary_player.spend_resources(player_being_hit.get_cost_given_pos(-2, unit_pos))
            player_being_hit.destroy_card_in_hq(unit_pos)
            if not primary_player.harbinger_of_eternity_active:
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.get_number()
    elif self.action_chosen == "Twisted Laboratory":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
            if possible_interrupts:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "In Play Action"
        if can_continue:
            if player_being_hit.headquarters[unit_pos].get_card_type() == "Army":
                player_being_hit.set_blanked_given_pos(-2, unit_pos, exp="EOP")
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                await self.send_update_message(
                    "Twisted Laboratory used on " + player_being_hit.headquarters[unit_pos].get_name()
                    + ", located at HQ, position " + str(unit_pos))
                self.position_of_actioned_card = (-1, -1)
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                if self.phase == "DEPLOY":
                    if not secondary_player.has_passed:
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.get_number()
    elif self.action_chosen == "Squiggify":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if not player_being_hit.headquarters[unit_pos].check_for_a_trait("Vehicle") and \
                player_being_hit.get_card_type_given_pos(-2, unit_pos) == "Army":
            if player_being_hit.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
            if can_continue:
                player_being_hit.headquarters[unit_pos].extra_traits_eop += "Squig"
                player_being_hit.set_blanked_given_pos(-2, unit_pos)
                player_being_hit.headquarters[unit_pos].attack_set_eop = 1
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                name_card = player_being_hit.get_name_given_pos(-2, unit_pos)
                await self.send_update_message(
                    name_card + " got Squiggified!"
                )
                self.action_cleanup()
    elif self.action_chosen == "Cenobyte Servitor":
        if self.chosen_first_card:
            card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
            player_getting_attachment = self.p1
            if game_update_string[1] == "2":
                player_getting_attachment = self.p2
            not_own_attachment = False
            if player_getting_attachment.number != primary_player.number:
                not_own_attachment = True
            if player_getting_attachment.attach_card(card, -2, unit_pos, not_own_attachment=not_own_attachment):
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Calculated Strike":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        can_continue = True
        if player_being_hit.name_player == secondary_player.name_player:
            is_support = False
            if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                is_support = True
            possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos,
                                                                                 targeting_support=is_support)
            if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
            elif possible_interrupts:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 0
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
        if can_continue:
            if player_being_hit.headquarters[unit_pos].get_limited():
                player_being_hit.destroy_card_in_hq(unit_pos)
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Master Program":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if not self.chosen_first_card:
                if primary_player.headquarters[unit_pos].check_for_a_trait("Drone"):
                    if primary_player.sacrifice_card_in_hq(unit_pos):
                        self.chosen_first_card = True
            else:
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999)
                        self.action_cleanup()
    elif self.action_chosen == "Command-Link Drone":
        planet_pos = -2
        unit_pos = int(game_update_string[2])
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.headquarters[unit_pos].get_is_unit():
                planet, position, attachment_position = self.position_of_selected_attachment
                og_player = self.misc_target_player
                if og_player == primary_player.name_player:
                    if primary_player.move_attachment_card(planet, position, attachment_position, planet_pos, unit_pos):
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
                else:
                    card = secondary_player.get_attachment_at_pos(planet, position, attachment_position)
                    if primary_player.attach_card(card, planet_pos, unit_pos):
                        secondary_player.remove_attachment_from_pos(planet, position, attachment_position)
                        secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                      self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
        else:
            if secondary_player.headquarters[unit_pos].get_is_unit():
                planet, position, attachment_position = self.position_of_selected_attachment
                og_player = self.misc_target_player
                if og_player == secondary_player.name_player:
                    card = secondary_player.get_attachment_at_pos(planet, position, attachment_position)
                    if secondary_player.attach_card(card, planet_pos, unit_pos, not_own_attachment=True):
                        secondary_player.remove_attachment_from_pos(planet, position, attachment_position)
                        secondary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                      self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
                else:
                    card = primary_player.get_attachment_at_pos(planet, position, attachment_position)
                    if secondary_player.attach_card(card, planet_pos, unit_pos, not_own_attachment=True):
                        primary_player.remove_attachment_from_pos(planet, position, attachment_position)
                        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                    self.position_of_actioned_card[1])
                        self.position_of_selected_attachment = (-1, -1, -1)
                        self.position_of_actioned_card = (-1, -1)
                        self.action_cleanup()
    elif self.action_chosen == "Mekaniak Repair Krew":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                if primary_player.get_faction_given_pos(-2, unit_pos) == "Orks":
                    primary_player.ready_given_pos(-2, unit_pos)
                    primary_player.assign_damage_to_pos(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1], 1)
                    primary_player.set_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                              self.position_of_actioned_card[1], "red")
                    self.action_cleanup()
    elif self.action_chosen == "Subdual":
        if game_update_string[1] == "1":
            target_player = self.p1
        else:
            target_player = self.p2
        planet_pos = -2
        unit_pos = int(game_update_string[2])
        if target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
            can_continue = True
            if target_player.name_player == secondary_player.name_player:
                is_support = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos,
                                                                                     targeting_support=is_support)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
            if can_continue:
                target_player.deck.insert(0, target_player.get_name_given_pos(planet_pos, unit_pos))
                target_player.remove_card_from_hq(unit_pos)
                self.action_cleanup()
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Awakening Cavern":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_is_unit():
                primary_player.ready_given_pos(planet_pos, unit_pos)
                if self.phase == "DEPLOY":
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
                self.action_chosen = ""
                self.mode = "Normal"
                self.player_with_action = ""
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Dark Cunning":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_is_unit() and \
                    primary_player.headquarters[unit_pos].get_card_type() != "Warlord":
                primary_player.ready_given_pos(planet_pos, unit_pos)
                self.action_chosen = ""
                self.mode = "Normal"
                self.player_with_action = ""
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Ksi'm'yen Orbital City":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.headquarters[unit_pos].get_is_unit():
                    if primary_player.headquarters[unit_pos].check_for_a_trait("Ethereal"):
                        self.misc_target_unit = (-2, unit_pos)
                        self.chosen_first_card = True
                        primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
    elif self.action_chosen == "Clogged with Corpses":
        planet_pos = -2
        unit_pos = int(game_update_string[2])
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.get_name_given_pos(planet_pos, unit_pos) == "Termagant":
                primary_player.sacrifice_card_in_hq(unit_pos)
                self.misc_counter += 1
            elif primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                if primary_player.get_cost_given_pos(planet_pos, unit_pos) <= self.misc_counter:
                    primary_player.destroy_card_in_hq(unit_pos)
                    self.action_chosen = ""
                    self.mode = "Normal"
                    self.player_with_action = ""
                    if self.phase == "DEPLOY":
                        if not secondary_player.has_passed:
                            self.player_with_deploy_turn = secondary_player.name_player
                            self.number_with_deploy_turn = secondary_player.number
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.misc_counter = 0
        else:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                if secondary_player.get_cost_given_pos(planet_pos, unit_pos) <= self.misc_counter:
                    can_continue = True
                    is_support = True
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        -2, unit_pos, targeting_support=is_support)
                    if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                        can_continue = False
                        await self.send_update_message("Immune to enemy events.")
                    elif possible_interrupts:
                        can_continue = False
                        await self.send_update_message("Some sort of interrupt may be used.")
                        self.choices_available = possible_interrupts
                        self.choices_available.insert(0, "No Interrupt")
                        self.name_player_making_choices = secondary_player.name_player
                        self.choice_context = "Interrupt Effect?"
                        self.nullified_card_name = self.action_chosen
                        self.cost_card_nullified = 0
                        self.nullify_string = "/".join(game_update_string)
                        self.first_player_nullified = primary_player.name_player
                        self.nullify_context = "Event Action"
                    if can_continue:
                        secondary_player.destroy_card_in_hq(unit_pos)
                        self.action_cleanup()
                        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                        primary_player.aiming_reticle_coords_hand = None
                        self.misc_counter = 0
    elif self.action_chosen == "Ferocious Strength":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_card_type() == "Synapse" or \
                    primary_player.headquarters[unit_pos].get_card_type() == "Warlord":
                primary_player.headquarters[unit_pos].brutal_eocr = True
                card_name = primary_player.headquarters[unit_pos].get_name()
                await self.send_update_message("Made " + card_name + " Brutal for one combat round.")
                self.action_chosen = ""
                self.mode = "Normal"
                self.player_with_action = ""
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
    elif self.action_chosen == "Death Korps Engineers":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.get_card_type_given_pos(-2, unit_pos) == "Support":
            if not player_being_hit.get_ready_given_pos(-2, unit_pos):
                can_continue = True
                is_support = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=is_support)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
                if can_continue:
                    player_being_hit.destroy_card_in_hq(unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Craftworld Gate":
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_is_unit():
                primary_player.return_card_to_hand(planet_pos, unit_pos)
                self.action_chosen = ""
                self.mode = "Normal"
                self.player_with_action = ""
                if self.phase == "DEPLOY":
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Reanimation Protocol":
        if primary_player.get_number() == game_update_string[1]:
            unit_pos = int(game_update_string[2])
            if primary_player.get_faction_given_pos(-2, unit_pos) == "Necrons" and \
                    primary_player.headquarters[unit_pos].get_is_unit():
                primary_player.remove_damage_from_pos(-2, unit_pos, 2)
                if not primary_player.harbinger_of_eternity_active:
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Ethereal Wisdom":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.headquarters[unit_pos].get_is_unit():
                if primary_player.get_faction_given_pos(-2, unit_pos) == "Tau":
                    primary_player.headquarters[unit_pos].extra_traits_eop += "Ethereal"
                    primary_player.headquarters[unit_pos].extra_attack_until_end_of_phase += 1
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.action_cleanup()
    elif self.action_chosen == "Kauyon Strike":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].check_for_a_trait("Ethereal"):
                self.khymera_to_move_positions.append((planet_pos, unit_pos))
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                self.chosen_first_card = True
    elif self.action_chosen == "Khymera Den":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if primary_player.get_number() == game_update_string[1]:
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].get_name() == "Khymera":
                self.khymera_to_move_positions.append((planet_pos, unit_pos))
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Ravenous Flesh Hounds":
        if primary_player.get_number() == game_update_string[1]:
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].check_for_a_trait("Cultist"):
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                primary_player.remove_damage_from_pos(self.position_of_actioned_card[0],
                                                      self.position_of_actioned_card[1], 999)
                primary_player.sacrifice_card_in_hq(unit_pos)
                self.action_cleanup()
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Ancient Keeper of Secrets":
        if primary_player.get_number() == game_update_string[1]:
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].check_for_a_trait("Cultist"):
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                primary_player.ready_given_pos(self.position_of_actioned_card[0],
                                               self.position_of_actioned_card[1])
                primary_player.sacrifice_card_in_hq(unit_pos)
                self.action_cleanup()
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Squadron Redeployment":
        if self.unit_to_move_position == [-1, -1]:
            if self.player_with_action == self.name_1:
                primary_player = self.p1
            else:
                primary_player = self.p2
            if game_update_string[1] == primary_player.get_number():
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if primary_player.headquarters[unit_pos].get_attachments():
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.unit_to_move_position = [planet_pos, unit_pos]
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
        else:
            await self.send_update_message("Already selected unit to move")
    elif self.action_chosen == "Mycetic Spores":
        if self.unit_to_move_position == [-1, -1]:
            if self.player_with_action == self.name_1:
                primary_player = self.p1
            else:
                primary_player = self.p2
            if game_update_string[1] == primary_player.get_number():
                planet_pos = -2
                unit_pos = int(game_update_string[2])
                if primary_player.headquarters[unit_pos].has_hive_mind:
                    self.unit_to_move_position = [planet_pos, unit_pos]
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Deception":
        if self.number_with_deploy_turn == "1":
            primary_player = self.p1
            secondary_player = self.p2
        else:
            primary_player = self.p2
            secondary_player = self.p1
        if game_update_string[1] == "1":
            player_returning = self.p1
        else:
            player_returning = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if player_returning.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos)
            if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy events.")
            elif possible_interrupts:
                can_continue = False
                await self.send_update_message("Some sort of interrupt may be used.")
                self.choices_available = possible_interrupts
                self.choices_available.insert(0, "No Interrupt")
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Interrupt Effect?"
                self.nullified_card_name = self.action_chosen
                self.cost_card_nullified = 2
                self.nullify_string = "/".join(game_update_string)
                self.first_player_nullified = primary_player.name_player
                self.nullify_context = "Event Action"
        if can_continue:
            card = player_returning.headquarters[unit_pos]
            if card.get_card_type() == "Army":
                if not card.check_for_a_trait("Elite"):
                    player_returning.return_card_to_hand(-2, unit_pos)
                    primary_player.aiming_reticle_color = None
                    primary_player.aiming_reticle_coords_hand = None
                    self.card_pos_to_deploy = -1
                    self.player_with_action = ""
                    self.action_chosen = ""
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.number
                    self.mode = self.stored_mode
    elif self.action_chosen == "Catachan Outpost":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if int(game_update_string[1] == "1"):
            player_receiving_buff = self.p1
        else:
            player_receiving_buff = self.p2
        if player_receiving_buff.check_is_unit_at_pos(-2, int(game_update_string[2])):
            player_receiving_buff.increase_attack_of_unit_at_pos(-2, int(game_update_string[2]), 2,
                                                                 expiration="NEXT")
            await self.send_update_message(
                "Catachan Outpost used on " + player_receiving_buff.headquarters[int(game_update_string[2])]
                .get_name() + ", located at HQ, position " + game_update_string[2])
            primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                        self.position_of_actioned_card[1])
            self.position_of_actioned_card = (-1, -1)
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
    elif self.action_chosen == "Squig Bombin'":
        if game_update_string[1] == "1":
            player_destroying_support = self.p1
        else:
            player_destroying_support = self.p2
        if player_destroying_support.headquarters[unit_pos].get_card_type() == "Support":
            can_continue = True
            is_support = True
            if player_destroying_support.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=is_support)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
                elif possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = self.action_chosen
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "Event Action"
            if can_continue:
                player_destroying_support.destroy_card_in_hq(unit_pos)
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Ambush Platform":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if game_update_string[1] == "1":
            player_receiving_attachment = self.p1
        else:
            player_receiving_attachment = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is not None:
            hand_pos = primary_player.aiming_reticle_coords_hand_2
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array, self.cards_dict)
            army_unit_as_attachment = False
            discounts = primary_player.search_hq_for_discounts("", "", is_attachment=True)
            if card.get_ability() == "Gun Drones" or \
                    card.get_ability() == "Shadowsun's Stealth Cadre":
                army_unit_as_attachment = True
            if primary_player.get_number() == player_receiving_attachment.get_number():
                print("Playing own card")
                played_card = primary_player. \
                    play_attachment_card_to_in_play(card, planet_pos, unit_pos,
                                                    army_unit_as_attachment=
                                                    army_unit_as_attachment,
                                                    discounts=discounts)
                enemy_card = False
            else:
                played_card = False
                if primary_player.spend_resources(int(card.get_cost()) - discounts):
                    played_card = player_receiving_attachment.play_attachment_card_to_in_play(
                        card, planet_pos, unit_pos, not_own_attachment=True,
                        army_unit_as_attachment=army_unit_as_attachment)
                    if not played_card:
                        primary_player.add_resources(int(card.get_cost()) - discounts, refund=True)
                enemy_card = True
            if played_card:
                if card.get_limited():
                    primary_player.can_play_limited = False
                primary_player.remove_card_from_hand(hand_pos)
                print("Succeeded (?) in playing attachment")
                primary_player.aiming_reticle_coords_hand_2 = None
                self.action_chosen = ""
                self.player_with_action = ""
                self.mode = "Normal"
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Tellyporta Pad":
        if self.player_with_action == self.name_1:
            primary_player = self.p1
        else:
            primary_player = self.p2
        if game_update_string[1] == primary_player.get_number():
            card = primary_player.headquarters[int(game_update_string[2])]
            if card.get_faction() == "Orks":
                if card.get_is_unit():
                    primary_player.move_unit_to_planet(-2, int(game_update_string[2]),
                                                       self.round_number)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.position_of_actioned_card = (-1, -1)
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
