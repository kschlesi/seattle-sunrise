'''
A class for interacting with z-wave bulbs using HASS
'''

__all__ = []

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
class bulbz_control():
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



