from requests import get, post
import json

url = "http://172.16.16.22:8123/api/services"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI",
    "content-type": "application/json",
}

response = get(url, headers=headers)
rj = json.loads(response.text)
for r in rj:
    print(r["domain"])
    if r["domain"] == "mqtt":
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
    "payload":"Essai3",
    "topic":"testTopic",
    "retain":False
}
dataj = json.dumps(data)
response = post("http://172.16.16.22:8123/api/services/mqtt/publish", headers=headers2, data=dataj)
print(response)