import bluetooth as bt
import vlc
from time import sleep

s = bt.BluetoothSocket(bt.RFCOMM)
s.connect(('00:17:AB:39:AB:21', 1))


p = vlc.MediaPlayer('vision.mp3')

sensibilite = 5


p.play()
#p.pause()


def VolumeUp():
    global p
    global sensibilite
    v = p.audio_get_volume()
    if v < 100:
        p.audio_set_volume(v + sensibilite)
        
def VolumeDown():
    global p
    global sensibilite
    v = p.audio_get_volume()
    if v > 0:
        p.audio_set_volume(v - sensibilite)
        
        


