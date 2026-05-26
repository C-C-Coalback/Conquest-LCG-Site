from .. import FindCard


async def update_game_event_action_discard(self, name, game_update_string):
    chosen_discard = int(game_update_string[1])
    pos_discard = int(game_update_string[2])
    if self.action_object.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    if not self.action_object.action_chosen:
        if chosen_discard == int(primary_player.number):
            ability = primary_player.discard[pos_discard]
            if ability == "Decaying Warrior Squad":
                if self.phase == "COMBAT":
                    primary_player.aiming_reticle_coords_discard = pos_discard
                    print("found a decaying warrior squad.")
                    self.action_object.action_chosen = ability
            elif ability == "Lethal Toxin Sacs":
                if self.phase == "DEPLOY":
                    if primary_player.resources > 1:
                        primary_player.aiming_reticle_coords_discard = pos_discard
                        self.action_object.action_chosen = ability
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "Hate":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    await self.send_update_message(
                        name + " is playing a " + ability + " from the discard; card removed."
                    )
                    self.action_object.action_chosen = ability
                    self.position_discard_of_card = pos_discard
                    primary_player.harbinger_of_eternity_active = True
                    del primary_player.discard[pos_discard]
                    primary_player.remove_card_from_game(ability)
            elif ability == "Awake the Sleepers":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(1):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        primary_player.discard.remove("Awake the Sleepers")
                        self.action_object.action_chosen = ability
                        primary_player.remove_card_from_game(ability)
                        primary_player.harbinger_of_eternity_active = True
                        await self.send_update_message(
                            "Press the pass button to stop shuffling any more cards in."
                        )
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "Eldritch Reaping":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    await self.send_update_message(
                        name + " is playing a " + ability + " from the discard; card removed."
                    )
                    del primary_player.discard[pos_discard]
                    self.choices_available = ["0", "1", "2", "3", "4", "5"]
                    self.choice_context = "Eldritch Reaping: Enemy Announce"
                    self.name_player_making_choices = secondary_player.name_player
                    self.misc_target_choice = ""
                    self.action_object.action_chosen = ability
            elif ability == "Drudgery":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.can_play_limited:
                        if primary_player.spend_resources(2):
                            await self.send_update_message(
                                name + " is playing a " + ability + " from the discard; card removed."
                            )
                            primary_player.can_play_limited = False
                            del primary_player.discard[pos_discard]
                            self.action_object.action_chosen = ability
                            primary_player.harbinger_of_eternity_active = True
                            primary_player.remove_card_from_game(ability)
                            self.action_object.chosen_first_card = False
                        else:
                            await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                              "Insufficient resources.")
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Already played a Limited card.")
            elif ability == "Vivisection":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(3):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        del primary_player.discard[pos_discard]
                        self.action_object.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        primary_player.remove_card_from_game(ability)
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "Recycle":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(1):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_object.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        primary_player.remove_card_from_game(ability)
                        del primary_player.discard[pos_discard]
                        self.action_object.misc_counter = 0
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "Extermination":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(5):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_object.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        primary_player.remove_card_from_game(ability)
                        del primary_player.discard[pos_discard]
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "Mechanical Enhancement":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(2):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_object.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        del primary_player.discard[pos_discard]
                        primary_player.remove_card_from_game(ability)
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "The Strength of the Enemy":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(2):
                        del primary_player.discard[pos_discard]
                        self.action_object.action_chosen = ability
                        self.action_object.chosen_first_card = False
                        await self.send_update_message("Please choose an enemy unit first.")
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                          "Insufficient resources.")
            elif ability == "Reanimation Protocol":
                if not primary_player.used_reanimation_protocol:
                    if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_object.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        del primary_player.discard[pos_discard]
                        primary_player.used_reanimation_protocol = True
                        primary_player.remove_card_from_game(ability)
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Cannot use ability",
                                                      "Already played a Reanimation Protocol.")
    elif self.action_object.action_chosen == "Drudgery":
        if not self.action_object.chosen_first_card:
            if chosen_discard == int(primary_player.number):
                card = self.preloaded_find_card(primary_player.discard[pos_discard])
                if card.get_cost() < 4:
                    if card.get_faction() != "Necrons" and card.get_card_type() == "Army":
                        self.action_object.chosen_first_card = True
                        self.misc_target_choice = card.get_name()
                        primary_player.aiming_reticle_coords_discard = pos_discard
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                          "Card is not a non-Necrons unit.")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Cost of the card is too great.")
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Drudgery only targets our discard pile.")
    elif self.action_object.action_chosen == "Eternity Gate":
        if chosen_discard == int(primary_player.number):
            primary_player.move_to_top_of_discard(pos_discard)
        else:
            secondary_player.move_to_top_of_discard(pos_discard)
        primary_player.reset_aiming_reticle_in_play(self.action_object.position_of_actioned_card[0],
                                                    self.action_object.position_of_actioned_card[1])
        self.action_cleanup()
    elif self.action_object.action_chosen == "Awake the Sleepers":
        if chosen_discard == int(primary_player.number):
            card = primary_player.get_card_in_discard(pos_discard)
            if card.get_faction() == "Necrons":
                primary_player.shuffle_card_in_discard_into_deck(pos_discard)
    elif self.action_object.action_chosen == "Soul Seizure":
        if not self.action_object.chosen_first_card:
            if chosen_discard == int(secondary_player.number):
                card = self.preloaded_find_card(secondary_player.discard[pos_discard])
                if card.get_card_type() == "Army":
                    if card.get_cost(primary_player.urien_relevant) <= primary_player.soul_seizure_value:
                        self.action_object.chosen_first_card = True
                        secondary_player.aiming_reticle_coords_discard = pos_discard
                        self.anrakyr_unit_position = pos_discard
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                          "Cost of the card is too great.")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Card is not a unit.")
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Soul Seizure targets the enemy discard.")
    elif self.action_object.action_chosen == "Merciless Reclamation":
        if self.action_object.chosen_first_card and not self.action_object.chosen_second_card:
            if chosen_discard == int(primary_player.number):
                card = self.preloaded_find_card(primary_player.discard[pos_discard])
                if card.get_card_type() == "Army" and card.get_faction() == "Necrons":
                    if card.check_for_a_trait("Soldier", primary_player.etekh_trait) or \
                            card.check_for_a_trait("Warrior", primary_player.etekh_trait):
                        if card.get_cost() == self.action_object.misc_counter + 1:
                            self.action_object.chosen_second_card = True
                            primary_player.aiming_reticle_coords_discard = pos_discard
                            self.anrakyr_unit_position = pos_discard
    elif self.action_object.action_chosen == "Triumvirate of Ynnead":
        if not self.action_object.chosen_first_card:
            if chosen_discard == int(primary_player.number):
                card = self.preloaded_find_card(primary_player.discard[pos_discard])
                if self.trium_tracker[0] != card.get_name():
                    if not card.check_for_a_trait("Elite"):
                        if card.get_card_type() == "Army":
                            self.card_to_deploy = card
                            self.action_object.chosen_first_card = True
                            primary_player.aiming_reticle_coords_discard = pos_discard
                        else:
                            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                              "Card is not a unit.")
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                          "Elite units cannot be deployed with Triumvirate of Ynnead.")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Triumvirate of Ynnead must deploy cards of different names.")
    elif self.action_object.action_chosen == "Spore Burst":
        if not self.action_object.chosen_first_card:
            if chosen_discard == int(primary_player.number):
                card = self.preloaded_find_card(primary_player.discard[pos_discard])
                if card.get_card_type() == "Army":
                    if card.get_cost() < 4:
                        self.action_object.chosen_first_card = True
                        primary_player.aiming_reticle_coords_discard = pos_discard
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                          "Cost of the card is too great.")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Card is not a unit.")
    elif self.action_object.action_chosen == "Evolutionary Adaptation":
        if chosen_discard == int(secondary_player.get_number()):
            if not self.action_object.chosen_first_card:
                choices = []
                card = self.preloaded_find_card(secondary_player.discard[pos_discard])
                if card.get_card_type() == "Army":
                    if card.by_base_brutal:
                        choices.append("Brutal")
                    if card.by_base_flying:
                        choices.append("Flying")
                    if card.by_base_armorbane:
                        choices.append("Armorbane")
                    if card.by_base_mobile:
                        choices.append("Mobile")
                    if card.by_base_area_effect > 0:
                        choices.append("Area Effect")
                        self.stored_area_effect_value = self.cards_in_play[planet_pos + 1][
                            unit_pos].by_base_area_effect
                    if card.by_base_ranged:
                        choices.append("Ranged")
                    if choices:
                        if len(choices) == 1:
                            self.misc_target_choice = choices[0]
                            await self.send_update_message(
                                "Only one keyword: skipping asking which one to take."
                            )
                        else:
                            self.choices_available = choices
                            self.name_player_making_choices = primary_player.name_player
                            self.choice_context = "Keyword copied from Evolutionary Adaptation"
                        self.action_object.chosen_first_card = True
                        secondary_player.remove_card_from_game(card.get_name())
                        del secondary_player.discard[pos_discard]
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                          "Target has no keywords to copy.")
    elif self.action_object.action_chosen == "Imotekh the Stormlord":
        if not self.action_object.chosen_first_card:
            if chosen_discard == int(primary_player.number):
                card = self.preloaded_find_card(primary_player.discard[pos_discard])
                if card.get_card_type() == "Army":
                    if not card.get_unique():
                        if not card.check_for_a_trait("Elite"):
                            self.action_object.misc_target_player = card.get_ability()
                            self.action_object.chosen_first_card = True
                            primary_player.remove_card_from_game(card.get_name())
                            del primary_player.discard[pos_discard]
                            await self.send_update_message("Granting the " + card.get_ability() + "'s text box.")
                        else:
                            await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                              "Imotekh the Stormlord cannot swap Elite cards.")
                    else:
                        await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                          "Imotekh the Stormlord cannot swap Unique cards.")
                else:
                    await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                      "Card is not a unit (Imotekh the Stormlord only supports units at this time).")
    elif self.action_object.action_chosen == "Particle Whip":
        if chosen_discard == int(primary_player.number):
            card = FindCard.find_card(primary_player.discard[pos_discard], self.card_array, self.cards_dict,
                                      self.apoka_errata_cards, self.cards_that_have_errata)
            if card.get_is_unit():
                primary_player.shuffle_card_in_discard_into_deck(pos_discard)
                self.action_object.misc_counter += 1
            else:
                await self.send_mistarget_message(primary_player.name_player, "Invalid Target",
                                                  "Card is not a unit.")
