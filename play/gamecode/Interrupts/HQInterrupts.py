import copy

from .. import FindCard


async def resolve_hq_interrupt(self, name, game_update_string, primary_player, secondary_player):
    planet_pos = -2
    unit_pos = int(game_update_string[2])
    if game_update_string[1] == primary_player.number:
        player_owning_card = primary_player
    else:
        player_owning_card = secondary_player
    current_interrupt = self.interrupts_waiting_on_resolution[0].get_interrupt_name()
    if current_interrupt == "Vanguard Soldiers":
        if game_update_string[1] == primary_player.number:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                primary_player.ready_given_pos(planet_pos, unit_pos)
                self.delete_interrupt()
    elif current_interrupt == "No Mercy":
        if game_update_string[1] == primary_player.number:
            hq_pos = int(game_update_string[2])
            if primary_player.headquarters[hq_pos].get_is_unit() and \
                    primary_player.headquarters[hq_pos].get_unique() and \
                    primary_player.headquarters[hq_pos].get_ready():
                primary_player.exhaust_given_pos(-2, hq_pos)
                primary_player.discard_card_name_from_hand("No Mercy")
                try:
                    secondary_player.discard_card_from_hand(self.pos_shield_card)
                except:
                    pass
                self.delete_interrupt()
                await self.better_shield_card_resolution(secondary_player.name_player, ["pass-P1"],
                                                         alt_shields=False, can_no_mercy=False)
    elif current_interrupt == "Chapter Champion Varn":
        if primary_player.get_number() == game_update_string[1]:
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                _, og_pla, og_pos = self.interrupts_waiting_on_resolution[0].get_position_unit_triggering()
                primary_player.remove_damage_from_pos(og_pla, og_pos, 1)
                primary_player.headquarters[unit_pos].increase_damage(1)
                if primary_player.get_cost_given_pos(-2, unit_pos) < primary_player.headquarters[unit_pos].get_damage():
                    primary_player.sacrifice_card_in_hq(unit_pos)
                self.delete_interrupt()
    elif current_interrupt == "Cardinal Agra Decree":
        if player_owning_card.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
            player_owning_card.increase_faith_given_pos(planet_pos, unit_pos, 1)
            primary_player.draw_card()
            self.delete_interrupt()
    elif current_interrupt == "World Engine Beam":
        if not player_owning_card.headquarters[unit_pos].get_unique() or \
                player_owning_card.get_card_type_given_pos(-2, unit_pos) == "Support":
            player_owning_card.destroy_card_in_hq(unit_pos)
            self.delete_interrupt()
    elif current_interrupt == "Transcendent Blessing":
        if not self.chosen_first_card:
            if game_update_string[1] == primary_player.number:
                if primary_player.spend_faith_given_pos(planet_pos, unit_pos, 1):
                    self.chosen_first_card = True
                    await self.send_update_message("Select target for the attachment.")
        else:
            card = self.preloaded_find_card("Transcendent Blessing")
            player_getting_attachment = self.p1
            if game_update_string[1] == "2":
                player_getting_attachment = self.p2
            not_own_attachment = False
            if player_getting_attachment.number != primary_player.number:
                not_own_attachment = True
            if player_getting_attachment.attach_card(card, -2, unit_pos, not_own_attachment=not_own_attachment):
                if "Transcendent Blessing" in primary_player.discard:
                    primary_player.discard.remove("Transcendent Blessing")
                self.delete_interrupt()
    elif current_interrupt == "The Broken Sigil Sacrifice Unit":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.check_is_unit_at_pos(planet_pos, unit_pos):
                if primary_player.sacrifice_card_in_play(planet_pos, unit_pos):
                    self.delete_interrupt()
    elif current_interrupt == "Singing Spear":
        if game_update_string[1] == primary_player.get_number():
            if primary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Army":
                last_planet = self.determine_last_planet()
                primary_player.move_unit_to_planet(planet_pos, unit_pos, last_planet)
                self.delete_interrupt()
    elif current_interrupt == "Liatha Punishment":
        player_owning_card.assign_damage_to_pos(planet_pos, unit_pos, 1)
        self.delete_interrupt()
    elif current_interrupt == "Savage Parasite":
        can_continue = True
        possible_interrupts = []
        if player_owning_card.name_player == primary_player.name_player:
            possible_interrupts = secondary_player.intercept_check()
        if player_owning_card.name_player == secondary_player.name_player:
            possible_interrupts = secondary_player.interrupt_cancel_target_check(
                planet_pos, unit_pos, intercept_possible=True)
            if secondary_player.get_immune_to_enemy_card_abilities(planet_pos, unit_pos):
                can_continue = False
                await self.send_update_message("Immune to enemy card abilities.")
        if possible_interrupts and can_continue:
            can_continue = False
            await self.send_update_message("Some sort of interrupt may be used.")
            self.choices_available = possible_interrupts
            self.choices_available.insert(0, "No Interrupt")
            self.name_player_making_choices = secondary_player.name_player
            self.choice_context = "Interrupt Effect?"
            self.nullified_card_name = current_interrupt
            self.cost_card_nullified = 0
            self.nullify_string = "/".join(game_update_string)
            self.first_player_nullified = primary_player.name_player
            self.nullify_context = "Interrupt"
        if can_continue:
            player_owning_card = self.p1
            if player_owning_card.get_number() != game_update_string[1]:
                player_owning_card = self.p2
            not_own_card = True
            if player_owning_card.name_player == primary_player.name_player:
                not_own_card = False
            card = FindCard.find_card("Savage Parasite", self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if player_owning_card.attach_card(card, planet_pos, unit_pos, not_own_attachment=not_own_card):
                self.delete_interrupt()
                try:
                    primary_player.discard.remove("Savage Parasite")
                except ValueError:
                    pass
    elif current_interrupt == "Mucolid Spores":
        if game_update_string[1] == secondary_player.number:
            if secondary_player.get_card_type_given_pos(planet_pos, unit_pos) == "Support":
                can_continue = True
                is_support = True
                possible_interrupts = secondary_player.interrupt_cancel_target_check(
                    -2, unit_pos, targeting_support=is_support)
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
                    self.nullify_context = "Interrupt"
                if can_continue:
                    secondary_player.destroy_card_in_hq(unit_pos)
                    self.misc_counter += 1
                    if self.misc_counter > 1:
                        self.delete_interrupt()


