import os

current_dir = os.path.dirname(__file__)

first_deck_location = os.path.join(current_dir, 'decksForTests/sample_deck_1.txt')
second_deck_location = os.path.join(current_dir, 'decksForTests/sample_deck_2.txt')
eldorath_deck_location = os.path.join(current_dir, "decksForTests/StarbaneCore.txt")
shadowsun_deck_location = os.path.join(current_dir, "decksForTests/ShadowsunCore.txt")

with open(first_deck_location, 'r') as file:
    deck_content_1 = file.read()
with open(second_deck_location, 'r') as file:
    deck_content_2 = file.read()

with open(os.path.join(current_dir, 'decksForTests/CatoCore.txt')) as file:
    cato_deck_content = file.read()
with open(os.path.join(current_dir, 'decksForTests/OOE.txt')) as file:
    ooe_deck_content = file.read()
with open(os.path.join(current_dir, 'decksForTests/NazdregCore.txt')) as file:
    nazdreg_deck_content = file.read()
with open(eldorath_deck_location, 'r') as file:
    eldorath_deck_content = file.read()
with open(shadowsun_deck_location, 'r') as file:
    shadowsun_deck_content = file.read()
with open(os.path.join(current_dir, 'decksForTests/StrakenCore.txt')) as file:
    straken_deck_content = file.read()
with open(os.path.join(current_dir, 'decksForTests/ZarathurCore.txt')) as file:
    zarathur_deck_content = file.read()
with open(os.path.join(current_dir, 'decksForTests/KithCore.txt')) as file:
    kith_deck_content = file.read()