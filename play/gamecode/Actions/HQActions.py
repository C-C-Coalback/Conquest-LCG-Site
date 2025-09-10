from .. import FindCard
from .. import CardClasses
import copy


async def update_game_event_action_hq(self, name, game_update_string):
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if game_update_string[1] == "1":
        player_owning_card = self.p1
    else:
        player_owning_card = self.p2
    planet_pos = -2
    unit_pos = int(game_update_string[2])
    if not self.action_chosen:
        self.position_of_actioned_card = (-2, int(game_update_string[2]))
        if int(game_update_string[1]) != int(primary_player.get_number()):
            card = secondary_player.headquarters[self.position_of_actioned_card[1]]
            if card.get_ability() == "World Engine Beam" and not card.world_engine_enemy:
                card.world_engine_enemy = True
                self.action_chosen = "World Engine Beam"
                self.choices_available = ["Increase", "Decrease"]
                self.name_player_making_choices = primary_player.name_player
                self.choice_context = "Increase or Decrease (WEB)?"
                self.misc_target_player = secondary_player.name_player
                self.resolving_search_box = True
        if game_update_string[1] == primary_player.get_number():
            card = primary_player.headquarters[self.position_of_actioned_card[1]]
            card_chosen = card
            ability = card.get_ability()
            if card.get_has_action_while_in_play():
                if card.get_allowed_phases_while_in_play() == self.phase or \
                        card.get_allowed_phases_while_in_play() == "ALL":
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
                    elif ability == "World Engine Beam" and not card.world_engine_owner:
                        card.world_engine_owner = True
                        self.action_chosen = "World Engine Beam"
                        self.choices_available = ["Increase", "Decrease"]
                        self.name_player_making_choices = primary_player.name_player
                        self.choice_context = "Increase or Decrease (WEB)?"
                        self.misc_target_player = primary_player.name_player
                        self.resolving_search_box = True
                    elif ability == "Awakening Cavern":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Mekaniak Repair Krew":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
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
                    elif ability == "Holy Crusade":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.misc_counter = 2
                    elif ability == "Canoness Vardina":
                        if not card_chosen.bloodied:
                            if not card_chosen.get_once_per_round_used():
                                card_chosen.set_once_per_round_used(True)
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.misc_counter = 2
                                await self.send_update_message("Place " + str(self.misc_counter) + " faith tokens.")
                    elif ability == "Followers of Asuryan":
                        if not card.get_once_per_phase_used():
                            if card.counter > 3:
                                card_chosen.set_once_per_phase_used(True)
                                primary_player.followers_of_asuryan_relevant = True
                                await self.send_update_message("Followers of Asuryan activated!")
                    elif ability == "Munitorum Support":
                        if not card.get_once_per_round_used():
                            if card.attachments:
                                card.set_once_per_round_used(True)
                                self.choices_available = []
                                for i in range(len(card.attachments)):
                                    self.choices_available.append(card.attachments[i].get_name())
                                self.choice_context = "Munitorum Support Take"
                                self.name_player_making_choices = primary_player.name_player
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.resolving_search_box = True
                    elif ability == "Mycetic Spores":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.unit_to_move_position = [-1, -1]
                    elif ability == "Big Mek Kagdrak":
                        if not card.get_once_per_round_used():
                            card.set_once_per_round_used(True)
                            await self.send_update_message("Choose target for Big Mek Kagrak.")
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Evangelizing Ships":
                        if not card_chosen.get_once_per_phase_used():
                            card_chosen.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.chosen_first_card = False
                            await self.send_update_message("Please pay 1 faith")
                    elif ability == "Twisted Laboratory":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Holy Chapel":
                        if card.get_ready():
                            if primary_player.sacrifice_card_in_hq(int(game_update_string[2])):
                                self.action_chosen = ability
                                self.misc_counter = 4
                                await self.send_update_message("4 targets left for Holy Chapel")
                    elif ability == "Reveal The Blade":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
                            self.chosen_first_card = False
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
                    elif ability == "Abomination Workshop":
                        primary_player.sacrifice_card_in_hq(unit_pos)
                        self.misc_counter = primary_player.get_highest_cost_units()
                        self.chosen_first_card = False
                        self.action_chosen = ability
                        if self.misc_counter >= len(primary_player.cards):
                            self.chosen_first_card = True
                            self.player_with_action = secondary_player.name_player
                            self.misc_counter = secondary_player.get_highest_cost_units()
                            if self.misc_counter >= len(secondary_player.cards):
                                self.player_with_action = primary_player.name_player
                                self.action_cleanup()
                                await self.send_update_message("Abomination Workshop could not discard any cards. "
                                                               "Did you mean to do that?")
                    elif ability == "Embarked Squads":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(-2, int(game_update_string[2]), "blue")
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
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
                    elif ability == "Farseer Tadheris":
                        if not card.get_bloodied():
                            if not primary_player.get_once_per_round_used_given_pos(planet_pos, unit_pos):
                                primary_player.set_once_per_round_used_given_pos(planet_pos, unit_pos, True)
                                primary_player.mulligan_hand()
                                self.action_cleanup()
                        else:
                            if not primary_player.get_once_per_game_used_given_pos(planet_pos, unit_pos):
                                primary_player.set_once_per_game_used_given_pos(planet_pos, unit_pos, True)
                                primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                                primary_player.mulligan_hand()
                                self.action_cleanup()
                    elif ability == "Wraithbone Armour":
                        if card.get_ready():
                            self.chosen_first_card = False
                            self.action_chosen = ability
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                    elif ability == "Nesting Chamber":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
                    elif ability == "Hunting Grounds":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
                            self.chosen_first_card = False
                    elif ability == "Castellan Crowe BLOODIED":
                        if not card.get_once_per_game_used():
                            card.set_once_per_game_used(True)
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Supreme Appearance":
                        if card.get_ready():
                            if primary_player.controls_no_ranged_units():
                                card.exhaust_card()
                                primary_player.sacrifice_card_in_hq(int(game_update_string[2]))
                                for i in range(len(primary_player.headquarters)):
                                    if primary_player.check_is_unit_at_pos(-2, i):
                                        if primary_player.get_card_type_given_pos(-2, i) != "Warlord":
                                            primary_player.exhaust_given_pos(-2, i)
                                for i in range(len(secondary_player.headquarters)):
                                    if secondary_player.check_is_unit_at_pos(-2, i):
                                        if secondary_player.get_card_type_given_pos(-2, i) != "Warlord":
                                            secondary_player.exhaust_given_pos(-2, i)
                                for i in range(7):
                                    for j in range(len(primary_player.cards_in_play[i + 1])):
                                        if primary_player.get_card_type_given_pos(i, j) != "Warlord":
                                            primary_player.exhaust_given_pos(i, j)
                                    for j in range(len(secondary_player.cards_in_play[i + 1])):
                                        if secondary_player.get_card_type_given_pos(i, j) != "Warlord":
                                            secondary_player.exhaust_given_pos(i, j, card_effect=True)
                                self.action_cleanup()
                            else:
                                await self.send_update_message("You control ranged units.")
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
                    elif ability == "Naval Surgeon":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.action_chosen = ability
                    elif ability == "Ba'ar Zul's Cleavers":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            primary_player.increase_attack_of_unit_at_pos(-2, unit_pos, 2, "NEXT")
                            primary_player.assign_damage_to_pos(-2, unit_pos, 2, by_enemy_unit=False)
                            self.action_cleanup()
                    elif ability == "Raging Krootox":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            amount = primary_player.resources
                            primary_player.increase_attack_of_unit_at_pos(-2, unit_pos, amount, "EOP")
                            await self.send_update_message("Raging Krootox gained +" + str(amount) + " ATK.")
                            self.action_cleanup()
                    elif ability == "Prey on the Weak":
                        if not primary_player.headquarters[unit_pos].once_per_game_used:
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos)
                            self.action_chosen = ability
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
                    elif ability == "Improbable Runt Machine":
                        if not card_chosen.get_once_per_round_used():
                            card_chosen.set_once_per_round_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Sivarla Soulbinder":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                            self.misc_target_unit = (-1, -1)
                            self.chosen_first_card = False
                    elif ability == "Forward Outpost":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Korporal Snagbrat":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                    elif ability == "Lekor Blight-Tongue":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Plagueburst Crawler":
                        if not card.get_ready():
                            primary_player.ready_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Kaptin Bluddflagg":
                        if not card.get_once_per_round_used():
                            card.set_once_per_round_used(True)
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
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
                    elif ability == "Crypt of Saint Camila":
                        if not card.get_once_per_phase_used():
                            if card.get_ready():
                                card.exhaust_card()
                                card.set_once_per_phase_used(True)
                                self.action_chosen = ability
                                self.chosen_first_card = False
                    elif ability == "Evolutionary Adaptation":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
                            self.chosen_first_card = False
                    elif ability == "Smuggler's Den":
                        if card.get_ready():
                            if primary_player.resources > 0:
                                primary_player.spend_resources(1)
                                primary_player.exhaust_given_pos(-2, unit_pos)
                                self.action_chosen = ability
                    elif ability == "Webway Passage":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.misc_target_unit = (-1, -1)
                    elif ability == "Sacrificial Altar":
                        if card.get_ready():
                            card.exhaust_card()
                            self.action_chosen = ability
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
                    elif ability == "Jungle Trench":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.jungle_trench_count += 1
                            await self.send_update_message("Jungle Trenches active: " + str(self.jungle_trench_count))
                            self.action_cleanup()
                    elif ability == "Fungal Turf":
                        primary_player.sacrifice_card_in_hq(unit_pos)
                        self.action_chosen = ability
                        self.misc_counter = primary_player.get_highest_cost_units()
                        await self.send_update_message(str(self.misc_counter) + " Snotlings left to place.")
                        if self.misc_counter < 1:
                            await self.send_update_message("Highest cost 0; no Snotlings for you.")
                    elif ability == "Hallow Librarium":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
                            self.action_chosen = ability
                    elif ability == "The Black Rage":
                        if card_chosen.get_ready():
                            primary_player.exhaust_given_pos(planet_pos, unit_pos)
                            self.action_chosen = ability
                            primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    elif ability == "Uncontrollable Rioters":
                        if not card_chosen.get_once_per_round_used():
                            card_chosen.set_once_per_round_used(True)
                            self.take_control_of_card(secondary_player, primary_player, planet_pos, unit_pos)
                            self.action_cleanup()
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
                    elif ability == "Shroud Cruiser":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.action_chosen = ability
                            self.chosen_first_card = False
                    elif ability == "Clearcut Refuge":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Dark Angels Cruiser":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Da Workship":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.action_chosen = ability
                    elif ability == "Repair Bay":
                        if card.get_ready():
                            card.exhaust_card()
                            self.choices_available = []
                            self.choice_context = "Repair Bay"
                            self.name_player_making_choices = primary_player.name_player
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array, self.cards_dict,
                                                          self.apoka_errata_cards, self.cards_that_have_errata)
                                if card.check_for_a_trait("Drone", primary_player.etekh_trait) or \
                                        card.check_for_a_trait("Pilot", primary_player.etekh_trait):
                                    if card.get_name() not in self.choices_available:
                                        self.choices_available.append(card.get_name())
                            if not self.choices_available:
                                await self.send_update_message(
                                    "No valid target for Repair Bay."
                                )
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                            self.action_cleanup()
                    elif ability == "Etekh the Awakener":
                        if not card.get_once_per_phase_used():
                            card.set_once_per_phase_used(True)
                            self.choices_available = self.all_traits
                            self.choice_context = "Choose trait: (EtA)"
                            self.name_player_making_choices = primary_player.name_player
                            self.resolving_search_box = True
                            self.action_chosen = ability
                    elif ability == "Imotekh the Stormlord":
                        if not card.get_once_per_phase_used():
                            if not card.bloodied:
                                card.set_once_per_phase_used(True)
                                self.action_chosen = ability
                                self.chosen_first_card = False
                                self.misc_target_player = ""
                                await self.send_update_message("Imotekh activated; only army units supported.")
                    elif ability == "Starblaze's Outpost":
                        if card.get_ready():
                            primary_player.exhaust_given_pos(-2, unit_pos)
                            self.misc_target_planet = -1
                            self.action_chosen = ability
                            self.chosen_first_card = False
                            self.misc_counter = -1
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                    elif ability == "The Wolf Within":
                        if primary_player.sacrifice_card_in_hq(unit_pos):
                            self.misc_target_unit = (-1, -1)
                            self.misc_counter = 0
                            self.misc_counter_2 = 0
                            self.action_chosen = ability
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
                    elif ability == "Imperial Bastion":
                        if card.get_ready():
                            self.action_chosen = ability
                            primary_player.exhaust_given_pos(-2, int(game_update_string[2]))
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
            if primary_player.sacrifice_card_in_hq(int(game_update_string[2])):
                primary_player.discard_card_from_hand(self.card_pos_to_deploy)
                interrupts = secondary_player.search_triggered_interrupts_enemy_discard()
                primary_player.aiming_reticle_coords_hand = None
                if interrupts:
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Enemy Discard Effect?"
                    self.resolving_search_box = True
                    self.stored_discard_and_target.append((self.action_chosen, primary_player.number))
                else:
                    secondary_player.discard_card_at_random()
                    primary_player.draw_card()
                    primary_player.draw_card()
                    self.card_pos_to_deploy = -1
                    self.action_cleanup()
                    await primary_player.dark_eldar_event_played()
    elif self.action_chosen == "Painboy Surjery":
        if game_update_string[1] == primary_player.get_number():
            if self.misc_target_unit == (-1, -1) or self.misc_target_unit == (planet_pos, unit_pos):
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Orks":
                    if not primary_player.deck:
                        self.action_cleanup()
                    else:
                        card_name = primary_player.deck[0]
                        card = self.preloaded_find_card(card_name)
                        self.misc_target_unit = (planet_pos, unit_pos)
                        await self.send_update_message("Revealed a " + card.get_name())
                        if card.get_card_type() == "Attachment":
                            if not card.planet_attachment:
                                if primary_player.attach_card(card, planet_pos, unit_pos):
                                    del primary_player.deck[0]
                                    self.action_cleanup()
                                else:
                                    primary_player.deck.append(primary_player.deck[0])
                                    del primary_player.deck[0]
                                    primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                            else:
                                primary_player.deck.append(primary_player.deck[0])
                                del primary_player.deck[0]
                                primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                        else:
                            primary_player.deck.append(primary_player.deck[0])
                            del primary_player.deck[0]
                            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
    elif self.action_chosen == "Webway Passage":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not self.chosen_first_card:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.chosen_first_card = True
                else:
                    other_pla, other_pos = self.misc_target_unit
                    primary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                    if other_pla != planet_pos:
                        card1 = primary_player.get_card_given_pos(planet_pos, unit_pos)
                        card2 = primary_player.get_card_given_pos(other_pla, other_pos)
                        if other_pla == -2:
                            primary_player.headquarters.append(copy.deepcopy(card1))
                        else:
                            primary_player.cards_in_play[other_pla + 1].append(copy.deepcopy(card1))
                        if planet_pos == -2:
                            primary_player.headquarters.append(copy.deepcopy(card2))
                        else:
                            primary_player.cards_in_play[planet_pos + 1].append(copy.deepcopy(card2))
                        if planet_pos == -2:
                            del primary_player.headquarters[unit_pos]
                        else:
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                        if other_pla == -2:
                            del primary_player.headquarters[other_pos]
                        else:
                            del primary_player.cards_in_play[other_pla + 1][other_pos]
                    self.action_cleanup()
    elif self.action_chosen == "Lost in the Webway Harlequin":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Harlequin"):
                    if not self.chosen_first_card:
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                        self.chosen_first_card = True
                    else:
                        other_pla, other_pos = self.misc_target_unit
                        primary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                        if other_pla != planet_pos:
                            card1 = primary_player.get_card_given_pos(planet_pos, unit_pos)
                            card2 = primary_player.get_card_given_pos(other_pla, other_pos)
                            if other_pla == -2:
                                primary_player.headquarters.append(copy.deepcopy(card1))
                            else:
                                primary_player.cards_in_play[other_pla + 1].append(copy.deepcopy(card1))
                            if planet_pos == -2:
                                primary_player.headquarters.append(copy.deepcopy(card2))
                            else:
                                primary_player.cards_in_play[planet_pos + 1].append(copy.deepcopy(card2))
                            if planet_pos == -2:
                                del primary_player.headquarters[unit_pos]
                            else:
                                del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                            if other_pla == -2:
                                del primary_player.headquarters[other_pos]
                            else:
                                del primary_player.cards_in_play[other_pla + 1][other_pos]
                        self.action_cleanup()
    elif self.action_chosen == "Lost in the Webway Opponent":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not self.chosen_first_card:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.chosen_first_card = True
                else:
                    other_pla, other_pos = self.misc_target_unit
                    primary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                    if other_pla != planet_pos:
                        card1 = primary_player.get_card_given_pos(planet_pos, unit_pos)
                        card2 = primary_player.get_card_given_pos(other_pla, other_pos)
                        if other_pla == -2:
                            primary_player.headquarters.append(copy.deepcopy(card1))
                        else:
                            primary_player.cards_in_play[other_pla + 1].append(copy.deepcopy(card1))
                        if planet_pos == -2:
                            primary_player.headquarters.append(copy.deepcopy(card2))
                        else:
                            primary_player.cards_in_play[planet_pos + 1].append(copy.deepcopy(card2))
                        if planet_pos == -2:
                            del primary_player.headquarters[unit_pos]
                        else:
                            del primary_player.cards_in_play[planet_pos + 1][unit_pos]
                        if other_pla == -2:
                            del primary_player.headquarters[other_pos]
                        else:
                            del primary_player.cards_in_play[other_pla + 1][other_pos]
                    self.action_cleanup()
    elif self.action_chosen == "World Engine Beam":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                self.misc_target_unit = (planet_pos, unit_pos)
                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "red")
                health_remaining = primary_player.get_health_given_pos(planet_pos, unit_pos)
                health_remaining = health_remaining - primary_player.get_damage_given_pos(planet_pos, unit_pos)
                self.choices_available = []
                for i in range(health_remaining):
                    self.choices_available.append(str(i + 1))
                self.choice_context = "Amount of damage (WEB)"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
    elif self.action_chosen == "The Siege Masters":
        if game_update_string[1] == secondary_player.get_number():
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                if secondary_player.get_ready_given_pos(planet_pos, unit_pos):
                    can_continue = True
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        -2, unit_pos, targeting_support=True, event=True)
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
                        secondary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.resolving_search_box = True
                        self.what_to_do_with_searched_card = "DRAW"
                        self.traits_of_searched_card = None
                        self.card_type_of_searched_card = "Support"
                        self.faction_of_searched_card = None
                        self.max_cost_of_searched_card = 999
                        self.all_conditions_searched_card_required = True
                        self.no_restrictions_on_chosen_card = False
                        primary_player.number_cards_to_search = 8
                        for i in range(len(primary_player.headquarters)):
                            if primary_player.get_ability_given_pos(-2, i) == "Gladius Strike Force":
                                if primary_player.headquarters[i].counter > 0:
                                    primary_player.number_cards_to_search += 2
                        if len(primary_player.deck) > primary_player.number_cards_to_search:
                            self.cards_in_search_box = primary_player.deck[:primary_player.number_cards_to_search]
                        else:
                            self.cards_in_search_box = primary_player.deck[:len(primary_player.deck)]
                        self.name_player_who_is_searching = primary_player.name_player
                        self.number_who_is_searching = primary_player.number
                        self.action_cleanup()
    elif self.action_chosen == "Evolutionary Adaptation":
        if self.chosen_first_card:
            if primary_player.get_number() == game_update_string[1]:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and \
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kroot"):
                    if self.misc_target_choice == "Brutal":
                        primary_player.headquarters[unit_pos].brutal_eor = True
                    if self.misc_target_choice == "Armorbane":
                        primary_player.headquarters[unit_pos].armorbane_eor = True
                    if self.misc_target_choice == "Flying":
                        primary_player.headquarters[unit_pos].flying_eor = True
                    if self.misc_target_choice == "Mobile":
                        primary_player.headquarters[unit_pos].mobile_eor = True
                    if self.misc_target_choice == "Ranged":
                        primary_player.headquarters[unit_pos].ranged_eor = True
                    if self.misc_target_choice == "Area Effect":
                        primary_player.headquarters[unit_pos].area_effect_eor = \
                            self.stored_area_effect_value
                    name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                    if self.misc_target_choice == "Area Effect":
                        self.misc_target_choice += " (" + str(self.stored_area_effect_value) + ")"
                    await self.send_update_message(
                        name + " gained " + self.misc_target_choice + "."
                    )
                    self.action_cleanup()
                    self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Forward Outpost":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Drone"):
                player_owning_card.headquarters[unit_pos].sweep_next += 2
                self.action_cleanup()
    elif self.action_chosen == "The Black Rage":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
                    primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
                    primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOG")
                    primary_player.increase_retaliate_given_pos_eop(planet_pos, unit_pos, 1)
                    primary_player.headquarters[unit_pos].sacrifice_end_of_phase = True
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.action_cleanup()
    elif self.action_chosen == "Imotekh the Stormlord":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if not primary_player.get_unique_given_pos(planet_pos, unit_pos) and not\
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                    og_card = self.preloaded_find_card(self.misc_target_player)
                    primary_player.headquarters[unit_pos].new_armorbane = og_card.armorbane
                    primary_player.headquarters[unit_pos].new_ambush = og_card.ambush
                    primary_player.headquarters[unit_pos].new_mobile = og_card.mobile
                    primary_player.headquarters[unit_pos].new_brutal = og_card.brutal
                    primary_player.headquarters[unit_pos].new_sweep = og_card.sweep
                    primary_player.headquarters[unit_pos].new_area_effect = og_card.area_effect
                    primary_player.headquarters[unit_pos].new_ranged = og_card.ranged
                    primary_player.headquarters[unit_pos].new_limited = og_card.limited
                    primary_player.headquarters[unit_pos].new_lumbering = og_card.lumbering
                    primary_player.headquarters[unit_pos].new_unstoppable = og_card.unstoppable
                    primary_player.headquarters[unit_pos].new_flying = og_card.flying
                    primary_player.headquarters[unit_pos].new_additional_resources_command_struggle = \
                        og_card.additional_resources_command_struggle
                    primary_player.headquarters[unit_pos].new_additional_cards_command_struggle = \
                        og_card.additional_cards_command_struggle
                    primary_player.headquarters[unit_pos].new_ability = self.misc_target_player
                    card_name = primary_player.get_name_given_pos(planet_pos, unit_pos)
                    self.action_cleanup()
                    await self.send_update_message(card_name + " in headquarters gained " +
                                                   self.misc_target_player + "'s text box!")
    elif self.action_chosen == "Clearcut Refuge":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        if player_being_hit.headquarters[unit_pos].get_is_unit():
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
                highest_cost = player_being_hit.get_highest_cost_units()
                player_being_hit.increase_health_of_unit_at_pos(-2, unit_pos, highest_cost, expiration="EOP")
                name_unit = player_being_hit.get_name_given_pos(-2, unit_pos)
                await self.send_update_message(name_unit + " gained +" + str(highest_cost) + " HP.")
                self.action_cleanup()
    elif self.action_chosen == "Holy Crusade":
        if game_update_string[1] == primary_player.get_number():
            primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.misc_counter = self.misc_counter - 1
            if self.misc_counter < 1:
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.action_cleanup()
    elif self.action_chosen == "Canoness Vardina":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "Particle Whip":
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
                    player_being_hit.assign_damage_to_pos(-2, unit_pos, self.misc_counter, by_enemy_unit=False)
                    player_being_hit.set_aiming_reticle_in_play(-2, unit_pos, "red")
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    self.misc_counter = 0
                    self.action_cleanup()
    elif self.action_chosen == "Plagueburst Crawler":
        if not player_owning_card.get_unique_given_pos(planet_pos, unit_pos):
            player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 2)
            self.action_cleanup()
    elif self.action_chosen == "Prey on the Weak":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Synapse":
                name_synapse = primary_player.get_name_given_pos(planet_pos, unit_pos)
                primary_player.sacrifice_card_in_play(planet_pos, unit_pos)
                og_pla, og_pos = self.position_of_actioned_card
                if unit_pos < og_pos:
                    self.position_of_actioned_card = (og_pla, og_pos - 1)
                self.choice_context = "Choose a new Synapse: (PotW)"
                self.choices_available = primary_player.synapse_list
                try:
                    self.choices_available.remove(name_synapse)
                except ValueError:
                    pass
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
    elif self.action_chosen == "Despise":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.headquarters[unit_pos].check_for_a_trait("Ally", primary_player.etekh_trait):
                if primary_player.sacrifice_card_in_hq(unit_pos):
                    self.player_with_action = secondary_player.name_player
                    primary_player.sacced_card_for_despise = True
                    if primary_player.sacced_card_for_despise and secondary_player.sacced_card_for_despise:
                        self.action_cleanup()
                        await secondary_player.dark_eldar_event_played()
    elif self.action_chosen == "Fetid Haze":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.headquarters[unit_pos].get_is_unit():
                if primary_player.headquarters[unit_pos].check_for_a_trait("Nurgle", primary_player.etekh_trait):
                    damage = primary_player.get_damage_given_pos(-2, unit_pos)
                    primary_player.remove_damage_from_pos(-2, unit_pos, 999, healing=True)
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
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos, event=True)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos, power=True):
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
                    secondary_player.assign_damage_to_pos(-2, unit_pos, damage, by_enemy_unit=False)
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.action_cleanup()
    elif self.action_chosen == "Big Mek Kagdrak":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                self.misc_target_unit = (planet_pos, unit_pos)
                self.misc_target_player = player_owning_card.name_player
                self.choices_available = ["Flying", "Armorbane", "Brutal",
                                          "Area Effect (1)", "Sweep (2)", "Retaliate (3)"]
                if primary_player.last_kagrak_trait in self.choices_available:
                    self.choices_available.remove(primary_player.last_kagrak_trait)
                self.choice_context = "Big Mek Kagdrak Keyword"
                self.name_player_making_choices = primary_player.name_player
                self.resolving_search_box = True
    elif self.action_chosen == "Power from Pain":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                if primary_player.sacrifice_card_in_hq(unit_pos):
                    self.action_cleanup()
                    await secondary_player.dark_eldar_event_played()
                    secondary_player.torture_event_played("Power from Pain")
    elif self.action_chosen == "A Thousand Cuts":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if player_being_hit.headquarters[unit_pos].get_card_type() == "Army":
            if not player_being_hit.check_for_trait_given_pos(-2, unit_pos, "Elite"):
                if player_being_hit.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos, event=True)
                    if secondary_player.get_immune_to_enemy_events(-2, unit_pos, power=True):
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
                    player_being_hit.assign_damage_to_pos(-2, unit_pos, 1, by_enemy_unit=False)
                    primary_player.shuffle_deck()
                    primary_player.aiming_reticle_coords_hand = None
                    await primary_player.dark_eldar_event_played()
                    primary_player.torture_event_played("A Thousand Cuts")
                    self.action_cleanup()
    elif self.action_chosen == "Keep Firing!":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Tank"):
                if not primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    primary_player.ready_given_pos(planet_pos, unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Missile Pod":
        resolved_something = False
        print('missile pod')
        can_continue = True
        if game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
                resolved_something = True
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
                    self.nullify_context = "Event Action"
                if can_continue:
                    secondary_player.assign_damage_to_pos(-2, unit_pos, 3, by_enemy_unit=False)
                    self.action_cleanup()
        if not resolved_something:
            print("support check")
            if game_update_string[1] == "1":
                player_being_hit = self.p1
            else:
                player_being_hit = self.p2
            if player_being_hit.get_card_type_given_pos(-2, unit_pos) == "Support":
                print('interrupt check')
                if player_being_hit.name_player == secondary_player.name_player:
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        -2, unit_pos, targeting_support=True)
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
                    player_being_hit.destroy_card_in_hq(unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Lekor Blight-Tongue":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            player_owning_card.headquarters[unit_pos].infection_lekor += 1
            await self.send_update_message(player_owning_card.get_name_given_pos(planet_pos, unit_pos) +
                                           " gained an infection token!")
            if player_owning_card.headquarters[unit_pos].infection_lekor > 1:
                player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 3)
                player_owning_card.headquarters[unit_pos].infection_lekor = 0
            self.action_cleanup()
    elif self.action_chosen == "Evangelizing Ships":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                await self.send_update_message("Faith paid, please continue.")
                self.chosen_first_card = True
                self.chosen_second_card = False
    elif self.action_chosen == "Tzeentch's Firestorm":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if player_being_hit.headquarters[unit_pos].get_card_type() != "Warlord":
            if player_being_hit.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos, event=True)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos, power=True):
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
                player_being_hit.assign_damage_to_pos(-2, unit_pos, self.amount_spend_for_tzeentch_firestorm,
                                                      by_enemy_unit=False)
                player_being_hit.set_aiming_reticle_in_play(-2, unit_pos, "red")
                primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                primary_player.aiming_reticle_coords_hand = None
                self.amount_spend_for_tzeentch_firestorm = -1
                self.action_cleanup()
    elif self.action_chosen == "Castellan Crowe BLOODIED":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                og_pla, og_pos = self.position_of_actioned_card
                primary_player.increase_attack_of_unit_at_pos(og_pla, og_pos, 3, expiration="NEXT")
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                primary_player.reset_aiming_reticle_in_play(og_pla, og_pos)
                self.action_cleanup()
    elif self.action_chosen == "The Wolf Within":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Space Wolves"):
                if (planet_pos, unit_pos) != self.misc_target_unit:
                    self.misc_target_unit = (planet_pos, unit_pos)
                    primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                    primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
                    await self.send_update_message(primary_player.get_name_given_pos(planet_pos, unit_pos) +
                                                   " gained +1 ATK and +1 HP!")
                    self.misc_counter = self.misc_counter + 1
                    if self.misc_counter > 1:
                        self.action_cleanup()
    elif self.action_chosen == "Overrun":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_card_type() == "Army":
            can_continue = True
            possible_interrupts = []
            if player_owning_card.name_player == primary_player.name_player:
                possible_interrupts = secondary_player.intercept_check()
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    planet_pos, unit_pos, intercept_possible=True, event=True)
                if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy card abilities.")
                elif secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                    can_continue = False
                    await self.send_update_message("Immune to enemy events.")
            if possible_interrupts and can_continue:
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
                player_being_hit.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                primary_player.discard_card_name_from_hand("Overrun")
                primary_player.aiming_reticle_coords_hand = None
                self.action_cleanup()
    elif self.action_chosen == "Reveal The Blade":
        if self.chosen_first_card:
            if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                player_owning_card.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, expiration="NEXT")
                self.action_cleanup()
    elif self.action_chosen == "Improbable Runt Machine":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Runt"):
                name_card = primary_player.get_name_given_pos(planet_pos, unit_pos)
                card_to_add = CardClasses.AttachmentCard(name_card, "", "Copilot.", 0, "Orks", "Common",
                                                         0, False)
                primary_player.attach_card(card_to_add, self.position_of_actioned_card[0],
                                           self.position_of_actioned_card[1])
                primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                            self.position_of_actioned_card[1])
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                del primary_player.headquarters[unit_pos]
                self.action_cleanup()
    elif self.action_chosen == "Overrun Rout":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.sacrifice_card_in_hq(unit_pos):
                og_pla, og_pos = self.misc_target_unit
                secondary_player.rout_unit(og_pla, og_pos)
                self.action_cleanup()
    elif self.action_chosen == "Naval Surgeon":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, "EOG")
                primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, 1, "EOG")
                self.action_cleanup()
    elif self.action_chosen == "Hate":
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
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos, event=True)
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
            self.action_cleanup()
    elif self.action_chosen == "Kaptin Bluddflagg":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                    if not primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
    elif self.action_chosen == "Imperial Bastion":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.check_is_unit_at_pos(planet_pos, unit_pos):
            attachments = player_being_hit.headquarters[unit_pos].get_attachments()
            magus_card = False
            for i in range(len(attachments)):
                if attachments[i].from_magus_harid:
                    magus_card = True
            if magus_card:
                player_being_hit.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
                self.action_cleanup()
    elif self.action_chosen == "Memories of Fallen Comrades":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                if (planet_pos, unit_pos) != self.misc_target_unit:
                    if primary_player.headquarters[unit_pos].get_damage() > 0:
                        primary_player.headquarters[unit_pos].decrease_damage(1)
                        self.misc_counter += 1
                        self.misc_target_unit = (planet_pos, unit_pos)
                        if self.misc_counter > 1:
                            self.action_cleanup()
    elif self.action_chosen == "Twisted Laboratory":
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
                self.action_cleanup()
    elif self.action_chosen == "Squiggify":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        unit_pos = int(game_update_string[2])
        can_continue = True
        if not player_being_hit.headquarters[unit_pos].check_for_a_trait("Vehicle", player_being_hit.etekh_trait) and \
                player_being_hit.get_card_type_given_pos(-2, unit_pos) == "Army":
            if player_being_hit.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos, event=True)
                if secondary_player.get_immune_to_enemy_events(-2, unit_pos, power=True):
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
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                -2, unit_pos, targeting_support=is_support, event=True)
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
                if primary_player.headquarters[unit_pos].check_for_a_trait("Drone", primary_player.etekh_trait):
                    if primary_player.sacrifice_card_in_hq(unit_pos):
                        self.chosen_first_card = True
            else:
                if primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Necrons":
                    if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                        primary_player.ready_given_pos(planet_pos, unit_pos)
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
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
                                                        self.position_of_actioned_card[1], 1,
                                                        by_enemy_unit=False)
                    primary_player.set_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                              self.position_of_actioned_card[1], "red")
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
    elif self.action_chosen == "+1 ATK Warrior":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_for_trait_given_pos(-2, unit_pos, "Warrior"):
                primary_player.increase_attack_of_unit_at_pos(-2, unit_pos, 1, expiration="EOP")
                self.action_cleanup()
    elif self.action_chosen == "Holy Chapel":
        if game_update_string[1] == "1":
            target_player = self.p1
        else:
            target_player = self.p2
        if target_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum" or \
                target_player.get_faction_given_pos(planet_pos, unit_pos) == "Space Marines":
            if target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                target_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    self.action_cleanup()
                    await self.send_update_message("Completed Holy Chapel")
                else:
                    await self.send_update_message(str(self.misc_counter) + " targets left for Holy Chapel")
    elif self.action_chosen == "Subdual":
        if game_update_string[1] == "1":
            target_player = self.p1
        else:
            target_player = self.p2
        if target_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
            can_continue = True
            if target_player.name_player == secondary_player.name_player:
                is_support = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=is_support, event=True)
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
    elif self.action_chosen == "Hunting Grounds":
        if game_update_string[1] == primary_player.number:
            if not self.chosen_first_card:
                if primary_player.get_name_given_pos(-2, unit_pos) == "Khymera":
                    if primary_player.sacrifice_card_in_hq(unit_pos):
                        self.chosen_first_card = True
            else:
                if primary_player.check_for_trait_given_pos(-2, unit_pos, "Creature"):
                    if primary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
                        if not primary_player.get_ready_given_pos(-2, unit_pos):
                            primary_player.ready_given_pos(-2, unit_pos)
                            self.action_cleanup()
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
                    if primary_player.headquarters[unit_pos].check_for_a_trait("Ethereal", primary_player.etekh_trait):
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
                    self.action_cleanup()
                    primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
                    primary_player.aiming_reticle_coords_hand = None
                    self.misc_counter = 0
        else:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                if secondary_player.get_cost_given_pos(planet_pos, unit_pos) <= self.misc_counter:
                    can_continue = True
                    is_support = True
                    possible_interrupts = secondary_player.interrupt_cancel_target_check(
                        -2, unit_pos, targeting_support=is_support, event=True)
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
    elif self.action_chosen == "Piercing Wail":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            if player_being_hit.get_cost_given_pos(planet_pos, unit_pos) <= self.misc_counter:
                can_continue = True
                if player_being_hit.name_player == secondary_player.name_player:
                    if secondary_player.get_immune_to_enemy_events(planet_pos, unit_pos):
                        can_continue = False
                if can_continue:
                    player_being_hit.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                    if not self.chosen_first_card:
                        self.chosen_first_card = True
                    else:
                        self.action_cleanup()
    elif self.action_chosen == "Ferocious Strength":
        if primary_player.get_number() == game_update_string[1]:
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
    elif self.action_chosen == "Alluring Daemonette":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Cultist"):
                    if primary_player.sacrifice_card_in_hq(unit_pos):
                        self.chosen_first_card = True
    elif self.action_chosen == "Embarked Squads":
        if game_update_string[1] == primary_player.number:
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Vehicle") and not \
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Upgrade"):
                    primary_player.headquarters[unit_pos].embarked_squads_active = True
                    primary_player.headquarters[unit_pos].extra_traits_eor += "Upgrade. Transport."
                    await self.send_update_message(primary_player.headquarters[unit_pos].name +
                                                   "gained the Embarked Squads effect!")
                    primary_player.reset_all_aiming_reticles_play_hq()
                    self.action_cleanup()
    elif self.action_chosen == "Saint Celestine":
        if self.chosen_first_card:
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                self.misc_counter = self.misc_counter - 1
                if self.misc_counter < 1:
                    card = primary_player.get_card_in_hand(primary_player.aiming_reticle_coords_hand)
                    del primary_player.cards[primary_player.aiming_reticle_coords_hand]
                    target_planet = self.position_of_actioned_card[0]
                    primary_player.add_card_to_planet(card, target_planet)
                    primary_player.aiming_reticle_coords_hand = None
                    self.action_cleanup()
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
    elif self.action_chosen == "Everlasting Rage":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Khorne"):
                if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                    x_value = int(self.misc_target_choice)
                    damage_on_unit = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                    if damage_on_unit > 0:
                        damage_to_remove = min(damage_on_unit, x_value)
                        primary_player.remove_damage_from_pos(planet_pos, unit_pos, damage_to_remove, healing=True)
                        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, x_value,
                                                                      expiration="NEXT")
                        self.action_cleanup()
    elif self.action_chosen == "Sivarla Soulbinder":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Cultist"):
                    self.misc_target_unit = (planet_pos, unit_pos)
                    self.chosen_first_card = True
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
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
                primary_player.remove_damage_from_pos(-2, unit_pos, 2, healing=True)
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
            if primary_player.headquarters[unit_pos].check_for_a_trait("Ethereal", primary_player.etekh_trait):
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
            if primary_player.headquarters[unit_pos].check_for_a_trait("Cultist", primary_player.etekh_trait):
                if primary_player.sacrifice_card_in_hq(unit_pos):
                    if planet_pos == self.position_of_actioned_card[0]:
                        if self.position_of_actioned_card[1] > unit_pos:
                            self.position_of_actioned_card = (planet_pos, self.position_of_actioned_card[1] - 1)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    primary_player.remove_damage_from_pos(self.position_of_actioned_card[0],
                                                          self.position_of_actioned_card[1], 999, healing=True)
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
                    self.action_cleanup()
                    self.position_of_actioned_card = (-1, -1)
    elif self.action_chosen == "Repent!":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.get_cost_given_pos(planet_pos, unit_pos) >= self.misc_counter:
                if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                    if not self.chosen_first_card:
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.chosen_first_card = True
                        self.player_with_action = secondary_player.name_player
                        self.misc_counter = secondary_player.get_highest_cost_units()
                        primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    else:
                        self.player_with_action = secondary_player.name_player
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        atk1 = primary_player.get_attack_given_pos(planet_pos, unit_pos)
                        other_pla, other_pos = self.misc_target_unit
                        atk2 = secondary_player.get_attack_given_pos(other_pla, other_pos)
                        secondary_player.exhaust_given_pos(other_pla, other_pos)
                        secondary_player.reset_aiming_reticle_in_play(other_pla, other_pos)
                        primary_player.assign_damage_to_pos(planet_pos, unit_pos, atk2, by_enemy_unit=False)
                        secondary_player.assign_damage_to_pos(other_pla, other_pos, atk1, by_enemy_unit=False)
                        self.action_cleanup()
    elif self.action_chosen == "Ancient Keeper of Secrets":
        if primary_player.get_number() == game_update_string[1]:
            unit_pos = int(game_update_string[2])
            if primary_player.headquarters[unit_pos].check_for_a_trait("Cultist", primary_player.etekh_trait):
                if primary_player.sacrifice_card_in_hq(unit_pos):
                    if planet_pos == self.position_of_actioned_card[0]:
                        if self.position_of_actioned_card[1] > unit_pos:
                            self.position_of_actioned_card = (planet_pos, self.position_of_actioned_card[1] - 1)
                    primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                                self.position_of_actioned_card[1])
                    primary_player.ready_given_pos(self.position_of_actioned_card[0],
                                                   self.position_of_actioned_card[1])
                    self.mask_jain_zar_check_actions(primary_player, secondary_player)
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
        if game_update_string[1] == "1":
            player_returning = self.p1
        else:
            player_returning = self.p2
        can_continue = True
        if player_returning.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(-2, unit_pos, event=True)
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
                    -2, unit_pos, targeting_support=is_support, event=True)
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
    elif self.action_chosen == "Supply Line Incursion":
        if player_owning_card.headquarters[unit_pos].get_card_type() == "Support":
            can_continue = True
            is_support = True
            if player_owning_card.name_player == secondary_player.name_player:
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=is_support, event=True)
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
                player_owning_card.exhaust_given_pos(planet_pos, unit_pos)
                if player_owning_card.headquarters[unit_pos].get_limited():
                    primary_player.draw_card()
                    primary_player.add_resources(1)
                await primary_player.dark_eldar_event_played()
                self.action_cleanup()
    elif self.action_chosen == "Consumed by the Kindred":
        if game_update_string[1] == primary_player.get_number():
            if not self.chosen_first_card:
                if primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Kroot"):
                    if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                        primary_player.exhaust_given_pos(planet_pos, unit_pos)
                        self.chosen_first_card = True
                        self.misc_target_unit = (planet_pos, unit_pos)
            else:
                if not primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Vehicle"):
                    if (planet_pos, unit_pos) != self.misc_target_unit:
                        cost = primary_player.get_cost_given_pos(planet_pos, unit_pos)
                        if primary_player.sacrifice_card_in_hq(unit_pos):
                            primary_player.add_resources(cost)
                            self.action_cleanup()
    elif self.action_chosen == "Ambush Platform":
        if game_update_string[1] == "1":
            player_receiving_attachment = self.p1
        else:
            player_receiving_attachment = self.p2
        if primary_player.aiming_reticle_coords_hand_2 is not None:
            hand_pos = primary_player.aiming_reticle_coords_hand_2
            planet_pos = -2
            unit_pos = int(game_update_string[2])
            card = FindCard.find_card(primary_player.cards[hand_pos], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            army_unit_as_attachment = False
            discounts = primary_player.search_hq_for_discounts("", "", is_attachment=True)
            if card.get_ability() == "Gun Drones" or \
                    card.get_ability() == "Shadowsun's Stealth Cadre" or \
                    card.get_ability() == "Escort Drone":
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
