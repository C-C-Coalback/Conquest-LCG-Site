"""Turn-notification utilities.

Publishes a small JSON summary to Redis Pub/Sub and dispatches HTTP webhooks
whenever the active player or required-action state changes for a game.
"""
from __future__ import annotations

import json
import logging
import threading
from typing import Any, Dict, List, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

import requests

logger = logging.getLogger(__name__)

# Game objects carry a dict we can attach arbitrary companion data to.
_WEBHOOK_KEY = "_conquest_webhooks"
_WEBHOOK_LOCK_KEY = "_conquest_webhooks_lock"


def get_webhooks(game) -> List[Dict[str, Any]]:
    """Return the configured webhooks for a game (auto-cleaning dead/unset)."""
    return list(getattr(game, _WEBHOOK_KEY, []) or [])


def _ensure_webhook_state(game) -> threading.RLock:
    if not hasattr(game, _WEBHOOK_KEY):
        setattr(game, _WEBHOOK_KEY, [])
    if not hasattr(game, _WEBHOOK_LOCK_KEY):
        setattr(game, _WEBHOOK_LOCK_KEY, threading.RLock())
    return getattr(game, _WEBHOOK_LOCK_KEY)


def register_webhook(game, url: str, events: Optional[List[str]] = None,
                     subscription_id: Optional[str] = None) -> Dict[str, Any]:
    """Register a webhook for a game and return its descriptor."""
    if not url or not isinstance(url, str):
        raise ValueError("Webhook url must be a string")
    import secrets
    lock = _ensure_webhook_state(game)
    events_list = events or ["turn"]
    descriptor = {
        "id": subscription_id or secrets.token_hex(8),
        "url": url,
        "events": events_list,
    }
    with lock:
        existing = getattr(game, _WEBHOOK_KEY)
        existing.append(descriptor)
    return descriptor


def remove_webhook(game, subscription_id: str) -> bool:
    lock = _ensure_webhook_state(game)
    with lock:
        existing = getattr(game, _WEBHOOK_KEY, [])
        for index, item in enumerate(list(existing)):
            if item.get("id") == subscription_id:
                del existing[index]
                return True
    return False


def build_turn_event(game) -> Dict[str, Any]:
    """Compute a compact, JSON-serializable turn event from a game snapshot."""
    async_to_sync(game.update_automated_info)()
    return {
        "type": "turn",
        "game_id": game.game_id,
        "phase": game.phase,
        "mode": game.mode,
        "round_number": game.round_number,
        "active_player": game.automated_player_waited_on,
        "required_action_type": game.what_is_required_automated,
        "legal_action_count": len(game.clickable_items_automated),
    }


def publish_turn_event(game) -> Dict[str, Any]:
    """Publish the turn event on the Redis Pub/Sub channel layer and dispatch webhooks.

    Returns the event dict that was broadcast, or an empty dict on error.
    """
    try:
        event = build_turn_event(game)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to build turn event: %s", exc)
        return {}

    payload = {"type": "turn.event", "event": event}
    try:
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(f"turn.{event['game_id']}", payload)
    except Exception as exc:  # noqa: BLE001
        logger.debug("Redis channel layer unavailable for turn event: %s", exc)

    _dispatch_webhooks(game, event)
    return event


def _dispatch_webhooks(game, event: Dict[str, Any]) -> None:
    """Best-effort HTTP POST to all subscribers listening for this event type."""
    webhooks = get_webhooks(game)
    if not webhooks:
        return
    event_kind = event.get("type", "")
    for hook in webhooks:
        if event_kind not in (hook.get("events") or []):
            continue
        url = hook.get("url")
        if not url:
            continue
        try:
            requests.post(
                url,
                json=event,
                timeout=getattr(settings, "TURN_WEBHOOK_TIMEOUT", 2.0),
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Webhook dispatch to %s failed: %s", url, exc)


def last_known_active_player(game) -> Optional[str]:
    return getattr(game, "_last_notified_active_player", None)


def last_known_required_action(game) -> Optional[str]:
    return getattr(game, "_last_notified_required_action", None)


def maybe_notify_turn_changed(game) -> None:
    """Notify subscribers when active player or required action changes.

    Saves a snapshot of last-notified state on the game object itself so the
    caller can call this safely every step without producing duplicate pings.
    """
    try:
        async_to_sync(game.update_automated_info)()
    except Exception as exc:  # noqa: BLE001
        logger.debug("update_automated_info failed during turn notify: %s", exc)
        return
    active = game.automated_player_waited_on
    required = game.what_is_required_automated
    last_active = last_known_active_player(game)
    last_required = last_known_required_action(game)
    if active == last_active and required == last_required:
        return
    setattr(game, "_last_notified_active_player", active)
    setattr(game, "_last_notified_required_action", required)
    publish_turn_event(game)


__all__ = [
    "build_turn_event",
    "publish_turn_event",
    "register_webhook",
    "remove_webhook",
    "get_webhooks",
    "maybe_notify_turn_changed",
]
