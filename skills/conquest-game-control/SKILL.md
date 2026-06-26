---
name: conquest-game-control
description: Operate the local Conquest LCG app through its lobby websocket and in-game REST API. Use this skill whenever the user asks to sign in, choose deck/faction, join or create a lobby, start or continue a live game, autoplay turns, or add debug logging while playing at localhost:8000.
---

# Conquest Game Control (localhost)
Use this skill to reliably control a live game without rediscovering endpoints.

## Goal
- Join lobby/game as a real user account with a selected deck.
- Play legal actions over REST.
- Emit debug logs for decisions and actions.

## Official game rules digest (for agent play decisions)
Use this as the gameplay baseline when selecting legal actions.

### Authoritative precedence
- If rules conflict: **card text > Rules Reference Guide (RRG) > Learn to Play**.
- Treat `cannot` as absolute.

### Win/loss conditions
- Win immediately if you claim **3 planets that share a common type icon**.
- Win immediately if the opponent’s **bloodied warlord is defeated**.
- Lose if your deck is empty when you must draw (engine/state should be treated as authoritative for this condition).

### Round structure (in order)
1. **Deploy phase**
2. **Command phase**
3. **Combat phase**
4. **Headquarters phase**

### Deploy phase essentials
- Players alternate deployment turns:
  - deploy one card, or
  - initiate one action, or
  - pass.
- After a player passes, that player takes no more deployment turns this phase.
- Phase ends when both players have passed.

### Command phase essentials
- Both players secretly set command dials, reveal simultaneously, then commit:
  - warlord + all HQ units move to the chosen planet number.
  - warlord arrives in current state; other committed HQ units arrive exhausted.
- Resolve command struggles from first planet downward:
  - if only one player has a ready warlord there, that player wins automatically;
  - otherwise compare command icons on ready units;
  - tie: neither player wins.
- Command winner may take both/either/none of that planet’s card/resource bonus.

### Combat phase essentials
- Battle at first planet, then check for additional battles as required by game state.
- Battle initiative:
  - if exactly one warlord is present at battle start, that side has initiative;
  - otherwise initiative token holder has initiative.
- Battle sequence:
  1) Ranged skirmish (ranged combat turns),
  2) regular combat rounds until battle ends.
- Attack sequence:
  1) declare ready attacker and exhaust it,
  2) declare defender,
  3) deal damage equal to attacker ATK.
- Damage handling:
  1) assign damage,
  2) optional shields (max 1 shield card per damaged unit),
  3) take remaining damage.
- Destruction/defeat:
  - army/token units at damage >= HP are destroyed,
  - hale warlord at damage >= HP becomes bloodied (damage cleared),
  - bloodied warlord defeated => controller loses.
- Retreat:
  - warlord may exhaust instead of attacking to retreat to HQ,
  - at end of combat round, each player may retreat any number of units to HQ exhausted.
- Winning a battle:
  - winner may trigger that planet’s Battle ability,
  - if won at first planet: winner claims that planet to victory display.

### Headquarters phase essentials
- Move first-planet token to next planet.
- Reveal next facedown planet (if any).
- Each player draws 2 cards.
- Each player gains 4 resources.
- Ready all cards.
- Pass initiative token.

### Timing windows and triggers
- **Action** abilities can be initiated only in action windows.
- **Interrupts** resolve before the triggering condition resolves.
- **Reactions** resolve after the triggering condition resolves.
- For both interrupts and reactions, initiative player gets first opportunity, then players alternate until both pass.

### Skill operating rule
- Always choose commands from `interaction.legal_actions_for_requested_player`.
- If inferred tabletop rules and API legal action tokens disagree, the API legal list is authoritative for execution.
- Use this rules digest for prioritization and planning among legal options only.

### AI account limitation policy
- Use a fixed AI account instead of creating new user accounts per run.
- Server policy is configured through:
  - `AI_CONTROL_ENFORCE_ALLOWED_USERNAMES` (default: `true`)
  - `AI_CONTROL_ALLOWED_USERNAMES` (default: `basicai`)
- AI control endpoints reject actions for players outside the allowlist.
- This does **not** prevent running multiple games at once with the same allowed account.
- For local scripts, set `CONQUEST_AI_PLAYER` (or pass `--player`) to an allowed account.

### Source documents
- `Learn-to-Play-web.pdf` (official Learn to Play)
- `Rules-Reference-web.pdf` (official Rules Reference Guide)

## Bundled helper script
- REST autoplay helper: `skills/conquest-game-control/scripts/play_turn.py`
- Use it when the user wants immediate turn execution without re-implementing loop logic.
- Typical usage:
  - `python skills/conquest-game-control/scripts/play_turn.py --player <username>`
  - `python skills/conquest-game-control/scripts/play_turn.py --player <username> --game-id <game_id>`
- Useful flags:
  - `--run-seconds` to keep watching for your turn.
  - `--max-actions` to cap how many actions script may apply.
  - `--no-debug-commands` to skip debug command injection.

## Preconditions
- Server is reachable at `http://localhost:8000`.
- Account already exists and is in `AI_CONTROL_ALLOWED_USERNAMES` when AI account restriction is enabled.
- Deck exists for that account under `decks/DeckStorage/<username>/`.

## Lobby control over websocket
1. Create an authenticated HTTP session:
   - `GET /accounts/login/`
   - Parse `csrfmiddlewaretoken`.
   - `POST /accounts/login/` with `username`, `password`, CSRF token.
   - Confirm authenticated session (e.g. homepage contains “Logged in as <username>”).
2. Open websocket:
   - URL: `ws://localhost:8000/ws/play/`
   - Include session cookies in `Cookie` header.
3. Read initial messages:
   - Lobby rows arrive as `Create lobby/<host>/<guest>/...`.
   - Open lobby means `<guest>` is empty.
4. Choose deck and join:
   - Send `{"message":"Select Deck/<deck_name>"}`.
   - Send `{"message":"Join lobby/<host>/<deck_name>"}`.
5. Confirm join:
   - Success signal: `Create lobby/<host>/<your_username>/...`.

## REST game control
Use these endpoints:
- `GET /api/games/`
- `GET /api/game/<game_id>/agent_state/?player=<username>`
- `POST /api/game/<game_id>/agent_command/`
- `POST /api/game/<game_id>/agent_action/`

### Action contract
- Only send `agent_action` when `turn.active_player == <username>`.
- Action must be exactly one token from `interaction.legal_actions_for_requested_player`.
- Never guess action format; always copy from legal list.

### Debug logging
Before or during turns, send:
- `debug-info`
- `debug-reactions`
- `debug-interrupts`

And log per step:
- phase
- active player
- required action type
- legal action candidates
- chosen action
- applied action

## Turn loop
1. Pull `agent_state`.
2. Stop if phase starts with `FIN`.
3. If not active player, wait/poll.
4. If active:
   - rank/select a legal action (win-seeking heuristic),
   - submit via `agent_action`,
   - repeat until control passes.

## Default decision policy (if no user-specific strategy provided)
- Prefer non-pass actions if any legal non-pass exists.
- Avoid concede/resign/force-quit actions.
- During mulligan choice, default to keeping a playable hand unless clearly unplayable.
- When uncertain, still choose from legal tokens only.

## Failure handling
- If login fails: report concise reason (bad creds, csrf parse failure, no session).
- If no open lobby: report currently visible lobbies and wait.
- If action rejected: refresh state and use current legal tokens only.
