import argparse
import logging
import logging.config
import requests
from yaml import load
from mastodon import Mastodon
from time import sleep
from random import choice

config = {}
prev_title = None


def main():
    global config
    global prev_title
    # setup and parse input arguments
    parser = argparse.ArgumentParser(description='Track dopelives.com streams \
and posts alerts to mastodon.')
    parser.add_argument('config',
                        nargs='?',
                        default='config.yaml',
                        help='Bot configuration file in YAML format.')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = load(f)

    # setup logging using the settings in the provided YAML config
    logging.config.dictConfig(config['logging'])

    logging.info("Config loaded!")

    while True:
        logging.info("Polling site...")
        # scrape the current stream state from goalitium's bot page
        try:
            site_data = requests.get(config['site_url'])
        except Exception as e:
            logging.error("Connection closed!")
            logging.error(e)
            continue
        # For the eventual case that Goa's server glitches out
        if site_data.status_code != 200:
            logging.error("HTTP Error: " + site_data.status_code)
            continue
        logging.info("Raw data from site: " + repr(site_data.text))
        # parse the site's string into a streamer and (game/movie) title
        streamer, title = parse_site(site_data.text)
        if okay_to_post(streamer, title):
            logging.info("Site data is okay to post!")
            # if there's no streamer, replace it with ???
            if streamer is None:
                logging.info("No streamer info included!")
                streamer = '???'
            msg = choice(config['toot_format']).format(streamer=streamer,
                                                       title=title)
            prev_title = title
            logging.info("Sending out toot: " + msg)
            send_toot(msg)
        # wait for the timeout period
        sleep(config['polling_interval'])


def parse_site(s):
    """ Takes the string from goalitium's site and parses it into the streamer
        and game/movie title """
    # For most pings there's nothing going on, so only 'Game: ' is given.
    # Just return with everything as None and don't waste time.
    # Ignore empty strings too.
    if s == 'Game: ' or s == '':
        logging.info("Empty stream string.")
        return (None, None)
    # split the string into a list around the "streamer\nGame: game_title"
    # newline and label.
    pieces = s.split("\nGame: ")
    # no listed streamer case, e.g. 'Game: Some Game Title'
    if len(pieces) < 2:
        return (None, pieces)
    streamer = pieces[0]
    # chop off the "Game: " from the string
    title = pieces[1]
    return (streamer, title)


def okay_to_post(streamer, title):
    global prev_title
    """ returns a boolean if this stream info is worth posting about """
    # if there's no game, don't post
    if title is None:
        return False
    # if the game hasn't changed, don't post a new toot
    if prev_title == title:
        logging.info("Same title, skipping.")
        return False
    return True


def send_toot(msg):
    global config
    logging.info("Sending toot: " + msg)
    mastodon = Mastodon(
        api_base_url=config['mastodon']['api_base_url'],
        client_id=config['mastodon']['client_key'],
        client_secret=config['mastodon']['client_secret'],
        access_token=config['mastodon']['access_token']
    )
    try:
        status = mastodon.status_post(msg)
    except Exception as e:
        logging.error(e)
        status = "Tweet not sent!"
        pass
    logging.debug(status)


if __name__ == '__main__':
    main()
