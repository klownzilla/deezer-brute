from time import sleep
from random import randint
import logging
from deezer import client, exceptions

def search_by_album_id(album_id):
    try:
        response = client.get_album(album_id)
    except exceptions.DeezerErrorResponse as e:
        if e.json_data['error']['code'] == 800:
            logging.info('NO DATA FOR ALBUM ID {}'.format(album_id))
        else:
            logging.critical('UNKNOWN ERROR FOR ALBUM ID {}'.format(album_id))
            logging.error(e)
            exit()
        return False

    search_albums_by_artist_id(response.artist.id, album_id)
    return True

def search_albums_by_artist_id(artist_id, album_id):
    logging.info('SEARCHING ARTIST ALBUMS USING ARTIST ID {} FROM ALBUM ID {}'.format(artist_id, album_id))
    artist = client.get_artist(artist_id)
    try:
        response = artist.get_albums()
    except exceptions.DeezerErrorResponse as e:
        logging.critical('UNKNOWN ERROR FOR ALBUM ID {}'.format(album_id))
        logging.error(e)
        exit()

    logging.info('FOUND {} ALBUMS FOR ARTIST {}'.format(response.total, artist.name))
    for album in response:
        log_release(album)

def log_release(response):
    try:
        title = response.title
        artist = response.artist.name
        track_count = response.nb_tracks
        release_date = response.release_date.strftime('%Y-%m-%d')
        length = response.duration
        length_sec = length % 60
        length_min = int(length / 60) % 60
        length_hour = int(length / 3600) % 60
        url = response.link

        if length_min > 20 and ("2024" in release_date or "2023" in release_date) and track_count > 2:
            logging.info('SUCCESS\n\nTITLE :: {}\nTRACKS :: {}\nARTIST :: {}\nDATE :: {}\nLENGTH :: {:02d}:{:02d}:{:02d}\nURL :: {}\n\n'.format(
                title, track_count, artist, release_date, length_hour, length_min, length_sec, url))
        else:
            logging.info('SKIPPING - {} - {} - {:02d}:{:02d}:{:02d} - {}'.format(
                title, release_date, length_hour, length_min, length_sec, url))
    except exceptions.DeezerErrorResponse as e:
        if e.json_data['error']['code'] == 800:
            logging.error('NO DATA FOR ALBUM ID {}'.format(response.id))
        else:
            logging.critical('UNKNOWN ERROR FOR ALBUM ID {}'.format(response.id))
            logging.error(e)
            exit()

def main():
    global client
    client = client.Client()
    logging.basicConfig(level=logging.INFO,
                        format='{asctime} :: {levelname} :: {funcName} :: {message}',
                        style='{',
                        handlers=[
                            logging.StreamHandler(),
                            logging.FileHandler('log.log', encoding='utf8')
                        ])
    
    start_id = 538869197
    id_step = 5
    total_searches = 1000
    for album_id in range(start_id, start_id + (total_searches * id_step), id_step):
        logging.debug('SEARCHING ALBUM ID {}'.format(album_id))
        search_by_album_id(album_id)
        random_sleep = randint(4, 8)
        logging.debug('SLEEPING FOR {} SEC'.format(random_sleep))
        sleep(random_sleep)
    logging.debug('DONE WITH SEARCH')

if __name__ == "__main__":
    main()