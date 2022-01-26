from operator import index
from turtle import pos
from scipy import optimize as opt
import numpy as np
import time
import cv2
from time import sleep
from multiprocessing import Process, Queue

from wiimotes_calibrate import Init_wiimotes, d



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
    return S1 - S2**2
 
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
          
 
            mx = -(dot[1][0] - width//2)
            my = (dot[1][1] - height//2)

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
    #connection.calibration()
    #connection.save_calibration("./calibration3.npy", "./calib_pt3.npy")
    connection.load_calibration("./calibration3.npy", "./calib_pt3.npy")

    wiimotes = connection.wiimotes


    print(wiimotes)
    
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
                    
    
    
    
    
    
    
    
    
        #     d = height/(2*np.tan(fovh/2))
    
    
    
        #     for dot in wiimote[0].state['ir_src'] :
    
        #         if dot != None :
        #             mx = dot["pos"][0] - width//2
        #             my = dot["pos"][1] - height//2
    
        #             theta = np.arctan(mx/d) # angle with the reference point along x axis 
        #             phi = np.arctan(my/d)
    
        #             u = np.array([np.cos(wiimote[5] + theta), np.sin(wiimote[5] + theta), np.sin(wiimote[6] + phi)]) 
        #             u = u/np.linalg.norm(u) 
    
    
    
        # ## trianguler
        # pass
    
    
