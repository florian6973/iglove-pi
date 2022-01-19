import dbus
import re

bus = dbus.SessionBus()

bus.get_unique_name()

bus.request_name('io.github.amhndu.test')

service = ""
for s in bus.list_names():
    if re.match('org.mpris.MediaPlayer2.', s):
        service = s
        print(s)
player = dbus.SessionBus().get_object(service, '/org/mpris/MediaPlayer2')

interface = dbus.Interface(player, dbus_interface = 'org.mpris.MediaPlayer2.Player')
prop = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
#interface.Play()
#interface.Pause()



