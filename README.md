# Dopefish_lives Mastodon Bot

A simple Mastodon bot built in python3 for sending out real time alerts when a Dopefish_lives videogame stream goes live.

A special thanks goes out to GoaLitiuM for exposing the QuakeNet channel topic information to the web so others can be spared the horror that is IRC.

### Prerequisites:

pip install -r /path/to/requirements.txt

### Setup & Usage:

The basic usage is to:

1. Copy the config.yml.sample to config.yaml

2. On your desired mastodon instance, create a bot account and add a new application to it in the Development menu within Settings. From there you can find the api_base_url, client key, client secret, and access token to add to the config.yaml template.

3. From here you can launch the bot with `python3 main.py config.yaml` or use the included systemd service file to turn it into a restarting service.

`$ python3 main.py -h`
```
usage: main.py [-h] [config]

Track Dopefish_lives live streams and posts alerts to Mastodon.

positional arguments:
  config                Bot configuration file in YAML format.

optional arguments:
  -h, --help            show this help message and exit
```
