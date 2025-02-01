# Conquest-LCG-site
Repo for the Warhammer 40k Conquest website using Python Django

Needs a bunch of explaining that I am not willing to do rn.

# What is this?

Warhammer 40k Conquest card game. Something something board game geek, see my other repos.

# What is the current progress?

Currently we have: async chat rooms; login/logout; deck-building; async lobbies. Only thing really left to do is the actual game.

Current game progress: displays hqs, hands (hidden to all but correct player), in play, planets. Not displaying resources.
Cards can be clicked on, with unique ids so server can tell what was clicked on, decks can be loaded.
Chat rooms present. Going to handle code for the game now; have to rewrite
the entire code from the previous pygame version, since I don't know how
to correctly wait for an input using multithreading that wouldn't either
blow up my pc from the workload, or introduce unneeded lag.

# Dependencies?

Yes. This is using Django for webpage stuff, channels and dahpne for web sockets, whitenoise for static files, and redis so that I can use Docker. I don't know what Docker is, but all the channels documentation recommended it so eh.
Probably some more that I am forgetting, but they should be relatively minor hiccups really.

# How can I run it myself?

Don't. I mean, you can, but I don't know how I run it. I'll give my steps here though:

In one console, run 'docker run --rm -p 6379:6379 redis:7' (while the docker app is open)
In the other, navigate to the manage.py file and run 'py manage.py runserver'

And it should just work. You need to set the secret key in the settings.py file first. May also need to collect static.

Really this is just for me to show that I am making progress on the site.
