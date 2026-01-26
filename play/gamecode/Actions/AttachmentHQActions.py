async def update_game_event_action_attachment_hq(self, name, game_update_string):
    if name == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    planet_pos = -2
    unit_pos = int(game_update_string[3])
    attachment_pos = int(game_update_string[4])
    if game_update_string[2] == "1":
        card_chosen = self.p1.headquarters[unit_pos].get_attachments()[attachment_pos]
        player_owning_card = self.p1
    else:
        card_chosen = self.p2.headquarters[unit_pos].get_attachments()[attachment_pos]
        player_owning_card = self.p2
    if not self.action_chosen:
        print("action not chosen")
        if card_chosen.get_has_action_while_in_play() and not card_chosen.from_magus_harid:
            if card_chosen.get_allowed_phases_while_in_play() == self.phase or \
                    card_chosen.get_allowed_phases_while_in_play() == "ALL":
                ability = card_chosen.get_ability()
                self.position_of_actioned_card = (planet_pos, unit_pos)
                if ability == "Command-link Drone":
                    if primary_player.get_name_player() == self.player_with_action:
                        if primary_player.spend_resources(1):
                            self.action_chosen = ability
                            self.misc_target_player = player_owning_card.name_player
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                            await self.send_update_message(ability + " activated")
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
                elif ability == "Steed of Slaanesh":
                    if card_chosen.get_ready():
                        card_chosen.exhaust_card()
                        self.action_chosen = ability
                elif ability == "Riptide Battlesuit":
                    if card_chosen.get_ready():
                        card_chosen.exhaust_card()
                        player_owning_card.increase_health_of_unit_at_pos(planet_pos, unit_pos, 2, "EOP")
                        self.action_cleanup()
                elif ability == "Searchlight":
                    if primary_player.get_name_player() == player_owning_card.name_player:
                        warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                        if primary_player.get_ready_given_pos(warlord_pla, warlord_pos):
                            primary_player.exhaust_given_pos(warlord_pla, warlord_pos)
                            self.action_chosen = ability
                            player_owning_card.set_aiming_reticle_in_play(planet_pos, unit_pos, "blue")
                            self.position_of_actioned_card = (planet_pos, unit_pos)
                            await self.send_update_message(ability + " activated")
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
                elif ability == "Missile Pod":
                    if primary_player.get_name_player() == self.player_with_action:
                        player_owning_card.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        self.position_of_actioned_card = (planet_pos, unit_pos)
                        self.position_of_selected_attachment = (planet_pos, unit_pos, attachment_pos)
                        self.action_chosen = ability
                        await self.send_update_message(ability + " activated")
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
                            await self.create_necrons_wheel_choice(primary_player)
                            self.action_cleanup()
                elif ability == "Blight Grenades":
                    if primary_player.get_name_player() == self.player_with_action:
                        primary_player.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                        primary_player.headquarters[unit_pos].area_effect_eocr += 2
                        self.action_cleanup()
                elif ability == "Terminator Armour":
                    if not card_chosen.get_once_per_game_used():
                        if primary_player.get_name_player() == self.player_with_action:
                            card_chosen.set_once_per_game_used(True)
                            self.misc_target_unit = (-2, unit_pos)
                            primary_player.set_aiming_reticle_in_play(-2, unit_pos)
                            self.action_chosen = ability
                elif ability == "Memories of Fallen Comrades":
                    if player_owning_card.name_player == primary_player.get_name_player():
                        if card_chosen.get_ready():
                            card_chosen.exhaust_card()
                            self.action_chosen = ability
                            self.misc_counter = 0
                            self.misc_target_unit = (-1, -1)
                elif ability == "Ymgarl Factor":
                    if primary_player.spend_resources(1):
                        self.action_chosen = ability
                        self.misc_target_unit = (planet_pos, unit_pos)
                        self.choices_available = ["+2 ATK", "+2 HP"]
                        self.choice_context = "Ymgarl Factor gains:"
                        self.name_player_making_choices = primary_player.get_name_player()
                        self.resolving_search_box = True
                elif ability == "Cenobyte Servitor":
                    primary_player.sacrifice_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
                    self.chosen_first_card = False
                    self.action_chosen = ability
                elif ability == "Mind Shackle Scarab":
                    if card_chosen.get_ready():
                        if primary_player.get_name_player() == self.player_with_action:
                            if primary_player.get_number() != player_owning_card.get_number():
                                if secondary_player.get_faction_given_pos(planet_pos, unit_pos) \
                                        == primary_player.enslaved_faction:
                                    card_chosen.exhaust_card()
                                    self.take_control_of_card(primary_player, secondary_player, planet_pos, unit_pos)
                                    last_el = len(primary_player.headquarters) - 1
                                    primary_player.headquarters[last_el].mind_shackle_scarab_effect = True
                            else:
                                await self.game_sockets[0].receive_game_update(
                                    "Mind Shackle Scarab on own unit not supported"
                                )
                            self.action_cleanup()
                elif ability == "Regeneration":
                    if card_chosen.get_ready():
                        if primary_player.get_name_player() == self.player_with_action:
                            player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                            card_chosen.exhaust_card()
                            self.action_cleanup()
                elif ability == "Pulsating Carapace":
                    if card_chosen.get_ready():
                        if primary_player.get_name_player() == self.player_with_action:
                            player_owning_card.remove_damage_from_pos(planet_pos, unit_pos, 2, healing=True)
                            card_chosen.exhaust_card()
                            self.action_cleanup()
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
    elif self.action_chosen == "Smuggler's Den":
        if card_chosen.name_owner == primary_player.get_name_player():
            if not player_owning_card.headquarters[unit_pos].attachments[attachment_pos].check_for_a_trait("Drone"):
                primary_player.add_resources(player_owning_card.headquarters[unit_pos].attachments[attachment_pos].get_cost())
                primary_player.cards.append(player_owning_card.headquarters[unit_pos].attachments[attachment_pos].get_name())
                del player_owning_card.headquarters[unit_pos].attachments[attachment_pos]
                self.action_cleanup()
    elif self.action_chosen == "Fire Caste Cadre":
        if self.position_of_actioned_card[0] == planet_pos and self.position_of_actioned_card[1] == unit_pos:
            if card_chosen.name_owner == primary_player.get_name_player():
                if game_update_string[2] == primary_player.get_number():
                    primary_player.cards.append(card_chosen.get_name())
                    del player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos]
                    primary_player.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Subdual":
        if card_chosen.name_owner == self.name_1:
            self.p1.deck.insert(0, card_chosen.get_name())
        else:
            self.p2.deck.insert(0, card_chosen.get_name())
        del player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos]
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        primary_player.aiming_reticle_coords_hand = None
        self.action_cleanup()
    elif self.action_chosen == "Pathfinder Shi Or'es":
        if game_update_string[2] == primary_player.get_number():
            if planet_pos == self.position_of_actioned_card[0]:
                if unit_pos == self.position_of_actioned_card[1]:
                    player_owning_card.add_card_to_discard(card_chosen.get_name())
                    del player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos]
                    player_owning_card.reset_aiming_reticle_in_play(planet_pos, unit_pos)
                    player_owning_card.ready_given_pos(planet_pos, unit_pos)
                    self.action_cleanup()
    elif self.action_chosen == "Calculated Strike":
        if player_owning_card.headquarters[unit_pos].get_attachments()[attachment_pos].get_limited():
            player_owning_card.destroy_attachment_from_pos(planet_pos, unit_pos, attachment_pos)
            primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
            primary_player.aiming_reticle_coords_hand = None
            self.action_cleanup()
