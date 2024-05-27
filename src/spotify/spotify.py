import json
import sys
import re
import base64
from requests import post, get
from pprint import pprint


def get_token(CLIENT_ID: str, CLIENT_SECRET: str) -> str:
    """
    This function requests access token to the API service provider and returns the access token.
    This access token is crucial for making any requests to the API.
    For each request to the API the access token is necessary.

    """
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token


def get_auth_header(token: str) -> dict:
    """
    The authenticated header string is a unique header that is required for making requests to the API
    (insert more info about auth_header here)

    parameters:
    - token (str) : the token from earlier

    """

    return {"Authorization": "Bearer " + token}


def get_link() -> str:
    """
    This function prompts the user for a spotify playlist link

    """
    link = input("Enter a spotify playlist or album link: ")
    return link


def identify_link(link: str):
    """
    This function informs the user about the type of link they have provided should the link be not a Spotify Playlist Link

    parameters:
    - link (str) : the link obtained from get_playlist_link function

    """
    link = link.strip()

    if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/track/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", link):
        return "Track"

    if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/episode/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", link):
        return "Episode"

    if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/artist/([a-zA-Z\d]{22})\?si=([a-zA-Z\d_]{22})$", link):
        return "Artist"

    if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/album/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{22})$", link):
        return "Album"

    if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/show/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", link):
        return "Show"

    if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/playlist/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", link):
        return "Playlist"


def get_album_id(album_link: str) -> str:
    album_split = album_link.split('?')
    album_split = album_split[0].rsplit('/', )
    album_id = album_split[4]

    return album_id


def get_album_name(token:str, album_id:str) -> str:
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    album_name = json.loads(result.content)['name']

    return album_name


def get_album_tracks(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    json_result = json.loads(result.content)["items"]
    track = [item['name'] for item in json_result]

    return track


def get_album_artist(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    json_result = json.loads(result.content)["items"]
    artists_list = [item['artists'] for item in json_result]

    artists_dict = []

    for inner_list in artists_list:
        count = 0
        for item in inner_list:
            count = count + 1
            if not count > 1:
                artists_dict.append(item)

    artists = [item['name'] for item in artists_dict]

    return artists


def get_playlist_id(playlist_link: str) -> str:
    """
    This function takes a playlist link and returns the playlist id (in API requests, all we care about is the object id)
    Every request is done referencing the id

    parameters:
    - playlist_link (str) - provided by the user

    """
    playlist_split = playlist_link.split('?')
    playlist_split = playlist_split[0].rsplit('/', )
    playlist_id = playlist_split[4]

    return playlist_id


def get_playlist_name(token:str, playlist_id:str) -> str:
    """
    This function returns the name of the playlist
    This name will be used as the name of the file when the results are stored locally

    parameters:
    - token (str) : token from earlier
    - playlist_id (str) : id of the playlist extracted from playlist link 

    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    playlist_name = json.loads(result.content)['name']

    return playlist_name


def get_playlist_tracks(token: str, playlist_id: str) -> list:
    """
    This function returns the track names of the playlist

    parameters:
    - token (str) : token from earlier
    - playlist_id (str) : id of the playlist extracted from playlist link

    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    json_result = json.loads(result.content)["items"]
    track = [item['track']['name'] for item in json_result]

    return track


def get_playlist_artist(token: str, playlist_id: str) -> list:
    """
    This function returns the name of one artist from a track
    (there could be multiple artists in a track but since the track is Search engine optimized in YouTube, we only need the name of one artist to make a search)

    parameters:
    - token (str) : token from earlier
    - playlist_id (str) : id of the playlist extracted from playlist link

    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    json_result = json.loads(result.content)["items"]
    artists_list = [item['track']['artists'] for item in json_result]

    artists_dict = []

    for inner_list in artists_list:
        count = 0
        for item in inner_list:
            count = count + 1
            if not count > 1:
                artists_dict.append(item)

    artists = [item['name'] for item in artists_dict]

    return artists_dict


def get_optimized_search(tracks: list, artists: list) -> list:
    """
    This function returns a list with the search_query for YouTube
    It takes the corresponding elements of each list(artist and track) and joins them together to form a string for each element in the list
    The string so formed will be our search query itself

    parameters:
    - tracks (list) : list of all the songs in the playlist
    - artist (list) : list of all the artists(one artist per song) in the playlist
    """
    for x in range(len(tracks)):
        tracks[x] = tracks[x] + ' ' + artists[x]

    return tracks


def main(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET):
    token = get_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    link = get_link()
    link_type = identify_link(link)

    if link_type == None: sys.exit("Invalid Input")
    if not link_type in ['Album', 'Playlist']:
        sys.exit(f"The link is a Spotify {identify_link(link)} link.")

    print(f"The link is a Spotify {link_type} link.")

    match link_type:
        case 'Playlist':
            playlist_id = get_playlist_id(link)
            playlist_name = get_playlist_name(token, playlist_id)
            tracks = get_playlist_tracks(token, playlist_id)
            artists = get_playlist_artist(token, playlist_id)

        case 'Album':
            album_id = get_album_id(link)
            album_name = get_album_name(token, album_id)
            tracks = get_album_tracks(token, album_id)
            artists = get_album_artist(token, album_id)

    optimized_search = get_optimized_search(tracks, artists)

    print(optimized_search)


if __name__ == "__main__":
    from ..config.env import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
    main(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
