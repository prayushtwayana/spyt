
import json
import base64
import os
from dotenv import load_dotenv
from requests import post, get


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token() -> str:
    """
    This function requests access token to the API service provider and returns the access token.
    This access token is crucial for making any requests to the API.
    For each request to the API the access token is necessary.

    """
    auth_string = client_id + ":" + client_secret
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


def get_playlist_link() -> str:
    """
    This function prompts the user for a spotify playlist link

    """
    playlist_link = input("Enter a spotify playlist link: ")
    return playlist_link


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

    return artists


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


def count_items(my_list: list) -> int:
    """
    This function counts the number of items in a list
    It is used to check the length of the Track list and Artist list
    This function is created just for testing

    parameters:
    - my_list (list) : the track or aritst list

    """
    count = 0
    for item in my_list:
        count = count + 1

    return count


def main():
    token = get_token()
    playlist_link = get_playlist_link()
    playlist_id = get_playlist_id(playlist_link)
    tracks = get_playlist_tracks(token, playlist_id)
    artists = get_playlist_artist(token, playlist_id)
    optimized_search = get_optimized_search(tracks, artists)


if __name__ == "__main__":
    main()
