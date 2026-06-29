import json
from pathlib import Path
from asgiref.sync import async_to_sync
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from play.consumers import create_bot_game, get_active_games, get_lobbies, join_lobby_for_player, persist_runtime_state
from play import turn_notifier
from decks.consumers import deck_check_and_save
import os


def _json_error(error_message, status=400, **extra):
    response = {
        "status": "error",
        "error": error_message
    }
    response.update(extra)
    return JsonResponse(response, status=status)


def _extract_request_data(request):
    data = {}
    content_type = request.content_type or ""
    if request.method == "POST" and "application/json" in content_type:
        try:
            decoded_body = request.body.decode("utf-8").strip()
            if decoded_body:
                parsed = json.loads(decoded_body)
                if isinstance(parsed, dict):
                    data = parsed
        except (UnicodeDecodeError, json.JSONDecodeError):
            data = {}
    if not data:
        data = request.POST.dict()
    return data

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SKILLS_ROOT = _PROJECT_ROOT / "skills"
_SKILL_FILENAMES = {"skill.md", "skills.md"}


def _collect_skill_files():
    if not _SKILLS_ROOT.exists():
        return []
    discovered_files = []
    for markdown_file in _SKILLS_ROOT.rglob("*.md"):
        if markdown_file.name.lower() in _SKILL_FILENAMES:
            discovered_files.append(markdown_file)
    discovered_files.sort(key=lambda file_path: str(file_path.relative_to(_SKILLS_ROOT)))
    return discovered_files


def _serialize_skill_file(skill_file_path, include_content=True):
    relative_repo_path = skill_file_path.relative_to(_PROJECT_ROOT).as_posix()
    relative_skill_path = skill_file_path.relative_to(_SKILLS_ROOT)
    skill_id = relative_skill_path.parent.as_posix()
    if not skill_id or skill_id == ".":
        skill_id = skill_file_path.stem.lower()
    payload = {
        "skill_id": skill_id,
        "filename": skill_file_path.name,
        "path": relative_repo_path,
        "content_url": f"/api/skills/{skill_id}/",
    }
    if include_content:
        try:
            payload["content"] = skill_file_path.read_text(encoding="utf-8")
        except Exception:
            payload["content"] = ""
            payload["content_error"] = "Unable to read skill file"
    return payload


def _get_serialized_skills(include_content=True):
    skill_files = _collect_skill_files()
    return [_serialize_skill_file(skill_file_path, include_content=include_content) for skill_file_path in skill_files]


def _normalize_username(username):
    return str(username).strip().lower()


def _ai_control_is_restricted():
    return bool(getattr(settings, "AI_CONTROL_ENFORCE_ALLOWED_USERNAMES", False))


def _get_allowed_ai_usernames():
    configured = getattr(settings, "AI_CONTROL_ALLOWED_USERNAMES", ())
    if isinstance(configured, str):
        configured = [configured]
    allowed = set()
    for username in configured:
        normalized_username = _normalize_username(username)
        if normalized_username:
            allowed.add(normalized_username)
    return allowed


def _validate_ai_control_player(player):
    if not _ai_control_is_restricted():
        return None
    allowed_usernames = _get_allowed_ai_usernames()
    if not allowed_usernames:
        return _json_error(
            "AI control account restriction is enabled but no allowed usernames are configured",
            status=500,
        )
    normalized_player = _normalize_username(player)
    if normalized_player not in allowed_usernames:
        return _json_error(
            "Player is not allowed for AI control endpoints",
            status=403,
            player=player,
            allowed_ai_accounts=sorted(allowed_usernames),
        )
    return None


def _find_game(game_id):
    active_games = get_active_games()
    for game in active_games:
        if game.game_id == game_id:
            return game
    return None


def _is_finished_game(game):
    phase = getattr(game, "phase", "")
    if isinstance(phase, str) and phase.startswith("FIN"):
        return True
    try:
        if game.p1.is_the_winner or game.p2.is_the_winner:
            return True
    except Exception:
        pass
    return False


def _safe_call(obj, method_name, *args, default=None):
    if obj is None:
        return default
    method = getattr(obj, method_name, None)
    if callable(method):
        try:
            return method(*args)
        except Exception:
            return default
    return default


def _serialize_card_name(card):
    if isinstance(card, str):
        return card
    card_name = _safe_call(card, "get_name", default=None)
    if card_name is not None:
        return card_name
    return str(card)


def _serialize_attachment(attachment):
    return {
        "name": _serialize_card_name(attachment),
        "ability": _safe_call(attachment, "get_ability", default=""),
        "ready": bool(_safe_call(attachment, "get_ready", default=False)),
        "owner": getattr(attachment, "name_owner", ""),
        "counter": getattr(attachment, "counter", None),
        "once_per_round_used": bool(getattr(attachment, "once_per_round_used", False)),
        "from_magus_harid": bool(getattr(attachment, "from_magus_harid", False)),
    }


def _get_attachments_for_unit(player, planet_pos, unit_pos):
    try:
        if planet_pos == -2:
            card = player.headquarters[unit_pos]
        else:
            card = player.cards_in_play[planet_pos + 1][unit_pos]
    except Exception:
        return []
    attachments = _safe_call(card, "get_attachments", default=[])
    if attachments is None:
        return []
    return [_serialize_attachment(a) for a in attachments]


def _serialize_unit(player, planet_pos, unit_pos):
    return {
        "planet": planet_pos,
        "index": unit_pos,
        "name": _safe_call(player, "get_name_given_pos", planet_pos, unit_pos, default=""),
        "card_type": _safe_call(player, "get_card_type_given_pos", planet_pos, unit_pos, default=""),
        "faction": _safe_call(player, "get_faction_given_pos", planet_pos, unit_pos, default=""),
        "traits": _safe_call(player, "get_traits_given_pos", planet_pos, unit_pos, default=""),
        "ability": _safe_call(player, "get_ability_given_pos", planet_pos, unit_pos, default=""),
        "ready": bool(_safe_call(player, "get_ready_given_pos", planet_pos, unit_pos, default=False)),
        "damage": _safe_call(player, "get_damage_given_pos", planet_pos, unit_pos, default=0),
        "health": _safe_call(player, "get_health_given_pos", planet_pos, unit_pos, default=0),
        "attack": _safe_call(player, "get_attack_given_pos", planet_pos, unit_pos, default=0),
        "ranged": bool(_safe_call(player, "get_ranged_given_pos", planet_pos, unit_pos, default=False)),
        "mobile": bool(_safe_call(player, "get_mobile_given_pos", planet_pos, unit_pos, default=False)),
        "armorbane": bool(_safe_call(player, "get_armorbane_given_pos", planet_pos, unit_pos, default=False)),
        "brutal": bool(_safe_call(player, "get_brutal_given_pos", planet_pos, unit_pos, default=False)),
        "bloodied": bool(_safe_call(player, "get_bloodied_given_pos", planet_pos, unit_pos, default=False)),
        "faith": _safe_call(player, "get_faith_given_pos", planet_pos, unit_pos, default=0),
        "attachments": _get_attachments_for_unit(player, planet_pos, unit_pos),
        "aiming_reticle": _safe_call(player, "get_aiming_reticle_given_pos", planet_pos, unit_pos, default=None),
    }


def _serialize_units_at_planet(player, planet_pos):
    try:
        number_of_units = len(player.cards_in_play[planet_pos + 1])
    except Exception:
        number_of_units = 0
    return [_serialize_unit(player, planet_pos, i) for i in range(number_of_units)]


def _serialize_hq(player):
    try:
        number_of_units = len(player.headquarters)
    except Exception:
        number_of_units = 0
    return [_serialize_unit(player, -2, i) for i in range(number_of_units)]


def _serialize_player(player):
    reserves_at_planets = []
    for planet_index in range(7):
        reserve_cards = []
        try:
            reserve_cards = player.cards_in_reserve[planet_index]
        except Exception:
            reserve_cards = []
        reserves_at_planets.append([_serialize_card_name(c) for c in reserve_cards])
    return {
        "name": player.name_player,
        "number": player.number,
        "resources": player.resources,
        "hand": list(player.cards),
        "hand_count": len(player.cards),
        "deck": list(player.deck),
        "deck_count": len(player.deck),
        "discard": list(player.discard),
        "removed": list(player.cards_removed_from_game),
        "victory_display": [_serialize_card_name(c) for c in player.victory_display],
        "headquarters": _serialize_hq(player),
        "units_at_planets": [_serialize_units_at_planet(player, i) for i in range(7)],
        "attachments_at_planets": [
            [_serialize_attachment(a) for a in player.attachments_at_planet[i]] for i in range(7)
        ],
        "reserves_at_planets": reserves_at_planets,
        "reserves_hq": [_serialize_card_name(c) for c in player.cards_in_reserve_hq],
        "has_initiative": player.has_initiative,
        "has_initiative_for_battle": player.has_initiative_for_battle,
        "has_passed": player.has_passed,
        "deck_loaded": player.deck_loaded,
        "committed_warlord": player.committed_warlord,
        "warlord_location": _safe_call(player, "get_location_of_warlord", default=(-1, -1)),
        "cardback_name": player.cardback_name,
    }


def _serialize_planets(game):
    planets = []
    for i in range(7):
        planet_name = game.planet_array[i]
        if not game.planets_in_play_array[i]:
            planet_name = "CardbackRotated"
        planets.append({
            "index": i,
            "name": planet_name,
            "in_play": bool(game.planets_in_play_array[i]),
            "infested": bool(game.infested_planets[i]),
            "is_current_first_planet": bool(game.round_number == i),
            "aiming_reticle": bool(game.planet_aiming_reticle_active and game.planet_aiming_reticle_position == i),
            "player_1_units": _serialize_units_at_planet(game.p1, i),
            "player_2_units": _serialize_units_at_planet(game.p2, i),
            "player_1_planet_attachments": [_serialize_attachment(a) for a in game.p1.attachments_at_planet[i]],
            "player_2_planet_attachments": [_serialize_attachment(a) for a in game.p2.attachments_at_planet[i]],
        })
    return planets


def _serialize_search_and_choices(game):
    return {
        "choices_available": list(game.choices_available),
        "choice_context": game.choice_context,
        "choice_player": game.name_player_making_choices,
        "show_choices_as_images": list(game.show_choices_as_images),
        "search_cards": list(game.cards_in_search_box),
        "search_player": game.name_player_who_is_searching,
        "search_target_context": game.what_to_do_with_searched_card,
        "search_card_type_filter": game.card_type_of_searched_card,
        "search_faction_filter": game.faction_of_searched_card,
        "search_trait_filter": game.traits_of_searched_card,
        "search_max_cost_filter": game.max_cost_of_searched_card,
        "searching_enemy_deck": bool(game.searching_enemy_deck),
    }


def _normalize_action_token(action):
    action = str(action).strip()
    if action.startswith("BUTTON PRESSED/"):
        action = action[len("BUTTON PRESSED/"):]
    if action.startswith("AUTOMATED_CHOICE/"):
        split_action = action.split("/", 2)
        if len(split_action) == 3:
            action = split_action[2]
    if action.startswith("/"):
        action = action[1:]
    return action


def _coerce_action_token(action, legal_actions):
    if action in legal_actions:
        return action
    if action == "pass":
        if "pass-P1" in legal_actions:
            return "pass-P1"
        if "pass-P2" in legal_actions:
            return "pass-P2"
    return action

def _append_game_event_log(game, player, action_parts):
    game.game_events_as_mono_string += player + "|||" + "/".join(action_parts) + "\n"


def _apply_action_window_between_combat_turns(game, player, action_token):
    _append_game_event_log(game, player, ["SpecialAction", action_token])
    if action_token == "pass-P1" or action_token == "pass-P2":
        if player == game.name_1:
            game.automated_1_has_passed_action = True
        elif player == game.name_2:
            game.automated_2_has_passed_action = True
        return
    _append_game_event_log(game, player, ["action-button"])
    async_to_sync(game.update_game_event)(player, ["action-button"], same_thread=True)
    game.automated_1_has_passed_action = False
    game.automated_2_has_passed_action = False
    async_to_sync(game.update_game_event)(player, action_token.split("/"))


def _apply_special_action_token(game, player, action_token):
    resolved_action = action_token[len("SPECIAL_ACTION_"):].strip()
    if not resolved_action:
        return
    action_parts = resolved_action.split("/")
    _append_game_event_log(game, player, ["action-button"])
    _append_game_event_log(game, player, action_parts)
    async_to_sync(game.update_game_event)(player, ["action-button"], same_thread=True)
    async_to_sync(game.update_game_event)(player, action_parts)


def _apply_agent_action(game, player, action_token):
    if game.what_is_required_automated == "Action Window Between Combat Turns":
        _apply_action_window_between_combat_turns(game, player, action_token)
        return
    if action_token.startswith("SPECIAL_ACTION_"):
        _apply_special_action_token(game, player, action_token)
        return
    _append_game_event_log(game, player, action_token.split("/"))
    async_to_sync(game.update_game_event)(player, action_token.split("/"))


def _get_game_snapshot(game, requested_player=""):
    game.condition_main_game.acquire()
    try:
        async_to_sync(game.update_automated_info)()
        try:
            turn_notifier.maybe_notify_turn_changed(game)
        except Exception:
            pass
        legal_actions = list(game.clickable_items_automated)
        active_player = game.automated_player_waited_on
        requested_player_is_active = bool(requested_player and requested_player == active_player)
        event_log_lines = game.game_events_as_mono_string.splitlines()
        state = {
            "game_id": game.game_id,
            "phase": game.phase,
            "mode": game.mode,
            "round_number": game.round_number,
            "sector": game.sector,
            "bot_is_present": bool(game.bot_is_present),
            "players": {
                "1": _serialize_player(game.p1),
                "2": _serialize_player(game.p2),
            },
            "planets": _serialize_planets(game),
            "turn": {
                "player_with_initiative": game.player_with_initiative,
                "player_with_deploy_turn": game.player_with_deploy_turn,
                "player_with_combat_turn": game.player_with_combat_turn,
                "active_player": active_player,
                "required_action_type": game.what_is_required_automated,
                "battle_in_progress": bool(game.battle_in_progress),
                "ranged_skirmish_active": bool(game.ranged_skirmish_active),
                "last_planet_checked_for_battle": game.last_planet_checked_for_battle,
            },
            "interaction": {
                "requested_player": requested_player,
                "requested_player_is_active": requested_player_is_active,
                "legal_actions": legal_actions,
                "legal_actions_for_requested_player": legal_actions if requested_player_is_active else [],
                "action_token_format": "Use one token from legal_actions exactly (examples: pass-P1, CHOICE/0, IN_PLAY/1/2/0).",
            },
            "search_and_choices": _serialize_search_and_choices(game),
            "chat_messages": list(game.chat_messages),
            "event_log_tail": event_log_lines[-300:],
            "saved_replay_moves_count": len(game.saved_moves),
            "saved_replay_index": game.saved_move_id,
        }
    finally:
        game.condition_main_game.release()
    return state


def index(request):
    return JsonResponse({
        "status": "success",
        "endpoints": {
            "skills": "/api/skills/",
            "skill_detail": "/api/skills/<skill_id>/",
            "lobbies": "/api/lobbies/",
            "join_lobby": "/api/join_lobby/",
            "games": "/api/games/",
            "create_bot_room": "/api/create_bot_room/",
            "game_state": "/api/game/<game_id>/agent_state/?player=<player_name>",
            "game_action": "/api/game/<game_id>/agent_action/",
            "game_command": "/api/game/<game_id>/agent_command/",
            "game_webhooks": "/api/games/<game_id>/webhooks/",
        },
        "ai_control_account_policy": {
            "enforced": _ai_control_is_restricted(),
            "allowed_usernames": sorted(_get_allowed_ai_usernames()),
        },
    })


def skills(request):
    include_content = str(request.GET.get("include_content", "true")).strip().lower() not in ["0", "false", "no"]
    serialized_skills = _get_serialized_skills(include_content=include_content)
    return JsonResponse({
        "status": "success",
        "skills": serialized_skills,
        "count": len(serialized_skills),
    })


def skill_detail(request, skill_id):
    skill_id = str(skill_id).strip().strip("/")
    if not skill_id:
        return _json_error("Missing required path parameter: skill_id", status=400)
    serialized_skills = _get_serialized_skills(include_content=True)
    for skill in serialized_skills:
        if skill["skill_id"] == skill_id:
            return JsonResponse({
                "status": "success",
                "skill": skill,
            })
    return _json_error("Skill not found", status=404, skill_id=skill_id)

def lobbies(request):
    active_lobbies, spectator_games = get_lobbies()
    lobby_rows = []
    for i in range(len(active_lobbies[0])):
        lobby_id = ""
        if len(active_lobbies) > 9 and i < len(active_lobbies[9]):
            lobby_id = active_lobbies[9][i]
        lobby_rows.append({
            "host_player": active_lobbies[0][i],
            "guest_player": active_lobbies[1][i],
            "visibility": active_lobbies[2][i],
            "errata": active_lobbies[3][i],
            "sector": active_lobbies[4][i],
            "host_deck": active_lobbies[5][i],
            "guest_deck": active_lobbies[6][i],
            "created_at": active_lobbies[7][i],
            "first_player_decider": active_lobbies[8][i],
            "lobby_id": lobby_id,
        })
    spectator_rows = []
    for game in spectator_games:
        end_time = game[3]
        end_time_string = str(end_time)
        if hasattr(end_time, "isoformat"):
            end_time_string = end_time.isoformat()
        spectator_rows.append({
            "player_1": game[0],
            "player_2": game[1],
            "game_id": game[2],
            "expires_at": end_time_string,
        })
    return JsonResponse({
        "status": "success",
        "lobbies": lobby_rows,
        "spectator_games": spectator_rows,
    })


@csrf_exempt
def join_lobby(request):
    if request.method != "POST":
        return _json_error("Only POST requests allowed", status=405)
    data = _extract_request_data(request)
    lobby_id = str(data.get("lobby_id", data.get("id", ""))).strip()
    host_player = str(data.get("host_player", data.get("host", ""))).strip()
    guest_player = str(data.get("guest_player", data.get("player", ""))).strip()
    guest_deck = str(data.get("guest_deck", data.get("deck", ""))).strip()
    join_result = join_lobby_for_player(host_player, guest_player, guest_deck=guest_deck, lobby_id=lobby_id)
    status_code = int(join_result.get("http_status", 200))
    response = dict(join_result)
    if "http_status" in response:
        del response["http_status"]
    return JsonResponse(response, status=status_code)


def games(request):
    all_games = get_active_games()
    summaries = []
    for game in all_games:
        if _is_finished_game(game):
            continue
        async_to_sync(game.update_automated_info)()
        summaries.append({
            "game_id": game.game_id,
            "player_1": game.name_1,
            "player_2": game.name_2,
            "phase": game.phase,
            "mode": game.mode,
            "round_number": game.round_number,
            "active_player": game.automated_player_waited_on,
            "required_action_type": game.what_is_required_automated,
            "legal_action_count": len(game.clickable_items_automated),
            "bot_is_present": bool(game.bot_is_present),
        })
    return JsonResponse({
        "status": "success",
        "games": summaries,
    })


def agent_state(request, game_id):
    game = _find_game(game_id)
    if game is None:
        return _json_error("Game not found", status=404, game_id=game_id)
    requested_player = request.GET.get("player", "").strip()
    if requested_player:
        account_error = _validate_ai_control_player(requested_player)
        if account_error is not None:
            return account_error
    return JsonResponse({
        "status": "success",
        "game": _get_game_snapshot(game, requested_player=requested_player),
    })


@csrf_exempt
def agent_action(request, game_id):
    if request.method != "POST":
        return _json_error("Only POST requests allowed", status=405)
    game = _find_game(game_id)
    if game is None:
        return _json_error("Game not found", status=404, game_id=game_id)
    data = _extract_request_data(request)
    player = str(data.get("player", "")).strip()
    action = str(data.get("action", "")).strip()
    if not player:
        return _json_error("Missing required field: player")
    account_error = _validate_ai_control_player(player)
    if account_error is not None:
        return account_error
    if player not in [game.name_1, game.name_2]:
        return _json_error("Player is not part of this game", player=player, game_id=game_id)
    if not action:
        return _json_error("Missing required field: action")
    async_to_sync(game.update_automated_info)()
    active_player = game.automated_player_waited_on
    legal_actions = list(game.clickable_items_automated)
    normalized_action = _normalize_action_token(action)
    normalized_action = _coerce_action_token(normalized_action, legal_actions)
    if player != active_player:
        return _json_error(
            "Player is not currently active",
            active_player=active_player,
            legal_actions=legal_actions
        )
    if normalized_action not in legal_actions:
        return _json_error(
            "Action is not legal in current game state",
            attempted_action=normalized_action,
            legal_actions=legal_actions
        )
    try:
        _apply_agent_action(game, player, normalized_action)
    except Exception as e:
        return _json_error("Failed to apply action", status=500, details=str(e))
    persist_runtime_state()
    return JsonResponse({
        "status": "success",
        "applied_action": normalized_action,
        "game": _get_game_snapshot(game, requested_player=player),
    })


@csrf_exempt
def agent_command(request, game_id):
    if request.method != "POST":
        return _json_error("Only POST requests allowed", status=405)
    game = _find_game(game_id)
    if game is None:
        return _json_error("Game not found", status=404, game_id=game_id)
    data = _extract_request_data(request)
    player = str(data.get("player", "")).strip()
    command = str(data.get("command", "")).strip()
    if not player:
        return _json_error("Missing required field: player")
    account_error = _validate_ai_control_player(player)
    if account_error is not None:
        return account_error
    if player not in [game.name_1, game.name_2]:
        return _json_error("Player is not part of this game", player=player, game_id=game_id)
    if not command:
        return _json_error("Missing required field: command")
    if command.startswith("/"):
        command = command[1:]
    split_command = [x for x in command.split("/") if x]
    if not split_command:
        return _json_error("Command cannot be empty")
    try:
        async_to_sync(game.resolve_chat_message)(player, [""] + split_command)
    except Exception as e:
        return _json_error("Failed to apply command", status=500, details=str(e))
    persist_runtime_state()
    return JsonResponse({
        "status": "success",
        "applied_command": split_command,
        "game": _get_game_snapshot(game, requested_player=player),
    })


@csrf_exempt
def webhook_subscriptions(request, game_id):
    game = _find_game(game_id)
    if game is None:
        return _json_error("Game not found", status=404, game_id=game_id)
    if request.method == "GET":
        return JsonResponse({
            "status": "success",
            "game_id": game_id,
            "webhooks": turn_notifier.get_webhooks(game),
        })
    if request.method == "DELETE":
        data = _extract_request_data(request) if request.body else request.GET.dict()
        subscription_id = str(data.get("id", "")).strip()
        if not subscription_id:
            return _json_error("Missing required field: id")
        removed = turn_notifier.remove_webhook(game, subscription_id)
        if not removed:
            return _json_error("Subscription not found", status=404, id=subscription_id)
        return JsonResponse({"status": "success", "removed": subscription_id})
    if request.method != "POST":
        return _json_error("Only GET/POST/DELETE requests allowed", status=405)
    data = _extract_request_data(request)
    url = str(data.get("url", "")).strip()
    if not url:
        return _json_error("Missing required field: url")
    events_raw = data.get("events", "turn")
    if isinstance(events_raw, str):
        events = [item.strip() for item in events_raw.split(",") if item.strip()]
    elif isinstance(events_raw, list):
        events = [str(item).strip() for item in events_raw if str(item).strip()]
    else:
        events = ["turn"]
    try:
        descriptor = turn_notifier.register_webhook(game, url, events=events)
    except ValueError as e:
        return _json_error(str(e))
    return JsonResponse({
        "status": "success",
        "subscription": descriptor,
        "webhooks": turn_notifier.get_webhooks(game),
    }, status=201)


@csrf_exempt
def create_bot_room(request):
    if request.method != "POST":
        return _json_error("Only POST requests allowed", status=405)
    data = _extract_request_data(request)
    try:
        bot_name_1 = data["name1"]
        bot_name_2 = data["name2"]
        for bot_name in [bot_name_1, bot_name_2]:
            account_error = _validate_ai_control_player(bot_name)
            if account_error is not None:
                return account_error
        game_id = data["id"]
        private = str(data.get("private", "False")).lower() in ["true", "1", "yes"]
        errata = str(data.get("errata", "No Errata"))
        sector = str(data.get("sector", "Traxis Sector"))
        deck_1 = str(data.get("deck1", ""))
        deck_2 = str(data.get("deck2", ""))
        game_id = create_bot_game(
            bot_name_1,
            bot_name_2,
            game_id,
            errata,
            sector=sector,
            deck_1=deck_1,
            deck_2=deck_2,
            private=private
        )
        response = {
            "status": "success",
            "id": game_id
        }
    except KeyError as e:
        response = {
            "status": "error",
            "error": f"Missing required field: {str(e)}"
        }
    except Exception as e:
        response = {
            "status": "error",
            "error": "server error 500",
            "details": str(e)
        }
    return JsonResponse(response)


@csrf_exempt
def receive_raw_deck_text(request):
    if request.method != "POST":
        return _json_error("Only POST requests allowed", status=405)
    data = _extract_request_data(request)
    try:
        bot_name = data["name"]
        deck = data["deck_text"]
        account_error = _validate_ai_control_player(bot_name)
        if account_error is not None:
            return account_error
        print(deck)
        result_of_saving = deck_check_and_save(bot_name, deck)
        response = {
            "status": result_of_saving["message"]
        }
    except KeyError as e:
        response = {
            "status": "error",
            "error": f"Missing required field: {str(e)}"
        }
    except Exception as e:
        response = {
            "status": "error",
            "error": "server error 500",
            "details": str(e)
        }
    return JsonResponse(response)


@csrf_exempt
def request_deck_text_given_name(request):
    if request.method != "POST":
        return _json_error("Only POST requests allowed", status=405)
    data = _extract_request_data(request)
    try:
        bot_name = data["name"]
        deck_name = data["deck_name"]
        account_error = _validate_ai_control_player(bot_name)
        if account_error is not None:
            return account_error
        target_deck_dir = os.getcwd() + "/decks/DeckStorage/" + bot_name + "/" + deck_name
        if not os.path.exists(target_deck_dir):
            response = {
                "status": "error",
                "error": "Deck does not exist"
            }
        else:
            with open(target_deck_dir, "r") as file:
                deck_text = file.read()
            response = {
                "status": "success",
                "deck_text": deck_text
            }
    except KeyError as e:
        response = {
            "status": "error",
            "error": f"Missing required field: {str(e)}"
        }
    except Exception as e:
        response = {
            "status": "error",
            "error": "server error 500",
            "details": str(e)
        }
    return JsonResponse(response)
