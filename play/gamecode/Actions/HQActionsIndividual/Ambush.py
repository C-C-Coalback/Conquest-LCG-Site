from ...Phases import DeployPhase

async def ambush(self, name, game_update_string, primary_player):
    if not self.omega_ambush_active:
        if self.card_type_of_selected_card_in_hand == "Attachment":
            await DeployPhase.deploy_card_routine_attachment(self, name, game_update_string, True)
    else:
        await self.send_mistarget_message(primary_player.name_player, "Invalid Target", "Subject Omega can only ambush cards at infested planets.")