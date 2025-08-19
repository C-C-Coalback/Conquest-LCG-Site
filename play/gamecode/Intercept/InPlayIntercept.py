from .. import FindCard
import copy


async def update_intercept_in_play(self, primary_player, secondary_player, name, game_update_string, name_effect):
    planet_pos = int(game_update_string[2])
    unit_pos = int(game_update_string[3])
    if name_effect == "Catachan Outpost":
        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 2, expiration="NEXT")
        name_unit = primary_player.get_name_given_pos(planet_pos, unit_pos)
        await self.send_update_message(name_unit + " got +2 ATK")
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Klaivex Warleader":
        primary_player.destroy_card_in_play(planet_pos, unit_pos)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Eldorath Starbane":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Sicarius's Chosen":
        origin_planet = self.positions_of_unit_triggering_reaction[0][1]
        primary_player.move_unit_to_planet(target_planet,
                                           int(game_update_string[3]),
                                           origin_planet)
        new_unit_pos = len(primary_player.cards_in_play[origin_planet + 1]) - 1
        primary_player.assign_damage_to_pos(origin_planet, new_unit_pos, 1,
                                            context="Sicarius's Chosen",
                                            rickety_warbuggy=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Cato's Stronghold":
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Captain Markis":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.mask_jain_zar_check_actions(secondary_player, primary_player)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Suppressive Fire":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Tellyporta Pad":
        primary_player.move_unit_to_planet(planet_pos, unit_pos,
                                           self.round_number)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Zarathur's Flamers":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True, shadow_field_possible=True)
        og_pla, og_pos = self.position_of_actioned_card
        secondary_player.sacrifice_card_in_play(og_pla, og_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Tzeentch's Firestorm":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, self.amount_spend_for_tzeentch_firestorm,
                                            by_enemy_unit=False)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Archon's Terror":
        primary_player.rout_unit(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Twisted Laboratory":
        primary_player.set_blanked_given_pos(planet_pos, unit_pos, exp="EOP")
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Shrouded Harlequin":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Spiritseer Erathal":
        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 1, healing=True)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Superiority":
        primary_player.cards_in_play[planet_pos + 1][unit_pos].hit_by_superiority = True
        card_name = primary_player.cards_in_play[planet_pos + 1][unit_pos].get_name()
        text = card_name + ", position " + str(planet_pos) + " " + str(unit_pos) + " hit by superiority."
        await self.send_update_message(text)
        secondary_player.discard_card_from_hand(secondary_player.aiming_reticle_coords_hand)
        secondary_player.aiming_reticle_coords_hand = None
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Craftworld Gate":
        primary_player.return_card_to_hand(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Deception":
        primary_player.return_card_to_hand(planet_pos, unit_pos)
        secondary_player.aiming_reticle_color = None
        secondary_player.aiming_reticle_coords_hand = None
        secondary_player.discard_card_from_hand(self.card_pos_to_deploy)
        self.card_pos_to_deploy = -1
        self.action_cleanup()
    elif name_effect == "Ferrin":
        primary_player.rout_unit(planet_pos, unit_pos)
        self.complete_intercept()
        await self.resolve_battle_conclusion(secondary_player, game_string="")
    elif name_effect == "Iridial":
        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
        self.complete_intercept()
        await self.resolve_battle_conclusion(secondary_player, game_string="")
    elif name_effect == "Awakening Cavern":
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Indescribable Horror":
        primary_player.rout_unit(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Blazing Zoanthrope":
        if self.infested_planets[planet_pos]:
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2)
        else:
            primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Dark Cunning":
        if self.infested_planets:
            secondary_player.add_resources(1)
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Vengeance!":
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Veteran Barbrus":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True, context="Veteran Barbrus")
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Nahumekh":
        primary_player.apply_negative_health_eop(planet_pos, unit_pos, primary_player.nahumekh_value)
        name = primary_player.get_name_given_pos(planet_pos, unit_pos)
        await self.send_update_message(
            name + " received -" + str(primary_player.nahumekh_value) + " HP."
        )
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Hate":
        primary_player.destroy_card_in_play(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Tomb Blade Squadron":
        primary_player.apply_negative_health_eop(planet_pos, unit_pos, 1)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Gauss Flayer":
        primary_player.apply_negative_health_eop(planet_pos, unit_pos, 2)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Master Program":
        primary_player.ready_given_pos(planet_pos, unit_pos)
        primary_player.remove_damage_from_pos(planet_pos, unit_pos, 999, healing=True)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Particle Whip":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter, by_enemy_unit=False)
        self.misc_counter = 0
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Venomous Fiend":
        damage = primary_player.get_command_given_pos(planet_pos, unit_pos)
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, damage, rickety_warbuggy=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Ragnar Blackmane":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Noble Deed":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter, by_enemy_unit=False)
        secondary_player.discard_card_from_hand(secondary_player.aiming_reticle_coords_hand)
        secondary_player.aiming_reticle_coords_hand = None
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Fenrisian Wolf":
        att_num, att_pla, att_pos = self.positions_of_unit_triggering_reaction[0]
        att_value = secondary_player.get_attack_given_pos(att_pla, att_pos)
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, att_value, by_enemy_unit=False)
        self.advance_damage_aiming_reticle()
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Inquisitorial Fortress":
        primary_player.rout_unit(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Ethereal Wisdom":
        primary_player.cards_in_play[planet_pos + 1][unit_pos].extra_traits_eop += "Ethereal"
        primary_player.cards_in_play[planet_pos + 1][unit_pos].extra_attack_until_end_of_phase += 1
        secondary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        secondary_player.aiming_reticle_coords_hand = None
        self.action_cleanup()
    elif name_effect == "Rotten Plaguebearers":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, shadow_field_possible=True, rickety_warbuggy=True)
        self.mask_jain_zar_check_actions(secondary_player, primary_player)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Rally the Charge":
        command = 2 * primary_player.get_command_given_pos(planet_pos, unit_pos)
        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, command, expiration="EOP")
        name_card = primary_player.get_name_given_pos(planet_pos, unit_pos)
        secondary_player.discard_card_from_hand(secondary_player.aiming_reticle_coords_hand)
        secondary_player.aiming_reticle_coords_hand = None
        await self.send_update_message(
            name_card + " gained +" + str(command) + " ATK from Rally the Charge!"
        )
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Doombolt":
        damage = primary_player.get_damage_given_pos(planet_pos, unit_pos)
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, damage, by_enemy_unit=False)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Searing Brand":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 3, preventable=False, by_enemy_unit=False)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Nocturne-Ultima Storm Bolter":
        origin_planet = self.positions_of_unit_triggering_reaction[0][1]
        origin_pos = self.positions_of_unit_triggering_reaction[0][2]
        attack = secondary_player.get_attack_given_pos(origin_planet, origin_pos)
        primary_player.assign_damage_to_pos(origin_planet, target_unit_pos, attack, by_enemy_unit=False)
        primary_player.set_aiming_reticle_in_play(origin_planet, target_unit_pos, "blue")
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Hallow Librarium":
        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, -2, expiration="EOP")
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Made Ta Fight":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, self.misc_counter, by_enemy_unit=False)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Squiggify":
        primary_player.cards_in_play[planet_pos + 1][unit_pos].extra_traits_eop += "Squig"
        primary_player.set_blanked_given_pos(planet_pos, unit_pos)
        primary_player.cards_in_play[planet_pos + 1][unit_pos].attack_set_eop = 1
        primary_player.discard_card_from_hand(primary_player.aiming_reticle_coords_hand)
        name_card = primary_player.get_name_given_pos(planet_pos, unit_pos)
        await self.send_update_message(
            name_card + " got Squiggified!"
        )
        primary_player.aiming_reticle_coords_hand = None
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Commissarial Bolt Pistol":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Mind War":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Vanguard Soldiers":
        primary_player.ready_given_pos(planet_pos)
        self.delete_interrupt()
        self.complete_intercept()
    elif name_effect == "Prodigal Sons Disciple":
        damage = primary_player.get_command_given_pos(planet_pos, unit_pos)
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, damage, rickety_warbuggy=True, preventable=False)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Fire Prism":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Invasive Genestealers":
        primary_player.cards_in_play[planet_pos + 1][unit_pos].negative_hp_until_eop += 1
        _, og_pla, og_pos = self.positions_of_unit_triggering_reaction[0]
        secondary_player.cards_in_play[og_pla + 1][og_pos].positive_hp_until_eop += 1
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Kabalite Harriers":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Chaplain Mavros":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
        primary_player.increase_attack_of_unit_at_pos(planet_pos, unit_pos, 1, expiration="EOP")
        self.mask_jain_zar_check_actions(secondary_player, primary_player)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "The Emperor's Champion":
        primary_player.cards_in_play[planet_pos + 1][unit_pos].emperor_champion_active = True
        secondary_player.reset_aiming_reticle_in_play(planet_pos, self.position_of_actioned_card[1])
        self.mask_jain_zar_check_actions(secondary_player, primary_player)
        self.action_cleanup()
    elif name_effect == "Staff of Change":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, by_enemy_unit=False)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Devourer Venomthrope":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Hallucinogen Grenade":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        atk = primary_player.cards_in_play[planet_pos + 1][unit_pos].attack
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, atk, by_enemy_unit=False)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "8th Company Assault Squad":
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Kommando Sneakaz":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True, by_enemy_unit=False)
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Crush of Sky-Slashers":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, rickety_warbuggy=True, shadow_field_possible=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Vezuel's Hunters":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2, rickety_warbuggy=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Dark Angels Cruiser":
        primary_player.set_damage_given_pos(planet_pos, unit_pos, 0)
        primary_player.discard_attachments_from_card(planet_pos, unit_pos)
        card = primary_player.cards_in_play[planet_pos + 1][unit_pos]
        primary_player.cards_in_reserve[planet_pos].append(card)
        primary_player.remove_card_from_play(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Clearcut Refuge":
        highest_cost = secondary_player.get_highest_cost_units()
        primary_player.increase_health_of_unit_at_pos(planet_pos, unit_pos, highest_cost, expiration="EOP")
        name_unit = primary_player.get_name_given_pos(planet_pos, unit_pos)
        await self.send_update_message(name_unit + " gained +" + str(highest_cost) + " HP.")
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Mandrake Cutthroat":
        primary_player.destroy_card_in_play(planet_pos, unit_pos)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "A Thousand Cuts":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1, by_enemy_unit=False)
        secondary_player.deck.append(secondary_player.cards[secondary_player.aiming_reticle_coords_hand])
        secondary_player.remove_card_from_hand(secondary_player.aiming_reticle_coords_hand)
        secondary_player.shuffle_deck()
        secondary_player.aiming_reticle_coords_hand = None
        await secondary_player.dark_eldar_event_played()
        secondary_player.torture_event_played()
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Missile Pod":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 3, by_enemy_unit=False)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Keep Firing!":
        primary_player.ready_given_pos(planet_pos, unit_pos)
        self.action_cleanup()
        self.complete_intercept()
    elif name_effect == "Run Down":
        dest = self.positions_of_unit_triggering_reaction[0][1]
        primary_player.move_unit_to_planet(planet_pos, unit_pos, dest)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Shrieking Exarch":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 1)
        secondary_player.draw_card()
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Mars Alpha Exterminator":
        primary_player.destroy_card_in_play(planet_pos, unit_pos)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Hydrae Stalker":
        primary_player.assign_damage_to_pos(planet_pos, unit_pos, 2)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()
    elif name_effect == "Scorpion Striker":
        primary_player.exhaust_given_pos(planet_pos, unit_pos, card_effect=True)
        self.mask_jain_zar_check_reactions(secondary_player, primary_player)
        self.delete_reaction()
        self.complete_intercept()


