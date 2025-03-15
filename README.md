# Conquest-LCG-site
Repo for the Warhammer 40k Conquest website using Python Django.

# News/similar:

I should really get a better name for this section.

Have been doing some thinking. Currently, the attack/defend and 
shielding systems are pretty terrible. I have a new, better idea 
for how to handle them.

- Unit is declared as an attacker. 
- Unit is declared as a defender/aoe.
- Damage is dealt to all units that need to be damaged. Each time
a unit is damaged, an internal value is set to say how much damage
they took, and that they need to be shielded. Likely use a list
to keep track of the individual instances of damage.
- Shielding mode. The player can shield/not shield each damage.
- After all units have had their shielding states resolved,
we proceed to unit destruction. Each unit is checked to see if it
has been destroyed. If yes, destroy. If this causes an interrupt,
pause unit destruction and resume after the interrupt.
- Once all unit destruction checks have been performed, continue
to the turn/action/whatever of the next player.

This will take considerable effort to implement. However,
it is nescessary for the long-term health of the game.

# What is this?

Warhammer 40k Conquest card game. See the Board Game Geek page: 
https://boardgamegeek.com/boardgame/156776/warhammer-40000-conquest

Here is a link to The Hive Tyrant's tutorial for the game: https://www.youtube.com/watch?v=NE8NL9PfjXU

# What is the current progress?

Currently we have: async chat rooms; login/logout; deck-building; async lobbies. Only thing really left to do is the actual game.

Current game progress: Everything, except:

- shielding (Half done, too closely tied with combat turns at the moment.)
- card text (A significant amount of the raw traits/warlord abilities are working.)
- action windows (getting there, added them to the deploy phase)
- attachment support
- a victory/loss screen
- ~~some targeting follicles so that players can see what planets/units are being targeted~~
- proper god damn multithreading
- ???
- and more!

# How can I run it myself?

In one console, run 'docker run --rm -p 6379:6379 redis:7' (while the docker app is open)

If you are wanting to run this for development purposes, I recommend navigating
to settings.py in the conquest_site app and adding
"IPAddr = 127.0.0.1" just before the CHANNEL_LAYERS assignment.
You can now open a second console, navigate to the manage.py file, and simply run
"py manage.py runserver", and it should work.

If you want to run this on a LAN/similar, no need to change anything. Open a second console,
navigate to the manage.py file and run 
'daphne -b {YOUR_IP_HERE} -p 8080 conquest_site.asgi:application'.
You will need to allow python through your firewall on the private network.
Then others can connect to the site using a web browser and heading
to "http://{YOUR_IP_HERE}:8080".

# Disclaimer

Warhammer 40,000: Conquest is a trademark of Fantasy Flight 
Publishing, Inc. and/or Games Workshop Group. This project is 
not affiliated with either Fantasy Flight Games or Games 
Workshop Group. 
