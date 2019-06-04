"""
These methods work only when spotifyProxy server is running
"""
import requests

host = "http://localhost:8080"

def nextSong():
    requests.get(f"{host}/next")


def previousSong():
    requests.get(f"{host}/previous")