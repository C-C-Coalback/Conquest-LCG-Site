from ..CardClasses import ArmyCard
from ..Phases import DeployPhase
from .. import FindCard


async def update_game_event_action_attachment_in_play(self, name, game_update_string):
    if name == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    planet_pos = int(game_update_string[3])
    unit_pos = int(game_update_string[4])
    attachment_pos = int(game_update_string[5])
    if game_update_string[2] == "1":
        card_chosen = self.p1.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        player_owning_card = self.p1
        other_player = self.p2
    else:
        card_chosen = self.p2.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        player_owning_card = self.p2
        other_player = self.p1
    if not self.action_chosen:
        print("action not chosen")
        if card_chosen.get_has_action_while_in_play() and not card_chosen.from_magus_harid:
            if card_chosen.get_allowed_phases_while_in_play() == self.phase or \
                    card_chosen.get_allowed_phases_while_in_play() == "ALL":
                ability = card_chosen.get_ability()
                self.position_of_actioned_card = (planet_pos, unit_pos)
                print("ability:", ability)
                if card_chosen.name_owner == self.player_with_action:
                    print("ok owner")
                    if ability == "Command-link Drone":
                        if primary_player.spend_resources(1):
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                            self.misc_target_player = player_owning_card.name_player
                            await self.send_update_message(ability + " activated")
                    elif ability == "Missile Pod":
                        player_owning_card.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                        self.action_chosen = ability
                        await self.send_update_message(ability + " activated")
                    elif ability == "Searchlight":
                        if primary_player.get_name_player() == player_owning_card.name_player:
                            warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                            if primary_player.get_ready_given_pos(warlord_pla, warlord_pos):
                                primary_player.exhaust_given_pos(warlord_pla, warlord_pos)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                await self.send_update_message(ability + " activated")
                    elif ability == "Gauss Flayer":
                        if primary_player.get_name_player() == player_owning_card.name_player:
                            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                self.action_chosen = ability
                                player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                                self.position_of_actioned_card = (planet_pos, unit_pos)
                                self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                                self.misc_target_player = player_owning_card.name_player
                                await self.send_update_message(ability + " activated")
                    elif ability == "Iridescent Wand":
                        if primary_player.get_name_player() == player_owning_card.name_player:
                            if card_chosen.get_ready():
                                if self.replaced_planets[planet_pos]:
                                    card_chosen.exhaust_card()
                                    self.misc_counter = 2
                                    self.action_chosen = ability
                                    self.misc_target_unit = (-1, -1)
                                    self.misc_target_planet = planet_pos
                    elif ability == "Departmento Munitorum Aid":
                        if primary_player.get_name_player() == player_owning_card.name_player:
                            if card_chosen.get_ready():
                                damage_before = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                                if damage_before > 0:
                                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                                    damage_after = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                                    if damage_after < damage_before:
                                        card_chosen.exhaust_card()
                                        primary_player.retreat_unit(planet_pos, unit_pos)
                                        self.action_cleanup()
                    elif ability == "Blight Grenades":
                        player_owning_card.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        player_owning_card.cards_in_play[planet_pos + 1][unit_pos].area_effect_eocr += 2
                        self.action_cleanup()
                    elif ability == "The Glovodan Eagle":
                        player_owning_card.remove_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        card = ArmyCard("The Glovodan Eagle", "Action: Return this unit to your hand.", "Familiar.",
                                        1, "Astra Militarum", "Signature", 1, 1, 0, True,
                                        action_in_play=True, allowed_phases_in_play="ALL")
                        primary_player.add_card_to_planet(card, planet_pos, triggered_card_effect=False)
                        self.action_cleanup()
                    elif ability == "Scribe Servo-Skull":
                        player_owning_card.remove_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        card = ArmyCard("Scribe Servo-Skull", "Action: Exhaust this unit to ready an"
                                                              " attachment at this planet.", "Drone.",
                                        1, "Astra Militarum", "Loyal", 0, 1, 0, False,
                                        action_in_play=True, allowed_phases_in_play="ALL")
                        primary_player.add_card_to_planet(card, planet_pos, triggered_card_effect=False)
                        self.action_cleanup()
                    elif ability == "Pulsating Carapace":
                        if card_chosen.get_ready():
                            if primary_player.get_name_player() == self.player_with_action:
                                self.choices_available = ["Infest planet", "Heal 2 damage"]
                                self.choice_context = "Pulsating Carapace choice"
                                self.misc_target_planet = planet_pos
                                self.misc_target_unit = (planet_pos, unit_pos)
                                self.misc_target_player = int(player_owning_card.get_number())
                                self.name_player_making_choices = primary_player.get_name_player()
                                self.resolving_search_box = True
                                card_chosen.exhaust_card()
                                self.action_cleanup()
                    elif ability == "Soot-Blackened Axe":
                        card_chosen.aiming_reticle_color = None
                        primary_player.cards_in_reserve[planet_pos].append(card_chosen)
                        self.action_chosen = ability
                        self.misc_target_choice = primary_player.get_number()
                        self.misc_target_unit = (planet_pos, unit_pos)
                        del player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
                        if player_owning_card.get_damage_given_pos(planet_pos, unit_pos) < 1:
                            self.action_cleanup()
                        elif player_owning_card.check_if_card_is_destroyed(planet_pos, unit_pos):
                            self.action_cleanup()
                        else:
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos)
                    elif ability == "Attuned Gyrinx":
                        if player_owning_card.name_player == primary_player.get_name_player():
                            if card_chosen.get_ready():
                                card_chosen.exhaust_card()
                                self.action_chosen = ability
                                self.misc_counter = 0
                                self.misc_target_unit = (-1, -1)
                    elif ability == "The Dawn Blade":
                        if card_chosen.get_ready():
                            if player_owning_card.name_player == primary_player.get_name_player():
                                card_chosen.exhaust_card()
                                self.action_chosen = "The Dawn Blade"
                                self.misc_target_choice = ""
                                self.chosen_first_card = False
                                self.choices_available = ["Deepstrike", "Move"]
                                self.choice_context = "The Dawn Blade Choice"
                                self.name_player_making_choices = primary_player.get_name_player()
                    elif ability == "Positional Relay":
                        if card_chosen.get_ready():
                            if player_owning_card.name_player == primary_player.get_name_player():
                                card_chosen.exhaust_card()
                                attachment_count = primary_player.count_attachments_controlled()
                                if attachment_count > 0:
                                    self.action_chosen = ability
                                    self.resolving_search_box = True
                                    self.what_to_do_with_searched_card = "DRAW"
                                    self.traits_of_searched_card = None
                                    self.card_type_of_searched_card = "Attachment"
                                    self.faction_of_searched_card = None
                                    self.max_cost_of_searched_card = 99
                                    self.all_conditions_searched_card_required = True
                                    self.no_restrictions_on_chosen_card = False
                                    primary_player.number_cards_to_search = attachment_count
                                    if primary_player.number_cards_to_search > len(primary_player.deck):
                                        primary_player.number_cards_to_search = len(primary_player.deck)
                                    self.cards_in_search_box = primary_player.deck[
                                                               0:primary_player.number_cards_to_search]
                                    self.name_player_who_is_searching = primary_player.get_name_player()
                                    self.number_who_is_searching = primary_player.get_number()
                                self.action_cleanup()
                    elif ability == "Memories of Fallen Comrades":
                        if player_owning_card.name_player == primary_player.get_name_player():
                            if card_chosen.get_ready():
                                card_chosen.exhaust_card()
                                self.action_chosen = ability
                                self.misc_counter = 0
                                self.misc_target_unit = (-1, -1)
                    elif ability == "Drivin' Ambishun'":
                        if player_owning_card.name_player == primary_player.get_name_player():
                            if card_chosen.get_ready():
                                card_chosen.exhaust_card()
                                self.action_chosen = ability
                                self.misc_target_planet = planet_pos
                    elif ability == "Talisman of Denial":
                        if player_owning_card.name_player == primary_player.get_name_player():
                            hale_warlord = False
                            enemy_warlord_pla = -1
                            enemy_warlord_pos = -1
                            for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                                if secondary_player.get_card_type_given_pos(planet_pos, i) == "Warlord":
                                    if not secondary_player.cards_in_play[planet_pos + 1][i].get_bloodied():
                                        hale_warlord = True
                                        enemy_warlord_pla = planet_pos
                                        enemy_warlord_pos = i
                            if hale_warlord:
                                primary_player.sacrifice_attachment_from_pos(planet_pos, unit_pos,
                                                                             attachment_pos)
                                own_damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                                enemy_damage = secondary_player.get_damage_given_pos(enemy_warlord_pla,
                                                                                     enemy_warlord_pos)
                                primary_player.set_damage_given_pos(planet_pos, unit_pos, enemy_damage)
                                secondary_player.set_damage_given_pos(planet_pos, unit_pos, own_damage)
                                self.action_cleanup()
                    elif ability == "Drone Defense System":
                        if player_owning_card.name_player == primary_player.get_name_player():
                            if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                                primary_player.exhaust_given_pos(planet_pos, unit_pos)
                                for i in range(len(secondary_player.cards_in_play[planet_pos + 1])):
                                    if not secondary_player.get_ready_given_pos(planet_pos, i):
                                        secondary_player.assign_damage_to_pos(planet_pos, i, 2, by_enemy_unit=False)
                                self.action_cleanup()
                    elif ability == "Terminator Armour":
                        if not card_chosen.get_once_per_game_used():
                            if player_owning_card.name_player == primary_player.get_name_player():
                                card_chosen.set_once_per_game_used(True)
                                self.misc_target_unit = (planet_pos, unit_pos)
                                primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos)
                                self.action_chosen = ability
                    elif ability == "Cenobyte Servitor":
                        primary_player.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        self.chosen_first_card = False
                        self.action_chosen = ability
                    elif ability == "Hallucinogen Grenade":
                        primary_player.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        self.action_chosen = ability
                        self.misc_target_planet = planet_pos
                    elif ability == "Ymgarl Factor":
                        if primary_player.spend_resources(1):
                            self.action_chosen = ability
                            self.misc_target_unit = (planet_pos, unit_pos)
                            self.choices_available = ["+2 ATK", "+2 HP"]
                            self.choice_context = "Ymgarl Factor gains:"
                            self.name_player_making_choices = primary_player.get_name_player()
                            self.resolving_search_box = True
                    elif ability == "Saim-Hann Jetbike":
                        self.misc_target_player = player_owning_card.name_player
                        player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                        await self.send_update_message(ability + " activated")
                        self.action_chosen = ability
                        self.chosen_first_card = False
                        card_chosen.exhaust_card()
                    elif ability == "Hyperphase Sword":
                        if primary_player.get_name_player() == self.player_with_action:
                            self.action_chosen = ability
                            self.misc_target_player = player_owning_card.name_player
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                            await self.send_update_message(ability + " activated")
                            self.chosen_first_card = False
                            self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
                    elif ability == "Crown of Control":
                        if card_chosen.get_ready():
                            card_chosen.exhaust_card()
                            self.action_chosen = ability
                            self.misc_target_planet = planet_pos
                            self.misc_counter = 0
                    elif ability == "Fabricator Claw Array":
                        if primary_player.get_ready_given_pos(planet_pos, unit_pos):
                            primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
                            self.action_chosen = ability
                            self.misc_target_planet = planet_pos
                            self.misc_counter = primary_player.get_attack_given_pos(planet_pos, unit_pos)
                    elif ability == "Steed of Slaanesh":
                        if card_chosen.get_ready():
                            card_chosen.exhaust_card()
                            self.action_chosen = ability
                    elif ability == "Soul Furnace":
                        if card_chosen.get_once_per_phase_used() < 2:
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            card_chosen.set_once_per_phase_used(card_chosen.get_once_per_phase_used() + 1)
                    elif ability == "Mind Shackle Scarab":
                        if card_chosen.get_ready():
                            if primary_player.get_number() != player_owning_card.get_number():
                                if secondary_player.get_faction_given_pos(planet_pos, unit_pos) \
                                        == primary_player.enslaved_faction:
                                    card_chosen.exhaust_card()
                                    self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
                                    last_el = len(primary_player.cards_in_play[planet_pos + 1]) - 1
                                    primary_player.cards_in_play[planet_pos + 1][last_el].mind_shackle_scarab_effect = True
                            else:
                                await self.send_update_message(
                                    "Mind Shackle Scarab on own unit not supported"
                                )
                            self.action_cleanup()
                    elif ability == "The Staff of Command":
                        if card_chosen.get_ready():
                            if primary_player.get_name_player() == self.player_with_action:
                                card_chosen.exhaust_card()
                                await self.create_necrons_wheel_choice(primary_player)
                                self.action_cleanup()
                    elif ability == "Gauntlet of Fire":
                        if card_chosen.get_ready():
                            if primary_player.get_name_player() == self.player_with_action:
                                card_chosen.exhaust_card()
                                self.choices_available = ["Change Enslavement", "Deal 2 Damage"]
                                self.choice_context = "Gauntlet of Fire"
                                self.name_player_making_choices = primary_player.get_name_player()
                                self.resolving_search_box = True
                                self.action_chosen = ability
                    elif ability == "Regeneration":
                        if card_chosen.get_ready():
                            player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                            card_chosen.exhaust_card()
                            self.action_cleanup()
                    elif ability == "Eldritch Lance":
                        if card_chosen.get_ready():
                            card_chosen.exhaust_card()
                            self.action_chosen = ability
                            self.misc_target_planet = planet_pos
                    elif ability == "Heavy Venom Cannon":
                        if not card_chosen.get_once_per_phase_used():
                            self.choice_context = ability
                            self.choices_available = ["Armorbane", "Area Effect (2)"]
                            self.name_player_making_choices = primary_player.get_name_player()
                            self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
                            self.misc_target_player = player_owning_card.name_player
    elif self.action_chosen == "Even the Odds":
        if not self.chosen_first_card:
            self.misc_player_storage = player_owning_card.get_number()
            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
            await self.send_update_message(card_chosen.get_name() + " chosen")
            self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
            self.chosen_first_card = True
    elif self.action_chosen == "Breach and Clear Sacrifice":
        if card_chosen.name_owner == primary_player.get_name_player():
            player_owning_card.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
            self.action_chosen = "Breach and Clear 2"
    elif self.action_chosen == "Smuggler's Den":
        if card_chosen.name_owner == primary_player.get_name_player():
            if not player_owning_card.cards_in_play[planet_pos + 1][unit_pos].attachments[attachment_pos].check_for_a_trait("Drone"):
                primary_player.add_resources(player_owning_card.cards_in_play[planet_pos + 1][unit_pos].attachments[attachment_pos].get_cost())
                primary_player.cards.append(player_owning_card.cards_in_play[planet_pos + 1][unit_pos].attachments[attachment_pos].get_name())
                del player_owning_card.cards_in_play[planet_pos + 1][unit_pos].attachments[attachment_pos]
                self.action_cleanup()
    elif self.action_chosen == "Scribe Servo-Skull":
        if planet_pos == self.position_of_actioned_card[0]:
            if not player_owning_card.cards_in_play[planet_pos + 1][unit_pos].attachments[attachment_pos].get_ready():
                player_owning_card.cards_in_play[planet_pos + 1][unit_pos].attachments[attachment_pos].ready_card()
                self.mask_jain_zar_check_actions(primary_player, secondary_player)
                primary_player.clear_aiming_reticle_actioned_card()
                self.action_cleanup()
    elif self.action_chosen == "Accelerated Gestation":
        if card_chosen.from_magus_harid and card_chosen.name_owner == primary_player.get_name_player():
            if card_chosen.get_card_type() == "Army":
                self.misc_target_player = int(player_owning_card.get_number())
                self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
                card_name = card_chosen.get_name()
                await self.send_update_message("Accelerated Gestation is deploying a " + card_name)
                card = FindCard.find_card(card_name, self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                self.card_to_deploy = card
                self.misc_target_planet = planet_pos
                self.planet_pos_to_deploy = planet_pos
                self.traits_of_card_to_play = card.get_traits()
                self.faction_of_card_to_play = card.get_faction()
                self.name_of_card_to_play = card.get_name()
                self.discounts_applied = 0
                hand_dis = primary_player.search_hand_for_discounts(card.get_faction(), card.get_traits())
                hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits(),
                                                                planet_chosen=planet_pos)
                in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
                same_planet_dis, same_planet_auto_dis = \
                    primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
                self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
                if self.available_discounts > self.discounts_applied:
                    self.stored_mode = self.mode
                    self.mode = "DISCOUNT"
                    self.planet_aiming_reticle_position = planet_pos
                    self.planet_aiming_reticle_active = True
                else:
                    await DeployPhase.deploy_card_routine(self, name, self.planet_pos_to_deploy,
                                                          discounts=self.discounts_applied)
            else:
                await self.send_update_message("That's not an army unit.")
    elif self.action_chosen == "Subdual":
        if card_chosen.name_owner == self.name_1:
            self.p1.deck.insert(0, card_chosen.get_name())
        else:
            self.p2.deck.insert(0, card_chosen.get_name())
        del player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
        self.action_chosen = ""
        self.player_with_action = ""
        self.mode = "Normal"
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        if self.phase == "DEPLOY":
            self.player_with_deploy_turn = secondary_player.name_player
            self.number_with_deploy_turn = secondary_player.number
    elif self.action_chosen == "Air Caste Courier":
        if game_update_string[2] == primary_player.get_number():
            if not self.chosen_first_card:
                if self.position_of_actioned_card[0] == planet_pos:
                    self.chosen_first_card = True
                    self.misc_target_attachment = (planet_pos, unit_pos, attachment_pos)
                    primary_player.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
    elif self.action_chosen == "Pathfinder Shi Or'es":
        if game_update_string[2] == primary_player.get_number():
            if planet_pos == self.position_of_actioned_card[0]:
                if unit_pos == self.position_of_actioned_card[1]:
                    player_owning_card.add_card_to_discard(card_chosen.get_name())
                    del player_owning_card.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos]
                    player_owning_card.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    player_owning_card.ready_given_pos(planet_pos, unit_pos)
                    self.position_of_actioned_card = (-1, -1)
                    self.action_chosen = ""
                    self.player_with_action = ""
                    self.mode = "Normal"
                    if self.phase == "DEPLOY":
                        self.player_with_deploy_turn = secondary_player.name_player
                        self.number_with_deploy_turn = secondary_player.number
    elif self.action_chosen == "Calculated Strike":
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
        if player_being_hit.cards_in_play[planet_pos + 1][unit_pos].get_attachments()[attachment_pos].get_limited():
            player_being_hit.destroy_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            self.action_chosen = ""
            self.player_with_action = ""
            self.mode = "Normal"
            if self.phase == "DEPLOY":
                if not secondary_player.has_passed:
                    self.player_with_deploy_turn = secondary_player.name_player
                    self.number_with_deploy_turn = secondary_player.get_number()
