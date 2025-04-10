# Conquest-LCG-site
Repo for the Warhammer 40k Conquest website using Python Django.

# Live from the Traxis Sector:

The Orks are fully implemented!

# What is this?

Warhammer 40k Conquest card game. See the Board Game Geek page: 
https://boardgamegeek.com/boardgame/156776/warhammer-40000-conquest

Here is a link to The Hive Tyrant's tutorial for the game: https://www.youtube.com/watch?v=NE8NL9PfjXU

# What is the current progress?

Currently we have: async chat rooms; login/logout; deck-building; async lobbies. Only thing really left to do is the actual game.

Current game progress: Everything, except:

- ~~shielding~~
- card text (See the spreadsheet)
- action windows (getting there, added them to the deploy phase)
- ~~attachment support~~
- a victory/loss screen
- ~~some targeting follicles so that players can see what planets/units are being targeted~~
- ~~proper god damn multithreading~~
- Better deck building/selecting interface (low priority)
- ???
- and more!

# How can I run it myself?

First run "py -m pip install -r requirements.txt" to install dependencies.

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
