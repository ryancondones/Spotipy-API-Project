import os
from flask import Flask, session, url_for, redirect, request

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

# Creating Flask web application and session
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

# Importing Spotipy variables for session
client_id = "6a800550ff604a19a435d0ce97856b18"
client_secret = "8f5e73613a6c4088a7c8db70724d5636"
redirect_uri = "http://localhost:5000/callback"
scope = "playlist-read-private"

# Setting up authentication
cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(auth_manager=sp_oauth)

# Adding login with Spotify (home)
@app.route("/")
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for("get_playlists"))

# Refreshing the token (callback)
@app.route("/callback")
def callback():
    sp_oauth.get_access_token(request.args["code"])
    return redirect(url_for("get_playlists"))

# Getting user playlists from Spotify
@app.route("/get_playlists")
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists()
    playlists_info = [(pl["name"], pl["external_urls"]["spotify"]) for pl in playlists["items"]]
    playlists_display = "<br>".join([f"{name}: {url}" for name, url in playlists_info])
    return playlists_display

# Clear the session (asking the user to log in again when using the web application again)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)