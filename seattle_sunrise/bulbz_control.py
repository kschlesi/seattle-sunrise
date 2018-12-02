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
        self.max_brightness = 255
        self.fade_on_time = 20. * 60. # 20 minutes in seconds

    @property
    def base_target(self):
        return "{}:{}/{}".format(self.hass_api['host'], self.hass_api['port'], self.hass_api['api_uri'])

    def set_output(self, bulb, level):
        url = '/'.join([self.base_target,self.hass_api['operations']['turn_on']])
        print("post to: [{}]".format(url))
        # this next line needs some error handling
        ret = requests.post('/'.join([self.base_target,self.hass_api['operations']['turn_on']]),
                            json={'brightness':level, 'entity_id': bulb},
                            headers=self.headers,
                           )
        if not ret.status_code in [200, 201]:
            print(ret.request)
            raise ValueError("request received non-success code")

    def turn_on(self, bulb):
        self.set_output(bulb, self.max_brightness)

    def turn_off(self, bulb):
        ret = requests.post('/'.join([self.base_target,self.hass_api['operations']['turn_off']]),
                            json={'entity_id': bulb},
                            headers=self.headers,
                           )
        if not ret.status_code in [200, 201]:
            raise ValueError("request received non-success code")

    @staticmethod
    def print_time(an_event):
        print("In print_time at: {}, with event:\n{}".format(datetime.datetime.now(), an_event))

    def be_on_interval(self, an_event):
        '''
        Turn on all bulbz to full at the start of the event, turn them off at the end
        '''
        to_sleep = (an_event['end_time'] - datetime.datetime.now()).total_seconds()
        print("Turn on (sleep {})".format(to_sleep))
        for a_bulb in self.list_of_bulbz:
            self.turn_on(a_bulb)
        time.sleep(to_sleep)
        print("-------> Turn off")
        for a_bulb in self.list_of_bulbz:
            self.turn_off(a_bulb)

    def fade_on(self, interval):
        n_steps = self.max_brightness * len(self.list_of_bulbz)
        print('will fade on for <{}> steps over <{}> seconds'.format(n_steps, interval))
        sleep_interval = interval / n_steps
        current_levels = [0 for i in range(len(self.list_of_bulbz))]
        for i_step in range(n_steps):
            this_bulb = i_step % len(self.list_of_bulbz)
            current_levels[this_bulb] += 1
            print("setting {} to {}".format(this_bulb, current_levels[this_bulb]))
            self.set_output(self.list_of_bulbz[this_bulb], current_levels[this_bulb])
            time.sleep(sleep_interval)
        print("fade on complete")

    def sunrise(self, an_event):
        '''
        Turn on/up all bulbz in an alternating fashion over the lesser of the event duration
        or self.fade_on_time, starting at the event's sart time.
        Turn them all off at the end of the event.
        '''
        print("starting sunrise")
        this_interval = min(self.fade_on_time, (an_event['end_time'] - an_event['start_time']).total_seconds())
        self.fade_on(this_interval)
        # if something went wrong, sleep 0, not negative time
        to_sleep = max(0.0, (an_event['end_time'] - datetime.datetime.now()).total_seconds())
        time.sleep(to_sleep)
        print("sunrise over, turning off")
        for a_bulb in self.list_of_bulbz:
            self.turn_off(a_bulb)
