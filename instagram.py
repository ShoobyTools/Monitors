import requests
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import time

import errors

load_dotenv()

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
WEBHOOK = os.environ["WEBHOOK"]
MONITOR_FREQUENCY = os.environ["MONITOR_FREQUENCY"]

session = requests.Session()

user_list = []

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

class Post:
    def __init__(self, shortcode: str, image: str, caption: str) -> None:
        self.shortcode = shortcode
        self.image = image
        self.caption = caption


class User:
    def __init__(self) -> None:
        self.handle = None
        self.icon = None
        self.latest_post = None

    def set_post(self, latest_post: Post):
        self.latest_post = latest_post
    
    def update_info(self, page):
        self.handle = page["username"]
        self.icon = page["profile_pic_url"]


def get_page_info(handle):
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

    page = script["entry_data"]["ProfilePage"][0]["graphql"]["user"]

    return page


# get the latest post on a user's timeline
def get_latest_post(page) -> Post:
    timeline = page["edge_owner_to_timeline_media"]["edges"][0]["node"]

    latest_post = Post(
        shortcode=timeline["shortcode"],
        image=timeline["display_url"],
        caption=timeline["edge_media_to_caption"]["edges"][0]["node"]["text"],
    )

    return latest_post

# initialize User objects for each handle get the latest post for each one
def init():
    all_handles = "```"
    with open("users.txt") as f:
        for line in f:
            handle = line.strip()
            print(f"INITIALIZED {handle}")
            all_handles += f"\n{handle}"
            page = get_page_info(handle)
            latest_post = get_latest_post(page)
            current_user = User()
            current_user.update_info(page)
            current_user.set_post(latest_post)

            user_list.append(current_user)

            time.sleep(5)
    print("DONE")
    all_handles += "```"

    data = {
        "username": "Instagram",
        "avatar_url": "https://media.discordapp.net/attachments/734938642790744097/871175923083386920/insta.png",
        "embeds": [
            {
            "title": "Instagram monitor launched",
            "color": 9059001,
            "fields": [{"name": "Monitoring the following users", "value": all_handles, "inline": False}]
            }
        ]
    }

    send_webhook(data)


def send_post(user: User):
    data = make_embed(user)
    send_webhook(data)


def make_embed(user: User) -> None:
    post = user.latest_post
    data = {
        "username": "Instagram",
        "avatar_url": "https://media.discordapp.net/attachments/734938642790744097/871175923083386920/insta.png",
        "embeds": [
            {
                "title": f"New post by @{user.handle}",
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "color": 13453419,
                "image": {"url": post.image},
                "fields": [{"name": "Caption", "value": post.caption, "inline": False}],
                "footer": {
                    "text": user.handle,
                    "icon_url": user.icon,
                },
            }
        ],
    }

    return data


def send_webhook(data) -> None:
    requests.post(WEBHOOK, json=data)


def monitor():
    while True:
        for user in user_list:
            page = get_page_info(user.handle)
            current_latest_post = get_latest_post(page)
            if user.latest_post.shortcode != current_latest_post.shortcode:
                user.set_post(current_latest_post)
                send_post(user)
            
            # sleep for 5 seconds after checking posts as to not spam
            time.sleep(5)

        time.sleep(int(MONITOR_FREQUENCY))

def start():
    # attempt to log in
    try:
        login()
    except errors.LoginFailed as e:
        print(f"Login failed. Code{e}")

    init()
    monitor()

start()