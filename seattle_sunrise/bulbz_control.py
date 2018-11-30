'''
A class for interacting with z-wave bulbs using HASS
'''
__all__ = []

import asyncio
import datetime
import time

import requests
import yaml

from .base_actor import base_actor

# these should be constructed in some reasonable way.
url_base = "http://192.168.0.11:8123/api/"
turn_on_target = "services/light/turn_on"
light_entity = 'light.linear_lb60z1_dimmable_led_light_bulb_level'
headers = {
    # this should clearly be from a credential file or something
    'Authorization': 'Bearer BABBLE_FISH',
    'content-type': 'application/json',
}
#requests.post(url_base+turn_on_target, json=json.dumps({'brightness':1, 'entity_id': light_entity}))

__all__.append("bulbz_control")
class bulbz_control(base_actor):
    '''
    Define a group of "bulbz" and expose some convenient actions to take with them.
    '''
    def __init__(self, headers_file, action_map={}, bulbz_list=[], hass_api_map={}):
        base_actor.__init__(self, action_map)

        self.list_of_bulbz = bulbz_list
        self.headers = yaml.load(open(headers_file, 'r'))

        self.hass_api = {
            'host': 'http://localhost',
            'port': 8123,
            'api_uri': 'api',
            'operations': {
                'turn_on': 'services/light/turn_on',
                'turn_off': 'services/light/turn_off',
            },
        }
        self.hass_api.update(hass_api_map)

    @property
    def base_target(self):
        return "{}:{}/{}".format(self.hass_api['host'], self.hass_api['port'], self.hass_api['api_uri'])

    # needs to look like: `r = requests.post("http://192.168.0.11:8123/api/services/light/turn_on", json={'entity_id':light_entity, 'brightness': 1}, headers=headers)`
    def set_output(self, bulb, level):
        url = '/'.join([self.base_target,self.hass_api['operations']['turn_on']])
        print("post to: [{}]".format(url))
        # this next line needs some error handling
        ret = requests.post('/'.join([self.base_target,self.hass_api['operations']['turn_on']]),
                            json={'brightness':level, 'entity_id': light_entity},
                            headers=self.headers,
                           )
        if not ret.status_code in [200, 201]:
            print(ret.request)
            raise ValueError("request received non-success code")

    def turn_on(self, bulb):
        self.set_output(bulb, 255)

    def turn_off(self, bulb):
        ret = requests.post('/'.join([self.base_target,self.hass_api['operations']['turn_off']]),
                            json={'entity_id': light_entity},
                            headers=self.headers,
                           )
        if not ret.status_code in [200, 201]:
            raise ValueError("request received non-success code")

    @staticmethod
    def print_time(an_event):
        print("In print_time at: {}, with event:\n{}".format(datetime.datetime.now(), an_event))

    def be_on_interval(self, an_event):
        to_sleep = (an_event['end_time'] - datetime.datetime.now()).total_seconds()
        print("Turn on (sleep {})".format(to_sleep))
        for a_bulb in self.list_of_bulbz:
            self.turn_on(a_bulb)
        time.sleep(to_sleep)
        print("-------> Turn off")
        for a_bulb in self.list_of_bulbz:
            self.turn_off(a_bulb)

    def fade_on(self, an_event):
        pass
