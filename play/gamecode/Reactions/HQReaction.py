from .. import FindCard


async def resolve_hq_reaction(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = -2
    unit_pos = int(game_update_string[2])
    current_reaction = self.reactions_needing_resolving[0]
    player_owning_card = self.p1
    if game_update_string[1] == "2":
        player_owning_card = self.p2
    print('hq reaction')
    if self.reactions_needing_resolving[0] == "Power from Pain":
        if primary_player.headquarters[unit_pos].get_card_type() == "Army":
            primary_player.sacrifice_card_in_hq(unit_pos)
            self.delete_reaction()
            await secondary_player.dark_eldar_event_played()
            secondary_player.torture_event_played("Power from Pain")
    elif self.reactions_needing_resolving[0] == "Nullify":
        if primary_player.valid_nullify_unit(-2, unit_pos):
            primary_player.exhaust_given_pos(-2, unit_pos)
            if primary_player.urien_relevant:
                primary_player.spend_resources(1)
            self.nullify_count += 1
            primary_player.num_nullify_played += 1
            if secondary_player.nullify_check():
                self.choices_available = ["Yes", "No"]
                self.name_player_making_choices = secondary_player.name_player
                self.choice_context = "Use Nullify?"
                await self.send_update_message(secondary_player.name_player +
                                               " counter nullify offered.")
            else:
                await self.complete_nullify()
            self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Obedience":
        if game_update_string[1] == primary_player.number:
            if primary_player.headquarters[unit_pos].get_is_unit():
                if primary_player.get_faction_given_pos(-2, unit_pos) != "Necrons":
                    self.chosen_first_card = True
                    self.misc_target_unit = (-2, unit_pos)
                    primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
    elif self.reactions_needing_resolving[0] == "Shrieking Basilisk":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                primary_player.exhaust_given_pos(-2, unit_pos, card_effect=True)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
        elif game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                secondary_player.exhaust_given_pos(-2, unit_pos, card_effect=True)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Seraphim Superior Allegra":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                primary_player.ready_given_pos(-2, unit_pos)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Alaitoc Shrine":
        if not self.alaitoc_shrine_activated:
            if primary_player.get_ability_given_pos(-2, unit_pos) == "Alaitoc Shrine":
                if primary_player.get_ready_given_pos(-2, unit_pos):
                    primary_player.exhaust_given_pos(-2, unit_pos)
                    self.alaitoc_shrine_activated = True
    elif self.reactions_needing_resolving[0] == "Cato's Stronghold":
        if not self.cato_stronghold_activated:
            if primary_player.get_ability_given_pos(-2, unit_pos) == "Cato's Stronghold":
                if primary_player.get_ready_given_pos(-2, unit_pos):
                    primary_player.exhaust_given_pos(-2, unit_pos)
                    self.cato_stronghold_activated = True
    elif current_reaction == "Burst Forth":
        card_type = primary_player.get_card_type_given_pos(planet_pos, unit_pos)
        if card_type == "Warlord" or card_type == "Synapse":
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.misc_target_planet)
            self.delete_reaction()
    elif current_reaction == "Tunneling Mawloc":
        card_type = primary_player.get_card_type_given_pos(planet_pos, unit_pos)
        if card_type == "Army":
            if not self.chosen_first_card:
                primary_player.move_unit_to_planet(planet_pos, unit_pos, self.misc_target_planet)
                self.infest_planet(self.misc_target_planet, primary_player)
                self.delete_reaction()
        elif card_type == "Token":
            primary_player.move_unit_to_planet(planet_pos, unit_pos, self.misc_target_planet)
            self.misc_counter += 1
            self.chosen_first_card = True
            if self.misc_counter > 3:
                self.infest_planet(self.misc_target_planet, primary_player)
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Murder Cogitator":
        if primary_player.get_ability_given_pos(-2, unit_pos) == "Murder Cogitator":
            if primary_player.headquarters[unit_pos].get_ready():
                primary_player.exhaust_given_pos(-2, unit_pos)
                await primary_player.reveal_top_card_deck()
                card = primary_player.get_top_card_deck()
                if card is not None:
                    if card.get_is_unit() and card.get_faction() == "Chaos":
                        await self.send_update_message("Card is drawn")
                        primary_player.draw_card()
                    else:
                        await self.send_update_message("Card is not drawn")
                more = primary_player.search_card_in_hq("Murder Cogitator", ready_relevant=True)
                if not more:
                    self.delete_reaction()
    elif current_reaction == "Devoted Hospitaller":
        if not self.chosen_first_card:
            if primary_player.get_number() == game_update_string[1]:
                primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                self.misc_counter += 1
                if self.misc_counter > 1:
                    self.chosen_first_card = True
    elif current_reaction == "Patron Saint":
        if game_update_string[1] == primary_player.get_number():
            if not self.chosen_first_card:
                if (primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army" and
                    primary_player.get_faction_given_pos(planet_pos, unit_pos) == "Astra Militarum") or \
                        primary_player.check_for_trait_given_pos(planet_pos, unit_pos, "Ecclesiarchy"):
                    before_damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                    primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
                    after_damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
                    if after_damage < before_damage:
                        self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        self.chosen_first_card = True
                        self.misc_counter = 3
                        await self.send_update_message("Now place 3 faith.")
            else:
                if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                    primary_player.increase_faith_given_pos(planet_pos, unit_pos, 1)
                    self.misc_counter = self.misc_counter - 1
                    if self.misc_counter < 1:
                        self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                        self.delete_reaction()
    elif current_reaction == "Wrathful Retribution":
        if player_owning_card.get_faith_given_pos(planet_pos, unit_pos) > 0:
            if not player_owning_card.check_for_trait_given_pos(planet_pos, unit_pos, "Elite"):
                player_owning_card.ready_given_pos(planet_pos, unit_pos)
                self.delete_reaction()
    elif current_reaction == "Zealous Cantus":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
            self.mask_jain_zar_check_reactions(primary_player, secondary_player)
            self.delete_reaction()
    elif current_reaction == "Vengeful Seraphim":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                num, pla, pos = self.positions_of_unit_triggering_reaction[0]
                primary_player.ready_given_pos(pla, pos)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
    elif current_reaction == "Saint Erika":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                self.chosen_first_card = True
                await self.send_update_message("Select card in discard to bring back.")
    elif current_reaction == "Hydra Flak Tank":
        if player_owning_card.cards_in_play[planet_pos + 1][unit_pos].valid_defense_battery_target:
            primary_player.set_once_per_phase_used_given_pos(planet_pos, unit_pos, True)
            damage = 1
            if player_owning_card.get_flying_given_pos(planet_pos, unit_pos):
                damage = 2
            elif player_owning_card.get_mobile_given_pos(planet_pos, unit_pos):
                damage = 2
            player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, damage, rickety_warbuggy=True)
            self.delete_reaction()
    elif current_reaction == "Magus Harid":
        if self.chosen_first_card:
            if game_update_string[1] == secondary_player.number:
                if secondary_player.headquarters[unit_pos].valid_target_magus_harid:
                    card = primary_player.get_card_in_hand(self.misc_player_storage)
                    secondary_player.headquarters[unit_pos].add_attachment(card, name_owner=primary_player.name_player,
                                                                           is_magus=True)
                    primary_player.remove_card_from_hand(self.misc_player_storage)
                    primary_player.draw_card()
                    primary_player.aiming_reticle_coords_hand = None
                    warlord_pla, warlord_pos = primary_player.get_location_of_warlord()
                    primary_player.set_once_per_round_used_given_pos(warlord_pla, warlord_pos, True)
                    self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                    self.delete_reaction()
    elif current_reaction == "Vow of Honor":
        if primary_player.headquarters[unit_pos].valid_target_vow_of_honor:
            primary_player.increase_attack_of_unit_at_pos(-2, unit_pos, 3, expiration="NEXT")
            self.delete_reaction()
            target_name = primary_player.get_name_given_pos(-2, unit_pos)
            await self.send_update_message(target_name + " got +3 ATK from Vow of Honor")
            if primary_player.resources > 0 and primary_player.search_hand_for_card("Vow of Honor"):
                self.create_reaction("Vow of Honor", primary_player.name_player,
                                     (int(primary_player.number), -1, -1))
    elif self.reactions_needing_resolving[0] == "Imperial Fists Devastators":
        if game_update_string[1] == "1":
            player_being_hit = self.p1
        else:
            player_being_hit = self.p2
        if player_being_hit.get_card_type_given_pos(-2, unit_pos) == "Support":
            if player_being_hit.check_for_trait_given_pos(-2, unit_pos, "Location"):
                player_being_hit.destroy_card_in_hq(unit_pos)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Tomb Blade Squadron":
        if not self.chosen_first_card and not self.chosen_second_card:
            if game_update_string[1] == primary_player.get_number():
                if primary_player.headquarters[unit_pos].get_ability() == "Tomb Blade Squadron":
                    if not primary_player.headquarters[unit_pos].misc_ability_used:
                        primary_player.headquarters[unit_pos].misc_ability_used = True
                        self.chosen_first_card = True
                        self.misc_target_unit = (-2, unit_pos)
                        primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
    elif self.reactions_needing_resolving[0] == "Defense Battery":
        if self.chosen_first_card:
            if game_update_string[1] == secondary_player.get_number():
                if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
                    if secondary_player.headquarters[unit_pos].valid_defense_battery_target:
                        secondary_player.assign_damage_to_pos(-2, unit_pos, 2, by_enemy_unit=False)
                        self.delete_reaction()
    elif self.reactions_needing_resolving[0] == "Beasthunter Wyches":
        if primary_player.get_ability_given_pos(-2, unit_pos) == "Beasthunter Wyches":
            if primary_player.headquarters[unit_pos].get_reaction_available():
                if primary_player.spend_resources(1):
                    primary_player.headquarters[unit_pos].set_reaction_available(False)
                    primary_player.summon_token_at_hq("Khymera", 1)
                    self.delete_reaction()
    elif current_reaction == "Run Down":
        print('run down')
        if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Army":
            print('army')
            if not secondary_player.check_for_trait_given_pos(-2, unit_pos, "Elite"):
                print('not elite')
                if not secondary_player.get_immune_to_enemy_events(-2, unit_pos):
                    dest = self.positions_of_unit_triggering_reaction[0][1]
                    secondary_player.move_unit_to_planet(-2, unit_pos, dest)
                    self.delete_reaction()
    elif current_reaction == "Deathskull Lootas":
        if game_update_string[1] == secondary_player.get_number():
            if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                secondary_player.destroy_card_in_hq(unit_pos)
                self.mask_jain_zar_check_reactions(primary_player, secondary_player)
                self.delete_reaction()
    elif current_reaction == "Emergent Cultists":
        if game_update_string[1] == secondary_player.get_number():
            if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                can_continue = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=True)
                if possible_interrupts:
                    can_continue = False
                    await self.send_update_message("Some sort of interrupt may be used.")
                    self.choices_available = possible_interrupts
                    self.choices_available.insert(0, "No Interrupt")
                    self.name_player_making_choices = secondary_player.name_player
                    self.choice_context = "Interrupt Effect?"
                    self.nullified_card_name = current_reaction
                    self.cost_card_nullified = 0
                    self.nullify_string = "/".join(game_update_string)
                    self.first_player_nullified = primary_player.name_player
                    self.nullify_context = "In Play Reaction"
                if can_continue:
                    secondary_player.exhaust_given_pos(-2, unit_pos)
                    self.delete_reaction()
