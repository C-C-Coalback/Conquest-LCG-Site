NOTE: If you have Docker instead, you can simply replace 'podman' with 'docker' in these instructions and be sure to have right root permissions.

To run the Conquest_LCG site locally in a rootless podman container;

From within your downloaded Conquest_LCG-Site folder

Run this the first time:
user@machine ~/Conquest-LCG-Site> podman run --rm -it --network=host -p 6379:6379/tcp docker.io/redis:latest

This will create a temporary container and place you inside it;
user@machine ~/Conquest-LCG-Site> podman run --rm -it --network=host -v ${PWD}:/app -w /app -p 8000:8000 docker.io/python:3.13-alpine ash

From within the container, run;

# python -m venv .venv

# source .venv/bin/activate

# pip install -r requirements.txt

# python manage.py makemigrations
# python manage.py migrate

# python all_tests.py

Now, you can start the site, if you like, with
# daphne -b 0.0.0.0 -p 8000 conquest_site.asgi:application  

Or, just exit the container.
# exit

After that to run the site again, you can just use:

user@machine ~/Conquest-LCG-Site> podman run --rm -it --network=host -p 6379:6379/tcp docker.io/redis:latest
user@machine ~/Conquest-LCG-Site> podman run --rm -it --network=host -v ${PWD}:/app -w /app -p 8000:8000 docker.io/python:3.13-alpine ash

# source .venv/bin/activate

# daphne -b 0.0.0.0 -p 8000 conquest_site.asgi:application

