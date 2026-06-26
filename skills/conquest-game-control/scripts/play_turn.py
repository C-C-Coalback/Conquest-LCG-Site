#!/usr/bin/env python3
"""Autoplay helper for Conquest LCG REST agent endpoints.

This script watches a live game and automatically plays legal actions whenever
the configured player becomes active. It uses only the public REST API.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class Client:
    base_url: str
    timeout: float = 10.0

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    def _get_json(self, path: str, *, params: dict[str, str] | None = None) -> dict[str, Any]:
        response = requests.get(self._url(path), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(self._url(path), json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def list_games(self) -> list[dict[str, Any]]:
        payload = self._get_json("/api/games/")
        if payload.get("status") != "success":
            raise RuntimeError(f"Unexpected /api/games response: {payload}")
        games = payload.get("games", [])
        if not isinstance(games, list):
            raise RuntimeError(f"Malformed /api/games payload: {payload}")
        return games

    def get_state(self, game_id: str, player: str) -> dict[str, Any]:
        payload = self._get_json(f"/api/game/{game_id}/agent_state/", params={"player": player})
        if payload.get("status") != "success":
            raise RuntimeError(f"agent_state failed: {payload}")
        game = payload.get("game")
        if not isinstance(game, dict):
            raise RuntimeError(f"Malformed agent_state payload: {payload}")
        return game

    def send_command(self, game_id: str, player: str, command: str) -> dict[str, Any]:
        return self._post_json(
            f"/api/game/{game_id}/agent_command/",
            {"player": player, "command": command},
        )

    def send_action(self, game_id: str, player: str, action: str) -> dict[str, Any]:
        return self._post_json(
            f"/api/game/{game_id}/agent_action/",
            {"player": player, "action": action},
        )


def _slot_for_player(state: dict[str, Any], player: str) -> str:
    players = state.get("players", {})
    p1 = players.get("1", {}).get("name", "")
    if p1 == player:
        return "1"
    return "2"


def _choice_score(choice_text: str, context: str) -> int:
    text = (choice_text or "").strip().lower()
    ctx = (context or "").strip().lower()

    # Explicit opening-hand policy.
    if "mulligan opening hand" in ctx:
        if text == "no":
            return 100
        if text == "yes":
            return 0

    score = 0
    if text in ("yes", "confirm", "accept"):
        score += 15
    if text in ("no", "decline", "cancel"):
        score -= 12
    if "card" in text:
        score += 8
    if "resource" in text:
        score += 7
    if "retreat" in text:
        score -= 20
    if "concede" in text or "resign" in text:
        score -= 500
    return score


def _action_score(action: str, state: dict[str, Any]) -> int:
    interaction = state.get("interaction", {})
    legal = interaction.get("legal_actions_for_requested_player") or interaction.get("legal_actions") or []
    non_pass_exists = any("pass" not in str(item).lower() for item in legal)
    lower = action.lower()

    if "concede" in lower or "resign" in lower or "force-quit" in lower:
        return -10000

    score = 0
    if "pass" in lower:
        score -= 1000 if non_pass_exists else 0

    if action.startswith("SPECIAL_ACTION_"):
        score += 90
    if action.startswith("IN_PLAY/"):
        score += 80
    if action.startswith("HAND/"):
        score += 75
    if action.startswith("HQ/"):
        score += 55
    if action.startswith("PLANETS/"):
        score += 40
        split_action = action.split("/")
        if len(split_action) >= 2 and split_action[1].isdigit():
            idx = int(split_action[1])
            score += max(0, 10 - idx)
    if action.startswith("CHOICE/"):
        score += 45
        split_action = action.split("/")
        context = state.get("search_and_choices", {}).get("choice_context", "")
        choices = state.get("search_and_choices", {}).get("choices_available", [])
        if len(split_action) >= 2 and split_action[1].isdigit():
            idx = int(split_action[1])
            if 0 <= idx < len(choices):
                score += _choice_score(str(choices[idx]), str(context))

    if "attack" in lower:
        score += 40
    if "retreat" in lower:
        score -= 50

    return score


def _choose_action(state: dict[str, Any]) -> tuple[str | None, list[tuple[str, int]]]:
    interaction = state.get("interaction", {})
    legal = interaction.get("legal_actions_for_requested_player")
    if not legal:
        legal = interaction.get("legal_actions", [])
    if not legal:
        return None, []
    ranked = sorted(
        ((str(action), _action_score(str(action), state)) for action in legal),
        key=lambda item: item[1],
        reverse=True,
    )
    return ranked[0][0], ranked


def _discover_game_id(client: Client, player: str) -> str:
    candidate_games = []
    for game in client.list_games():
        player_1 = game.get("player_1", "")
        player_2 = game.get("player_2", "")
        if player not in (player_1, player_2):
            continue
        candidate_games.append(game)
    if not candidate_games:
        raise RuntimeError(f"No active game found for player '{player}'.")
    for game in candidate_games:
        if game.get("active_player", "") == player:
            return str(game.get("game_id", ""))
    return str(candidate_games[0].get("game_id", ""))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Watch a live Conquest game and autoplay legal actions when your player is active.",
    )
    parser.add_argument(
        "--player",
        default=os.environ.get("CONQUEST_AI_PLAYER", "basicai").strip(),
        help="Exact in-game player name (defaults to CONQUEST_AI_PLAYER or 'basicai').",
    )
    parser.add_argument("--game-id", default="", help="Target game ID. If omitted, auto-discovers by player name.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Server base URL.")
    parser.add_argument("--run-seconds", type=float, default=180.0, help="How long to watch for turns.")
    parser.add_argument("--max-actions", type=int, default=50, help="Max actions to submit before stopping.")
    parser.add_argument("--poll-interval", type=float, default=1.0, help="Sleep interval while waiting on opponent.")
    parser.add_argument("--post-action-sleep", type=float, default=0.35, help="Sleep interval after applying action.")
    parser.add_argument("--top-candidates", type=int, default=5, help="Number of scored actions to print per step.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds.")
    parser.add_argument("--no-debug-commands", action="store_true", help="Skip debug command injection.")
    parser.add_argument("--dry-run", action="store_true", help="Score and print actions but do not submit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.player:
        raise SystemExit("Player name cannot be empty. Set --player or CONQUEST_AI_PLAYER.")
    client = Client(base_url=args.base_url, timeout=args.timeout)

    game_id = args.game_id.strip()
    if not game_id:
        game_id = _discover_game_id(client, args.player)

    print(f"=== play_turn start: player={args.player} game_id={game_id} base={args.base_url} ===")

    if not args.no_debug_commands and not args.dry_run:
        for command in ("debug-info", "debug-reactions", "debug-interrupts"):
            try:
                result = client.send_command(game_id, args.player, command)
                print(f"[DEBUG-CMD] /{command} -> {result.get('status', 'unknown')}")
            except Exception as exc:
                print(f"[DEBUG-CMD] /{command} failed: {exc}")

    start_time = time.time()
    deadline = start_time + max(0.0, args.run_seconds)
    last_wait_log = 0.0
    actions_applied = 0
    steps = 0

    while time.time() < deadline and actions_applied < max(0, args.max_actions):
        steps += 1
        state = client.get_state(game_id, args.player)
        phase = str(state.get("phase", ""))
        turn = state.get("turn", {})
        active_player = str(turn.get("active_player", ""))
        required_action_type = str(turn.get("required_action_type", ""))

        if phase.startswith("FIN"):
            print("[STOP] Game finished.")
            break

        # Determine if it's our turn using multiple signals
        interaction = state.get("interaction", {})
        requested_player_is_active = bool(interaction.get("requested_player_is_active", False))
        legal_actions = interaction.get("legal_actions_for_requested_player", [])
        player_with_combat_turn = str(turn.get("player_with_combat_turn", ""))
        my_slot = _slot_for_player(state, args.player)
        my_role = "firstplayer" if my_slot == "1" else "secondplayer"
        
        # During combat, trust player_with_combat_turn as the authoritative turn indicator
        # The UI uses this field, so we should too
        is_our_turn = requested_player_is_active
        if not is_our_turn and phase == "COMBAT" and player_with_combat_turn == args.player:
            # We have the combat turn - the UI shows it's our turn
            # Even if action window hasn't closed or no legal actions yet, we should proceed
            is_our_turn = True
        
        if not is_our_turn:
            now = time.time()
            if now - last_wait_log >= 10.0:
                print(f"[WAIT] phase={phase} active={active_player} required={required_action_type} (combat_turn={player_with_combat_turn})")
                last_wait_log = now
            time.sleep(max(0.0, args.poll_interval))
            continue

        chosen_action, ranked = _choose_action(state)
        legal_count = len(ranked)
        context = state.get("search_and_choices", {}).get("choice_context", "")
        print(f"\n[TURN {steps}] phase={phase} required={required_action_type} legal={legal_count}")
        if context:
            print(f"  context={context}")

        if not chosen_action:
            print("  [SKIP] No legal action tokens available.")
            time.sleep(max(0.0, args.poll_interval))
            continue

        print("  candidates:")
        for candidate, score in ranked[: max(1, args.top_candidates)]:
            print(f"    - {candidate} ({score})")
        print(f"  chosen={chosen_action}")

        if args.dry_run:
            print("  [DRY-RUN] Action not submitted.")
            time.sleep(max(0.0, args.post_action_sleep))
            continue

        result = client.send_action(game_id, args.player, chosen_action)
        status = result.get("status", "unknown")
        if status != "success":
            print("  [ERROR] Action rejected:")
            print(json.dumps(result, indent=2))
            break

        applied_action = result.get("applied_action", "")
        print(f"  applied={applied_action}")
        actions_applied += 1
        time.sleep(max(0.0, args.post_action_sleep))
    else:
        if actions_applied >= max(0, args.max_actions):
            print("[STOP] Reached max-actions cap.")
        else:
            print("[STOP] Watch window expired.")

    final_state = client.get_state(game_id, args.player)
    my_slot = _slot_for_player(final_state, args.player)
    opp_slot = "2" if my_slot == "1" else "1"
    summary = {
        "game_id": game_id,
        "steps_observed": steps,
        "actions_applied": actions_applied,
        "phase": final_state.get("phase", ""),
        "active_player": final_state.get("turn", {}).get("active_player", ""),
        "required_action_type": final_state.get("turn", {}).get("required_action_type", ""),
        "our_resources": final_state.get("players", {}).get(my_slot, {}).get("resources", None),
        "our_hand_count": final_state.get("players", {}).get(my_slot, {}).get("hand_count", None),
        "opponent_resources": final_state.get("players", {}).get(opp_slot, {}).get("resources", None),
        "opponent_hand_count": final_state.get("players", {}).get(opp_slot, {}).get("hand_count", None),
        "event_log_tail_last_10": final_state.get("event_log_tail", [])[-10:],
    }
    print("\n=== play_turn summary ===")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
