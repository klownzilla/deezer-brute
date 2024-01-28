import deezer
import time
from datetime import datetime
import random

def main():
    id = 468383835
    client = deezer.Client()
    output_file = open("releases_found.txt", "a")
    count = 1000

    while(count > 0):
        result = None
        try:
            result = client.get_album(id)
            result = result.as_dict()
            title = result["title"]
            album_link = result["link"]
            album_track_amount = result["nb_tracks"]
            album_length = result["duration"] / 60
            album_release_date = result["release_date"]
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if album_length > 20 and "2023" in album_release_date and album_track_amount > 2:
                message = "\n\n{} ::: FOUND RELEASE ::: {}\nTRACK AMOUNT ::: {}\nDATE ::: {}\nMINUTES ::: {:.2f}\nLINK ::: {}\n\n"
                print(message.format(current_time, title, album_track_amount, album_release_date, album_length, album_link))
                output_file.write(message.format(current_time, title, album_track_amount, album_release_date, album_length, album_link))
            else:
                print("{} ::: RELEASE ::: {} - {:.2f} MIN - {} - {} ::: NOT VALID".format(current_time, title, album_length, album_release_date, album_link))
        except:
            print("{} ::: NO RELEASE FOR ALBUM ID ::: https://www.deezer.com/album/{}".format(current_time, id))
            pass
        id += 10
        count -= 1
        random_number = random.randint(4, 8)
        time.sleep(random_number)
    print("DONE WITH SEARCH")
    output_file.flush()
    output_file.close()

if __name__ == "__main__":
    main()