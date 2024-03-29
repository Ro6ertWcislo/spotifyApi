import json
from os import getenv
import os

from flask import Flask, request, redirect, g, render_template
import requests
from urllib.parse import quote

app = Flask(__name__)

#  Client Keys

CLIENT_ID = getenv("CLIENT_ID")

CLIENT_SECRET = getenv("CLIENT_SECRET")

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private user-modify-playback-state"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


authorization_header = None


@app.route("/callback/q")
def callback():
    global authorization_header

    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    return render_template("index.html")


@app.route("/next")
def next():
    global authorization_header
    next_song_api_endpoint = "{}/me/player/next".format(SPOTIFY_API_URL)
    requests.post(next_song_api_endpoint, headers=authorization_header)


@app.route("/previous")
def previous():
    global authorization_header
    next_song_api_endpoint = "{}/me/player/previous".format(SPOTIFY_API_URL)
    requests.post(next_song_api_endpoint, headers=authorization_header)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
