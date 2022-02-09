import bluetooth as bt
import vlc
from time import sleep

class SpeakerController:
    def __init__(self):
       self.volume = 50
       self.sensibilite = 5
       self.socket = bt.BluetoothSocket(bt.RFCOMM)
       self.player = vlc.MediaPlayer('vision.mp3')
       self.player.audio_set_volume(self.volume)

    def connect(self):
        bt.discover_devices(lookup_names = True, lookup_class = True)
        self.socket = bt.BluetoothSocket(bt.RFCOMM)
        self.socket.settimeout(5)
        self.socket.connect(('08:DF:1F:BD:D0:98', 1))

    def volumeUp(self):
        if self.volume < 100 - self.sensibilite:
            self.player.audio_set_volume(self.volume + self.sensibilite)

    def volumeDown(self):
        if self.volume >= self.sensibilite:
            self.player.audio_set_volume(self.volume - self.sensibilite)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()
    
    def stop(self):
        self.player.stop()


sc = SpeakerController()
#sc.connect()
sc.play()
sleep(10)
sc.pause()
sleep(2)
sc.play()
sleep(2)
sc.volumeUp()
sleep(2)
sc.volumeDown()
sleep(2)
sc.stop()