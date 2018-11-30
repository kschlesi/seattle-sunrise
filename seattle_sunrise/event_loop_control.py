'''
A class for interacting with z-wave bulbs using HASS
'''
__all__ = []

import asyncio
import datetime
import random
import uuid

from .base_actor import base_actor

__all__.append("LightFlicker")
class LightFlicker(base_actor):
    '''
    a placeholder class with a function to "do an action" in the event loop
    '''
    def __init__(self, action_map={}):
        base_actor.__init__(self, action_map=action_map)

    @staticmethod
    def print_time(an_event):
        print("In print_time at: {}, with event:\n{}".format(datetime.datetime.now(), an_event['event_id']))


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
            #datetime.datetime.now() + datetime.timedelta(seconds=30),
            datetime.datetime.now() + datetime.timedelta(seconds=18),
            #datetime.datetime.now() + datetime.timedelta(seconds=47),
        ]
        for a_time in times:
            self.events.append(base_event.copy())
            self.events[-1]['start_time'] = a_time
            self.events[-1]['end_time'] = a_time + datetime.timedelta(seconds=10)
            self.events[-1]['event_id'] = uuid.uuid1()

    def get_events(self):
        self.events = [e for e in self.events if e['end_time']>datetime.datetime.now()]
        if not self.events:
            a_time = datetime.datetime.now() + datetime.timedelta(seconds=random.random()*45)
            self.events.append(base_event.copy())
            self.events[-1]['start_time'] = a_time
            self.events[-1]['end_time'] = a_time + datetime.timedelta(seconds=10)
            self.events[-1]['event_id'] = uuid.uuid1()
        return self.events

__all__.append("event_loop_control")
class event_loop_control():
    def __init__(self, event_poll_interval=10, actor_map={}):
        # configurables
        self.event_poll_interval = event_poll_interval #seconds

        # other member objects
        self.loop = asyncio.get_event_loop()
        self.events = {}
        self.to_pop = set()
        self.actor_map = actor_map

    # this should be replaced at runtime
    def get_events(self):
        print("WARNING: you should override get_events at runtime")
        return []

    def __call__(self):
        self.loop.run_until_complete(self.main_loop())
        self.loop.close()

    def execute_event(self, an_event):
        to_call = self.actor_map[an_event['calendar']].do_event
        to_call(an_event)
        self.to_pop.add(an_event['event_id'])

    def schedule_event(self, an_event):
        seconds_until_call = self.loop.time() + (an_event['start_time'] - datetime.datetime.now()).total_seconds()
        self.events[an_event['event_id']] = {'cancelable': self.loop.call_at(seconds_until_call, self.execute_event, an_event)}
        self.events[an_event['event_id']].update(an_event)

    def update_events(self, new_events):
        # make sure that every item in new_events exists in self.events (add if missing)
        add_count = 0
        update_count = 0
        for an_event in new_events:
            if not an_event['event_id'] in self.events:
                self.schedule_event(an_event)
                add_count += 1
            else:
                if not an_event == self.events[an_event['event_id']]:
                    self.events[an_event['event_id']]['cancelable'].cancel()
                    self.events.pop(an_event['event_id'])
                    self.schedule_event(an_event)

        # make sure that every item in self.events is in new_events (if not cancel)
        new_ids = [t['event_id'] for t in new_events]
        for id in self.events:
            if not id in new_ids:
                self.events[id]['cancelable'].cancel()
                self.to_pop.add(id)
        for id in self.to_pop:
            self.events.pop(id, None)
        print('<{}> new events added, <{}> existing events updated, <{}> stale events removed'.format(add_count, update_count, len(self.to_pop)))
        self.to_pop = set()

    async def main_loop(self):
        while True:
            new_events = self.get_events()
            self.update_events(new_events)
            print("about to sleep at: {}".format(datetime.datetime.now()))
            print("there are <{}> events pending".format(len(self.events)))
            await asyncio.sleep(self.event_poll_interval)
