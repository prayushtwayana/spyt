from spotify import spotify
from youtube import youtube

def main():
    token = spotify.get_token()
    playlist_link = spotify.get_playlist_link()
    playlist_id = spotify.get_playlist_id(playlist_link)
    tracks = spotify.get_playlist_tracks(token, playlist_id)
    artists = spotify.get_playlist_artist(token, playlist_id)
    optimized_search = spotify.get_optimized_search(tracks, artists)

    youtube_key = youtube.build_youtube_key(youtube.API_KEY)
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
        youtube.write_to_file(links, playlist_name)


if __name__ == "__main__":
    main()

