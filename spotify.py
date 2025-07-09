# TODO load and store data in object values, pass reload=True to update

import json
import math

import requests


class Spotify:

    redirect_uri = "https://www.google.com"

    scope = "%20".join(
        [
            "user-read-recently-played",
            "user-top-read",
            "user-library-read",
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-email",
            "user-read-currently-playing",
            "user-read-playback-state",
            "user-modify-playback-state",
            "app-remote-control",
            "streaming",
            "user-follow-read",
        ]
    )

    def __init__(self, client_id, client_secret, user=None):

        self.client_id = client_id
        self.client_secret = client_secret
        if user is None:

            url = (
                "https://accounts.spotify.com/authorize/?client_id="
                + self.client_id
                + "&response_type=code&redirect_uri="
                + self.redirect_uri
                + "&scope="
                + self.scope
            )

            print(url)
            print()
            code = input("code:")

            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            self.user = requests.post(
                "https://accounts.spotify.com/api/token", data=data
            ).json()
            self.token = self.user["access_token"]
        else:
            self.user = user
            self.refresh()

        # self.user = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer " + user['access_token']}).json()
        # print(self.user)
        # self.user_name = self.user['display_name'] or self.user['id']
        # self.user.update(user)
        # print(json.dumps(self.user))

    @property
    def headers(self):
        return {"Authorization": "Bearer " + self.token}

    def refresh(self):
        # print('Refreshing token and retrying...')
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.user["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        res = requests.post("https://accounts.spotify.com/api/token", data=data)
        js = res.json()
        if res.status_code == 400:
            print(js)
        self.token = js["access_token"]

    def _make_request(self, url):

        res = requests.get(url, headers=self.headers)

        if res.status_code == 204:
            return None

        js = res.json()
        if "error" in js:
            if js["error"]["message"] == "The access token expired":
                self.refresh()
                return self._make_request(url)
            else:
                raise ("error here:", js)
            # elif js['error']['message'] == "Permissions missing":
            #     return None
        else:
            return js

    def get_recent(self):
        url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
        res = self._make_request(url)

        return res

    def get_currently_playing(self):
        url = "https://api.spotify.com/v1/me/player/currently-playing"
        res = self._make_request(url)

        with open("current.json", "w") as f:
            json.dump(res, f)

        return res

    def get_artists(self, ids):

        artists = []
        for i in range(0, len(ids), 50):
            some_ids = ",".join(ids[i : i + 50])
            url = "https://api.spotify.com/v1/artists?ids=" + some_ids
            res = self._make_request(url)
            print(".", end="")
            artists += res["artists"]
        return artists

    def get_albums(self, ids):  # to loop 50
        ids = ",".join(ids)
        url = "https://api.spotify.com/v1/albums?ids=" + ids
        return self._make_request(url)

    def get_tracks(self, ids):  # to loop 50
        ids = ",".join(ids)
        url = "https://api.spotify.com/v1/tracks?ids=" + ids
        return self._make_request(url)

    def following(self):

        url = "https://api.spotify.com/v1/me/following?type=artist&limit=50"
        res = self._make_request(url)

        artists = []
        while True:
            artists += res["artists"]["items"]

            if res["artists"]["next"]:
                url = res["artists"]["next"]
                res = self._make_request(url)
                print(".", end="")
            else:
                break

        return artists

    def saved_tracks(self):

        url = "https://api.spotify.com/v1/me/tracks?limit=50&offset=0"
        res = self._make_request(url)

        tracks = []
        while True:
            tracks += res["items"]

            if res["next"]:
                url = res["next"]
                res = self._make_request(url)
                print(".", end="")
            else:
                break

        return tracks

    def get_saved_albums(self):

        url = "https://api.spotify.com/v1/me/albums?limit=50"
        js = self._make_request(url)

        saved_albums = []
        while True:
            saved_albums += js["items"]

            if js["next"]:
                print(".", end="")
                js = self._make_request(js["next"])
            else:
                break

        return saved_albums

    def get_audio_features(self, ids):

        features = []
        for i in range(0, len(ids), 50):
            some_ids = ",".join(ids[i : i + 50])
            url = "https://api.spotify.com/v1/audio-features?ids=" + some_ids
            res = self._make_request(url)
            print(".", end="")
            features += res["audio_features"]
        return features

    def add_to_playlist(self, ids, playlist_id):

        for i in range(math.ceil(len(ids) / 100)):

            uris = ids[i * 100 : (i + 1) * 100]

            res = requests.post(
                f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                headers=self.headers,
                data=json.dumps({"uris": uris}),
            )

    # def get_audio_analysis(self, id):
    #     url = "https://api.spotify.com/v1/audio-analysis/" + id + "?access_token=" + token
    #     print (url)
    #     res = requests.get(url)
    #     js = res.json()
