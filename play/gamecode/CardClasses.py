import copy


class Card:
    def __init__(self, name, text, traits, cost, faction, loyalty, shields, card_type, unique, image_name="",
                 applies_discounts=None, action_in_hand=False, allowed_phases_in_hand=None,
                 action_in_play=False, allowed_phases_in_play=None, is_faction_limited_unique_discounter=False,
                 limited=False, ambush=False, deepstrike=-1):
        if applies_discounts is None:
            applies_discounts = [False, 0, False]
        self.name_owner = ""
        self.can_retreat = True
        self.name = name
        self.ability = name
        self.text = text
        self.blanked_eop = False
        self.traits = traits
        self.cost = cost
        self.faction = faction
        self.loyalty = loyalty
        self.shields = shields
        self.card_type = card_type
        self.valid_target_vow_of_honor = False
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
        self.once_per_round_used = False
        self.once_per_combat_round_used = False
        self.aiming_reticle_color = None
        self.bloodied = False
        self.is_faction_limited_unique_discounter = is_faction_limited_unique_discounter
        self.limited = limited
        self.counter = 0
        self.emperor_champion_active = False
        self.sacrifice_end_of_phase = False
        self.has_hive_mind = False
        self.resolving_attack = False
        self.misc_ability_used = False
        self.mind_shackle_scarab_effect = False
        self.valid_defense_battery_target = False
        self.ethereal_movement_active = False
        self.valid_kugath_nurgling_target = False
        self.damage_from_kugath_nurgling = 0
        self.extra_traits_eop = ""
        self.ambush = ambush
        self.attachments = []
        self.deepstrike = deepstrike
        self.immortal_loyalist_ok = True
        self.salamanders_flamers_id_number = 0
        self.hit_by_which_salamanders = []
        self.techmarine_aspirant_available = True
        self.lost_keywords_eop = False
        self.cannot_ready_phase = False
        self.follower_of_gork_available = True
        self.once_per_game_used = False
        self.from_magus_harid = False
        self.from_deck = True
        self.valid_target_dynastic_weaponry = False

    def get_has_deepstrike(self):
        if self.deepstrike == -1:
            return False
        return True

    def get_deepstrike_value(self):
        return self.deepstrike

    def get_attachments(self):
        return self.attachments

    def add_attachment(self, attachment_card, name_owner="", is_magus=False):
        self.attachments.append(copy.deepcopy(attachment_card))
        self.attachments[-1].name_owner = name_owner
        self.attachments[-1].from_magus_harid = is_magus

    def get_damage(self):
        return 0

    def get_indirect_damage(self):
        return 0

    def reset_own_eocr_values(self):
        pass

    def get_once_per_round_used(self):
        return self.once_per_round_used

    def set_once_per_round_used(self, new_val):
        self.once_per_round_used = new_val

    def get_ambush(self):
        return self.ambush

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
        if self.blanked_eop:
            return "BLANKED"
        if bloodied_relevant:
            if self.bloodied:
                return self.ability + " BLOODIED"
        return self.ability

    def set_blanked(self, new_val, exp="EOP"):
        if exp == "EOP":
            self.blanked_eop = new_val

    def reset_blanked_eop(self):
        self.blanked_eop = False

    def get_blanked(self):
        return self.blanked_eop

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
        extra_traits = ""
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Lucky Warpaint":
                extra_traits += "Blue."
            if self.attachments[i].get_ability() == "Autarch Powersword":
                if self.get_card_type() == "Army":
                    extra_traits += "Warrior. Psyker."
            if self.attachments[i].get_ability() == "Great Iron Gob":
                extra_traits += "Nob."
        return trait_to_find in (self.traits + self.extra_traits_eop + extra_traits)

    def get_image_name(self):
        return self.image_name

    def get_cost(self, urien_relevant=False):
        if urien_relevant:
            if self.card_type == "Event":
                if self.check_for_a_trait("Torture"):
                    return self.cost - 1
                return self.cost + 1
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
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Flesh Hooks":
                return None
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
                 mobile=False, ambush=False, hive_mind=False, unstoppable=False, deepstrike=-1,
                 lumbering=False):
        super().__init__(name, text, traits, cost, faction, loyalty, 0,
                         card_type, unique, image_name, applies_discounts, action_in_hand, allowed_phases_in_hand,
                         action_in_play, allowed_phases_in_play, limited, deepstrike=deepstrike)
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
        self.extra_attack_until_end_of_game = 0
        self.positive_hp_until_eog = 0
        self.by_base_ranged = ranged
        self.ranged = ranged
        self.wargear_attachments_permitted = wargear_attachments_permitted
        self.no_attachments = no_attachments
        self.additional_resources_command_struggle = additional_resources_command_struggle
        self.additional_cards_command_struggle = additional_cards_command_struggle
        self.ambush = ambush
        self.shadowed_thorns_venom_valid = False
        self.reaction_available = True
        self.hit_by_superiority = False
        self.has_hive_mind = hive_mind
        self.brutal_eocr = False
        self.armorbane_eop = False
        self.area_effect_eop = 0
        self.brutal_eop = False
        self.ranged_eop = False
        self.mobile_eop = False
        self.flying_eop = False
        self.area_effect_eor = 0
        self.area_effect_eocr = 0
        self.mobile_eor = False
        self.armorbane_eor = False
        self.negative_hp_until_eop = 0
        self.positive_hp_until_eop = 0
        self.positive_hp_until_eob = 0
        self.extra_command_eop = 0
        self.choice_nurgling_bomb = ""
        self.need_to_resolve_nurgling_bomb = False
        self.valid_target_ashen_banner = False
        self.attack_set_eop = -1
        self.unstoppable = unstoppable
        self.lost_ranged_eop = False
        self.lumbering = lumbering
        self.valid_target_magus_harid = False

    def get_lumbering(self):
        if self.blanked_eop:
            return False
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Traumatophobia":
                return True
        return self.lumbering

    def exhaust_first_attachment_name(self, card_name):
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == card_name:
                if self.attachments[i].get_ready():
                    self.attachments[i].exhaust_card()
                    return None
        return None

    def get_indirect_and_direct_damage(self):
        return self.damage + self.not_yet_assigned_damage

    def get_unstoppable(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        return self.unstoppable

    def get_has_hive_mind(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        return self.hive_mind

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
        if self.lost_keywords_eop:
            return False
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

    def increase_extra_health_until_end_of_phase(self, amount):
        self.positive_hp_until_eop += amount

    def reset_extra_attack_until_next_attack(self):
        self.extra_attack_until_next_attack = 0

    def get_available_mobile(self):
        return self.available_mobile

    def set_available_mobile(self, new_val):
        self.available_mobile = new_val

    def get_by_base_mobile(self):
        return self.by_base_mobile

    def get_mobile(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        if self.mobile_eop:
            return True
        if self.mobile_eor:
            return True
        if self.get_ability() == "Vectored Vyper Squad":
            if self.damage == 0:
                return True
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Mobility":
                return True
        return self.mobile

    def get_additional_resources_command_struggle(self):
        if self.blanked_eop:
            return 0
        return self.additional_resources_command_struggle

    def get_additional_cards_command_struggle(self):
        if self.blanked_eop:
            return 0
        return self.additional_cards_command_struggle

    def get_no_attachments(self):
        return self.no_attachments

    def get_wargear_attachments_permitted(self):
        return self.wargear_attachments_permitted

    def get_attachments(self):
        return self.attachments

    def add_attachment(self, attachment_card, name_owner="", is_magus=False):
        self.attachments.append(copy.deepcopy(attachment_card))
        self.attachments[-1].name_owner = name_owner
        self.attachments[-1].from_magus_harid = is_magus

    def set_ranged(self, new_val):
        self.ranged = new_val

    def get_ranged(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        if self.lost_ranged_eop:
            return False
        if self.ranged_eop:
            return True
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Rokkit Launcha":
                return True
            if self.attachments[i].get_ability() == "Bladed Lotus Rifle":
                if self.check_for_a_trait("Kabalite"):
                    return True
        return self.ranged

    def get_ignores_flying(self):
        if self.blanked_eop:
            return False
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Godwyn Pattern Bolter":
                return True
        return False

    def reset_ranged(self):
        self.ranged = self.by_base_ranged

    def get_by_base_armorbane(self):
        return self.by_base_armorbane

    def get_armorbane(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        if self.armorbane_eop:
            return True
        if self.armorbane_eor:
            return True
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Tallassarian Tempest Blade":
                return True
            if self.attachments[i].get_ability() == "Hyperphase Sword":
                return True
            if self.attachments[i].get_ability() == "Starcannon":
                return True
            if self.attachments[i].get_ability() == "Goff Big Choppa":
                return True
            if self.attachments[i].get_ability() == "The Butcher's Nails":
                if self.bloodied:
                    return True
        return self.armorbane

    def get_by_base_area_effect(self):
        return self.by_base_area_effect

    def get_area_effect(self):
        if self.blanked_eop:
            return 0
        if self.lost_keywords_eop:
            return 0
        area_effect = self.area_effect
        area_effect += self.area_effect_eop
        area_effect += self.area_effect_eor
        area_effect += self.area_effect_eocr
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Gun Drones":
                area_effect += 2
            if self.attachments[i].get_ability() == "Predatory Instinct":
                area_effect += 1
        if self.get_ability() == "Sa'cea XV88 Broadside":
            if self.attachments:
                area_effect += 2
        return area_effect

    def get_by_base_flying(self):
        return self.by_base_flying

    def get_flying(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        if self.flying_eop:
            return True
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "Valkyris Pattern Jump Pack":
                return True
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

    def reset_extra_health_until_end_of_battle(self):
        self.positive_hp_until_eob = 0

    def remove_damage(self, amount):
        self.damage = self.damage - amount
        if self.damage < 0:
            self.damage = 0

    def reset_own_eocr_values(self):
        self.brutal_eocr = False
        self.area_effect_eocr = 0

    def get_brutal(self):
        if self.blanked_eop:
            return False
        if self.lost_keywords_eop:
            return False
        if self.brutal_eocr:
            return True
        if self.brutal_eop:
            return True
        for i in range(len(self.attachments)):
            if self.attachments[i].get_ability() == "The Butcher's Nails":
                if not self.bloodied:
                    return True
        return self.brutal

    def set_brutal(self, new_val):
        self.brutal = new_val

    def reset_brutal(self):
        self.brutal = self.by_base_brutal

    def get_extra_attack_until_end_of_game(self):
        return self.extra_attack_until_end_of_game

    def get_extra_health_until_end_of_game(self):
        return self.positive_hp_until_eog

    def increase_extra_attack_until_end_of_game(self, value):
        self.extra_attack_until_end_of_game += value

    def increase_extra_health_until_end_of_game(self, value):
        self.positive_hp_until_eog += value

    def get_attack(self):
        attack = self.attack
        attack += self.get_extra_attack_until_end_of_battle()
        attack += self.get_extra_attack_until_next_attack()
        attack += self.get_extra_attack_until_end_of_phase()
        attack += self.get_extra_attack_until_end_of_game()
        for i in range(len(self.attachments)):
            if self.attachments[i].get_card_type() == "Attachment":
                if not self.attachments[i].from_magus_harid:
                    attack += self.attachments[i].get_extra_attack()
            elif self.attachments[i].get_ability() == "Shadowsun's Stealth Cadre":
                attack += 2
        if self.get_ability() == "Fire Warrior Strike Team":
            attack += len(self.attachments)
        return attack

    def get_health(self):
        health = self.health
        health -= self.negative_hp_until_eop
        health += self.positive_hp_until_eop
        health += self.positive_hp_until_eob
        health += self.positive_hp_until_eog
        for i in range(len(self.attachments)):
            if self.attachments[i].get_card_type() == "Attachment":
                if not self.attachments[i].from_magus_harid:
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
        command += self.extra_command_eop
        if self.hit_by_superiority:
            return 0
        for i in range(len(self.attachments)):
            if self.attachments[i].get_card_type() == "Attachment":
                if not self.attachments[i].from_magus_harid:
                    command += self.attachments[i].get_extra_command()
            if self.attachments[i].get_ability() == "Auxiliary Armor":
                if self.get_faction() != "Tau":
                    command += 1
        if self.get_ability() == "Bad Dok" and self.damage > 0:
            command = command + 3
        return command

    def damage_card(self, player, amount, can_shield=True, reassign=False):
        self.assign_damage(amount)
        if self.check_health():
            print("Card still standing")
            return 0
        else:
            print("Damage exceeds health")
            return 1

    def assign_damage(self, amount):
        self.damage = self.damage + amount

    def check_health(self):
        if self.get_health() > self.damage:
            return 1
        else:
            return 0


class WarlordCard(UnitCard):
    def __init__(self, name, text, traits, faction, attack, health, bloodied_attack, bloodied_health, bloodied_text,
                 starting_cards, starting_resources, signature_squad, image_name="", brutal=False, flying=False,
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
        self.area_effect = 0
        self.health = self.bloodied_health
        self.attack = self.bloodied_attack
        self.text = self.bloodied_text
        self.bloodied = True
        if self.name == "Baharroth":
            self.mobile = False

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


class SynapseCard(UnitCard):
    def __init__(self, name, text, traits, attack, health, command, unique,
                 action_in_play=False, allowed_phases_in_play=""):
        super().__init__(name, text, traits, -1, "Tyranids", "Loyal", "Synapse", attack, health, command, unique,
                         action_in_play=action_in_play, allowed_phases_in_play=allowed_phases_in_play)


class ArmyCard(UnitCard):
    def __init__(self, name, text, traits, cost, faction, loyalty, attack, health, command, unique,
                 image_name="", brutal=False, flying=False, armorbane=False, area_effect=0,
                 applies_discounts=None, action_in_hand=False,
                 allowed_phases_in_hand=None, action_in_play=False, allowed_phases_in_play=None,
                 limited=False, ranged=False, wargear_attachments_permitted=True, no_attachments=False,
                 additional_cards_command_struggle=0, additional_resources_command_struggle=0, mobile=False,
                 ambush=False, hive_mind=False, unstoppable=False, deepstrike=-1, lumbering=False):
        super().__init__(name, text, traits, cost, faction, loyalty, "Army", attack, health, command,
                         unique, image_name, brutal, flying, armorbane, area_effect,
                         applies_discounts, action_in_hand, allowed_phases_in_hand,
                         action_in_play, allowed_phases_in_play, limited, ranged=ranged,
                         wargear_attachments_permitted=wargear_attachments_permitted, no_attachments=no_attachments,
                         additional_cards_command_struggle=additional_cards_command_struggle,
                         additional_resources_command_struggle=additional_resources_command_struggle, mobile=mobile,
                         ambush=ambush, hive_mind=hive_mind, unstoppable=unstoppable, deepstrike=deepstrike,
                         lumbering=lumbering)

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
                 limited=False, deepstrike=-1):
        super().__init__(name, text, traits, cost, faction, loyalty,
                         shields, "Event", unique, image_name, applies_discounts, action_in_hand
                         , allowed_phases_in_hand, action_in_play, allowed_phases_in_play,
                         limited=limited, deepstrike=deepstrike)

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
                 extra_command=0, required_traits="", forbidden_traits="NO FORBIDDEN TRAITS",
                 planet_attachment=False, ambush=False, blue_required=False, green_required=False, red_required=False,
                 deepstrike=-1):
        super().__init__(name, text, traits, cost, faction, loyalty,
                         shields, "Attachment", unique, applies_discounts=applies_discounts,
                         action_in_hand=action_in_hand, allowed_phases_in_hand=allowed_phases_in_hand,
                         action_in_play=action_in_play, allowed_phases_in_play=allowed_phases_in_play,
                         limited=limited, ambush=ambush, deepstrike=deepstrike)
        self.type_of_units_allowed_for_attachment = type_of_units_allowed_for_attachment
        self.unit_must_be_unique = unit_must_be_unique
        self.unit_must_match_faction = unit_must_match_faction
        self.must_be_own_unit = must_be_own_unit
        self.must_be_enemy_unit = must_be_enemy_unit
        self.limit_one_per_unit = limit_one_per_unit
        self.extra_attack = extra_attack
        self.extra_health = extra_health
        self.extra_command = extra_command
        self.required_traits = required_traits
        self.forbidden_traits = forbidden_traits
        self.planet_attachment = planet_attachment
        self.blue_required = blue_required
        self.red_required = red_required
        self.green_required = green_required
        self.defense_battery_activated = False

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
