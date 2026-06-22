import datetime
import json
import os

import update_settings


DEFAULT_DECK_NAME = "custom"
MAX_MATCH_RECORDS = 200


def _settings_file_path(username):
    return os.path.join(os.getcwd(), "user_preferences_storage", username + ".json")


def _load_profile_data(username):
    data = update_settings.get_user_settings(username)
    if isinstance(data, dict):
        return data
    return {}


def _save_profile_data(username, data):
    with open(_settings_file_path(username), "w") as settings_file:
        json.dump(data, settings_file)


def _extract_deck_name_from_deck_string(deck_string):
    if not isinstance(deck_string, str):
        return DEFAULT_DECK_NAME
    lines = [line.strip() for line in deck_string.splitlines() if line.strip()]
    if len(lines) < 2:
        return DEFAULT_DECK_NAME
    if set(lines[1]) != {"-"}:
        return DEFAULT_DECK_NAME
    if lines[0]:
        return lines[0]
    return DEFAULT_DECK_NAME


def _is_profile_user(username):
    if not username:
        return False
    if username == "Anonymous":
        return False
    return True


def _calculate_wins_and_losses(match_record):
    wins = 0
    losses = 0
    for match in match_record:
        if not isinstance(match, dict):
            continue
        result = match.get("result", "")
        if result == "win":
            wins += 1
        elif result == "loss":
            losses += 1
    return wins, losses


def record_finished_game_result(game, winner_name, reason):
    if winner_name not in [game.name_1, game.name_2]:
        return
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    players_data = [
        (game.name_1, game.p1, game.p2),
        (game.name_2, game.p2, game.p1),
    ]
    for username, player, opponent in players_data:
        if not _is_profile_user(username):
            continue
        result = "loss"
        if username == winner_name:
            result = "win"
        profile_data = _load_profile_data(username)
        match_record = profile_data.get("match_record", [])
        if not isinstance(match_record, list):
            match_record = []
        match_record.append({
            "recorded_at": timestamp,
            "game_id": game.game_id,
            "result": result,
            "faction": player.warlord_faction or "Unknown",
            "opponent_faction": opponent.warlord_faction or "Unknown",
            "deck_name": _extract_deck_name_from_deck_string(player.deck_string),
            "reason": reason,
        })
        if len(match_record) > MAX_MATCH_RECORDS:
            match_record = match_record[-MAX_MATCH_RECORDS:]
        wins, losses = _calculate_wins_and_losses(match_record)
        profile_data["match_record"] = match_record
        profile_data["wins"] = wins
        profile_data["losses"] = losses
        _save_profile_data(username, profile_data)


def get_user_match_record(username, limit=50):
    profile_data = _load_profile_data(username)
    match_record = profile_data.get("match_record", [])
    if not isinstance(match_record, list):
        return []
    cleaned_record = [match for match in match_record if isinstance(match, dict)]
    if limit and limit > 0:
        cleaned_record = cleaned_record[-limit:]
    cleaned_record.reverse()
    return cleaned_record


def get_user_win_loss(username):
    profile_data = _load_profile_data(username)
    wins = profile_data.get("wins")
    losses = profile_data.get("losses")
    if isinstance(wins, int) and isinstance(losses, int):
        return wins, losses
    match_record = profile_data.get("match_record", [])
    if not isinstance(match_record, list):
        return 0, 0
    return _calculate_wins_and_losses(match_record)
