from .. import FindCard


async def update_game_event_action_discard(self, name, game_update_string):
    chosen_discard = int(game_update_string[1])
    pos_discard = int(game_update_string[2])
    if self.player_with_action == self.name_1:
        primary_player = self.p1
        secondary_player = self.p2
    else:
        primary_player = self.p2
        secondary_player = self.p1
    ability = primary_player.discard[pos_discard]
    if not self.action_chosen:
        if chosen_discard == int(primary_player.number):
            if ability == "Decaying Warrior Squad":
                if self.phase == "COMBAT":
                    primary_player.aiming_reticle_coords_discard = pos_discard
                    print("found a decaying warrior squad.")
                    self.action_chosen = ability
            elif ability == "Hate":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    await self.send_update_message(
                        name + " is playing a " + ability + " from the discard; card removed."
                    )
                    self.action_chosen = ability
                    self.position_discard_of_card = pos_discard
                    primary_player.harbinger_of_eternity_active = True
            elif ability == "Awake the Sleepers":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(1):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        primary_player.discard.remove("Awake the Sleepers")
                        self.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        self.name_player_making_choices = primary_player.name_player
                        self.choices_available = []
                        self.choice_context = "Awake the Sleepers"
                        for i in range(len(primary_player.discard)):
                            card = FindCard.find_card(primary_player.discard[i], self.card_array)
                            if card.get_faction() == "Necrons":
                                self.choices_available.append(card.get_name())
                        self.resolving_search_box = True
                        if not self.choices_available:
                            self.choice_context = ""
                            self.name_player_making_choices = ""
                            self.resolving_search_box = False
                            await self.send_update_message(
                                "No valid targets for Awake the Sleepers"
                            )
                            self.action_cleanup()
                        else:
                            await self.send_update_message(
                                "Press the pass button to stop shuffling any more cards in."
                            )
            elif ability == "Drudgery":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.can_play_limited:
                        if primary_player.spend_resources(2):
                            await self.send_update_message(
                                name + " is playing a " + ability + " from the discard; card removed."
                            )
                            primary_player.can_play_limited = False
                            del primary_player.discard[pos_discard]
                            self.action_chosen = ability
                            primary_player.harbinger_of_eternity_active = True
                            self.name_player_making_choices = primary_player.name_player
                            self.choices_available = []
                            self.choice_context = ability
                            for i in range(len(primary_player.discard)):
                                card = FindCard.find_card(primary_player.discard[i], self.card_array)
                                if card.get_is_unit() and card.get_faction() != "Necrons" and card.get_cost() < 4:
                                    self.choices_available.append(card.get_name())
                            self.resolving_search_box = True
                            if not self.choices_available:
                                self.choice_context = ""
                                self.name_player_making_choices = ""
                                self.resolving_search_box = False
                                await self.send_update_message(
                                    "No valid targets for Drudgery"
                                )
                                self.action_cleanup()
            elif ability == "Recycle":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(1):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        del primary_player.discard[pos_discard]
                        self.misc_counter = 0
            elif ability == "Extermination":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(5):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        del primary_player.discard[pos_discard]
            elif ability == "Mechanical Enhancement":
                if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                    if primary_player.spend_resources(2):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        del primary_player.discard[pos_discard]
            elif ability == "Reanimation Protocol":
                if not primary_player.used_reanimation_protocol:
                    if primary_player.search_for_card_everywhere("Harbinger of Eternity"):
                        await self.send_update_message(
                            name + " is playing a " + ability + " from the discard; card removed."
                        )
                        self.action_chosen = ability
                        primary_player.harbinger_of_eternity_active = True
                        del primary_player.discard[pos_discard]
                        primary_player.used_reanimation_protocol = True
    elif self.action_chosen == "Eternity Gate":
        if chosen_discard == int(primary_player.number):
            primary_player.move_to_top_of_discard(pos_discard)
        else:
            secondary_player.move_to_top_of_discard(pos_discard)
        primary_player.reset_aiming_reticle_in_play(self.position_of_actioned_card[0],
                                                    self.position_of_actioned_card[1])
        self.action_cleanup()
    elif self.action_chosen == "Particle Whip":
        if chosen_discard == int(primary_player.number):
            card = FindCard.find_card(primary_player.discard[pos_discard], self.card_array)
            if card.get_is_unit():
                primary_player.shuffle_card_in_discard_into_deck(pos_discard)
                self.misc_counter += 1
