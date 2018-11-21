'''
A class for interacting with z-wave bulbs using HASS
'''

__all__ = []

import asyncio
import datetime
import json
import uuid

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
#requests.post(url_base+turn_on_target, json=json.dumps({'brightness':1, 'entity_id': light_entity}))

__all__.append("LightFlicker")
class LightFlicker:
    '''
    a placeholder class with a function to "do an action" in the event loop
    '''
    @staticmethod
    def print_time():
        print("In print_time at: ", datetime.datetime.now())


base_event = {
    'event_id': None,
    'start_time': None,
    'end_time': None,
    'action': None,
    'created': None,
    'updated': None,
    'calendar': None,
    'calendar_id': None,
}

__all__.append("EventGetter")
class EventGetter:
    '''
    a placeholder class to define/return some events for testing
    '''
    def __init__(self):
        self.events = []
        times = [
            datetime.datetime.now() + datetime.timedelta(seconds=3),
            datetime.datetime.now() + datetime.timedelta(seconds=30),
            datetime.datetime.now() + datetime.timedelta(seconds=18),
            datetime.datetime.now() + datetime.timedelta(seconds=47),
        ]
        for a_time in times:
            self.events.append(base_event.copy())
            self.events[-1]['start_time'] = a_time
            self.events[-1]['event_id'] = uuid.uuid1()

    def get_events(self):
        return self.events

__all__.append("event_loop_control")
class event_loop_control():
    def __init__(self):
        # configurables
        self.event_poll_interval = 10 #seconds

        # other member objects
        self.loop = asyncio.get_event_loop()
        self.tasks = {}

    def __call__(self):
        self.loop.run_until_complete(self.main_loop())
        self.loop.close()

    def schedule_task(self, a_task):
        seconds_until_call = self.loop.time() + (a_task['start_time'] - datetime.datetime.now()).total_seconds()
        self.tasks[a_task['event_id']] = {'cancelable': self.loop.call_at(seconds_until_call, light_flicker.print_time)}
        self.tasks[a_task['event_id']].update(a_task)

    def update_tasks(self, new_tasks):

        # make sure that every item in new_tasks exists in self.tasks (add if missing)
        for a_task in new_tasks:
            if not a_task['event_id'] in self.tasks:
                self.schedul_task(a_task)
        print('new tasks added')

        # make sure that all existing tasks are in new_tasks (cancel and remove if missing)
        to_pop = []
        for id in self.tasks:
            if not id in new_tasks:
                self.tasks[id]['cancelable'].cancel()
                to_pop.append(id)
        for id in to_pop:
            self.tasks.pop(id)

    async def main_loop(self):
        # make instances
        light_flicker = LightFlicker()
        event_getter = EventGetter()

        count = 0
        while True:
            print('existing tasks are: ', self.tasks)
            new_events = event_getter.get_events()
            self.update_tasks(new_events)
            print("task list updated")
            count += 1
            print('about to sleep for the {}th time: '.format(count))
            await asyncio.sleep(self.event_poll_interval)
            # for now, break after 10 loops, remove this when first version comes out
            if count > 10:
                break

