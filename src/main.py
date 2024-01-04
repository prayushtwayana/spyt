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

        print("Enter the destination (leave blank for current directory)")
        destination = str(input(">> ")) or '.'

        for i, (title, link) in enumerate(reader):
            print("\n")
            print(i, title)
            choice = input("Do you want to download this track?(y/n) ")
            
            if choice != 'y':
                continue
            
            print("Downloading...")
            yt = YouTube(link)
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path=destination)

            base, ext = os.path.splitext(out_file)
            os.rename(out_file, base + '.mp3')


def main():
    token = spotify.get_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    playlist_link = spotify.get_playlist_link()
    if not spotify.is_playlist_link(playlist_link):
        if spotify.identify_link(playlist_link) == None: sys.exit("Invalid Input")
        sys.exit(f"The link is a {spotify.identify_link(playlist_link)} link.")
    playlist_id = spotify.get_playlist_id(playlist_link)
    tracks = spotify.get_playlist_tracks(token, playlist_id)
    artists = spotify.get_playlist_artist(token, playlist_id)
    optimized_search = spotify.get_optimized_search(tracks, artists)

    youtube_key = youtube.build_youtube_key(YOUTUBE_API_KEY)
    search_list = optimized_search
    playlist_name = spotify.get_playlist_name(token, playlist_id)
    file_name = playlist_name + '.csv'
    for search_query in search_list:
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

