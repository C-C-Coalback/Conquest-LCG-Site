import os
import json


valid_cardbacks = ["Cardback", "Space_Marines_Cardback", "Necrons_Cardback", "Chaos_Cardback", "Tyranids_Cardback",
                   "Orks_Cardback", "Astra_Militarum_Cardback", "Dark_Eldar_Cardback",
                   "Eldar_Cardback", "Tau_Cardback"]
valid_backgrounds = ["Imperial Aquila", "Heldrakes", "Box Art", "Death Guard", "Necrons Awakening",
                     "Chaos v Orks", "Tyranids v Tau"]


def convert_settings_text_file_to_json(username):
    if not os.path.exists(os.path.join(os.getcwd(), "user_preferences_storage/")):
        os.mkdir(os.path.join(os.getcwd(), "user_preferences_storage/"))
    cwd = os.getcwd()
    settings_file_txt = os.path.join(cwd, "user_preferences_storage/" + username + ".txt")
    zoom = "1.0"
    volume = "1.0"
    cardback = "Default"
    background = "Default"
    choices_box_h = "-1"
    choices_box_v = "-1"
    info_box_h = "-1"
    info_box_v = "-1"
    if os.path.exists(settings_file_txt):
        with open(settings_file_txt, "r") as f:
            contents = f.read()
            content_split = contents.split(sep="\n")
            while len(content_split) < 7:
                content_split.append("-1")
            zoom = content_split[0]
            cardback = content_split[1]
            background = content_split[2]
            choices_box_h = content_split[3]
            choices_box_v = content_split[4]
            info_box_h = content_split[5]
            info_box_v = content_split[6]
    json_dict_settings_data = {"zoom": zoom, "volume": volume, "cardback": cardback, "background": background,
                               "choices_box_h": choices_box_h, "choices_box_v": choices_box_v,
                               "info_box_h": info_box_h, "info_box_v": info_box_v}
    settings_file_json = os.path.join(cwd, "user_preferences_storage/" + username + ".json")
    with open(settings_file_json, "w") as f:
        json.dump(json_dict_settings_data, f)


def get_user_settings(username):
    if not os.path.exists(os.path.join(os.getcwd(), "user_preferences_storage/")):
        os.mkdir(os.path.join(os.getcwd(), "user_preferences_storage/"))
    settings_file_json = os.path.join(os.getcwd(), "user_preferences_storage/" + username + ".json")
    if not os.path.exists(settings_file_json):
        create_default_settings_file(username)
    with open(settings_file_json) as json_file:
        data = json.load(json_file)
    return data


def create_default_settings_file(username):
    if not os.path.exists(os.path.join(os.getcwd(), "user_preferences_storage/")):
        os.mkdir(os.path.join(os.getcwd(), "user_preferences_storage/"))
    json_dict_settings_data = {"zoom": "1.0", "volume": "1.0", "cardback": "Cardback", "background": "Imperial Aquila",
                               "choices_box_h": "-1", "choices_box_v": "-1",
                               "info_box_h": "-1", "info_box_v": "-1"}
    settings_file_json = os.path.join(os.getcwd(), "user_preferences_storage/" + username + ".json")
    with open(settings_file_json, "w") as f:
        json.dump(json_dict_settings_data, f)


def update_settings(username, zoom=None, volume=None, cardback=None, background=None,
                    choices_box_h=None, choices_box_v=None, info_box_h=None, info_box_v=None):
    if not os.path.exists(os.path.join(os.getcwd(), "user_preferences_storage/")):
        os.mkdir(os.path.join(os.getcwd(), "user_preferences_storage/"))
    cwd = os.getcwd()
    settings_file = os.path.join(cwd, "user_preferences_storage/" + username + ".json")
    if not os.path.exists(settings_file):
        create_default_settings_file(username)
    with open(settings_file) as json_file:
        data = json.load(json_file)
        if zoom is not None:
            data["zoom"] = str(zoom)
        if volume is not None:
            data["volume"] = str(volume)
        if cardback is not None:
            if cardback == "Default":
                cardback = "Cardback"
            else:
                cardback = cardback.replace(" ", "_") + "_Cardback"
            if cardback not in valid_cardbacks:
                cardback = "Cardback"
            else:
                cardback = cardback
            data["cardback"] = cardback
        if background is not None:
            if background not in valid_backgrounds:
                background = "Imperial Aquila"
            data["background"] = background
        if choices_box_h is not None:
            data["choices_box_h"] = choices_box_h
        if choices_box_v is not None:
            data["choices_box_v"] = choices_box_v
        if info_box_h is not None:
            data["info_box_h"] = info_box_h
        if info_box_v is not None:
            data["info_box_v"] = info_box_v
    with open(settings_file, "w") as json_file:
        json.dump(data, json_file)
