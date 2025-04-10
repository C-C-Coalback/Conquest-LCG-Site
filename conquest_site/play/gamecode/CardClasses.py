import copy


class Card:
    def __init__(self, name, text, traits, cost, faction, loyalty, shields, card_type, unique, image_name="",
                 applies_discounts=None, action_in_hand=False, allowed_phases_in_hand=None,
                 action_in_play=False, allowed_phases_in_play=None, is_faction_limited_unique_discounter=False,
                 limited=False):
        if applies_discounts is None:
            applies_discounts = [False, 0, False]
        self.name = name
        self.ability = name
        self.text = text
        self.blanked = False
        self.traits = traits
        self.cost = cost
        self.faction = faction
        self.loyalty = loyalty
        self.shields = shields
        self.card_type = card_type
        self.is_unit = False
        if self.card_type == "Army" or self.card_type == "Warlord"\
                or self.card_type == "Token" or self.card_type == "Synapse":
            self.is_unit = True
        self.unique = unique
        self.ready = True
        self.image_name = image_name
        self.applies_discounts = applies_discounts[0]
        self.discount_amount = applies_discounts[1]
        self.discount_match_factions = applies_discounts[2]
        self.has_action_while_in_hand = action_in_hand
        self.allowed_phases_while_in_hand = allowed_phases_in_hand
        self.has_action_while_in_play = action_in_play
        self.allowed_phases_while_in_play = allowed_phases_in_play
        self.once_per_phase_used = False
        self.aiming_reticle_color = None
        self.bloodied = False
        self.is_faction_limited_unique_discounter = is_faction_limited_unique_discounter
        self.limited = limited
        self.counter = 0
        self.sacrifice_end_of_phase = False

    def get_ambush(self):
        return False

    def set_sacrifice_end_of_phase(self, new_val):
        self.sacrifice_end_of_phase = new_val

    def get_sacrifice_end_of_phase(self):
        return self.sacrifice_end_of_phase

    def get_is_unit(self):
        return self.is_unit

    def set_available_mobile(self, new_val):
        return None

    def get_counter(self):
        return self.counter

    def set_counter(self, new_val):
        self.counter = new_val

    def increment_counter(self):
        self.counter += 1

    def decrement_counter(self):
        self.counter -= 1

    def get_limited(self):
        return self.limited

    def get_name(self):
        return self.name

    def get_ability(self, bloodied_relevant=False):
        if self.blanked:
            return "BLANKED"
        if bloodied_relevant:
            if self.bloodied:
                return "BLOODIED"
        return self.ability

    def set_blanked(self, new_val):
        self.blanked = new_val

    def get_blanked(self):
        return self.blanked

    def get_is_faction_limited_unique_discounter(self):
        return self.is_faction_limited_unique_discounter

    def get_once_per_phase_used(self):
        return self.once_per_phase_used

    def set_once_per_phase_used(self, value):
        self.once_per_phase_used = value

    def get_has_action_while_in_play(self):
        return self.has_action_while_in_play

    def get_allowed_phases_while_in_play(self):
        return self.allowed_phases_while_in_play

    def get_has_action_while_in_hand(self):
        return self.has_action_while_in_hand

    def get_allowed_phases_while_in_hand(self):
        return self.allowed_phases_while_in_hand

    def get_applies_discounts(self):
        return self.applies_discounts

    def get_discount_amount(self):
        return self.discount_amount

    def get_discount_match_factions(self):
        return self.discount_match_factions

    def get_text(self):
        return self.text

    def get_traits(self):
        return self.traits

    def check_for_a_trait(self, trait_to_find):
        return trait_to_find in self.traits

    def get_image_name(self):
        return self.image_name

    def get_cost(self):
        return self.cost

    def get_faction(self):
        return self.faction

    def get_loyalty(self):
        return self.loyalty

    def get_shields(self):
        return self.shields

    def get_card_type(self):
        return self.card_type

    def get_unique(self):
        return self.unique

    def get_ready(self):
        return self.ready

    def ready_card(self):
        self.ready = True

    def exhaust_card(self):
        self.ready = False

    def print_info(self):
        print("If you are seeing this the card is the error handling card.")


class UnitCard(Card):
    def __init__(self, name, text, traits, cost, faction, loyalty, card_type, attack, health, command,
                 unique, image_name="", brutal=False, flying=False, armorbane=False, area_effect=0,
                 applies_discounts=None, action_in_hand=False
                 , allowed_phases_in_hand=None, action_in_play=False, allowed_phases_in_play=None,
                 limited=False, ranged=False, wargear_attachments_permitted=True, no_attachments=False,
                 additional_resources_command_struggle=0, additional_cards_command_struggle=0,
                 mobile=False, ambush=False):
        super().__init__(name, text, traits, cost, faction, loyalty, 0,
                         card_type, unique, image_name, applies_discounts, action_in_hand, allowed_phases_in_hand,
                         action_in_play, allowed_phases_in_play, limited)
        self.attack = attack
        self.health = health
        self.damage = 0
        self.not_yet_assigned_damage = 0
        self.command = command
        self.attachments = []
        self.by_base_brutal = brutal
        self.brutal = brutal
        self.by_base_flying = flying
        self.flying = flying
        self.by_base_armorbane = armorbane
        self.armorbane = armorbane
        self.by_base_mobile = mobile
        self.mobile = mobile
        self.available_mobile = False
        self.by_base_area_effect = area_effect
        self.area_effect = area_effect
        self.extra_attack_until_end_of_battle = 0
        self.extra_attack_until_next_attack = 0
        self.extra_attack_until_end_of_phase = 0
        self.by_base_ranged = ranged
        self.ranged = ranged
        self.wargear_attachments_permitted = wargear_attachments_permitted
        self.no_attachments = no_attachments
        self.additional_resources_command_struggle = additional_resources_command_struggle
        self.additional_cards_command_struggle = additional_cards_command_struggle
        self.ambush = ambush
        self.reaction_available = True

    def get_reaction_available(self):
        return self.reaction_available

    def set_reaction_available(self, new_val):
        self.reaction_available = new_val

    def get_indirect_damage(self):
        return self.not_yet_assigned_damage

    def increase_not_yet_assigned_damage(self, amount):
        self.not_yet_assigned_damage += amount

    def reset_indirect_damage(self):
        self.not_yet_assigned_damage = 0

    def get_ambush(self):
        return self.ambush

    def get_extra_attack_until_end_of_phase(self):
        return self.extra_attack_until_end_of_phase

    def increase_extra_attack_until_end_of_phase(self, amount):
        self.extra_attack_until_end_of_phase += amount

    def reset_extra_attack_until_end_of_phase(self):
        self.extra_attack_until_end_of_phase = 0

    def get_extra_attack_until_next_attack(self):
        return self.extra_attack_until_next_attack

    def increase_extra_attack_until_next_attack(self, amount):
        self.extra_attack_until_next_attack += amount

    def reset_extra_attack_until_next_attack(self):
        self.extra_attack_until_next_attack = 0

    def get_available_mobile(self):
        return self.available_mobile

    def set_available_mobile(self, new_val):
        self.available_mobile = new_val

    def get_by_base_mobile(self):
        return self.by_base_mobile

    def get_mobile(self):
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Mobility":
                return True
        return self.mobile

    def get_additional_resources_command_struggle(self):
        return self.additional_resources_command_struggle

    def get_additional_cards_command_struggle(self):
        return self.additional_cards_command_struggle

    def get_no_attachments(self):
        return self.no_attachments

    def get_wargear_attachments_permitted(self):
        return self.wargear_attachments_permitted

    def get_attachments(self):
        return self.attachments

    def add_attachment(self, attachment_card):
        print("Adding attachment to:", self.name)
        print(attachment_card.name)
        self.attachments.append(copy.deepcopy(attachment_card))
        for i in range(len(self.attachments)):
            print(self.attachments[i].get_name())

    def set_ranged(self, new_val):
        self.ranged = new_val

    def get_ranged(self):
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Rokkit Launcha":
                return True
        return self.ranged

    def get_ignores_flying(self):
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Godwyn Pattern Bolter":
                return True
        return False

    def reset_ranged(self):
        self.ranged = self.by_base_ranged

    def get_by_base_armorbane(self):
        return self.by_base_armorbane

    def get_armorbane(self):
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Tallassarian Tempest Blade":
                return True
        return self.armorbane

    def get_by_base_area_effect(self):
        return self.by_base_area_effect

    def get_area_effect(self):
        area_effect = self.area_effect
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Gun Drones":
                area_effect += 2
        return area_effect

    def get_by_base_flying(self):
        return self.by_base_flying

    def get_flying(self):
        return self.flying

    def set_flying(self, new_val):
        self.flying = new_val

    def get_by_base_brutal(self):
        return self.by_base_brutal

    def get_extra_attack_until_end_of_battle(self):
        return self.extra_attack_until_end_of_battle

    def increase_extra_attack_until_end_of_battle(self, amount):
        self.extra_attack_until_end_of_battle += amount

    def reset_extra_attack_until_end_of_battle(self):
        self.extra_attack_until_end_of_battle = 0

    def remove_damage(self, amount):
        self.damage = self.damage - amount
        if self.damage < 0:
            self.damage = 0

    def get_brutal(self):
        return self.brutal

    def set_brutal(self, new_val):
        self.brutal = new_val

    def reset_brutal(self):
        self.brutal = self.by_base_brutal

    def get_attack(self):
        attack = self.attack
        for i in range(len(self.attachments)):
            if self.attachments[i].get_card_type() == "Attachment":
                attack += self.attachments[i].get_extra_attack()
            elif self.attachments[i].get_ability() == "Shadowsun's Stealth Cadre":
                attack += 2
        if self.get_ability() == "Fire Warrior Strike Team":
            attack += len(self.attachments)
        return attack

    def get_health(self):
        health = self.health
        for i in range(len(self.attachments)):
            if self.attachments[i].get_card_type() == "Attachment":
                health += self.attachments[i].get_extra_health()
            elif self.attachments[i].get_ability() == "Shadowsun's Stealth Cadre":
                health += 2
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Cybork Body":
                health = 2 * health
        return health

    def get_damage(self):
        return self.damage

    def set_damage(self, amount):
        self.damage = amount

    def get_command(self):
        command = self.command
        for i in range(len(self.attachments)):
            if self.attachments[i].get_card_type() == "Attachment":
                command += self.attachments[i].get_extra_command()
        if self.name == "Bad Dok" and self.damage > 0:
            command = command + 3
        return command

    def damage_card(self, player, amount, can_shield=True):
        self.assign_damage(amount)
        if self.check_health():
            print("Card still standing")
            return 0
        else:
            print("Damage exceeds health")
            return 1

    def assign_damage(self, amount):
        if amount > 0:
            if self.get_ability() == "Blood Angels Veterans":
                if self.get_ready():
                    amount = amount - 1
        self.damage = self.damage + amount

    def check_health(self):
        if self.get_health() > self.damage:
            return 1
        else:
            return 0


class WarlordCard(UnitCard):
    def __init__(self, name, text, traits, faction, attack, health, bloodied_attack, bloodied_health, bloodied_text,
                 starting_resources, starting_cards, signature_squad, image_name="", brutal=False, flying=False,
                 armorbane=False, area_effect=0,
                 applies_discounts=None, action_in_hand=False, allowed_phases_in_hand=None,
                 action_in_play=False, allowed_phases_in_play=None, ranged=False,
                 wargear_attachments_permitted=True, no_attachments=False, mobile=False):
        super().__init__(name, text, traits, -1, faction, "Signature", "Warlord", attack, health, 999,
                         True, image_name, brutal, flying, armorbane, area_effect,
                         applies_discounts, action_in_hand, allowed_phases_in_hand,
                         action_in_play, allowed_phases_in_play, ranged=ranged,
                         wargear_attachments_permitted=wargear_attachments_permitted,
                         no_attachments=no_attachments, additional_cards_command_struggle=0,
                         additional_resources_command_struggle=0, mobile=mobile)
        self.bloodied = False
        self.bloodied_attack = bloodied_attack
        self.bloodied_health = bloodied_health
        self.bloodied_text = bloodied_text
        self.starting_resources = starting_resources
        self.starting_cards = starting_cards
        self.signature_squad = signature_squad

    def get_signature_squad(self):
        return self.signature_squad

    def get_bloodied_state(self):
        return self.bloodied

    def get_bloodied_attack(self):
        return self.bloodied_attack

    def get_bloodied_health(self):
        return self.bloodied_health

    def get_bloodied_text(self):
        return self.bloodied_text

    def get_bloodied(self):
        return self.bloodied

    def get_starting_resources(self):
        return self.starting_resources

    def get_starting_cards(self):
        return self.starting_cards

    def bloody_warlord(self):
        self.damage = 0
        self.health = self.bloodied_health
        self.attack = self.bloodied_attack
        self.text = self.bloodied_text
        self.bloodied = True

    def print_info(self):
        if self.unique:
            print("Name: *", self.name)
        else:
            print("Name:", self.name)
        print("Type:", self.card_type)
        print("Faction:", self.faction)
        print("Traits:", self.traits)
        print("Resources:", self.starting_resources, "\nCards:", self.starting_cards)
        if not self.bloodied:
            print("Text:", self.text, "\nStats:", self.attack, "Attack,", self.health, "Health")
        else:
            print("Text:", self.bloodied_text, "\nStats:", self.bloodied_attack, "Attack,",
                  self.bloodied_health, "Health")


class ArmyCard(UnitCard):
    def __init__(self, name, text, traits, cost, faction, loyalty, attack, health, command, unique,
                 image_name="", brutal=False, flying=False, armorbane=False, area_effect=0,
                 applies_discounts=None, action_in_hand=False,
                 allowed_phases_in_hand=None, action_in_play=False, allowed_phases_in_play=None,
                 limited=False, ranged=False, wargear_attachments_permitted=True, no_attachments=False,
                 additional_cards_command_struggle=0, additional_resources_command_struggle=0, mobile=False,
                 ambush=False):
        super().__init__(name, text, traits, cost, faction, loyalty, "Army", attack, health, command,
                         unique, image_name, brutal, flying, armorbane, area_effect,
                         applies_discounts, action_in_hand, allowed_phases_in_hand,
                         action_in_play, allowed_phases_in_play, limited, ranged=ranged,
                         wargear_attachments_permitted=wargear_attachments_permitted, no_attachments=no_attachments,
                         additional_cards_command_struggle=additional_cards_command_struggle,
                         additional_resources_command_struggle=additional_resources_command_struggle, mobile=mobile,
                         ambush=ambush)

    def print_info(self):
        if self.unique:
            print("Name: *", self.name)
        else:
            print("Name:", self.name)
        print("Type:", self.card_type)
        print("Faction:", self.faction)
        print("Cost:", self.cost)
        print("Traits:", self.traits)
        print("Loyalty:", self.loyalty)
        print("Text:", self.text, "\nStats:", self.attack, "Attack,", self.health, "Health,", self.command, "Command")


class EventCard(Card):
    def __init__(self, name, text, traits, cost, faction, loyalty,
                 shields, unique, image_name="", applies_discounts=None, action_in_hand=False
                 , allowed_phases_in_hand=None, action_in_play=False, allowed_phases_in_play=None,
                 limited=False):
        super().__init__(name, text, traits, cost, faction, loyalty,
                         shields, "Event", unique, image_name, applies_discounts, action_in_hand
                         , allowed_phases_in_hand, action_in_play, allowed_phases_in_play,
                         limited=limited)

    def print_info(self):
        if self.unique:
            print("Name: *", self.name)
        else:
            print("Name:", self.name)
        print("Type:", self.card_type)
        print("Faction:", self.faction)
        print("Cost:", self.cost)
        print("Traits:", self.traits)
        print("Loyalty:", self.loyalty)
        print("Shields:", self.shields)
        print("Text:", self.text)


class AttachmentCard(Card):
    def __init__(self, name, text, traits, cost, faction, loyalty,
                 shields, unique, image_name="", applies_discounts=None, action_in_hand=False
                 , allowed_phases_in_hand=None, action_in_play=False, allowed_phases_in_play=None,
                 limited=False, type_of_units_allowed_for_attachment="Army/Token/Warlord/Synapse",
                 unit_must_be_unique=False, unit_must_match_faction=False, must_be_own_unit=False,
                 must_be_enemy_unit=False, limit_one_per_unit=False, extra_attack=0, extra_health=0,
                 extra_command=0):
        super().__init__(name, text, traits, cost, faction, loyalty,
                         shields, "Attachment", unique, applies_discounts=applies_discounts,
                         action_in_hand=action_in_hand, allowed_phases_in_hand=allowed_phases_in_hand,
                         action_in_play=action_in_play, allowed_phases_in_play=allowed_phases_in_play,
                         limited=limited)
        self.type_of_units_allowed_for_attachment = type_of_units_allowed_for_attachment
        self.unit_must_be_unique = unit_must_be_unique
        self.unit_must_match_faction = unit_must_match_faction
        self.must_be_own_unit = must_be_own_unit
        self.must_be_enemy_unit = must_be_enemy_unit
        self.limit_one_per_unit = limit_one_per_unit
        self.extra_attack = extra_attack
        self.extra_health = extra_health
        self.extra_command = extra_command

    def get_extra_command(self):
        return self.extra_command

    def get_extra_attack(self):
        return self.extra_attack

    def get_extra_health(self):
        return self.extra_health

    def print_info(self):
        if self.unique:
            print("Name: *", self.name)
        else:
            print("Name:", self.name)
        print("Type:", self.card_type)
        print("Faction:", self.faction)
        print("Cost:", self.cost)
        print("Traits:", self.traits)
        print("Loyalty:", self.loyalty)
        print("Shields:", self.shields)
        print("Text:", self.text)


class SupportCard(Card):
    def __init__(self, name, text, traits, cost, faction, loyalty, unique, image_name="", applies_discounts=None
                 , action_in_hand=False, allowed_phases_in_hand=None,
                 action_in_play=False, allowed_phases_in_play=None, is_faction_limited_unique_discounter=False,
                 limited=False):
        super().__init__(name, text, traits, cost, faction, loyalty,
                         0, "Support", unique, image_name, applies_discounts, action_in_hand
                         , allowed_phases_in_hand, action_in_play, allowed_phases_in_play,
                         is_faction_limited_unique_discounter, limited)

    def get_attachments(self):
        return []

    def print_info(self):
        if self.unique:
            print("Name: *", self.name)
        else:
            print("Name:", self.name)
        print("Type:", self.card_type)
        print("Faction:", self.faction)
        print("Cost:", self.cost)
        print("Traits:", self.traits)
        print("Loyalty:", self.loyalty)
        print("Shields:", self.shields)
        print("Text:", self.text)


class TokenCard(UnitCard):
    def __init__(self, name, text, traits, faction, attack, health, applies_discounts=None,
                 no_attachments=False):
        super().__init__(name, text, traits, -1, faction, "Common", "Token",
                         attack, health, 0, False, applies_discounts=applies_discounts, action_in_hand=False,
                         allowed_phases_in_hand=None, action_in_play=False, allowed_phases_in_play=None,
                         ranged=False, wargear_attachments_permitted=True, no_attachments=no_attachments,
                         additional_resources_command_struggle=0, additional_cards_command_struggle=0, mobile=False)

    def print_info(self):
        print("Name:", self.name)
        print("Type:", self.card_type)
        print("Faction:", self.faction)
        print("Cost:", self.cost)
        print("Traits:", self.traits)
        print("Loyalty:", self.loyalty)
        print("Text:", self.text, "\nStats:", self.attack, "Attack,", self.health, "Health")


class PlanetCard:
    def __init__(self, name, text, cards, resources, red, blue, green, image_name):
        self.name = name
        self.text = text
        self.cards = cards
        self.resources = resources
        self.red = red
        self.blue = blue
        self.green = green
        self.image_name = image_name

    def get_name(self):
        return self.name

    def get_image_name(self):
        return self.image_name

    def get_text(self):
        return self.text

    def get_resources(self):
        return self.resources

    def get_cards(self):
        return self.cards

    def get_red(self):
        return self.red

    def get_blue(self):
        return self.blue

    def get_green(self):
        return self.green

    def print_info(self):
        print("Name:", self.name)
        print("Text:", self.text)
        print("Command:", self.resources, "resource(s),", self.cards, "card(s)")
        print("Icons:")
        if self.red:
            print("Red")
        if self.blue:
            print("Blue")
        if self.green:
            print("Green")
