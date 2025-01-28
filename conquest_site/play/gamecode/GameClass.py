from . import PlayerClass
import random
from .Phases import DeployPhase, CommandPhase, CombatPhase, HeadquartersPhase


def create_planets(planet_array_objects):
    planet_names = []
    for i in range(10):
        string = planet_array_objects[i].get_name()
        planet_names.append(string)
    random.shuffle(planet_names)
    planets_in_play_return = []
    for i in range(7):
        planets_in_play_return.append(planet_names[i])
    return planets_in_play_return


class Game:
    def __init__(self, player_one_name, player_two_name):
        self.name_1 = player_one_name
        self.name_2 = player_two_name
        self.stored_deck_1 = None
        self.stored_deck_2 = None
        self.p1 = None
        self.p2 = None
        self.phase = ""
        self.round_number = 0
        self.current_board_state = ""
        self.running = True
