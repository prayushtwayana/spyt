import json
import sys
import base64
import re
from requests import post, get

class Spotify:
    def __init__(self, link):
        self._link = link.strip()
        self._type = None
        self._token = None
        self._auth_header = None
        self._id = None
        self._entity_name = None
        self._tracks = None

        if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/track/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", self._link):
            self._type = "Track"

        if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/episode/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", self._link):
            self._type = "Episode"

        if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/artist/([a-zA-Z\d]{22})\?si=([a-zA-Z\d_]{22})$", self._link):
            self._type = "Artist"

        if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/album/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{22})$", self._link):
            self._type = "Album"

        if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/show/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", self._link):
            self._type = "Show"

        if re.search(r".*(?:https?://)?(?:open\.)?spotify\.com/playlist/([a-zA-Z\d]{22})\?si=([a-zA-Z\d]{16})$", self._link):
            self._type = "Playlist"

        self._check_type()


    def _check_type(self):
        """
        This function checks whether the type of link is eligible for spyt (for now only Playlist and ALbums are supported)

        """
        if not self._type in ['Album', 'Playlist']:
            sys.exit("Invalid Input! (Enter a Spotify Album or Playlist Link)")
        else:
            print(f"The link is a Spotify {self._type} link.")


    def get_auth_token(self, CLIENT_ID, CLIENT_SECRET):
        """
        This function returns an authentication token, which is used to generate the authentication header

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
        self._token = json_result["access_token"]

        return self._token


    def get_auth_header(self):
        """
        This function returns an authentication header, which is required for API interaction

        """
        if (self._token):
            self._auth_header = {"Authorization": "Bearer " + self._token}
        else:
            sys.exit("Please get the authentication token first from `get_auth_token()`")


    def get_link_id(self):
        """
        This function returns the id of a spotify link

        """
        link_split = self._link.split('?')
        link_split = link_split[0].rsplit('/', )
        self._id = link_split[4]

        return self._id


    def get_name(self):
        """
        This function returns the name of the album or playlist name

        """
        if self._type == "Album":
            url = f"https://api.spotify.com/v1/albums/{self._id}"
            result = get(url, headers=self._auth_header)

            self._entity_name = json.loads(result.content)['name']

        if self._type == "Playlist":
            url = f"https://api.spotify.com/v1/playlists/{self._id}"
            result = get(url, headers=self._auth_header)

            self._entity_name = json.loads(result.content)['name']

        return self._entity_name


    def get_tracks(self):
        """
        This function returns the tracks in an album or a playlist

        """
        if self._type == "Album":
            url = f"https://api.spotify.com/v1/albums/{self._id}/tracks"
            result = get(url, headers=self._auth_header)

            json_result = json.loads(result.content)["items"]
            self._tracks = [item['name'] for item in json_result]

        if self._type == "Playlist":
            url = f"https://api.spotify.com/v1/playlists/{self._id}/tracks"
            result = get(url, headers=self._auth_header)

            json_result = json.loads(result.content)["items"]
            self._tracks = [item['track']['name'] for item in json_result]

        return self._tracks


    def get_artists(self):
        """
        This function returns the name of one artist from a track
        (there could be multiple artists in a track but since the track is Search engine optimized in YouTube, we only need the name of one artist to make a search)

        """
        if self._type == "Playlist":
            url = f"https://api.spotify.com/v1/playlists/{self._id}/tracks"
            result = get(url, headers=self._auth_header)

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

        if self._type == "Album":
            url = f"https://api.spotify.com/v1/albums/{self._id}/tracks"
            result = get(url, headers=self._auth_header)

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


    def optimized_search(self, artists):
        """
        This function returns a list with the search_query for YouTube
        It takes the corresponding elements of each list(artist and track) and joins them together to form a string for each element in the list
        The string so formed will be our search query itself

        parameters:
        - artist (list) : list of all the artists(one artist per song) in the playlist
        """
        for x in range(len(self._tracks)):
            self._tracks[x] = self._tracks[x] + ' ' + artists[x]

        return self._tracks


def main(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET):
    link = input("Enter a link: ")
    s = Spotify(link)
    token = s.get_auth_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    header = s.get_auth_header()
    id = s.get_link_id()
    entity_name = s.get_name()
    tracks = s.get_tracks()
    artists = s.get_artists()
    search = s.optimized_search(artists)

    print(search)


if __name__ == "__main__":
    from ..config.env import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
    main(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
