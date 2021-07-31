import requests
import re
import json

USERNAME = "spamming6@gmail.com"
PASSWORD = "HtG4a!qnxTcP9NzFx7HpAy9g4*nDhBAo"

handle = "undefeatedinc"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}

page_url = f"https://www.instagram.com/{handle}/"

r = requests.get(page_url, verify=True, headers=headers)

script = re.findall(r'"entry_data":.*', r.text)
if len(script) != 0:
    script = script[0].strip("'")
    script = script.replace(";</script>", "")
    script = "{" + script
    script = json.loads(script)

print(script)
timeline = script["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]

for post in timeline:
    print(post["node"]["shortcode"])