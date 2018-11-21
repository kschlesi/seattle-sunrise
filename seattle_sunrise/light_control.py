'''
A class for interacting with z-wave bulbs using HASS
'''

__all__ = []

import asyncio
import datetime
import json

import requests

# these should be constructed in some reasonable way.
url_base = "http://192.168.0.11:8123/api/"
turn_on_target = "services/light/turn_on"
light_entity = 'light.linear_lb60z1_dimmable_led_light_bulb_level'
headers = {
    # this should clearly be from a credential file or something
    'Authorization': 'Bearer BABBLE_FISH',
    'content-type': 'application/json',
}
requests.post(url_base+turn_on_target, json=json.dumps({'brightness':1, 'entity_id': light_entity}))

__all__.append("LightFlicker")
class LightFlicker:
    '''
    a placeholder class with a function to "do an action" in the event loop
    '''
    @staticmethod
    def print_time():
        print("In print_time at: ", datetime.datetime.now())

__all__.append("EventGetter")
class EventGetter:
    '''
    a placeholder class to define/return some events for testing
    '''
    def __init__(self):
        self.events = {
            'a': datetime.datetime.now() + datetime.timedelta(seconds=3),
            'b': datetime.datetime.now() + datetime.timedelta(seconds=30),
            'c': datetime.datetime.now() + datetime.timedelta(seconds=18),
            'd': datetime.datetime.now() + datetime.timedelta(days=60, seconds=3),
        }
    def get_events(self):
        return self.events

__all__.append("event_loop_control")
class event_loop_control():
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def __call__(self):
        self.loop.run_until_complete(self.main_loop())
        self.loop.close()

    async def main_loop(self):
        # make instances
        light_flicker = LightFlicker()
        event_getter = EventGetter()

        # pre-schedule an event so I can see it get removed
        tasks = {'fail': self.loop.call_at(self.loop.time()+10000, light_flicker.print_time)}

        count = 0
        while True:
            print('tasks are: ', tasks)
            new_events = event_getter.get_events()
            for id,a_time in new_events.items():
                if not id in tasks:
                    when_to_call = self.loop.time()+(a_time-datetime.datetime.now()).total_seconds()
                    tasks[id] = self.loop.call_at(when_to_call, light_flicker.print_time)
            print('new tasks added')
            to_pop = []
            for id in tasks:
                if not id in new_events:
                    tasks[id].cancel()
                    to_pop.append(id)
            [tasks.pop(id) for id in to_pop]
            print("removed tasks purged")
            count += 1
            print('about to sleep again: ', count)
            await asyncio.sleep(10)
            if count > 10:
                break

