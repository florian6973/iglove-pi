from os.path import exists
import cwiid
import time
import numpy as np
import cv2
from scipy import optimize as opt
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("tkagg")
import final as ff
import asyncio

from multiprocessing import Process, Queue, Manager
manager = Manager()
last_pos_s = manager.list()
for i in range(3):
    last_pos_s.append(0.)

default_MACs = ["00:19:1D:93:DD:E4", "CC:9E:00:5D:2C:ED", "E0:0C:7F:E7:CE:F8", "00:1E:A9:40:EA:9F"]#, "00:19:1D:78:02:71"]

width, height = 1024, 768
fovw = 43.
fovh = 33.
d = width/(2*np.tan(fovw*np.pi/180.))
dh = height/(2*np.tan(fovh*np.pi/180.))

def string_to_numpy(text, dtype=None):
    """
    Convert text into 1D or 2D arrays using np.matrix().
    The result is returned as an np.ndarray.
    """
    import re
    text = text.strip()
    # Using a regexp, decide whether the array is flat or not.
    # The following matches either: "[1 2 3]" or "1 2 3"
    is_flat = bool(re.match(r"^(\[[^\[].+[^\]]\]|[^\[].+[^\]])$",
                            text, flags=re.S))
    # Replace newline characters with semicolons.
    text = text.replace("]\n", "];")
    # Prepare the result.
    result = np.asarray(np.matrix(text, dtype=dtype))
    return result.flatten() if is_flat else result


class Wiimote:
    def __init__(self, mac, i):
        self.MAC = mac
        self.wiimote = cwiid.Wiimote(mac)
        self.i = i

        self.wiimote.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN
        self.wiimote.rumble = 1
        time.sleep(0.2)
        self.wiimote.rumble = 0
        self.wiimote.led = self.i + 1

        self.pos = np.array([0., 0., 0.])
        self.angles = np.array([0., 0.])

    def get_buttons(self):
        return self.wiimote.state["buttons"]

    def set_pos(self, x, y, z):
        self.pos = np.array([x, y, z])

    def __repr__(self) -> str:
        return f"{self.MAC};{self.i};{self.pos};{self.angles}"

    def __str__(self) -> str:
        return self.__repr__()

    def get_point(self):
        dots = []
        for dot in self.wiimote.state['ir_src']:
            if dot != None:
                dots.append(np.array([width-dot["pos"][0],height-dot["pos"][1]]))
        if len(dots) > 0:
            #print(dots)
            #print(np.mean(dots, axis=0))
            return np.mean(dots, axis=0)
        else:
            return None
                
    @staticmethod
    def get_deltapoint(x, y):
        mx = -(x - width//2)
        my = -(y - height//2)
        return mx, my

        
    def __c_arctan__(self, x1, x2):
        act = np.arctan(x2/x1)
        if x2 > 0 and x1 > 0:
            return act
        elif x2 > 0 and x1 < 0:
            return np.pi + act
        elif x2 < 0 and x1 < 0:
            return act - np.pi
        else:
            return act
    
    def calc_angles(self, calib_pt):
        res = self.get_point()
        if res is not None:
            res = res[0], res[1]
            x, y = res
            mx, my = Wiimote.get_deltapoint(x, y)
            u = calib_pt - self.pos
            normu = np.linalg.norm(u)
            self.angles[0] = self.__c_arctan__(calib_pt[0] - self.pos[0],(calib_pt[1] - self.pos[1])) + np.arctan(mx/d) 
            self.angles[1] = np.arcsin((calib_pt[2] - self.pos[2])/normu) - np.arctan(my/dh)
            print("angles",
                    x, y, mx, my, 
                    np.arctan(mx/d),
                    -np.arctan(my/dh),
                    self.angles, end ="\r")
            return int(x), int(y)
        else:
            return None #res


 
class PosSolver: 
    P0_list = [] 
    U_list = []
    angles = []

    def __init__(self) : 
       pass 

    def clear(self):
        self.P0_list = []
        self.U_list = []
        self.angles = []

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.clear()
        for i, u in enumerate(self.U_list):
            U, V, W = u*40
            X, Y, Z = self.P0_list[i]
            print("points pl", X, Y, Z, U, V, W)
            ax.quiver(X, Y, Z, U, V, W)
        ax.set_xlim([-10, 130])
        ax.set_ylim([-10, 250])
        ax.set_zlim([-10, 110])
        plt.show()

    def not_enough(self):
        return len(self.U_list) < 2

    def rot_yaw(self, alpha):
        return np.array([
            [np.cos(alpha), -np.sin(alpha), 0.],
            [np.sin(alpha), np.cos(alpha), 0.],
            [0., 0., 1.]
        ])
    def rot_pitch(self, beta):
        return np.array([
            [np.cos(beta), 0., np.sin(beta)],
            [0., 1., 0.],
            [-np.sin(beta), 0., np.cos(beta)]
        ])

    def compute_u(self, angles, x, y):
        mx, my = Wiimote.get_deltapoint(x, y)
        theta = -np.arctan(mx/d)
        phi = -np.arctan(my/dh)
        u_manette = np.array([
            np.cos(theta)*np.cos(phi),
            np.sin(theta)*np.cos(phi),
            np.sin(phi)
        ])
        print(u_manette)
        rot = self.rot_yaw(angles[0]) @ self.rot_pitch(angles[1])
        u_rep = rot.dot(u_manette)
        u_rep[2] = -u_rep[2]
        return u_rep

    def append(self, wiimote):
        pt = wiimote.get_point()
        if pt is not None:
            self.angles.append(wiimote.angles) # TODO refactor
            self.P0_list.append(wiimote.pos)
            x, y = pt
            self.U_list.append(self.compute_u(wiimote.angles, x, y))

       
    @staticmethod
    def distance(X, U : np.array, P0 : np.array) :
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
        return S1 - S2**2

    @staticmethod
    def Z(X, U_list, P0_list, detail=False) :
        '''
        Cost function of a given point X
        '''
        S = 0
        for i, U in enumerate(U_list) :
            lc = PosSolver.distance(X, np.array(U), np.array(P0_list[i]))
            if detail:
                print(U, lc)
            S += lc
    
        return S
 
    def cost_function(self, X) :
        '''
        Function to optimize
        '''

        return PosSolver.Z(X, self.U_list, self.P0_list)
 
    def find_inter(self) :
        try:
            #print(self.U_list)
            #print(self.P0_list)
            #res = opt.minimize(self.cost_function, self.P0_list[0], method="Powell")
            res = opt.minimize(self.cost_function, self.P0_list[0], method="Nelder-Mead")
            print(res.message)
            print(res.success)
            print(res.fun)
            #print(PosSolver.Z(res.x, self.U_list, self.P0_list, True))
            #print(PosSolver.Z([50, 90, 3], self.U_list, self.P0_list, True))
            #print(PosSolver.Z(self.P0_list[0], self.U_list, self.P0_list, True))
            return res.x
        except Exception as ee:
            print(ee)
            return [-1, -1, -1]



class Room:
    def __init__(self, mac_wiimotes):
        self.MACs = mac_wiimotes
        self.wms = []
        self.calib_pt = np.array([0.,0.,0.])
        self.connect_wiimotes()
    
    def init(self, conf_file):
        if exists(conf_file):
            self.load_conf(conf_file)
        else:
            self.calibrate()
            self.save_conf(conf_file)
        print(self.wms)
        print(self.calib_pt)

    def load_conf(self, file):
        with open(file, "r") as f:
            self.calib_pt = string_to_numpy(f.readline())
            nb = int(f.readline())
            for i in range(nb):
                line = f.readline().split(';')

                # wiimote = Wiimote(line[0], line[1])
                # check right wiimote

                self.wms[i].pos = string_to_numpy(line[2])
                self.wms[i].calc_angles(self.calib_pt)   
                self.wms[i].angles = string_to_numpy(line[3])
        print(self.calib_pt, self.wms)

    def save_conf(self, file):
        with open(file, "w") as f:
            f.write(np.array_str(self.calib_pt) + "\n")
            f.write(str(len(self.wms))+"\n")
            for w in self.wms:
                f.write(f"{w.MAC};{w.i};{np.array_str(w.pos)};{np.array_str(w.angles)}\n")#;{np.array_str(w.angles)}\n")

    def connect_wiimotes(self) :
        for i, mac in enumerate(self.MACs):
            while True :
                try:                    
                    print(f'Please press buttons 1 + 2 on Wiimote n°{i+1}')
                    time.sleep(0.2)
                    self.wms.append(Wiimote(mac, i))
                    print(f"Wiimote {i+1} connected")                    
                except RuntimeError:
                    print("Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!")
                    continue
                break    

        print("All Wiimotes connected!")

    def calibrate(self):
        print("To calibrate your wiimotes place a IR source in the middle of your room and make sure that each wiimote sees the dot inside the square")
        print("When it's done press A or B on the wiimote")
        print("Warning : make sure that the wiimote is leveled along the left-right axis (horizontal calibration in progress)")
        
        self.calib_pt[0] = input("Calibration point x (in cm) = ")
        self.calib_pt[1] = input("Calibration point y (in cm) = ")
        self.calib_pt[2] = input("Calibration point z (in cm) = ")

        for i, wiimote in enumerate(self.wms):            
            x = int(input(f"Wiimote n°{i+1} point x (in cm) = "))
            y = int(input(f"Wiimote n°{i+1} point y (in cm) = "))
            z = int(input(f"Wiimote n°{i+1} point z (in cm) = "))
            
            wiimote.set_pos(x, y, z)
            
            while(True):
                screen = np.zeros((768,1024))
                screen[378 : 392, 515:529] = 1
                screen[380 : 390, 517:527] = 0
     
                res = wiimote.calc_angles(self.calib_pt)       
                if res is not None:
                    x, y = res
                else:
                    x = 5
                    y = 5

                #print(x,y)                                
                screen[y-5:y+5, x-5:x+5] = 1

                cv2.imshow(f"IR Wiimote n°{i+1}", screen)
                cv2.waitKey(10)
              
                buttons = wiimote.get_buttons()
                if buttons == 8 or buttons == 12 :
                    break                 
            
                if buttons == 16+4096 :
                    quit()
            cv2.destroyAllWindows()

            print("\ncorrection finale", wiimote.angles)  
        pass

    def get_position(self):
        try:
            solver = PosSolver()
            print("Looking for an IR LED...")
            while solver.not_enough():
                solver.clear()
                print(self.wms)
                for i, wiimote in enumerate(self.wms):
                    solver.append(wiimote)
                print(len(solver.U_list), "objects", end="\r")
            queue = Queue()
            p = Process(target=Room.triangulate, args=(queue, solver))
            p.start()
            p.join()
        except Exception as ee:
            print(ee)
        pos = queue.get()
        print("loc", pos)
        return pos

    @staticmethod
    def triangulate(q, solver):     
        solver.plot() 
        res = solver.find_inter()
        q.put(res)
        return res

room = None
list_objets = []

def init_position():
    global room
    room = Room(default_MACs)
    room.init("conf03.txt")

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
        raise ValueError("Object behind")

import asyncio, time, random

start_time = time.time()
is_look = False


def stuff():
    global room
    global is_look
    global last_pos_s
    if not is_look:
        is_look = True
        pos = room.get_position()
        if pos is not None:
            print("changing")
            last_pos_s[0] = pos[0]
            last_pos_s[1] = pos[1]
            last_pos_s[2] = pos[2]
        print("loc", last_pos_s)
        print(round(time.time() - start_time, 1), "Finished doing stuff")
        is_look = False
    else:
        print("ignore")


def do_stuff_periodically():
    print("Running...")
    while True:
        print(round(time.time() - start_time, 1), "Starting periodic function")
        stuff()
        time.sleep(3)

def start_proc():
    p = Process(target=do_stuff_periodically, args=())
    p.start()

def update_pointage(c_data):      
    global room     
    global list_objets   
    global last_pos_s
    print("update", last_pos_s)      
    #recuperer etats gants
    pointage = True
    if pointage:
        #recuperer direction carte arduino
        direction_gant = np.array([c_data["heading"], c_data["pitch"], c_data["roll"]])
        position_gant = np.array(last_pos_s)
        print("position", position_gant)
        print("position", direction_gant)
        print("position", list_objets)

        distance_objet = [-1] * len(list_objets)
        for i, objet in enumerate(list_objets):
            try:
                distance_objet[i] = distance2(objet.position, direction_gant, position_gant)
                #if distance_objet[i] is ValueError:
                #    raise distance_objet[i]
                print(distance_objet[i], objet.position)
            except ValueError:
                distance_objet[i] = 10**15
                print("objet derriere", distance_objet[i])
            
        seuil = 500**2 #distance seuil

        d = 0
        i_min = -1
        #find first distance != -1
        for i, dist in enumerate(distance_objet):
            if dist >= 0:
                d = dist
                i_min = i
                break
        print(distance_objet)  
        print(i_min)          
        #if exists at least one distance != -1, find min distance > 0
        if i_min != -1:
            for i, dist in enumerate(distance_objet):
                if dist >= 0. and dist < d:
                    d = dist
                    i_min = i
            if d < seuil:
                print("Recherche objet", type(list_objets[0]).__name__)
                objet_min = list_objets[i_min]
                if type(objet_min).__name__ == "Lampe":
                    print("Envoi commande L")
                    objet_min.switch()
                    #envoyer commande pour interragir avec objet_min
                elif type(objet_min).__name__ == "Speaker":
                    print("Envoi commande S")
                    objet_min.switch()
            else:
                print("Too far")

if __name__ == "__main__":
    room = Room(default_MACs)
    room.init("conf03.txt")
    print("End init")
    while True:
        print(room.get_position())
        print("Waiting...")
        input()
    