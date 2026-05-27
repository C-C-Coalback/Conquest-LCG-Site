ability_targets_dictionary = {
    "Exterminatus": {
        "Type": "Planet",
        "Restrictions": {
            "Non-first": True,
            "Icons": None
        }
    },
    "Veteran Brother Maxos": {
        "Type": "Hand",
        "Restrictions": {
            "Faction": "Space Marines",
            "Card Type": "Army",
            "Max Cost": None,
            "Payment": True,
            "Payment Details": {
                "Deploy": False
            },
            "Card Enters Play": True,
        }
    },
    "No Mercy": {
        "Type": "Unit",
        "Restrictions": {
            "Unit Only": True,
            "Own Unit": True,
            "Enemy Unit": False,
            "Unique": True,
            "Ready": True,
            "Exhaust": False,
            "Faction": None,
            "Card Type": None,
            "Forbidden Card Type": None,
            "Required Traits": [],
            "Forbidden Traits": [],
            "Special": False,
            "Ability Type": "Interrupt"
        }
    },
    "Cato's Stronghold": {
        "Type": "Unit",
        "Restrictions": {
            "Unit Only": True,
            "Own Unit": True,
            "Enemy Unit": False,
            "Unique": False,
            "Ready": False,
            "Exhaust": True,
            "Faction": "Space Marines",
            "Card Type": None,
            "Forbidden Card Type": None,
            "Required Traits": [],
            "Forbidden Traits": [],
            "Special": True,
            "Ability Type": "Reaction"
        }
    },
    "Sicarius's Chosen": {
        "Type": "Unit",
        "Restrictions": {
            "Unit Only": True,
            "Own Unit": False,
            "Enemy Unit": True,
            "Unique": False,
            "Ready": False,
            "Exhaust": False,
            "Faction": None,
            "Card Type": "Army",
            "Forbidden Card Type": None,
            "Required Traits": [],
            "Forbidden Traits": [],
            "Special": True,
            "Ability Type": "Reaction"
        }
    }
}

action_ability_starts = {
    "Veteran Brother Maxos": {
        "Special": False,
        "Requires Hand Card": True,
        "Attributes Hand Card": {
            "Faction": "Space Marines",
            "Card Type": "Army",
            "Max Cost": None,
            "Payment": True,
            "Payment Details": {
                "Deploy": False
            },
            "Card Enters Play": True,
        }
    }
}
