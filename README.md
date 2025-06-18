# Conquest-LCG-site
Repo for the Warhammer 40k Conquest website using Python Django.

# Live from the Traxis Sector:

All FFG cards supported. _except for 'idden Base and Storm of Silence in some cases._
Working on Apoka fan cards now.
# What is this?

Warhammer 40k Conquest card game. See the Board Game Geek page: 
https://boardgamegeek.com/boardgame/156776/warhammer-40000-conquest

Here is a link to The Hive Tyrant's tutorial for the game: https://www.youtube.com/watch?v=NE8NL9PfjXU

# What is the current progress?

See the online spreadsheet: 
https://docs.google.com/spreadsheets/d/19WVZDINaXXJkV-hodJnYNgk2xx7UQQGF9aBtdWPVL_k/edit?gid=0#gid=0

# How can I run it myself?

First run "py -m pip install -r requirements.txt" to install dependencies.

In one console, run 'docker run --rm -p 6379:6379 redis:7' (while the docker app is open)

Then, you need to run "py manage.py makemigrations", followed by "py manage.py migrate" to create the user database.

To run tests, navigate to the all_tests.py file and run "py all_tests.py".

If you are wanting to run this for development purposes,
navigate to the manage.py file, and simply run
"py manage.py runserver", and it should work.

# Disclaimer

Warhammer 40,000: Conquest is a trademark of Fantasy Flight 
Publishing, Inc. and/or Games Workshop Group. This project is 
not affiliated with either Fantasy Flight Games or Games 
Workshop Group. 
