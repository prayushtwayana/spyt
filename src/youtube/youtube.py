import csv
from googleapiclient.discovery import build


def build_youtube_key(api_key: str):
    """
    This function builds a token to interact with the YouTube API

    parameters:
    - api_key (str) : the key for the API

    """
    return build('youtube', 'v3', developerKey = api_key)


def get_result(response) -> dict:
    """
    This function returns a dictionary with the video title and it's video link
    The result is a combination of both video name and the video link

    Parameters:
    - response (dict) : The API response to our `search` query

    """
    results = {}

    items = response.get('items')
    vId_dict = [item['id'] for item in items]
    snippets = [item['snippet'] for item in items]
    video_id = [vId['videoId'] for vId in vId_dict]
    title = [snippet['title'] for snippet in snippets]

    for title_instance, id_instance in zip(title, video_id):
        results.update(
            {title_instance: f"https://youtu.be/watch?v={id_instance}"})

    return results


def save_results_to_file(search_result: dict, file_name: str):
    """
    This function writes the the title and YouTube links of the tracks in the playlist to a '.csv' file

    parameters:
    - search_result (dict) : a list of all the tracks in a playlist
    - playlist_name (str) : the name of the playlist for `spyt` (the name will be used for the file name as well)
    """
    title, link = str, str

    search_result_tuple = tuple(search_result.items())
    for values in search_result_tuple:
        (title, link) = values    

    with open(file_name, 'a', newline = '') as file:
        writer = csv.DictWriter(file, fieldnames = ['title', 'link'])
        writer.writerow({'title':title, 'link':link})


def main(api_key):

    youtube_key = build_youtube_key(api_key)

    search_list = []
    playlist_name = input('Name of the playlist: ')

    for search_query in search_list:
        request = youtube_key.search().list(
            part = 'snippet',
            type = 'video',
            maxResults = 1,
            order ='relevance',
            q = search_query
        )

        response = request.execute()
        links = get_result(response)
        save_results_to_file(links, playlist_name)


if __name__ == '__main__':
    from ..config.env import YOUTUBE_API_KEY
    main(YOUTUBE_API_KEY)
