'''
'''

__all__ = []

class base_actor():
    '''
    Abstraction layer for handling event loop interface
    '''
    def __init__(self, action_map={}):
        '''
        action_map (dict):
        '''
        if not isinstance(action_map, dict):
            raise TypeError("action_map must be a dictionary")
        self.action_map = action_map

    def do_event(self, an_event):
        to_do = self.action_map[an_event['action']]
        to_do(an_event)
