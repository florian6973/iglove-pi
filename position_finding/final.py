#pour l'enceinte:
from distutils.log import error
import bluetooth as bt
import vlc

#pour la triangulation :
from operator import index
from turtle import pos
from scipy import optimize as opt
import numpy as np
import time
import cv2
import sys
import os
import cwiid
import json
from multiprocessing import Process, Queue

sys.path.append((os.path.dirname(os.path.abspath(__file__))))
from wiimotes_calibrate import Init_wiimotes
from ha_api import HomeAssistantAPI

ip = "172.16.16.22"
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIyOTZkZjA5ODNjYjU0MTQxOWY3ZDdlMTgyMTdhMTEyMSIsImlhdCI6MTY0MjU5NjYxMCwiZXhwIjoxOTU3OTU2NjEwfQ.FqvXpK27-NL7qkrlrvBWmVCgvjw41acrdIGihQLlQDI"

class ObjetConnecte:
    def __init__(self, position):
        self.position = position
        
    def run_script(self, name):
        api = HomeAssistantAPI(ip, token)
        api.run_script(name)
        
    def mqtt_top(self, payload, topic="default"):        
        api = HomeAssistantAPI(ip, token)
        api.mqtt_top(payload, topic)
        

class Lampe(ObjetConnecte):
    def __init__(self, position, name, state=False):
        super().__init__(position)
        self.name = name
        self.state = state
        #if not self.state:
        #    self.switch_off()
        #else:
        #    self.switch_on()

    def switch(self):
        if self.state:
            self.switch_off()
        else:
            self.switch_on()  
        self.state = not self.state          

    def switch_on(self):
        api = HomeAssistantAPI(ip, token)
        api.light_on(self.name)
        print("\tLight on")

    def switch_off(self):
        api = HomeAssistantAPI(ip, token)
        api.light_off(self.name)
        print("\tLight off")

class Speaker(ObjetConnecte):
    def __init__(self, position):
        super().__init__(position)
        self.volume = 50
        self.sensibilite = 5
        self.socket = bt.BluetoothSocket(bt.RFCOMM)
        self.player = vlc.MediaPlayer('vision.mp3')
        self.player.audio_set_volume(self.volume)

    def connect(self):
        bt.discover_devices(lookup_names = True, lookup_class = True)
        self.socket.settimeout(10)
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







width, height = 1024, 768
x = 0
y = 0
z = 0
fovw = 41.3
fovh = 33.2
 



# fcts utilitaires
def distance2(X, U : np.array, P0 : np.array) :
    '''
    Returns the distance between a point X and the line passing through P0 and P
    '''
    S1 = 0
    S2 = 0
    U = U/np.linalg.norm(U) # make sure U is normalized (useless after tests)
 
    for i in range(3) :
        tmp = (X[i]-P0[i]) 
        S1 += tmp**2
 
        S2 += tmp*U[i]

    if S2 >= 0:  #verifier que ca vise dans la bonne direction
        return S1 - S2**2
    else:
        raise ValueError
 
def Z(X, U_list, P0_list) :
    '''
    Cost function of a given point X
    '''
    S = 0
    for i, U in enumerate(U_list) :
        S += distance2(X, np.array(U), np.array(P0_list[i]))
 
    return S
 
 
 
class Triangulation :
 
    P0_list = []
 
    U_list = []
 
 
    def __init__(self, close_dots) : 
        for dot in close_dots :
            wiimote = dot[0]
            self.P0_list.append([wiimote[2], wiimote[3], wiimote[4]]) #positions de la wiimote
 
 
            # trouver le vecteur directeur du point
            d = height/(2*np.tan(np.pi*fovh/(2*180)))
 
            mx = dot[1][0] - width//2
            my = dot[1][1] - height//2

            theta = np.arctan(mx/d) # angle with the reference point along x axis 
            phi = np.arctan(my/d)




            u = np.array([np.cos(wiimote[6] + phi) * np.cos(wiimote[5] + theta), np.cos(wiimote[6] + phi) * np.sin(wiimote[5] + theta), np.sin(wiimote[6] + phi)]) 
          
            self.U_list.append(u)
 
 
    def cost_function(self, X) :
        '''
        Function to optimize
        '''
 
        return Z(X, self.U_list, self.P0_list)
 
    def find_inter(self) :
        return opt.minimize(self.cost_function, np.array([0, 0, 0])).x


 


def trian(q, close_dots):
    triangulation = Triangulation(close_dots)
    X = triangulation.find_inter()
    print(X)

if __name__ == '__main__':


    connection = Init_wiimotes()
    connection.connect_wiimotes()
    connection.calibration()
    connection.save_calibration("./calibration3.npy", "./calib_pt3.npy")
    #connection.load_calibration("./calibration3.npy", "./calib_pt3.npy")

    wiimotes = connection.wiimotes
    print(wiimotes)


    #on cree une lampe
    pos_lampe = np.array([0, 0, 0])
    pos_lampe[0] = input("Position de la lampe selon x (en cm) = ")
    pos_lampe[1] = input("Position de la lampe selon y (en cm) = ")
    pos_lampe[2] = input("Position de la lampe selon z (en cm) = ")

    lampe = Lampe(pos_lampe, False)
    list_objets = [lampe]


    DotsTS = np.array([(None, -1)]*len(wiimotes), dtype = object)
    i_count = 0

    while True :
        
        
        ## recuperer des points avec date de peromption et n° de la wiimote qui l'a pris
        for i, wiimote in enumerate(wiimotes) :
            
            # enregistrer les points dans un tuple avec son timestampe
            
            #print("wiimote : ", wiimote)
            dot = wiimote[0].state['ir_src'][0] # ATTENTION on suppose qu'on a un seul point percu
            #print(wiimote[0], dot)
            if dot != None :
                i_count += 1
                if i_count%50000 == 0:
                    TS = time.time()
                    DotsTS[i] = (dot["pos"], TS)
                    
                    
                    y = dot["pos"][0]
                    x = 1024-dot["pos"][1]
                    #screen = np.zeros((768,1024))
                    #screen[0:5,0:5] = 1
                    #screen[173:178,0:5] = 1
                    #screen[87:92,142:147] = 1
                    
                    #screen [x-5:x+5, y-5:y+5] =1
                    #cv2.imshow(f"IR Wiimote n°{i+1}", screen)
                    #cv2.waitKey(10)
                    
                    
                    
                    
                    absolute_found = False
                    close_dots = [(wiimotes[i], dot["pos"])]
                    
                    for j, DotTS in enumerate(DotsTS) :
                        if j != i and DotTS[1] > 0 :
                            #print(i, TS, j, DotTS[1])
                            if abs(DotTS[1] - TS) < 1 : 
                                absolute_found = True
                                print("found by " + str(i) + " " + str(j))
                                # on stocke les points proches temporellement
                                close_dots.append((wiimotes[j], DotTS[0]))
        
            
        
                    if not absolute_found :
                        # on integre la pos sur le capteur
                        pass
                    else :
                        # ici on triangule
                        queue = Queue()
                        p = Process(target=trian, args=(queue, close_dots))
                        p.start()
                        DotsTS = np.array([(None, -1)]*len(wiimotes), dtype = object)
                        TS2 = time.time()
                        print(TS2 - TS)
        #recuperer etats gants
        pointage = True
        if pointage:
            #recuperer direction carte arduino
            direction_gant = np.array([0., 0., 0.])

            distance_objet = [-1] * len(list_objets)
            for i, objet in enumerate(list_objets):
                try:
                    distance_objet[i] = distance2(objet.position, direction_gant, X)
                
                except ValueError:
                    print("objet derriere")
                
            seuil = 50 #distance seuil

            d = 0
            i_min = -1
            #find first distance != -1
            for i, dist in enumerate(distance_objet):
                if dist >= 0:
                    d = dist
                    i_min = i
                    break
            #if exists at least one distance != -1, find min distance > 0
            if i_min != -1:
                for i, dist in enumerate(distance_objet):
                    if dist >= 0 and dist < d:
                        d = dist
                        i_min = i
                if d < seuil:
                    objet_min = list_objets[i_min]
                    if isinstance(objet_min, Lampe):
                        objet_min.switch()
                        #envoyer commande pour interragir avec objet_min

