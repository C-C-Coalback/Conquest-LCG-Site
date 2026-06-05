import update_settings
import os

for username in os.listdir("user_preferences_storage"):
    if ".json" not in username:
        username = username.replace(".txt", "")
        update_settings.convert_settings_text_file_to_json(username)
