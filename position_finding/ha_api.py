# 172.16.16.22
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI

from requests import get, post
import json

class HomeAssistantAPI:
  def __init__(self, ip, token):
    self.url = "http://" + ip + ":8123/api/services" # token local network
    self.headers = {
      "Authorization": "Bearer " + token,
      "content-type": "application/json",
    }
    
  def __prep_data_json__(self, type, name):
    return json.dumps(
      {
        "entity_id": type + "." + name
      }
    )
 
  # ex : antela_9w_rgb_cct
  def light_on(self, name):
    response = post(self.url + "/light/turn_on", headers=self.headers, data=self.__prep_data_json__("light", name))
    return response
  
  def light_off(self, name):
    response = post(self.url + "/light/turn_off", headers=self.headers, data=self.__prep_data_json__("light", name))
    return response
  
  # ex : iled_blink
  def run_script(self, name):
    response = post(self.url + "/script/turn_on", headers=self.headers, data=self.__prep_data_json__("script", name))
    return response    
  
  # MQTT needs to be configured in Home Assistant before
  # ex : testTopic
  def mqtt_top(self, payload, topic="default"):    
    data = json.dumps({
        "payload": payload,
        "topic": topic,
        "retain": False
    })
    response = post(self.url + "/mqtt/publish", headers=self.headers, data=data)
    return response
    
