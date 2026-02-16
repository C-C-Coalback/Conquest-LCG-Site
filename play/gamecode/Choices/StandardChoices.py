import copy
import random
import os
import sys
from .. import FindCard
from ..Phases import DeployPhase, CommandPhase, CombatPhase, HeadquartersPhase, PlanetBattleAbilities
from .. import CardClasses


async def resolve_choice(self, primary_player, secondary_player, name, game_update_string):
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
            self.reset_choices_available()
            await self.complete_nullify()
            self.nullify_count = 0
    elif self.choice_context == "Use Nullify?":
        if game_update_string[1] == "0":
            self.reset_choices_available()
            self.choosing_unit_for_nullify = True
            self.name_player_using_nullify = primary_player.name_player
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
                self.create_choices(
                    self.choices_available,
                    general_imaging_format="All"
                )
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
                self.create_choices(
                    self.choices_available,
                    general_imaging_format="All"
                )
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
        self.create_choices(
            self.choices_available,
            general_imaging_format="All"
        )
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
        self.resolving_search_box = False
        self.discounts_applied = 0
        diff = 0
        if game_update_string[1] == self.misc_target_choice:
            self.discounts_applied = -2
            diff = 2
        await self.calculate_available_discounts_unit(self.misc_target_planet, card, primary_player)
        await self.calculate_automatic_discounts_unit(self.misc_target_planet, card, primary_player)
        self.reset_choices_available()
        if card.check_for_a_trait("Elite"):
            primary_player.master_warpsmith_count = 0
        if self.available_discounts > (self.discounts_applied + diff):
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
            self.choice_context = "Choose card to discard for Searing Brand"
            self.choices_available = []
            for i in range(len(primary_player.cards)):
                self.choices_available.append(primary_player.cards[i])
            self.create_choices(
                self.choices_available,
                general_imaging_format="All"
            )
            self.misc_counter = 0
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
                self.resolving_search_box = False
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
                self.reset_choices_available()
                self.resolving_search_box = False
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
        self.resolving_search_box = False
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
        self.resolving_search_box = False
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
            secondary_player.total_indirect_damage = int(enemy_choice)
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
                        self.create_choices(
                            self.choices_available,
                            general_imaging_format="All"
                        )
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
                        self.create_choices(
                            self.choices_available,
                            general_imaging_format="All"
                        )
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
        self.create_choices(
            self.choices_available,
            general_imaging_format="All"
        )
        if self.misc_counter > 1:
            if "Searing Brand" in secondary_player.cards:
                secondary_player.discard_card_name_from_hand("Searing Brand")
            secondary_player.aiming_reticle_coords_hand = None
            primary_player.create_enemy_played_event_reactions()
            self.action_cleanup()
            self.reset_choices_available()
    elif self.choice_context == "Searing Brand":
        if game_update_string[1] == "0":
            self.choices_available = primary_player.cards
            self.create_choices(
                self.choices_available,
                general_imaging_format="All"
            )
            self.misc_counter = 0
            self.choice_context = "Choose card to discard for Searing Brand"
        elif game_update_string[1] == "1":
            self.reset_choices_available()

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
        self.choices_available = ["0"]
        target_player = primary_player
        if game_update_string[1] == "1":
            target_player = secondary_player
        for i in range(len(target_player.cards)):
            if len(self.choices_available) < 4:
                self.choices_available.append(str(i + 1))
        self.choice_context = "How Many Cards? (Slake the Thirst):"
    elif self.choice_context == "Overrun: Followup Rout?":
        self.reset_choices_available()
        if game_update_string[1] == "1":
            secondary_player.create_enemy_played_event_reactions()
            self.action_cleanup()
    elif self.choice_context == "How Many Cards? (Slake the Thirst):":
        num_cards = int(chosen_choice)
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
            self.misc_target_unit = (-1, -1)
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
            self.reset_choices_available()
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
            self.reset_choices_available()
    elif self.choice_context == "Blood Axe Strategist Destination":
        self.reset_choices_available()
        self.resolving_search_box = False
        if game_update_string[1] == "0":
            num, planet_pos, unit_pos = self.positions_of_unit_triggering_reaction[0]
            primary_player.move_unit_at_planet_to_hq(planet_pos, unit_pos)
            self.delete_reaction()
    elif self.choice_context == "Use Reanimating Warriors?":
        self.reset_choices_available()
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
            primary_player.exhaust_given_pos(self.attacker_planet, self.attacker_position)
            primary_player.retreat_unit(self.attacker_planet, self.attacker_position)
            self.reset_combat_positions()
            self.number_with_combat_turn = secondary_player.get_number()
            self.player_with_combat_turn = secondary_player.get_name_player()
        elif game_update_string[1] == "1":
            self.can_retreat_warlord = False
            self.reset_choices_available()
            self.resolving_search_box = False
            self.attacker_planet = -1
            self.attacker_position = -1
            await CombatPhase.update_game_event_combat_section(
                self, primary_player.name_player, self.last_game_update_string
            )
            self.last_game_update_string = []
            self.can_retreat_warlord = True
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
        self.reset_choices_available()
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
        if chosen_choice == "Normal Deploy":
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
        self.reset_choices_available()
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
                        self.create_choices(
                            self.choices_available,
                            general_imaging_format="All"
                        )
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
                self.reset_choices_available()
                primary_player.dark_possession_active = False
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
                self.reset_choices_available()
                self.create_interrupt("No Mercy", name, (-1, -1, -1))
                self.already_resolving_interrupt = True
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
            if self.apoka or self.blackstone:
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
        primary_player.cards_recently_discarded.remove(target)
        primary_player.exhaust_card_in_hq_given_name("Holy Sepulchre")
        self.choices_available = []
        if self.holy_sepulchre_check(primary_player):
            for i in range(len(primary_player.cards_recently_discarded)):
                card = FindCard.find_card(primary_player.cards_recently_discarded[i],
                                          self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_faction() == "Space Marines" and card.get_is_unit():
                    self.choices_available.append(card.get_name())
                    self.create_choices(
                        self.choices_available,
                        general_imaging_format="All"
                    )
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
        self.reset_choices_available()

    elif self.choice_context == "Repair Bay":
        card_name = self.choices_available[int(game_update_string[1])]
        primary_player.deck.insert(0, card_name)
        primary_player.discard.remove(card_name)
        self.reset_choices_available()
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
            primary_player.cards_recently_discarded.remove(target)
            primary_player.cards_recently_destroyed.remove(target)
        except ValueError:
            pass
        self.choices_available = primary_player.stored_targets_the_emperor_protects
        self.create_choices(
            self.choices_available,
            general_imaging_format="All"
        )
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
            primary_player.cards_recently_discarded.remove(target)
            primary_player.cards_recently_destroyed.remove(target)
        except ValueError:
            pass
        primary_player.discard_card_name_from_hand("Fall Back!")
        if len(self.choices_available) > 1:
            if primary_player.search_hand_for_card("Fall Back!") and primary_player.resources > 0:
                self.create_reaction("Fall Back!", primary_player.name_player,
                                     (int(primary_player.number), -1, -1))
        self.choices_available = []
        if not self.choices_available:
            self.resolving_search_box = False
            self.reset_choices_available()
        self.delete_reaction()
    elif self.choice_context == "Choose target for Canoptek Scarab Swarm:":
        target = self.choices_available[int(game_update_string[1])]
        primary_player.cards.append(target)
        primary_player.discard.remove(target)
        self.reset_choices_available()
        self.delete_reaction()
        self.resolving_search_box = False
    elif self.choice_context == "Autarch Celachia":
        self.reset_choices_available()
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
        self.reset_choices_available()
    elif self.choice_context == "Move how much damage to Old One Eye?":
        self.reset_choices_available()
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
        self.reset_choices_available()
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
                self.create_choices(
                    self.choices_available,
                    general_imaging_format="All"
                )
                self.choice_context = "Target Made Ta Fight:"
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
                self.create_choices(
                    self.choices_available,
                    general_imaging_format="All"
                )
                self.choice_context = "Target The Emperor Protects:"
        elif game_update_string[1] == "1":
            primary_player.stored_targets_the_emperor_protects = []
            self.reset_choices_available()
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
                for i in range(len(primary_player.cards_recently_destroyed)):
                    card = FindCard.find_card(primary_player.cards_recently_destroyed[i],
                                              self.card_array, self.cards_dict,
                                              self.apoka_errata_cards, self.cards_that_have_errata)
                    if card.check_for_a_trait("Elite") and card.get_is_unit():
                        self.choices_available.append(card.get_name())
                        self.create_choices(
                            self.choices_available,
                            general_imaging_format="All"
                        )
        elif game_update_string[1] == "1":
            self.reset_choices_available()
            self.resolving_search_box = False
    elif self.choice_context == "Use Holy Sepulchre?":
        if game_update_string[1] == "0":
            self.choices_available = []
            self.choice_context = "Target Holy Sepulchre:"
            for i in range(len(primary_player.cards_recently_discarded)):
                card = FindCard.find_card(primary_player.cards_recently_discarded[i],
                                          self.card_array, self.cards_dict,
                                          self.apoka_errata_cards, self.cards_that_have_errata)
                if card.get_faction() == "Space Marines" and card.get_is_unit():
                    self.choices_available.append(card.get_name())
                    self.create_choices(
                        self.choices_available,
                        general_imaging_format="All"
                    )
        elif game_update_string[1] == "1":
            self.reset_choices_available()
            self.resolving_search_box = False
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
            self.reset_choices_available()
    elif self.choice_context == "Use Crushing Blow?":
        planet_pos, unit_pos = self.furiable_unit_position
        if game_update_string[1] == "0":
            self.reset_choices_available()
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
            self.reset_choices_available()
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
            self.reset_choices_available()
            await self.better_shield_card_resolution(name, self.last_shield_string, alt_shields=False)
        elif game_update_string[1] == "1":
            self.reset_choices_available()
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
        self.reset_choices_available()
        if game_update_string[1] == "0":
            self.shadowsun_chose_hand = True
            self.reactions_needing_resolving[0] = "Commander Shadowsun hand"
            self.location_hand_attachment_shadowsun = -1
            self.resolving_search_box = False
            await self.send_update_message("Choose card in hand")
        else:
            self.reactions_needing_resolving[0] = "Commander Shadowsun discard"
            self.shadowsun_chose_hand = False
            self.location_attachment_discard_shadowsun = -1
            self.name_player_making_choices = name
            self.resolving_search_box = False
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