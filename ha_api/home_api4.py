from requests import get, post
import json
from time import sleep

url = "http://172.16.16.22:8123/api/services" # token local network
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI",
    "content-type": "application/json",
}

response = get(url, headers=headers)
rj = json.loads(response.text)
for r in rj:
    print(r["domain"])
    if r["domain"] in ["mqtt", "script"]:
        for r2 in r["services"]:
            print(r2)
        print(r)

    #print(r)
    print("")

headers2 = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI",
#    "x-ha-access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI",
    "content-type": "application/json",
}
data = {
    "entity_id":"light.antela_9w_rgb_cct"
}
dataj = json.dumps(data)
response = post("http://172.16.16.22:8123/api/services/light/turn_on", headers=headers2, data=dataj)
print(response.text)
print(response)

sleep(2)
response = post("http://172.16.16.22:8123/api/services/light/turn_off", headers=headers2, data=dataj)
print(response.text)
print(response)