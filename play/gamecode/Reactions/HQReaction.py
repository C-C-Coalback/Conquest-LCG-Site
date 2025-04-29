from .. import FindCard


async def resolve_hq_reaction(self, name, game_update_string, primary_player, secondary_player):
    unit_pos = int(game_update_string[2])
    if int(primary_player.get_number()) == int(self.positions_of_unit_triggering_reaction[0][0]):
        if self.reactions_needing_resolving[0] == "Power from Pain":
            if primary_player.headquarters[unit_pos].get_card_type() == "Army":
                primary_player.sacrifice_card_in_hq(unit_pos)
                self.delete_reaction()
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
                self.delete_reaction()
                await primary_player.send_hq()
        elif self.reactions_needing_resolving[0] == "Obedience":
            if game_update_string[1] == primary_player.number:
                if primary_player.headquarters[unit_pos].get_is_unit():
                    if primary_player.get_faction_given_pos(-2, unit_pos) != "Necrons":
                        self.chosen_first_card = True
                        self.misc_target_unit = (-2, unit_pos)
                        primary_player.set_aiming_reticle_in_play(-2, unit_pos, "blue")
                        await primary_player.send_hq()
        elif self.reactions_needing_resolving[0] == "Seraphim Superior Allegra":
            if game_update_string[1] == primary_player.number:
                if primary_player.get_card_type_given_pos(-2, unit_pos) == "Support":
                    primary_player.ready_given_pos(-2, unit_pos)
                    await primary_player.send_hq()
                    self.delete_reaction()
        elif self.reactions_needing_resolving[0] == "Alaitoc Shrine":
            if not self.alaitoc_shrine_activated:
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
                        self.delete_reaction()
                    await self.send_info_box()
        elif self.reactions_needing_resolving[0] == "Beasthunter Wyches":
            if primary_player.get_ability_given_pos(-2, unit_pos) == "Beasthunter Wyches":
                if primary_player.headquarters[unit_pos].get_reaction_available():
                    if primary_player.spend_resources(1):
                        primary_player.headquarters[unit_pos].set_reaction_available(False)
                        primary_player.summon_token_at_hq("Khymera", 1)
                        self.delete_reaction()
                        await self.send_info_box()
                        await primary_player.send_hq()
                        await primary_player.send_resources()