class Interrupt:
    def __init__(self, interrupt_name, player_name_resolving, position_trigger, additional_info):
        self.interrupt_name = interrupt_name
        self.name_player_resolving_interrupt = player_name_resolving
        self.position_unit_triggering_interrupt = position_trigger
        self.additional_interrupt_info = additional_info

    def get_interrupt_name(self):
        return self.interrupt_name

    def set_interrupt_name(self, new_val):
        self.interrupt_name = new_val

    def get_player_resolving_interrupt(self):
        return self.name_player_resolving_interrupt

    def set_player_resolving_interrupt(self, new_val):
        self.name_player_resolving_interrupt = new_val

    def get_position_unit(self):
        return self.get_position_unit_triggering()

    def get_position_unit_triggering(self):
        return self.position_unit_triggering_interrupt

    def set_position_unit_triggering(self, new_val):
        self.position_unit_triggering_interrupt = new_val

    def get_additional_interrupt_info(self):
        return self.additional_interrupt_info

    def set_additional_interrupt_info(self, new_val):
        self.additional_interrupt_info = new_val

    def get_number(self):
        return self.position_unit_triggering_interrupt[0]

    def get_planet_pos(self):
        return self.position_unit_triggering_interrupt[1]

    def get_unit_pos(self):
        return self.position_unit_triggering_interrupt[2]

    def check_position_unit(self, position_tuple):
        return self.position_unit_triggering_interrupt == position_tuple