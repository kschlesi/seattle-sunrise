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
    @staticmethod
    def print_time():
        print("In print_time at: ", datetime.datetime.now())

__all__.append("EventGetter")
class EventGetter:
    def __init__(self):
        self. events = {
            'a': datetime.datetime.now() + datetime.timedelta(seconds=3),
            'b': datetime.datetime.now() + datetime.timedelta(seconds=30),
            'c': datetime.datetime.now() + datetime.timedelta(seconds=18),
            'd': datetime.datetime.now() + datetime.timedelta(days=1, seconds=3),
        }
    def get_events(self):
        return self.events

__all__.append("light_loop")
async def light_loop(loop):
    # make instances
    light_flicker = LightFlicker()
    event_getter = EventGetter()

    # pre-schedule an event so I can see it get removed
    tasks = {'fail': loop.call_at(loop.time()+10000, light_flicker.print_time)}

    count = 0
    while True:
        print('tasks are: ', tasks)
        new_events = event_getter.get_events()
        for id,a_time in new_events.items():
            if not id in tasks:
                when_to_call = loop.time()+(a_time-datetime.datetime.now()).total_seconds()
                tasks[id] = loop.call_at(when_to_call, light_flicker.print_time)
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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(light_loop(loop))
    loop.close()
