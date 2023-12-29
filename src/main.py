import sys
from spotify import spotify
from youtube import youtube
from config.env import YOUTUBE_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

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
    playlist_name = input("Name of the playlist: ")
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
        youtube.save_results_to_file(links, playlist_name)


if __name__ == "__main__":
    main()

