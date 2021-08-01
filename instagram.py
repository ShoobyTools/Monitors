import requests
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import os

import errors

load_dotenv()

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
WEBHOOK = os.environ["WEBHOOK"]

session = requests.Session()


def login():
    token = getCsrftoken()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-csrftoken": token,
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "user-agent": "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    }

    time = int(datetime.now().timestamp())

    form = {
        "username": USERNAME,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{time}:{PASSWORD}",
        "queryParams": {},
        "optIntoOneTap": "false",
    }
    r = session.post(
        "https://www.instagram.com/accounts/login/ajax/", headers=headers, data=form
    )

    authenticated = json.loads(r.text)
    if r.status_code == 200 and authenticated:
        pass
    else:
        raise errors.LoginFailed(r.status_code, authenticated)


def getCsrftoken() -> str:
    headers = {
        "user-agent": "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }

    r = session.get("https://www.instagram.com/accounts/login", headers=headers)

    script = re.findall(r"window._sharedData = .*", r.text)
    if len(script) != 0:
        script = script[0].strip("</script>").strip("window._sharedData = ").strip(";")
        script = json.loads(script)

    return str(script["config"]["csrf_token"])

class User:
    def __init__(self, handle: str, icon: str) -> None:
        self.handle = handle
        self.icon = icon
        self.latest_post = ""


class Post:
    def __init__(self, user: User, shortcode: str, image: str, caption: str) -> None:
        self.user = user
        self.shortcode = shortcode
        self.image = image
        self.caption = caption


def get_posts(handle):
    headers = {
        "user-agent": "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }
    page_url = f"https://www.instagram.com/{handle}/"

    r = session.get(page_url, verify=True, headers=headers)

    script = re.findall(r'"entry_data":.*', r.text)
    if len(script) != 0:
        script = script[0].strip("'")
        script = script.replace(";</script>", "")
        script = "{" + script
        script = json.loads(script)

    user = script["entry_data"]["ProfilePage"][0]["graphql"]["user"]
    timeline = user["edge_owner_to_timeline_media"]["edges"]

    current_user = User(handle, user["profile_pic_url"])
    posts = []
    for post in timeline:
        current_post = Post(
            user=current_user,
            shortcode=post["node"]["shortcode"],
            image=post["node"]["display_url"],
            caption=post["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"],
        )
        posts.append(current_post)

    return posts


def get_latest_post(user: User, handle: str):
    posts = get_posts(handle)
    if user.latest_post != posts[0].shortcode:
        user.latest_post = posts[0].shortcode
        data = make_embed(posts[0])
        send_webhook(data)


def make_embed(post):
    data = {
        "username": "Instagram Monitor",
        "avatar_url": "https://media.discordapp.net/attachments/734938642790744097/871175923083386920/insta.png",
        "embeds": [
            {
                "title": f"New post by @{post.user.handle}",
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "color": 13453419,
                "image": {"url": post.image},
                "fields": [{"name": "Caption", "value": post.caption, "inline": False}],
                "footer": {
                    "text": post.user.handle,
                    "icon_url": post.user.user_icon,
                },
            }
        ],
    }

    return data


def send_webhook(data):
    requests.post(WEBHOOK, json=data)


try:
    login()
except errors.LoginFailed as e:
    print(f"Login failed. Code{e}")

posts = get_latest_post("undefeatedinc")
