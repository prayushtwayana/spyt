import sys
import csv
import os
from pytube import YouTube
from spotify import spotify
from youtube import youtube
from config.env import YOUTUBE_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


def download_tracks(file_name):
    """
    This function downloads the tracks selected by the user to a location selected by the user

    parameters:
    - file_name (str) : name of the file where the results are stored

    """
    with open(file_name, mode = 'r') as file:
        reader = csv.reader(file)
        dir_name = file_name.replace(".csv", "")

        print("Enter the destination (leave blank for current directory)")
        destination = str(input(">> ") + dir_name) or f"{dir_name}"

        for i, (title, link) in enumerate(reader):
            print("\n")
            print(i, title)
            choice = input("Do you want to download this track?(y/n) ")

            if choice != 'y': continue

            print("Downloading...")
            yt = YouTube(link)
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path=destination)

            base, ext = os.path.splitext(out_file)
            os.rename(out_file, base + '.mp3')


def main():
    # token = spotify.get_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    # link = spotify.get_link()
    # link_type = spotify.identify_link(link)
    #
    # if link_type == None: sys.exit("Invalid Input")
    # if not link_type in ['Album', 'Playlist']:
    #     sys.exit(f"The link is a Spotify {identify_link(link)} link.")
    #
    # print(f"The link is a Spotify {link_type} link.")
    #
    # match link_type:
    #     case 'Playlist':
    #         playlist_id = spotify.get_playlist_id(link)
    #         playlist_name = spotify.get_playlist_name(token, playlist_id)
    #         tracks = spotify.get_playlist_tracks(token, playlist_id)
    #         artists = spotify.get_playlist_artist(token, playlist_id)
    #         search_list = spotify.get_optimized_search(tracks, artists)
    #         file_name = playlist_name + '.csv'
    #
    #     case 'Album':
    #         album_id = spotify.get_album_id(link)
    #         album_name = spotify.get_album_name(token, album_id)
    #         tracks = spotify.get_album_tracks(token, album_id)
    #         artists = spotify.get_album_artist(token, album_id)
    #         search_list = spotify.get_optimized_search(tracks, artists)
    #         file_name = album_name + '.csv'
    #
    # youtube_key = youtube.build_youtube_key(YOUTUBE_API_KEY)
    # for search_query in search_list:
    #     request = youtube_key.search().list(
    #         part = 'snippet',
    #         type = 'video',
    #         maxResults = 1,
    #         order ='relevance',
    #         q = search_query
    #     )
    #
    #     response = request.execute()
    #     links = youtube.get_result(response)
    #     print(links)
    #     youtube.save_results_to_file(links, file_name)
    #
    # download_tracks(file_name)



    link = input("Enter a link: ")
    s = spotify.Spotify(link)
    token = s.get_auth_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    header = s.get_auth_header()
    id = s.get_link_id()
    entity_name = s.get_name()
    tracks = s.get_tracks()
    artists = s.get_artists()
    search = s.optimized_search(artists)
    file_name = entity_name + '.csv'

    youtube_key = youtube.build_youtube_key(YOUTUBE_API_KEY)
    for search_query in search:
        request = youtube_key.search().list(
            part = 'snippet',
            type = 'video',
            maxResults = 1,
            order ='relevance',
            q = search_query
        )

        response = request.execute()
        links = youtube.get_result(response)
        print(links)
        youtube.save_results_to_file(links, file_name)

    download_tracks(file_name)


if __name__ == "__main__":
    main()

