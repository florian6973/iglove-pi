import cwiid
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import cv2
import json

default_MACs = ["00:19:1D:93:DD:E4", "CC:9E:00:5D:2C:ED", "E0:0C:7F:E7:CE:F8", "00:1E:A9:40:EA:9F"]#, "00:19:1D:78:02:71"]

width, height = 1024, 768
fovw = 41.3
fovh = 33.2
 
 
class Init_wiimotes :
    
    n = None

    #coordinates of the point used tofor calibration
    calib_pt = np.array([0,0,0])
    
    # all wiimotes infos
    wiimotes = None
    
    
    
    
    def __init__(self, MACs = default_MACs) :
        self.MACs = MACs
        self.n = len(self.MACs)
        
        #contains : cwiid.wiimote, MAC address, x, y, z, theta (angle in (O,x,y) /x), phi (angle in (O, y, z) /y)
        self.wiimotes = np.empty((self.n, 7), dtype = object)     

    def connect_wiimotes(self) :

        for i, mac in enumerate(self.MACs) :
                            
            
            while True :
                try:
                    
                    print(f'Please press buttons 1 + 2 on Wiimote n°{i+1}')
                    time.sleep(0.2)
                    wiimote = cwiid.Wiimote(mac)
                    print(f"Wiimote {i+1} connected")
                    
                except RuntimeError:
                    print("Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!")
                    continue
                break


            wiimote.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN
            wiimote.rumble = 1
            time.sleep(0.2)
            wiimote.rumble = 0
            wiimote.led = i + 1
            
            self.wiimotes[i, 0] = wiimote
            self.wiimotes[i, 1] = mac
        

        print("All Wiimotes connected!")
        
    def calibration(self) :
        print("To calibrate your wiimotes place a IR source in the middle of your room and make sure that each wiimote sees the dot inside the square")
        print("When it's done press A or B on the wiimote")
        print("Warning : make sure that the wiimote is leveled along the left-right axis (horizontal calibration in progress)")
        #print('Press PLUS and MINUS together on Wiimote n°1 to disconnect and quit.\n')

        

        self.calib_pt[0] = input("Calibration point x (in cm) = ")
        self.calib_pt[1] = input("Calibration point y (in cm) = ")
        self.calib_pt[2] = input("Calibration point z (in cm) = ")

        for i, wiimote in enumerate(self.wiimotes) :
            
            x = int(input(f"Wiimote n°{i+1} point x (in cm) = "))
            y = int(input(f"Wiimote n°{i+1} point y (in cm) = "))
            z = int(input(f"Wiimote n°{i+1} point z (in cm) = "))
            
            wiimote[2:5] = np.array([x, y, z])
            
            wiimote[5] = np.arctan((self.calib_pt[1] - y)/(self.calib_pt[0] - x))
            wiimote[6] = np.arctan((self.calib_pt[2] - z)/(self.calib_pt[1] - y))
            
                         
            
            
            while(True):
                
                # display the IR viewer
                screen = np.zeros((768,1024))
                screen[378 : 392, 515:529] = 1
                screen[380 : 390, 517:527] = 0
                
                x=0 
                y=0
                theta = 0
                phi = 0
                for dot in wiimote[0].state['ir_src']: 
                    
                    
                    if dot != None:
                        y = dot["pos"][0]
                        x = 1024-dot["pos"][1]
                        #rajoute par JE :
                        d = height/(2*np.tan(fovh/2))
     
                        mx = x - width//2
                        my = y - height//2

                        theta = np.arctan(mx/d) # angle with the reference point along x axis 
                        phi = np.arctan(my/d)
                        print("theta,phi")
                        print(theta)
                        print(phi)
                        
                        
                        screen[x-5:x+5, y-5:y+5] = 1
                cv2.imshow(f"IR Wiimote n°{i+1}", screen)
                cv2.waitKey(10)
              
                buttons = wiimote[0].state["buttons"]
                if buttons == 8 or buttons == 12 :
                    
                    #JE:
                    
                    wiimote[5] += theta
                    wiimote[6] += phi
                    break
                
                if buttons == 16+4096 :
                    quit()
            cv2.destroyAllWindows()
       
    def save_calibration(self, filename, filename_calib) :
        np.save(filename, self.wiimotes[:, 1:])
        np.save(filename_calib, self.calib_pt)

        
        
    def load_calibration(self, filename, filename_calib) :
        self.calib_pt = np.load(filename_calib, allow_pickle=True)
        data = np.load(filename, allow_pickle=True)
        for i, wiimote in enumerate(self.wiimotes) :
            wiimote[1:] = data[i]
 
        #data = np.genfromtxt(filepath, delimiter=',', dtype = object)
        #print(type(data))
        #print(self.wiimotes)
        #if self.wiimotes.shape[0] == 1 :
        #    self.wiimotes[0, 1:] = data[:]
        #else :
        #    for i, wiimote in enumerate(self.wiimotes) :
        #        wiimote[1:] = data[i]
        #print(self.wiimotes)
        
           
       


# tests
                    
#connection = Init_wiimotes()
#connection.connect_wiimotes()
#connection.calibration()
#connection.save_calibration("./calibration.npy")
#connection.load_calibration("./calibration.npy")


#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

#for wiimote in connection.wiimotes :
#    ax.scatter(wiimote[2], wiimote[3], wiimote[4], cmap = "blue")
#    u = np.array([np.cos(wiimote[5]), np.sin(wiimote[5]), np.sin(wiimote[6])])
#    u = u/np.linalg.norm(u)
#    ax.quiver(wiimote[2], wiimote[3], wiimote[4], u[0], u[1], u[2])
#    
#ax.scatter(connection.calib_pt[0], connection.calib_pt[1], connection.calib_pt[2], cmap = "red")
#plt.show()

