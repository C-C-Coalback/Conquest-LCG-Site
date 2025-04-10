async def update_game_event_command_section(self, name, game_update_string):
    print("Run warlord assignment code.")
    if len(game_update_string) == 2:
        if game_update_string[0] == "PLANETS":
            print("Save warlord to this planet")
            if name == self.name_1:
                if not self.p1.committed_warlord:
                    self.p1.warlord_commit_location = int(game_update_string[1])
                    self.p1.committed_warlord = True
            else:
                if not self.p2.committed_warlord:
                    self.p2.warlord_commit_location = int(game_update_string[1])
                    self.p2.committed_warlord = True
            if self.p1.committed_warlord and self.p2.committed_warlord:
                print("Both warlords need to be committed.")
                print(self.p1.warlord_commit_location, self.p2.warlord_commit_location)
                self.p1.commit_warlord_to_planet()
                self.p2.commit_warlord_to_planet()
                await self.p1.send_hq()
                await self.p2.send_hq()
                await self.send_planet_array()
                await self.p1.send_units_at_all_planets()
                await self.p2.send_units_at_all_planets()
                self.resolve_command_struggle()
                await self.p1.send_hand()
                await self.p2.send_hand()
                await self.p1.send_resources()
                await self.p2.send_resources()
                await self.p1.send_units_at_all_planets()
                await self.p2.send_units_at_all_planets()
                await self.change_phase("COMBAT")
                self.p1.set_available_mobile_all(True)
                self.p2.set_available_mobile_all(True)
                self.p1.mobile_resolved = False
                self.p2.mobile_resolved = False
                if not self.p1.search_cards_for_available_mobile():
                    self.p1.mobile_resolved = True
                if not self.p2.search_cards_for_available_mobile():
                    self.p2.mobile_resolved = True
                if self.p1.mobile_resolved and self.p2.mobile_resolved:
                    self.check_battle(self.round_number)
                    self.last_planet_checked_for_battle = self.round_number
                    self.set_battle_initiative()
                    self.planet_aiming_reticle_active = True
                    self.planet_aiming_reticle_position = self.last_planet_checked_for_battle
                    await self.send_planet_array()
                    self.p1.has_passed = False
                    self.p2.has_passed = False
                    await self.send_info_box()
