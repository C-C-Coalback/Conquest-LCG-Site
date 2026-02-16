import copy

from ..Phases import DeployPhase
from .. import FindCard
from .. import CardClasses


async def resolve_planet_interrupt(self, name, game_update_string, primary_player, secondary_player):
    print("planets interrupt")
    chosen_planet = int(game_update_string[1])
    current_interrupt = self.interrupts_waiting_on_resolution[0].get_interrupt_name()
    if current_interrupt == "Berzerker Warriors":
        print("check planet")
        if primary_player.valid_planets_berzerker_warriors[chosen_planet]:
            card = FindCard.find_card("Berzerker Warriors", self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            self.card_to_deploy = card
            self.card_pos_to_deploy = primary_player.aiming_reticle_coords_hand
            self.planet_pos_to_deploy = chosen_planet
            self.traits_of_card_to_play = card.get_traits()
            self.faction_of_card_to_play = card.get_faction()
            self.name_of_card_to_play = card.get_name()
            print("Trying to discount: ", card.get_name())
            self.discounts_applied = 0
            hand_dis = primary_player.search_hand_for_discounts(card.get_faction(), card.get_traits())
            hq_dis = primary_player.search_hq_for_discounts(card.get_faction(), card.get_traits())
            in_play_dis = primary_player.search_all_planets_for_discounts(card.get_traits(), card.get_faction())
            same_planet_dis, same_planet_auto_dis = \
                primary_player.search_same_planet_for_discounts(card.get_faction(), self.planet_pos_to_deploy)
            self.available_discounts = hq_dis + in_play_dis + same_planet_dis + hand_dis
            if self.available_discounts > self.discounts_applied:
                self.stored_mode = self.mode
                self.mode = "DISCOUNT"
                self.planet_aiming_reticle_position = int(game_update_string[1])
                self.planet_aiming_reticle_active = True
            else:
                await DeployPhase.deploy_card_routine(self, name, self.planet_pos_to_deploy,
                                                      discounts=self.discounts_applied)
    elif current_interrupt == "Prey on the Weak":
        if primary_player.valid_prey_on_the_weak[chosen_planet]:
            self.infest_planet(chosen_planet, primary_player)
            self.delete_interrupt()
    elif current_interrupt == "Cajivak the Hateful":
        card = self.preloaded_find_card("Cajivak the Hateful")
        if primary_player.add_card_to_planet(card, chosen_planet) != -1:
            primary_player.remove_card_name_from_hand("Cajivak the Hateful")
            if primary_player.search_hand_for_card("Cajivak the Hateful"):
                self.create_interrupt("Cajivak the Hateful", primary_player.name_player,
                                      (int(primary_player.number), -1, -1))
        self.delete_interrupt()
    elif current_interrupt == "Dodging Land Speeder":
        _, og_planet, og_pos = self.interrupts_waiting_on_resolution[0].get_position_unit_triggering()
        if abs(chosen_planet - og_planet) == 1:
            primary_player.reset_aiming_reticle_in_play(og_planet, og_pos)
            primary_player.move_unit_to_planet(og_planet, og_pos, chosen_planet)
            secondary_player.reset_aiming_reticle_in_play(self.attacker_planet, self.attacker_position)
            self.reset_combat_positions()
            self.shining_blade_active = False
            self.number_with_combat_turn = primary_player.get_number()
            self.player_with_combat_turn = primary_player.get_name_player()
            self.need_to_move_to_hq = True
            self.attack_being_resolved = False
            self.delete_interrupt()
    elif current_interrupt == "Shas'el Lyst":
        card = self.preloaded_find_card("Shas'el Lyst")
        primary_player.add_card_to_planet(card, chosen_planet)
        if "Shas'el Lyst" in primary_player.cards:
            primary_player.cards.remove("Shas'el Lyst")
        self.delete_interrupt()
    elif current_interrupt == "The Shadow Suit":
        if not self.chosen_first_card:
            if not secondary_player.search_ready_card_at_planet(chosen_planet):
                card = self.preloaded_find_card("The Shadow Suit")
                if "The Shadow Suit" in primary_player.discard:
                    primary_player.discard.remove("The Shadow Suit")
                primary_player.put_card_into_reserve(card, chosen_planet, payment=False)
                self.delete_interrupt()
            else:
                await self.send_update_message(primary_player.name_player + " is trying to put The Shadow Suit into "
                                                                            "reserve at " +
                                               self.planet_array[chosen_planet] + ". You may exhaust a " +
                                               "unit at that planet to cancel this effect.")
                self.interrupts_waiting_on_resolution[0].set_player_resolving_interrupt(secondary_player.name_player)
                self.chosen_first_card = True
                self.misc_target_planet = chosen_planet
    elif current_interrupt == "Trazyn the Infinite":
        origin_planet, origin_pos = primary_player.get_location_of_warlord()
        if chosen_planet != origin_planet:
            primary_player.remove_damage_from_pos(origin_planet, origin_pos, 999)
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            last_element_index = len(primary_player.cards_in_play[chosen_planet + 1]) - 1
            try:
                if self.recently_damaged_units:
                    self.recently_damaged_units[0] = (int(primary_player.number), chosen_planet, last_element_index)
            except:
                pass
            self.delete_interrupt()
    elif current_interrupt == "Magus Harid: Final Form":
        card = CardClasses.WarlordCard("Termagant", "", "Termagant", "Tyranids", 1, 1, 1, 1, "", 6, 6, [])
        card.aiming_reticle_color = "red"
        primary_player.add_card_to_planet(card, chosen_planet)
        self.delete_interrupt()
    elif current_interrupt == "Surrogate Host":
        origin_planet, origin_pos = primary_player.get_location_of_warlord()
        if primary_player.valid_surrogate_host[chosen_planet]:
            primary_player.move_unit_to_planet(origin_planet, origin_pos, chosen_planet)
            self.delete_interrupt()
    elif current_interrupt == "Reanimating Warriors":
        print("reanimating warriors")
        if not self.asked_if_resolve_effect:
            self.choices_available = ["Yes", "No"]
            self.choice_context = "Use Reanimating Warriors?"
            self.name_player_making_choices = name
        else:
            if self.chosen_first_card:
                origin_planet, origin_pos = self.misc_target_unit
                target_planet = int(game_update_string[1])
                if abs(origin_planet - target_planet) == 1:
                    primary_player.reset_aiming_reticle_in_play(origin_planet, origin_pos)
                    primary_player.move_unit_to_planet(origin_planet, origin_pos, target_planet)
                    self.delete_interrupt()
                    self.asked_if_resolve_effect = False
                    self.chosen_first_card = False