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
    def __init__(self, game_id, player_one_name, player_two_name, card_array):
        self.game_sockets = []
        self.card_array = card_array
        self.game_id = game_id
        self.name_1 = player_one_name
        self.name_2 = player_two_name
        self.stored_deck_1 = None
        self.stored_deck_2 = None
        self.p1 = PlayerClass.Player(player_one_name, 1, card_array, self)
        self.p2 = PlayerClass.Player(player_two_name, 2, card_array, self)
        self.phase = ""
        self.round_number = 0
        self.current_board_state = ""
        self.running = True
        self.planet_array = ["Barlus", "Osus IV", "Ferrin", "Elouith", "Iridial", "Y'varn", "Atrox Prime"]

    async def joined_requests_graphics(self):
        await self.p1.send_hand()
        await self.p2.send_hand()

    async def send_planet_array(self):
        planet_string = "GAME_INFO/PLANETS/" + "/".join(self.planet_array)
        await self.game_sockets[0].receive_game_update(planet_string)
