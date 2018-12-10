import seattle_sunrise

cr = seattle_sunrise.CalendarReader(credendials_path='var/seattle_sunrise/secrets')

all_events = cr.get_scheduled_events()

bl_events = cr.get_scheduled_events(device_name='Bedroom Light')

print(all_events)
print(bl_events)
