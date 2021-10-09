from flask import Flask, render_template, request
from handle import get_api_key, get_channel_id, get_uploads_id, get_video_list, get_video_info, is_within_ratio, sort_by_likes
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        form = request.form
        url = form["url"]
        min_ratio = float(form["minratio"])
        max_ratio = float(form["maxratio"])
        sort_by = form["sortby"]
        with build('youtube', 'v3', developerKey=get_api_key()) as youtube:
            try: 
                channelId = get_channel_id(url)
                uploadsId = get_uploads_id(channelId, youtube)
                uploads_by_id = get_video_list(uploadsId, youtube)
                uploads = [get_video_info(video_id, youtube) for video_id in uploads_by_id]
            except HttpError as e:
                return f"There was an unexpected server error: {e}"
        valid_uploads = filter(lambda v: is_within_ratio(min_ratio, max_ratio, v), uploads)
        if sort_by == "likes":
            valid_uploads = sort_by_likes(valid_uploads)    
        return render_template("index.html", videos=valid_uploads)               
    else:
        return render_template("index.html", videos=[])