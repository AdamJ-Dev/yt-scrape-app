from bs4 import BeautifulSoup
import urllib.request
import os

def get_api_key():
    return os.environ.get("GOOG_API")

def get_channel_id(url):
    source = urllib.request.urlopen(url)
    html = source.read()
    source.close()
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find(attrs={"itemprop": "channelId"})
    channelId = meta.get("content")
    return channelId if channelId else False


def get_uploads_id(channel_id, youtube):
    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()
    uploadsId = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return uploadsId

def get_video_ids(response):
    return [item["contentDetails"]["videoId"] for item in response["items"]]

def get_video_list(uploads_id, youtube):
    request = youtube.playlistItems().list(part="contentDetails", maxResults=50, playlistId=uploads_id)
    response = request.execute()
    videoIds = get_video_ids(response)
    while True:
        try:
            request = youtube.playlistItems().list(part="contentDetails", maxResults=50, playlistId=uploads_id, pageToken=response["nextPageToken"])
            response = request.execute()
            videoIds += get_video_ids(response)
        except KeyError:
            break;
    return videoIds


def get_video_info(video_id, youtube):
    request = youtube.videos().list(part="statistics,snippet", id=video_id)
    response = request.execute()
    stats = response["items"][0]["statistics"]
    title = response["items"][0]["snippet"]["title"]
    return {"url": "https://www.youtube.com/watch?v=" + video_id, "title": title, "likes": stats["likeCount"], "dislikes": stats["dislikeCount"]}

def is_within_ratio(min_ratio, max_ratio, video):
    if min_ratio < 0:
        min_ratio = float("inf")
    if max_ratio < 0:
        max_ratio = float("inf")
    likes = int(video["likes"])
    dislikes = int(video["dislikes"])
    if likes == 0 and dislikes == 0:
        return True
    elif dislikes == 0:
        ratio = float("inf")
    else:
        ratio = likes/dislikes
    return min_ratio <= ratio <= max_ratio
   
def sort_by_likes(videos):
    def get_likes(video):
        return int(video["likes"])
    return sorted(videos, key=get_likes, reverse=True)
   