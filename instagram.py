import requests
import re
import json
from datetime import datetime

USERNAME = "spamming6@gmail.com"
PASSWORD = "HtG4a!qnxTcP9NzFx7HpAy9g4*nDhBAo"
WEBHOOK = "https://discord.com/api/webhooks/871062047864004669/ce8nQYNVUkaHQWl1TV-Czt74R5nTAdONH6AABSfeC-cScWQpP6wgkh6qeGV7QXA4OgAc"

common_headers = {
    "user-agent": "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}

latest_post_shortcode = ""

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
        print("logged in")
    else:
        print(f"Could not log in. Code {r.status_code}")


def getCsrftoken() -> str:
    r = session.get("https://www.instagram.com/accounts/login", headers=common_headers)

    script = re.findall(r"window._sharedData = .*", r.text)
    if len(script) != 0:
        script = script[0].strip("</script>").strip("window._sharedData = ").strip(";")
        script = json.loads(script)

    return str(script["config"]["csrf_token"])


class Post:
    def __init__(self, handle, user_icon, shortcode, image, caption) -> None:
        self.handle = handle
        self.user_icon = user_icon
        self.shortcode = shortcode
        self.image = image
        self.caption = caption


def get_posts(handle):
    page_url = f"https://www.instagram.com/{handle}/"

    r = session.get(page_url, verify=True, headers=common_headers)

    script = re.findall(r'"entry_data":.*', r.text)
    if len(script) != 0:
        script = script[0].strip("'")
        script = script.replace(";</script>", "")
        script = "{" + script
        script = json.loads(script)

    user = script["entry_data"]["ProfilePage"][0]["graphql"]["user"]
    timeline = user["edge_owner_to_timeline_media"]["edges"]

    posts = []
    for post in timeline:
        current_post = Post(
            handle,
            user["profile_pic_url"],
            post["node"]["shortcode"],
            post["node"]["display_url"],
            post["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"],
        )
        posts.append(current_post)

    return posts


def get_latest_post(handle):
    posts = get_posts(handle)
    if latest_post_shortcode != posts[0].shortcode:
        data = make_embed(posts[0])
        send_webhook(data)


def make_embed(post):
    data = {
        "username": "Instagram Monitor",
        "avatar_url": "https://media.discordapp.net/attachments/734938642790744097/871175923083386920/insta.png",
        "embeds": [
            {
                "title": f"New post by @{post.handle}",
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "color": 13453419,
                "image": {"url": post.image},
                "fields": [{"name": "Caption", "value": post.caption, "inline": False}],
                "footer": {
                    "text": post.handle,
                    "icon_url": post.user_icon,
                },
            }
        ],
    }

    return data


def send_webhook(data):
    requests.post(WEBHOOK, json=data)


login()
posts = get_latest_post("undefeatedinc")
