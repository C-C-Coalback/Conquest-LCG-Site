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

- Official rule PDF's are here:
  * Full rules URL: https://images-cdn.fantasyflightgames.com/ffg_content/warhammer-40k-conquest/support/Learn-to-Play-web.pdf
  * Rules reference URL: https://images-cdn.fantasyflightgames.com/ffg_content/warhammer-40k-conquest/support/Rules-Reference-web.pdf

### Authoritative precedence
- If rules conflict: **card text > Rules Reference Guide (RRG) > Learn to Play**.
- Treat `cannot` as absolute.

### Win/loss conditions
- Win immediately if you claim **3 planets that share a common type icon**.
- Win immediately if the opponent’s **bloodied warlord is defeated**.
- Lose if your deck is empty when you must draw (engine/state should be treated as authoritative for this condition).

### First turn of the game
- On your very first turn of any game, you will be asked if you want to mulligan (redraw) your hand.
  * Look over your cards and make an estimated guess if you belive them to be adventagious towards your strategy to win.
    * Choosing **Yes** will give you a new hand
    * Choosing **No** will keep your current hand.
    
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

### REST skill discovery bootstrap
- `GET /api/` first, then read:
  - `GET /api/skills/`
  - `GET /api/skills/<skill_id>/` (for full skill content)

### Action contract
- Only send `agent_action` when `turn.active_player == <username>`.
- Action must be exactly one token from `interaction.legal_actions_for_requested_player`.
- Never guess action format; always copy from legal list.

### Start-of-turn checklist (always do this first)
1. Pull `agent_state`.
2. Check question-box equivalents first:
   - `search_and_choices.choice_context`
   - `search_and_choices.choices_available`
3. Check info-box/turn equivalents:
   - `phase`
   - `mode`
   - `turn.required_action_type`
   - `turn.active_player`
4. Use only `interaction.legal_actions_for_requested_player` for execution.
5. If choices are present, treat them as highest priority before non-choice actions.

### Setup + mulligan notes
- The first meaningful setup decision is mulligan (yes/no) once a hand is loaded.
- If `deck_loaded == false`, immediately load a deck before evaluating lines:
  - `POST /api/game/<game_id>/agent_command/` with `command: "loaddeck/<deck_name>"`.
- If in `SETUP` with:
  - `players.<me>.deck_loaded == false`
  - `players.<me>.hand_count == 0`
  - legal actions only `pass-P1`/`pass-P2`
  then the deck is not actually loaded for that player yet.
- `loaddeck/<deck_name>` resolves from `decks/DeckStorage/<player>/<deck_name>`. If file is missing, setup will not progress to mulligan.

## Game notes (mechanics and API behavior)
- If `deck_loaded == false`, load a deck immediately before making strategic decisions.
- If setup is stuck with only `pass-P1`/`pass-P2` and no hand, treat it as a deck-load/path issue, not a tactical choice.
- `agent_action` must use an exact token from `interaction.legal_actions_for_requested_player`; never synthesize token formats.
- Planet reward values in engine data are stored as `(cards, resources)` order (not `(resources, cards)`), so a planet entry like `(0, 2)` means 0 cards and 2 resources.
- Many deploy plays are staged token chains: `HAND/...` selects a card, then a follow-up token such as `PLANETS/x` is required to finish resolution.
- After any staged first token, immediately refresh/check legal actions and complete the chain before ending the turn.
- Some plays temporarily switch `mode` to `ACTION` with only `pass-P1` legal; that pass only closes the subwindow. Re-check state afterward and, if back in normal deploy with `my_has_passed == false`, send another deploy-phase pass to truly pass.
- In combat `Indirect` steps, assignments can require multiple sequential `IN_PLAY/...` selections; after each pick, refresh state and continue until legal actions clear or active player changes.
- In combat `Damage` windows, legal actions can be `HAND/<player>/<index>` plus `pass`; those `HAND` tokens are shield-card plays from hand for the pending damage packet.
- In `required_action_type: Combat Turn`, attack declaration can be a two-step chain: first select your attacker (`IN_PLAY/<you>/<planet>/<unit>`), then select the defender (`IN_PLAY/<opponent>/<planet>/<unit>`).
- Command winner calculation in this engine uses command totals; warlords are represented with effectively auto-win command strength (`999`) unless opposed by another warlord.
- Helvetis has two separate effects at different times: command reward (`0 cards, 2 resources`) during command struggle resolution, and a separate forced activity coin-flip/indirect-damage effect when activities resolve in combat setup.
- Read question-box equivalents first (`choice_context`, `choices_available`) before normal deploy/combat planning.
- In `agent_state`, players are keyed by number (`"1"`, `"2"`); identify your side by matching `players[*].name` to your account name.
- `Earth Caste Technician` search is filtered to cards matching **Drone trait OR Attachment type**; legal selections appear as `SEARCH/<index>` tokens for matching cards only.
- In `required_action_type: Commitment`, your legal actions are `PLANETS/x`; after choosing one, state may switch to `required_action_type: Command not Commitment` with zero legal actions while command struggles auto-resolve.
- In `required_action_type: Command not Commitment`, a pass-only window (`pass-P1`) can still appear for you; consume it, then re-check whether legal actions clear.
- Planet activity prompts can chain across multiple planets in one sequence (for example `Hostaryn XXI` -> `Deltadurne` -> `Hangyz`), with each step requiring a fresh legal-action check before acting.
- For activity prompts where `choice_context` is the planet name (for example `Deltadurne`, `Hangyz`), `CHOICE/0` is the resolve path and `CHOICE/1` skips that activity.
- `Hangyz Scrying` reveals the top card name in `choices_available`; `CHOICE/0` discards that card, while `CHOICE/1` keeps it on top.
- Caldera activity can transition into a `required_action_type: Reaction` subwindow where only `pass-P1` is legal; always consume that pass if it is the only legal token.
- Combat flow can also present `required_action_type: Outside Combat` with only `pass-P1` legal; this is another pass-through subwindow and should be consumed immediately.
- If `requested_player` appears to still be your name but `legal_actions_for_requested_player` is empty, treat it as no actionable step for you and wait for the next state change.

## General strategy notes
- Prefer proactive board/economy development over early passes when legal non-pass deploys exist.
- Keep resources and hand quality in mind across phases, not just the current legal action list.
- Opening hand decisions should prioritize a functional curve (early playable cards + economy/tempo plan) over narrow high-roll lines.

## Deck strategy notes
### Aunshi Assassin FFG
- Keep opening hands that already contain multiple early deploy options and command presence.
- Early `Ksi'm'yen Orbital City` deployment is a strong tempo line when legal and affordable.
- Cheap Tau units (`Ethereal Envoy`, `Bork'an Recruits`, `Vior'la Marksman`) are reliable early-game deploy pieces for command and board setup.
- In mirror-style openings, early command spread (for example, `Bork'an Recruits` to a non-first planet) can pressure economy while avoiding overcommitting to first-planet fights.
- Follow-up mirror line: after establishing off-first command pressure, deploying `Vior'la Marksman` to first planet helps contest first battle tempo without collapsing the wider command spread.
- With ~2 resources remaining in deploy, `Ethereal Envoy` to an uncontested mid planet is a strong efficiency line for incremental command advantage.
- With only ~1 resource left late in deploy, a final cheap unit to an uncontested trailing planet is often better than passing, because it widens command coverage going into command phase.
- In first-planet mirror combat, when forced to allocate indirect damage across your own units, splitting damage to preserve a live ranged attacker can outperform soaking everything on one body.
- In shield windows, preserving `Vior'la Marksman` for ranged pressure by spending lower-impact shield cards can be better than spending premium combat events.

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
2. ~~Stop if phase starts with `FIN`.~~ CHANGED: please replace with a game complete check that does not rely on phase (was breaking my neural network). I recommend simply not having any legal actions if the game is completed.
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
