ability_targets_dictionary = {
    "Exterminatus": {
        "Num Stages": 1,
        "Type 1": "Planet",
        "Restrictions 1": {
            "Non-first": True,
            "Icons": None,
            "Not Same Planet": False
        }
    },
    "Veteran Brother Maxos": {
        "Num Stages": 1,
        "Type 1": "Hand",
        "Restrictions 1": {
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
        "Num Stages": 1,
        "Type 1": "Unit",
        "Restrictions 1": {
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
            "Target": False,
            "Ability Type": "Interrupt"
        }
    },
    "Cato's Stronghold": {
        "Num Stages": 1,
        "Type 1": "Unit",
        "Restrictions 1": {
            "Unit Only": True,
            "Own Unit": False,
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
            "Target": True,
            "Ability Type": "Reaction"
        }
    },
    "Sicarius's Chosen": {
        "Num Stages": 1,
        "Type 1": "Unit",
        "Restrictions 1": {
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
            "Target": True,
            "Ability Type": "Reaction"
        }
    },
    "Ferrin": {
        "Num Stages": 1,
        "Type 1": "Unit",
        "Restrictions 1": {
            "Unit Only": True,
            "Own Unit": True,
            "Enemy Unit": True,
            "Unique": False,
            "Ready": False,
            "Exhaust": False,
            "Faction": None,
            "Card Type": None,
            "Forbidden Card Type": "Warlord",
            "Required Traits": [],
            "Forbidden Traits": [],
            "Special": False,
            "Target": True,
            "Ability Type": "Planet"
        }
    },
    "Plannum": {
        "Num Stages": 2,
        "Type 1": "Unit",
        "Restrictions 1": {
            "Unit Only": True,
            "Own Unit": True,
            "Enemy Unit": False,
            "Unique": False,
            "Ready": False,
            "Exhaust": False,
            "Faction": None,
            "Card Type": None,
            "Forbidden Card Type": "Warlord",
            "Required Traits": [],
            "Forbidden Traits": [],
            "Special": True,
            "Target": False,
            "Ability Type": "Planet"
        },
        "Type 2": "Planet",
        "Restrictions 2": {
            "Non-first": False,
            "Icons": None,
            "Not Same Planet": False,
            "Not Same Planet Unit": True,
        }
    },
    "Carnath": {
        "Num Stages": 1,
        "Type 1": "Planet",
        "Restrictions 1": {
            "Non-first": False,
            "Icons": None,
            "Not Same Planet": True,
            "Not Same Planet Unit": False
        }
    },
    "Y'varn": {
        "Num Stages": 1,
        "Type 1": "Hand",
        "Restrictions 1": {
            "Faction": None,
            "Card Type": "Army",
            "Max Cost": None,
            "Payment": False,
            "Card Enters Play": True,
        }
    },
    "Iridial": {
        "Num Stages": 1,
        "Type 1": "Unit",
        "Restrictions 1": {
            "Unit Only": True,
            "Own Unit": True,
            "Enemy Unit": True,
            "Unique": False,
            "Ready": False,
            "Exhaust": False,
            "Faction": None,
            "Card Type": None,
            "Forbidden Card Type": None,
            "Required Traits": [],
            "Forbidden Traits": [],
            "Special": False,
            "Target": True,
            "Ability Type": "Planet"
        }
    },
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
