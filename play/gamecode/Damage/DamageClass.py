class Damage:
    def __init__(self, damage_amount, preventable, position_unit, can_shield, position_attacker, context,
                 card_name_causing_damage=""):
        self.damage_amount = damage_amount
        self.preventable = preventable
        self.position_unit = position_unit
        self.can_shield = can_shield
        self.position_attacker = position_attacker
        self.context = context
        self.card_name_triggering_damage = card_name_causing_damage
        self.damage_taken_was_from_attack = False
        self.faction_of_attacker = ""
        self.card_name_that_caused_damage = card_name_causing_damage
        self.on_kill_effects_of_attacker = []

    def get_on_kill_effects_of_attacker(self):
        return self.on_kill_effects_of_attacker

    def get_card_name_triggering_damage(self):
        return self.card_name_triggering_damage

    def get_amount_that_can_be_blocked(self):
        return self.damage_amount

    def get_no_damage_left(self):
        return self.damage_amount <= 0

    def set_amount_that_can_be_blocked(self, new_val):
        self.damage_amount = new_val

    def decrease_amount_that_can_be_blocked(self, amount=1):
        self.damage_amount = self.damage_amount - amount
        return self.get_no_damage_left()

    def increase_amount_that_can_be_blocked(self, amount=1):
        self.damage_amount = self.damage_amount + amount

    def get_preventable(self):
        return self.preventable

    def get_position_attacker(self):
        return self.position_attacker

    def decrement_position_attacker(self):
        if self.position_attacker is not None:
            self.position_attacker = (self.position_attacker[0], self.position_attacker[1],
                                      self.position_attacker[2] - 1)

    def set_position_attacker(self, new_val):
        self.position_attacker = new_val

    def get_context(self):
        return self.context

    def get_can_shield(self):
        return self.can_shield

    def get_position_unit(self):
        return self.position_unit

    def set_position_unit(self, new_val):
        self.position_unit = new_val

    def decrement_position_unit(self):
        self.position_unit = (self.position_unit[0], self.position_unit[1], self.position_unit[2] - 1)
