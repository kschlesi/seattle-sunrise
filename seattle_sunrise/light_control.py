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
    def __init__(self, action_map={}):
        self.action_map = action_map

    def do_event(self, an_event):
        to_do = self.action_map[an_event['action']]
        to_do(an_event)

    @staticmethod
    def print_time(an_event):
        print("In print_time at: {}, with event:\n{}".format(datetime.datetime.now(), an_event))


base_event = {
    'event_id': None,
    'start_time': None,
    'end_time': None,
    'action': 'wake',
    'created': None,
    'updated': None,
    'calendar': 'alarmclock',
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
            self.events[-1]['end_time'] = a_time + datetime.timedelta(seconds=1)
            self.events[-1]['event_id'] = uuid.uuid1()

    def get_events(self):
        self.events = [e for e in self.events if e['end_time']>datetime.datetime.now()]
        return self.events

__all__.append("event_loop_control")
class event_loop_control():
    def __init__(self, event_poll_interval=10, actor_map={}):#, actions_map={}):
        # configurables
        self.event_poll_interval = event_poll_interval #seconds

        # other member objects
        self.loop = asyncio.get_event_loop()
        self.tasks = {}
        self.to_pop = set()
        self.actor_map = actor_map

    # this should be replaced at runtime
    def get_events(self):
        print("WARNING: you should override get_events at runtime")
        return []

    def __call__(self):
        self.loop.run_until_complete(self.main_loop())
        self.loop.close()

    def execute_task(self, a_task):
        to_call = self.actor_map[a_task['calendar']].do_event
        to_call(a_task)
        self.to_pop.add(a_task['event_id'])

    def schedule_task(self, a_task):
        seconds_until_call = self.loop.time() + (a_task['start_time'] - datetime.datetime.now()).total_seconds()
        #to_call = self.actor_map[a_task['calendar']].do_event
        #self.tasks[a_task['event_id']] = {'cancelable': self.loop.call_at(seconds_until_call, to_call, a_task)}
        self.tasks[a_task['event_id']] = {'cancelable': self.loop.call_at(seconds_until_call, self.execute_task, a_task)}
        self.tasks[a_task['event_id']].update(a_task)

    def update_tasks(self, new_tasks):
        # make sure that every item in new_tasks exists in self.tasks (add if missing)
        add_count = 0
        for a_task in new_tasks:
            if not a_task['event_id'] in self.tasks:
                self.schedule_task(a_task)
                add_count += 1
        print('<{}> new tasks added'.format(add_count))

        # ensure that all known tasks are in new_tasks (cancel and remove if not)
        #self.to_pop = []
        new_ids = [t['event_id'] for t in new_tasks]
        for id in self.tasks:
            if not id in new_ids:
                self.tasks[id]['cancelable'].cancel()
                self.to_pop.add(id)
        for id in self.to_pop:
            self.tasks.pop(id)
        self.to_pop = set()
        print("<{}> stale events removed".format(len(self.to_pop)))

    async def main_loop(self):
        while True:
            new_events = self.get_events()
            self.update_tasks(new_events)
            print("about to sleep at: {}".format(datetime.datetime.now()))
            print("there are <{}> events pending".format(len(self.tasks)))
            await asyncio.sleep(self.event_poll_interval)
