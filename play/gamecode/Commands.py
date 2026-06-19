import os
import datetime
import random


async def resolve_command(self, name, message):
    game_relevant_string = name + "|||" + "/".join(message)
    self.game_events_as_mono_string += game_relevant_string + "\n"
    if message[1] != "loaddeck":
        await self.send_update_message(name + " is using a command: " + "/".join(message))
    if (message[1] == "loaddeck" or message[1] == "LOADDECK") and len(message) > 2:
        deck_name = message[2]
        print(deck_name)
        path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + name + "/" + deck_name
        print(path_to_player_decks)
        if os.path.exists(path_to_player_decks):
            with open(path_to_player_decks, 'r') as f:
                deck_content = f.read()
                if self.name_1 == name:
                    if not self.p1.deck_loaded:
                        await self.p1.setup_player(deck_content, self.planet_array)
                elif self.name_2 == name:
                    if not self.p2.deck_loaded:
                        await self.p2.setup_player(deck_content, self.planet_array)
    elif message[1] == "loadrandom":
        decks_lists = os.listdir(os.getcwd() + "/decks/DeckStorage/" + name)
        if decks_lists:
            random.shuffle(decks_lists)
            path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + name + "/" + decks_lists[0]
            if os.path.exists(path_to_player_decks):
                with open(path_to_player_decks, 'r') as f:
                    deck_content = f.read()
                    if self.name_1 == name:
                        if not self.p1.deck_loaded:
                            await self.p1.setup_player(deck_content, self.planet_array)
                    elif self.name_2 == name:
                        if not self.p2.deck_loaded:
                            await self.p2.setup_player(deck_content, self.planet_array)
    elif message[1] == "loaddeckbot" and len(message) > 3:
        name_player = message[2]
        deck_name = message[3]
        print(deck_name)
        path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + name_player + "/" + deck_name
        print(path_to_player_decks)
        if os.path.exists(path_to_player_decks):
            with open(path_to_player_decks, 'r') as f:
                deck_content = f.read()
                if self.name_1 == name_player:
                    if not self.p1.deck_loaded:
                        await self.p1.setup_player(deck_content, self.planet_array)
                        await self.update_automated_info()
                        await self.send_automated_info(force=True)
                elif self.name_2 == name_player:
                    if not self.p2.deck_loaded:
                        await self.p2.setup_player(deck_content, self.planet_array)
                        await self.update_automated_info()
                        await self.send_automated_info(force=True)
    elif message[1] == "loadrandombot":
        if self.phase == "SETUP":
            name_player = message[2]
            if name_player == self.name_1 or name_player == self.name_2 and self.bot_is_present:
                decks_lists = os.listdir(os.getcwd() + "/decks/DeckStorage/" + name_player)
                if decks_lists:
                    random.shuffle(decks_lists)
                    path_to_player_decks = os.getcwd() + "/decks/DeckStorage/" + name_player + "/" + decks_lists[0]
                    if os.path.exists(path_to_player_decks):
                        with open(path_to_player_decks, 'r') as f:
                            deck_content = f.read()
                            if self.name_1 == name_player:
                                if not self.p1.deck_loaded:
                                    await self.p1.setup_player(deck_content, self.planet_array)
                                    await self.update_automated_info()
                                    await self.send_automated_info(force=True)
                            elif self.name_2 == name_player:
                                if not self.p2.deck_loaded:
                                    await self.p2.setup_player(deck_content, self.planet_array)
                                    await self.update_automated_info()
                                    await self.send_automated_info(force=True)
    elif message[1] == "concede" or message[1] == "resign":
        if name == self.name_1:
            await self.send_victory_proper(self.name_2, "concession")
        elif name == self.name_2:
            await self.send_victory_proper(self.name_1, "concession")
    elif message[1] == "savegame":
        cwd = os.getcwd()
        stored_game_data_dir = os.path.join(cwd, "saved_games")
        if not os.path.exists(stored_game_data_dir):
            os.mkdir(stored_game_data_dir)
        target_save_file = os.path.join(stored_game_data_dir, self.game_id) + ".txt"
        with open(target_save_file, "w") as f:
            current_string = "-----\nDECK P1\n-----\n"
            current_string += self.p1.deck_string
            current_string += "\n-----\nDECK P2\n-----\n"
            current_string += self.p2.deck_string
            current_string += "\n-----GAME DETAILS-----\nERRATA:\t"
            if self.blackstone:
                current_string += "BLACKSTONE"
            elif self.apoka:
                current_string += "APOKA"
            else:
                current_string += "NONE"
            current_string += "\n"
            current_string += "SECTOR:\t" + self.sector
            current_string += "\n"
            current_string += "WINNER:\t"
            if self.p1.is_the_winner:
                current_string += self.p1.name_player
            elif self.p2.is_the_winner:
                current_string += self.p2.name_player
            else:
                current_string += "N/A"
            current_string += "\n"
            current_string += "\n-----\nP1 DETAILS\n-----\n"
            current_string += "NAME:\t" + str(self.p1.name_player) + "\n"
            current_string += "RESOURCES GAINED:\t" + str(self.p1.total_resources_gained) + "\n"
            current_string += "CARDS DRAWN:\t" + str(self.p1.total_cards_draw) + "\n"
            current_string += "DAMAGE DEALT (ATTACKS):\t" + str(self.p1.total_damage_dealt_by_attacks) + "\n"
            current_string += "\n-----\nP2 DETAILS\n-----\n"
            current_string += "NAME:\t" + str(self.p2.name_player) + "\n"
            current_string += "RESOURCES GAINED:\t" + str(self.p2.total_resources_gained) + "\n"
            current_string += "CARDS DRAWN:\t" + str(self.p2.total_cards_draw) + "\n"
            current_string += "DAMAGE DEALT (ATTACKS):\t" + str(self.p2.total_damage_dealt_by_attacks) + "\n"
            current_string += "\n-----\nREPLAY DETAILS\n-----\n"
            current_string += "RANDOM SEED:\t" + self.random_seed + "\n"
            current_string += "MOVE DETAILS:\n" + self.game_events_as_mono_string + "\n"
            f.write(current_string)
        await self.send_update_message("Saved the game!")
    elif message[1] == "request-seed":
        await self.send_update_message(str(self.random_seed))
    elif message[1] == "force-send-auto-data":
        if self.bot_is_present:
            await self.update_automated_info()
            await self.send_automated_info(force=True)
    elif message[1] == "Advance":
        num_times = 1
        if len(message) == 3:
            num_times = int(message[2])
        start_time = datetime.datetime.now()
        for i in range(num_times):
            move_id = self.saved_move_id
            moves_list = self.saved_moves
            if move_id >= len(moves_list):
                await self.send_update_message("Reached end of replay")
            else:
                move_string = moves_list[move_id]
                if "/savegame" in move_string:
                    await self.send_update_message("Reached end of replay")
                else:
                    self.saved_move_id = move_id + 1
                    name_user, move_details = move_string.split(sep="|||")
                    move_details_split = move_details.split(sep="/")
                    print(move_details_split)
                    if move_details[0] == "/":
                        await self.resolve_chat_message(name_user, move_details_split)
                    elif move_details_split[0] == "SpecialAction":
                        if move_details_split[1] == "pass-P1":
                            pass
                        else:
                            await self.update_game_event(name_user, ["action-button"], same_thread=True)
                            await self.update_game_event(name_user, move_details_split[1:])
                    elif move_details_split[0] == "REARRANGE_HAND":
                        if name_user == self.name_1:
                            player = self.p1
                        else:
                            player = self.p2
                        player.reorder_card_in_hand(int(move_details_split[1]), int(move_details_split[2]))
                        await player.send_hand()
                    else:
                        await self.update_game_event(name_user, move_details_split)
        end_time = datetime.datetime.now()
        print("TIME\n\n\n", end_time - start_time, "\n\n\n")
    elif message[1] == "Error":
        raise ValueError
    elif message[1] == "force-quit-reactions":
        await self.send_update_message("FORCEFULLY QUITTING REACTIONS")
        self.reset_reactions_data()
        await self.send_info_box()
    elif message[1] == "force-quit-effects":
        await self.send_update_message("FORCEFULLY QUITTING EFFECTS")
        self.reset_effects_data()
        await self.send_info_box()
    elif message[1] == "force-quit-damage":
        await self.send_update_message("FORCEFULLY QUITTING DAMAGE")
        self.reset_damage_data()
        await self.send_info_box()
    elif message[1] == "force-quit-action":
        await self.send_update_message("FORCEFULLY QUITTING ACTION")
        self.reset_action_data()
        self.action_cleanup()
        await self.send_info_box()
    elif message[1] == "force-quit-moves":
        await self.send_update_message("FORCEFULLY QUITTING MOVES")
        self.queued_moves = []
        if self.choice_context == "Interrupt Enemy Movement Effect?":
            self.reset_choices_available()
        await self.send_info_box()
    elif message[1] == "force-quit-choices":
        await self.send_update_message("FORCEFULLY QUITTING CHOICES")
        self.reset_choices_available()
        self.resolving_search_box = False
        await self.send_info_box()
    elif message[1] == "swap-choice":
        await self.send_update_message("Swapping Choices")
        if self.name_player_making_choices == self.name_1:
            self.name_player_making_choices = self.name_2
        elif self.name_player_making_choices == self.name_2:
            self.name_player_making_choices = self.name_1
        await self.send_search(force=True)
        await self.send_info_box()
    elif message[1] == "cancel-attack":
        if self.attacker_planet != -1:
            if self.number_with_combat_turn == "1":
                self.p1.reset_aiming_reticle_in_play(
                    self.attacker_planet,
                    self.attacker_position
                )
                self.p1.ready_given_pos(
                    self.attacker_planet,
                    self.attacker_position
                )
                await self.p1.send_units_at_planet(
                    self.attacker_planet)
                self.attacker_planet = -1
                self.attacker_position = -1
            else:
                self.p2.reset_aiming_reticle_in_play(
                    self.attacker_planet,
                    self.attacker_position
                )
                self.p2.ready_given_pos(
                    self.attacker_planet,
                    self.attacker_position
                )
                await self.p2.send_units_at_planet(
                    self.attacker_planet)
                self.attacker_planet = -1
                self.attacker_position = -1
    elif message[1] == "cancel-mode" or message[1] == "cancel-debug":
        self.cancel_debug_mode()
        await self.send_update_message("Cancelled debug mode")
        await self.send_everything()
    elif message[1] == "debug-info":
        sent_string = "Debug Info: "
        if self.resolving_search_box:
            sent_string += "Search Box"
        else:
            sent_string += "Not Searching"
        sent_string += "."
        await self.send_update_message(
            sent_string
        )
    elif message[1] == "toggle-search":
        self.resolving_search_box = \
            not self.resolving_search_box
        await self.send_update_message(
            "Toggled Search"
        )
    elif message[1] == "debug-reactions":
        sent_string = "Current Reaction Info: "
        sent_string += self.name_1
        sent_string += ": "
        for i in range(len(self.reactions_needing_resolving)):
            if self.reactions_needing_resolving[i].get_player_resolving_reaction() \
                    == self.name_1:
                sent_string += self.reactions_needing_resolving[
                    i].get_reaction_name()
                sent_string += ", "
        sent_string += ". "
        sent_string += self.name_2
        sent_string += ": "
        for i in range(len(self.reactions_needing_resolving)):
            if self.reactions_needing_resolving[i].get_player_resolving_reaction() \
                    == self.name_2:
                sent_string += self.reactions_needing_resolving[
                    i].get_reaction_name()
                sent_string += ", "
        sent_string += "."
        await self.send_update_message(
            sent_string
        )
    elif message[1] == "debug-interrupts":
        sent_string = "Current Interrupt Info: "
        sent_string += self.name_1
        sent_string += ": "
        for i in range(len(self.interrupts_waiting_on_resolution)):
            if self.interrupts_waiting_on_resolution[
                i].get_player_resolving_interrupt() \
                    == self.name_1:
                sent_string += self.interrupts_waiting_on_resolution[
                    i].get_interrupt_name()
                sent_string += ", "
        sent_string += ". "
        sent_string += self.name_2
        sent_string += ": "
        for i in range(len(self.interrupts_waiting_on_resolution)):
            if self.interrupts_waiting_on_resolution[
                i].get_player_resolving_interrupt() \
                    == self.name_2:
                sent_string += self.interrupts_waiting_on_resolution[
                    i].get_interrupt_name()
                sent_string += ", "
        sent_string += "."
        await self.send_update_message(
            sent_string
        )
    elif not self.safety_check():
        await self.send_update_message(
            "Command prevented; game is in an unsafe state."
        )
    elif message[1] == "unpass-combat":
        if self.phase == "COMBAT":
            self.p1.has_passed = False
            self.p2.has_passed = False
            self.reset_combat_positions()
            await self.send_update_message("Unpassed both players")
    elif message[1] == "restore-warlord":
        if len(message) == 2:
            if name == self.name_1:
                warlord_pla, warlord_pos = self.p1.get_location_of_warlord()
                if warlord_pla != -1:
                    self.p1.make_warlord_hale_given_pos(warlord_pla, warlord_pos)
                    await self.p1.send_units_at_planet(warlord_pla)
            elif name == self.name_2:
                warlord_pla, warlord_pos = self.p2.get_location_of_warlord()
                if warlord_pla != -1:
                    self.p2.make_warlord_hale_given_pos(warlord_pla, warlord_pos)
                    await self.p2.send_units_at_planet(warlord_pla)
        if len(message) == 3:
            if message[2] == "1":
                warlord_pla, warlord_pos = self.p1.get_location_of_warlord()
                if warlord_pla != -1:
                    self.p1.make_warlord_hale_given_pos(warlord_pla, warlord_pos)
                    await self.p1.send_units_at_planet(warlord_pla)
            elif message[2] == "2":
                warlord_pla, warlord_pos = self.p2.get_location_of_warlord()
                if warlord_pla != -1:
                    self.p2.make_warlord_hale_given_pos(warlord_pla, warlord_pos)
                    await self.p2.send_units_at_planet(warlord_pla)
    elif message[1] == "toggle-command-rewards":
        if name == self.name_1:
            self.p1.automated_command_rewards = not self.p1.automated_command_rewards
            if self.p1.automated_command_rewards:
                await self.send_update_message("Accepting command results")
            else:
                await self.send_update_message("Declining command results")
        if name == self.name_2:
            self.p2.automated_command_rewards = not self.p2.automated_command_rewards
            if self.p2.automated_command_rewards:
                await self.send_update_message("Accepting command results")
            else:
                await self.send_update_message("Declining command results")
    elif message[1] == "unpass-deploy":
        if self.phase == "DEPLOY":
            self.p1.has_passed = False
            self.p2.has_passed = False
            await self.send_update_message("Unpassed both players")
    elif message[1] == "skip-deploy":
        if self.phase == "DEPLOY":
            if self.player_with_deploy_turn == \
                    self.name_1:
                self.player_with_deploy_turn = \
                    self.name_2
                self.number_with_deploy_turn = "2"
            else:
                self.player_with_deploy_turn = \
                    self.name_1
                self.number_with_deploy_turn = "1"
            await self.send_update_message("Skipped a deploy turn")
            await self.send_info_box()
    elif message[1] == "sort-hand" and len(message) == 2:
        if self.name == self.name_1:
            self.p1.sort_hand()
            await self.p1.send_hand()
        elif self.name == self.name_2:
            self.p2.sort_hand()
            await self.p2.send_hand()
    elif message[1] == "rearrange-hand":
        if name == self.name_1 or name == self.name_2:
            await self.send_update_message(name + " is rearranging their hand.")
            self.debug_mode = "rearrange-hand"
            self.active_debug_user = name
            self.chosen_first_card = False
    elif message[1] == "shuffle-deck" and len(message) == 3:
        if message[2] == "1":
            self.p1.shuffle_deck()
            await self.send_decks()
            await self.send_update_message("Deck shuffled")
        elif message[2] == "2":
            self.p2.shuffle_deck()
            await self.send_decks()
            await self.send_update_message("Deck shuffled")
    elif message[1] == "rearrange-deck" and len(message) == 4:
        try:
            print("got here")
            if not self.rearranging_deck:
                print("not rearranging")
                amount = int(message[3])
                if message[2] == "1":
                    if amount > 0:
                        self.rearranging_deck = True
                        self.name_player_rearranging_deck = \
                            self.name_1
                        self.deck_part_being_rearranged = \
                            self.p1.deck[:amount]
                        self.deck_part_being_rearranged.append("FINISH")
                        self.number_cards_to_rearrange = amount
                        await self.send_search()
                        await self.send_info_box()
                elif message[2] == "2":
                    if amount > 0:
                        self.rearranging_deck = True
                        self.name_player_rearranging_deck = \
                            self.name_2
                        self.deck_part_being_rearranged = \
                            self.p2.deck[:amount]
                        self.deck_part_being_rearranged.append("FINISH")
                        self.number_cards_to_rearrange = amount
                        await self.send_search()
                        await self.send_info_box()
        except Exception as e:
            print(e)
    elif message[1] == "stop-rearrange-deck":
        self.stop_rearranging_deck()
        await self.send_search()
        await self.send_info_box()
    elif message[1] == "cards-deck" and len(message) == 3:
        if message[2] == "1":
            amount = len(self.p1.deck)
            await self.send_update_message(
                "Num cards in P1's deck: " + str(amount)
            )
        elif message[2] == "2":
            amount = len(self.p2.deck)
            await self.send_update_message(
                "Num cards in P2's deck: " + str(amount)
            )
    elif message[1] == "show-discard" and len(message) == 3:
        if message[2] == "1":
            discard = self.p1.discard
            new_message = ", ".join(discard)
            await self.send_update_message(
                "Current discard of P1 is: " + new_message
            )
        elif message[2] == "2":
            discard = self.p2.discard
            new_message = ", ".join(discard)
            await self.send_update_message(
                "Current discard of P2 is: " + new_message
            )
    elif message[1] == "set-resources" and len(message) == 4:
        player_num = message[2]
        resources = int(message[3])
        if player_num == "1":
            self.p1.resources = resources
            await self.p1.send_resources()
        elif player_num == "2":
            self.p2.resources = resources
            await self.p2.send_resources()
    elif message[1] == "add-to-hq" and len(message) > 3:
        card_name = message[3]
        card = self.preloaded_find_card(card_name)
        if card.get_shields() != -1:
            if card.get_card_type() in ["Army", "Token", "Synapse", "Support"]:
                if message[2] == "1":
                    self.p1.add_to_hq(card)
                    await self.p1.send_hq()
                elif message[2] == "2":
                    self.p2.add_to_hq(card)
                    await self.p2.send_hq()
    elif message[1] == "add-to-play" and len(message) > 4:
        planet_pos = int(message[3])
        if -1 < planet_pos < 7:
            if self.planets_in_play_array[planet_pos]:
                card_name = message[4]
                card = self.preloaded_find_card(card_name)
                if card.get_shields() != -1:
                    if card.get_card_type() in ["Army", "Token", "Synapse"]:
                        if message[2] == "1":
                            self.p1.add_card_to_planet(card, planet_pos)
                            await self.p1.send_units_at_planet(planet_pos)
                        elif message[2] == "2":
                            self.p2.add_card_to_planet(card, planet_pos)
                            await self.p2.send_units_at_planet(planet_pos)
    elif (message[1] == "addcard" or message[1] == "add-card") and len(message) > 3:
        card_name = message[3]
        card = self.preloaded_find_card(card_name)
        if card.get_shields() != -1:
            if card.get_card_type() in ["Army", "Event", "Support", "Attachment"]:
                if message[2] == "1":
                    self.p1.cards.append(card.get_name())
                    await self.p1.send_hand()
                elif message[2] == "2":
                    self.p2.cards.append(card.get_name())
                    await self.p2.send_hand()
    elif message[1] == "draw" and len(message) > 2:
        if message[2] == "1":
            num_times = 1
            if len(message) == 4:
                try:
                    num_times = int(message[3])
                except:
                    pass
            if num_times > 50:
                num_times = 50
            for i in range(num_times):
                self.p1.draw_card()
            await self.p1.send_hand()
            await self.send_decks()
        elif message[2] == "2":
            num_times = 1
            if len(message) == 4:
                try:
                    num_times = int(message[3])
                except:
                    pass
            if num_times > 50:
                num_times = 50
            for i in range(num_times):
                self.p2.draw_card()
            await self.p2.send_hand()
            await self.send_decks()
    elif message[1] == "retreat-unit":
        if len(message) == 2:
            self.debug_mode = "retreat-unit"
            await self.send_update_message("Click card in play to retreat.")
    elif message[1] == "discard":
        if len(message) == 2:
            self.debug_mode = "discard-hand"
            await self.send_update_message("Click card in hand to discard.")
        if len(message) > 3:
            hand_pos = int(message[3])
            if message[2] == "1":
                self.p1.discard_card_from_hand(hand_pos)
                await self.p1.send_hand()
                await self.p1.send_discard()
            elif message[2] == "2":
                self.p2.discard_card_from_hand(hand_pos)
                await self.p2.send_hand()
                await self.p2.send_discard()
    elif message[1] == "force-deepstrike":
        if len(message) == 2:
            if self.last_planet_checked_for_battle != -1:
                self.start_battle_deepstrike = True
                await self.send_info_box()
    elif message[1] == "move-to-top-discard":
        if len(message) == 2:
            self.debug_mode = "move-to-top-discard"
            await self.send_update_message("Click card in discard to move to top.")
    elif message[1] == "destroy":
        if len(message) == 2:
            self.debug_mode = "destroy"
            await self.send_update_message("Click card to destroy.")
    elif message[1] == "discard-name" and len(message) > 3:
        if message[2] == "1":
            self.p1.discard_card_name_from_hand(message[3])
            await self.p1.send_hand()
            await self.p1.send_discard()
        elif message[2] == "2":
            self.p2.discard_card_name_from_hand(message[3])
            await self.p2.send_hand()
            await self.p2.send_discard()
    elif message[1] == "fully-remove" and len(message) > 3:
        hand_pos = int(message[3])
        if message[2] == "1":
            del self.p1.cards_removed_from_game[hand_pos]
            del self.p1.cards_removed_from_game_hidden[hand_pos]
            await self.p1.send_removed_cards()
        elif message[2] == "2":
            del self.p2.cards_removed_from_game[hand_pos]
            del self.p2.cards_removed_from_game_hidden[hand_pos]
            await self.p2.send_removed_cards()
    elif message[1] == "remove-discard" and len(message) > 3:
        hand_pos = int(message[3])
        if message[2] == "1":
            card_name = self.p1.discard[hand_pos]
            self.p1.remove_card_from_game(card_name)
            del self.p1.discard[hand_pos]
            await self.p1.send_discard()
            await self.p1.send_removed_cards()
        elif message[2] == "2":
            card_name = self.p2.discard[hand_pos]
            self.p2.remove_card_from_game(card_name)
            del self.p2.discard[hand_pos]
            await self.p2.send_discard()
            await self.p2.send_removed_cards()
    elif message[1] == "remove-hand" and len(message) > 3:
        hand_pos = int(message[3])
        if message[2] == "1":
            card_name = self.p1.cards[hand_pos]
            self.p1.remove_card_from_game(card_name)
            del self.p1.cards[hand_pos]
            await self.p1.send_hand()
            await self.p1.send_removed_cards()
        elif message[2] == "2":
            card_name = self.p2.cards[hand_pos]
            self.p2.remove_card_from_game(card_name)
            del self.p2.cards[hand_pos]
            await self.p2.send_hand()
            await self.p2.send_removed_cards()
    elif message[1] == "clear-reticle":
        if len(message) == 2:
            self.debug_mode = "clear-reticle"
            await self.send_update_message("Click card in play to clear reticle.")
        if len(message) > 3:
            num_player = message[2]
            planet_pos = int(message[3])
            unit_pos = int(message[4])
            unit_position = ["IN_PLAY", message[2], message[3], message[4]]
            if message[3] == "-2":
                unit_position = ["HQ", message[2], message[4]]
            if self.validate_received_game_string(unit_position):
                if num_player == "1":
                    self.p1.reset_aiming_reticle_in_play(
                        planet_pos, unit_pos)
                    await self.p1.send_units_at_planet(planet_pos)
                elif unit_position[1] == "2":
                    self.p2.reset_aiming_reticle_in_play(
                        planet_pos, unit_pos)
                    await self.p2.send_units_at_planet(planet_pos)
    elif (message[1] == "infest-planet" or message[1] == "infest") and len(message) > 2:
        planet_pos = int(message[2])
        self.infested_planets[planet_pos] = True
        await self.send_planet_array()
    elif message[1] == "clear-infestation" and len(message) > 2:
        planet_pos = int(message[2])
        self.infested_planets[planet_pos] = False
        await self.send_planet_array()
    elif message[1] == "return" and len(message) == 2:
        self.debug_mode = "return"
        await self.send_update_message("Click card to return it to your hand.")
    elif message[1] == "ready-card" or message[1] == "ready":
        if len(message) == 2:
            self.debug_mode = "ready-card"
            await self.send_update_message("Click card in play to ready it.")
        if len(message) > 3:
            num_player = message[2]
            planet_pos = int(message[3])
            unit_pos = int(message[4])
            unit_position = ["IN_PLAY", message[2], message[3], message[4]]
            if message[3] == "-2":
                unit_position = ["HQ", message[2], message[4]]
            if self.validate_received_game_string(unit_position):
                if num_player == "1":
                    self.p1.ready_given_pos(planet_pos, unit_pos)
                    await self.p1.send_units_at_planet(planet_pos)
                elif unit_position[1] == "2":
                    self.p2.ready_given_pos(planet_pos, unit_pos)
                    await self.p2.send_units_at_planet(planet_pos)
    elif message[1] == "exhaust-card" or message[1] == "exhaust":
        if len(message) == 2:
            self.debug_mode = "exhaust-card"
            await self.send_update_message("Click card in play to exhaust it.")
        if len(message) > 3:
            num_player = message[2]
            planet_pos = int(message[3])
            unit_pos = int(message[4])
            unit_position = ["IN_PLAY", message[2], message[3], message[4]]
            if message[3] == "-2":
                unit_position = ["HQ", message[2], message[4]]
            if self.validate_received_game_string(unit_position):
                if num_player == "1":
                    self.p1.exhaust_given_pos(planet_pos, unit_pos)
                    await self.p1.send_units_at_planet(planet_pos)
                elif unit_position[1] == "2":
                    self.p2.exhaust_given_pos(planet_pos, unit_pos)
                    await self.p2.send_units_at_planet(planet_pos)
    elif message[1] == "move-unit":
        if len(message) == 2:
            self.chosen_first_card = False
            self.debug_mode = "move-unit"
            await self.send_update_message("Click card in play to move.")
        if len(message) > 4:
            num_player = message[2]
            planet_pos = int(message[3])
            unit_pos = int(message[4])
            destination = int(message[5])
            unit_position = ["IN_PLAY", message[2], message[3], message[4]]
            if message[3] == "-2":
                unit_position = ["HQ", message[2], message[4]]
            if self.validate_received_game_string(unit_position):
                if (self.planets_in_play_array[destination] and 0 <= destination <= 6) or destination == -2:
                    if num_player == "1":
                        if self.p1.check_is_unit_at_pos(planet_pos, unit_pos):
                            if destination == -2:
                                self.p1.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                            else:
                                self.p1.move_unit_to_planet(planet_pos, unit_pos, destination)
                            await self.p1.send_units_at_planet(planet_pos)
                            await self.p1.send_units_at_planet(destination)
                    elif unit_position[1] == "2":
                        if self.p2.check_is_unit_at_pos(planet_pos, unit_pos):
                            if destination == -2:
                                self.p2.move_unit_at_planet_to_hq(planet_pos, unit_pos)
                            else:
                                self.p2.move_unit_to_planet(planet_pos, unit_pos, destination)
                            await self.p2.send_units_at_planet(planet_pos)
                            await self.p2.send_units_at_planet(destination)
    elif message[1] == "set-faith" and len(message) > 4:
        num_player = message[2]
        planet_pos = int(message[3])
        unit_pos = int(message[4])
        faith = int(message[5])
        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
        if message[3] == "-2":
            unit_position = ["HQ", message[2], message[4]]
        if self.validate_received_game_string(unit_position):
            if num_player == "1":
                self.p1.set_faith_given_pos(planet_pos, unit_pos, faith)
                await self.p1.send_units_at_planet(planet_pos)
            elif unit_position[1] == "2":
                self.p2.set_faith_given_pos(planet_pos, unit_pos, faith)
                await self.p2.send_units_at_planet(planet_pos)
    elif message[1] == "set-damage" and len(message) > 4:
        num_player = message[2]
        planet_pos = int(message[3])
        unit_pos = int(message[4])
        damage = int(message[5])
        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
        if message[3] == "-2":
            unit_position = ["HQ", message[2], message[4]]
        if self.validate_received_game_string(unit_position):
            if num_player == "1":
                self.p1.set_damage_given_pos(planet_pos, unit_pos, damage)
                await self.p1.send_units_at_planet(planet_pos)
            elif unit_position[1] == "2":
                self.p2.set_damage_given_pos(planet_pos, unit_pos, damage)
                await self.p2.send_units_at_planet(planet_pos)
    elif message[1] == "remove-damage" and len(message) > 4:
        num_player = message[2]
        planet_pos = int(message[3])
        unit_pos = int(message[4])
        damage = int(message[5])
        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
        if message[3] == "-2":
            unit_position = ["HQ", message[2], message[4]]
        if self.validate_received_game_string(unit_position):
            if num_player == "1":
                if self.p1.check_is_unit_at_pos(planet_pos, unit_pos):
                    self.p1.remove_damage_from_pos(planet_pos, unit_pos, damage)
                    await self.p1.send_units_at_planet(planet_pos)
            elif unit_position[1] == "2":
                if self.p2.check_is_unit_at_pos(planet_pos, unit_pos):
                    self.p2.remove_damage_from_pos(planet_pos, unit_pos, damage)
                    await self.p2.send_units_at_planet(planet_pos)
            await self.update_game_event(name, [])
    elif message[1] == "assign-damage" and len(message) > 4:
        num_player = message[2]
        planet_pos = int(message[3])
        unit_pos = int(message[4])
        damage = int(message[5])
        unit_position = ["IN_PLAY", message[2], message[3], message[4]]
        if message[3] == "-2":
            unit_position = ["HQ", message[2], message[4]]
        if self.validate_received_game_string(unit_position):
            if num_player == "1":
                if self.p1.check_is_unit_at_pos(planet_pos, unit_pos):
                    self.p1.assign_damage_to_pos(planet_pos, unit_pos, damage, by_enemy_unit=False)
                    await self.p1.send_units_at_planet(planet_pos)
            elif unit_position[1] == "2":
                if self.p2.check_is_unit_at_pos(planet_pos, unit_pos):
                    self.p2.assign_damage_to_pos(planet_pos, unit_pos, damage, by_enemy_unit=False)
                    await self.p2.send_units_at_planet(planet_pos)
            await self.update_game_event(name, [])
