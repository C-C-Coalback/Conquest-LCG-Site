from .. import FindCard


async def resolve_hq_reaction(self, name, game_update_string, primary_player, secondary_player):
    unit_pos = int(game_update_string[2])
    current_reaction = self.reactions_needing_resolving[0]
    if int(primary_player.get_number()) == int(self.positions_of_unit_triggering_reaction[0][0]):
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
                    self.delete_reaction()
            elif game_update_string[1] == secondary_player.number:
                if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                    secondary_player.exhaust_given_pos(-2, unit_pos, card_effect=True)
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Seraphim Superior Allegra":
            if game_update_string[1] == primary_player.number:
                if primary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                    primary_player.ready_given_pos(-2, unit_pos)
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
        elif self.reactions_needing_resolving[0] == "Deathskull Lootas":
            if game_update_string[1] == secondary_player.get_number():
                if secondary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                    secondary_player.destroy_card_in_hq(unit_pos)
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
                            secondary_player.assign_damage_to_pos(-2, unit_pos, 2)
                            self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Beasthunter Wyches":
            if primary_player.get_ability_given_pos(-2, unit_pos) == "Beasthunter Wyches":
                if primary_player.headquarters[unit_pos].get_reaction_available():
                    if primary_player.spend_resources(1):
                        primary_player.headquarters[unit_pos].set_reaction_available(False)
                        primary_player.summon_token_at_hq("Khymera", 1)
                        self.delete_reaction()
