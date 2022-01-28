import homeassistant
url = 'http://172.16.16.22:8123/api/'
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI'


client = Client(
    url, token
)

services = client.get_domains()

#print(services.mqtt.publish(payload="test", topic="try"))
#services.light.turn_on(entity_id='light.living_room_lamp')



api = API(url, token)

print('-- Available services:')
services = remote.get_services(api)
for service in services:
    print(service['services'])

print('\n-- Available events:')
events = remote.get_event_listeners(api)
for event in events:
    print(event)

print('\n-- Available entities:')
entities = remote.get_states(api)
for entity in entities:
    print(entity)
