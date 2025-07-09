import requests


class Instagram:

    base_url = "https://graph.instagram.com/v23.0"

    def __init__(self, ig_id, token):
        self.ig_id = ig_id
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def create_container(
        self, url: str, is_carousel=False, caption=None, user_tag=None, alt_text=None
    ) -> dict:

        data = {"image_url": url, "is_carousel_item": is_carousel}
        if caption:
            data["caption"] = caption

        if alt_text:
            data["alt_text"] = alt_text

        if user_tag:
            data["user_tags"] = [
                {
                    "username": user_tag,
                    "x": 0.3,
                    "y": 0.8,
                }
            ]
        res = requests.post(
            f"{self.base_url}/{self.ig_id}/media", json=data, headers=self.headers
        ).json()

        if "error" in res and "user_tags" in data:
            print(res)
            del data["user_tags"]
            res = requests.post(
                f"{self.base_url}/{self.ig_id}/media", json=data, headers=self.headers
            ).json()

        return res

    def create_carousel(
        self, children: list, caption: str, user_tag: str = None
    ) -> dict:
        data = {
            "media_type": "CAROUSEL",
            "children": children,
            "caption": caption,
            "collaborators": ["pinkbuttocks"],
        }
        if user_tag:
            data["collaborators"].append(user_tag)
        res = requests.post(
            f"{self.base_url}/{self.ig_id}/media", json=data, headers=self.headers
        ).json()
        return res

    def post_media(self, creation_id: int) -> dict:

        data = {"creation_id": creation_id}
        res = requests.post(
            f"{self.base_url}/{self.ig_id}/media_publish",
            data=data,
            headers=self.headers,
        ).json()
        return res
