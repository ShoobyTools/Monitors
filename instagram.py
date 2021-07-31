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

def login():
    token = getCsrftoken()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-csrftoken": token,
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "user-agent": "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }

    time = int(datetime.now().timestamp())

    form = {
        "username": USERNAME,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{time}:{PASSWORD}",
        "queryParams": {},
        "optIntoOneTap": "false",
    }
    session = requests.Session()
    r = session.post(
        "https://www.instagram.com/accounts/login/ajax/", headers=headers, data=form
    )

    authenticated = json.loads(r.text)["authenticated"]
    if r.status_code == 200 and authenticated:
        print("logged in")
    else:
        print(f"Could not log in. Code {r.status_code}")


def getCsrftoken() -> str:
    r = requests.get("https://www.instagram.com/accounts/login", headers=common_headers)

    script = re.findall(r"window._sharedData = .*", r.text)
    if len(script) != 0:
        script = script[0].strip("</script>").strip("window._sharedData = ").strip(";")
        script = json.loads(script)

    return str(script["config"]["csrf_token"])


login()


def get_posts():
    handle = "undefeatedinc"

    page_url = f"https://www.instagram.com/{handle}/"

    r = requests.get(page_url, verify=True, headers=common_headers)

    script = re.findall(r'"entry_data":.*', r.text)
    if len(script) != 0:
        script = script[0].strip("'")
        script = script.replace(";</script>", "")
        script = "{" + script
        script = json.loads(script)

    timeline = script["entry_data"]["ProfilePage"][0]["graphql"]["user"][
        "edge_owner_to_timeline_media"
    ]["edges"]

    for post in timeline:
        print(post["node"]["shortcode"])
