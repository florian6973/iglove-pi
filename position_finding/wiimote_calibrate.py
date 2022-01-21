import cwiid
import time
import matplotlib.pyplot as plt
import numpy as np
import cv2

default_IPs = ["00:19:1D:93:DD:E4"]# ", CC:9E:00:5D:2C:ED", "E0:0C:7F:E7:CE:F8", "00:1E:A9:40:EA:9F", "00:19:1D:78:02:71"]
    
class Calibrate :
    
    n = None

    #coordinates of the point used tofor calibration
    calib_pt = np.array([0,0,0])
    
    # all wiimotes infos
    wiimotes = None
    
    
    
    
    def __init__(self, IPs = default_IPs) :
        self.IPs = IPs
        self.n = len(self.IPs)
        self.wiimotes = np.empty((self.n, 5), dtype = object)
        
    

    def connect_wiimotes(self) :

        for i, ip in enumerate(self.IPs) :
                            
            
            while True :
                try:
                    
                    print(f'Please press buttons 1 + 2 on Wiimote n°{i+1}')
                    time.sleep(0.2)
                    wiimote = cwiid.Wiimote(ip)
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
            self.wiimotes[i, 1] = ip
        

        print("All Wiimotes connected!")
        
    def calibration(self) :
        print("To calibrate your wiimotes place a IR source in the middle of your room and make sure that each wiimote sees the dot inside the square")
        print("When it's done press A or B on the wiimote")
        #print('Press PLUS and MINUS together on Wiimote n°1 to disconnect and quit.\n')

        

        self.calib_pt[0] = input("Calibration point x (in cm) = ")
        self.calib_pt[1] = input("Calibration point y (in cm) = ")
        self.calib_pt[2] = input("Calibration point z (in cm) = ")

        for i, wiimote in enumerate(self.wiimotes) :
            
            x = input(f"Wiimote n°{i+1} point x (in cm) = ")
            y = input(f"Wiimote n°{i+1} point y (in cm) = ")
            z = input(f"Wiimote n°{i+1} point z (in cm) = ")
            
            wiimote[2:5] = np.array([x, y, z])
            
            
            while(True):
                
                # display the IR viewer
                screen = np.zeros((768,1024))
                screen[378 : 392, 515:529] = 1
                screen[380 : 390, 517:527] = 0
                
                x=0 
                y=0
                
                for dot in wiimote[0].state['ir_src']: 
                    
                    
                    if dot != None:
                        y = dot["pos"][0]
                        x = -dot["pos"][1]
                        
                    screen[x-5:x+5, y-5:y+5] = 1
                cv2.imshow("IR_cam", screen)
                cv2.waitKey(10)
              
                buttons = wiimote[0].state["buttons"]
                if buttons == 4 or buttons == 8 or buttons == 12 :
                    break
                
                if buttons == 16+4096 :
                    quit()
                    
calibrate = Calibrate()

calibrate.connect_wiimotes()
calibrate.calibration()