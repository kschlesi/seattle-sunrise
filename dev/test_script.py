from calendar_reader import CalendarReader

cr = CalendarReader(cred_path='../../tokens')

all_events = cr.get_scheduled_events()

bl_events = cr.get_scheduled_events(device_name='Bedroom Light')

print(all_events)
print(bl_events)
