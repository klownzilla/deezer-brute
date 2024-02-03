from time import sleep
from random import randint
import logging
from deezer import client, exceptions

def search_by_album_id(album_id):
    try:
        return client.get_album(album_id)
    except exceptions.DeezerErrorResponse as e:
        if e.json_data['error']['code'] == 800:
            logging.info('NO DATA FOR ALBUM ID {}'.format(album_id))
        else:
            logging.critical('UNKNOWN ERROR FOR ALBUM ID {}'.format(album_id))
            logging.error(e)
            exit()

    return None

def search_albums_by_artist_id(artist_id, album_id):
    if artist_id in searched_artist_ids:
        logging.info('SKIPPING -- FOUND ARTIST ID {} FROM PREVIOUS SEARCH'.format(artist_id))
    else:
        searched_artist_ids.add(artist_id)
        logging.info('SEARCHING ARTIST ALBUMS USING ARTIST ID {} FROM ALBUM ID {}'.format(artist_id, album_id))
        artist = client.get_artist(artist_id)
        try:
            response = artist.get_albums()
        except exceptions.DeezerErrorResponse as e:
            logging.critical('UNKNOWN ERROR FOR ALBUM ID {}'.format(album_id))
            logging.error(e)
            exit()

        logging.info('FOUND {} ALBUMS BY ARTIST {}'.format(response.total, artist.name))
        if response.total > 50:
            logging.info('FOUND MORE THAN 50 ALBUMS -- SEARCHING NEWEST 50 ONLY')
            response = response[0:50]
        filtered_albums = filter_albums(response)
        for album in filtered_albums:
            log_release(album)

def filter_albums(response):
    filtered_albums = list(filter(lambda album: album.release_date.year in [2024, 2023]
                                  and album.duration > 1200
                                  and album.nb_tracks < 30
                                  and album.nb_tracks > 2,
                                  response))
    logging.info('FILTERED {} ALBUMS'.format(len(filtered_albums)))
    return filtered_albums

def log_release(album):
    try:
        title = album.title
        artist = album.artist.name
        track_count = album.nb_tracks
        release_date = album.release_date
        length = album.duration
        length_sec = length % 60
        length_min = int(length / 60) % 60
        length_hour = int(length / 3600) % 60
        url = album.link

        logging.info('SUCCESS\n\nTITLE :: {}\nTRACKS :: {}\nARTIST :: {}\nDATE :: {}\nLENGTH :: {:02d}:{:02d}:{:02d}\nURL :: {}\n\n'.format(
            title, track_count, artist, release_date, length_hour, length_min, length_sec, url))
    except exceptions.DeezerErrorResponse as e:
        if e.json_data['error']['code'] == 800:
            logging.warning('NO DATA FOR ALBUM ID {}'.format(album.id))
        else:
            logging.critical('UNKNOWN ERROR FOR ALBUM ID {}'.format(album.id))
            logging.error(e)
            exit()

def main():
    # TODO: add DB to make searched_artist_ids persistent?
    global client, searched_artist_ids
    client = client.Client()
    searched_artist_ids = set()
    logging.basicConfig(level=logging.INFO,
                        format='{asctime} :: {levelname} :: {funcName} :: {message}',
                        style='{',
                        handlers=[
                            logging.StreamHandler(),
                            logging.FileHandler('log.log', encoding='utf8')
                        ])
    
    start_id = 542512702
    id_step = 5
    total_searches = 1000
    for album_id in range(start_id, start_id + (total_searches * id_step), id_step):
        logging.debug('SEARCHING ALBUM ID {}'.format(album_id))

        response = search_by_album_id(album_id)
        if response is not None:
            search_albums_by_artist_id(response.artist.id, album_id)
        
        random_sleep = randint(4, 8)
        logging.debug('SLEEPING FOR {} SEC'.format(random_sleep))
        sleep(random_sleep)
    logging.debug('DONE WITH SEARCH')

if __name__ == "__main__":
    main()