# Conquest-LCG-site
Repo for the Warhammer 40k Conquest website using Python Django

Needs a bunch of explaining that I am not willing to do rn.

# Update 06/03/2025

Like any good ping pong ball, I am all over the place.

Going to use Daphne for deployment, simply because there
is more documentation compared to uvicorn.

# Version alpha-1.0

The website is now developed enough for me to want to deploy it.
Everything appears to be working, but it needs to have a public test
to see if it survives coming into contact with the public. I can only
test so many possible sources of errors myself.

I plan on self-hosting the site, unsure what with. It's a coin toss between NGINX and Apache.
If I can't figure it out, I will use DigitalOcean instead.

# What is this?

Warhammer 40k Conquest card game. Something something board game geek, see my other repos.

# What is the current progress?

Currently we have: async chat rooms; login/logout; deck-building; async lobbies. Only thing really left to do is the actual game.

Current game progress: Everything, except:

- shielding
- card text (brutal is already working though)
- action windows
- a victory/loss screen
- ~~some targeting follicles so that players can see what planets/units are being targeted~~
- proper god damn multithreading
- ???
- and more!

# Dependencies?

Yes. This is using Django for webpage stuff, channels and dahpne for web sockets, whitenoise for static files, and redis so that I can use Docker. I don't know what Docker is, but all the channels documentation recommended it so eh.
Probably some more that I am forgetting, but they should be relatively minor hiccups really.

More dependencies added. Uvicorn[standard] is the main one. Just read the requirements file.

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