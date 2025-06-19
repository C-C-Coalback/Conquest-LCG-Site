from PIL import Image
import os, glob
from play.gamecode import Initfunctions
from play.gamecode import FindCard


card_array = Initfunctions.init_player_cards()
cards_dict = {}
for key in range(len(card_array)):
    cards_dict[card_array[key].name] = card_array[key]


def crop_images(card_array, cards_dict):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = dir_path + '/staticfiles/images/CardImages/'
    output_path = dir_path + '/staticfiles/images/CroppedImages/'

    os.makedirs(output_path, exist_ok=True)
    for filename in glob.glob(path+"*.jpg"):
        base_name = os.path.basename(filename)
        current_image, ext = os.path.splitext(base_name)
        card_name = current_image.replace("_", " ")
        print("Cropping", card_name)
        card = FindCard.find_card(card_name, card_array, cards_dict)
        if card.get_card_type() != "Attachment":
            with Image.open(path + current_image + ".jpg") as im:
                width, height = im.size
                (left, upper, right, lower) = (0, 0, width, height * 0.59)
                im_crop = im.crop((left, upper, right, lower))
                im_crop = im_crop.convert("RGB")
                im_crop.save(output_path + current_image + ".jpg")
        else:
            with Image.open(path + current_image + ".jpg") as im:
                width, height = im.size
                (left, upper, right, lower) = (0, height * 0.05, width, height * 0.64)
                im_crop = im.crop((left, upper, right, lower))
                im_crop = im_crop.convert("RGB")
                im_crop.save(output_path + current_image + ".jpg")


crop_images(card_array, cards_dict)
