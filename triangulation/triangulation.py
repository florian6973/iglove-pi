import numpy as np


default_fovw = 41.3
default_fovh = 33.2


class Camera :

    width, height = 1024, 768
    x = 0
    y = 0
    z = 0
    fovw = default_fovw
    fovh = default_fovh

    def __init__(self, wiimotes) :
        self.x = x
        self.y = y
        self.z = z
        self.fovw = fovw
        self.fovh = fovh

    def get_points_tracked(self) :
        return self.points_tracked

    def set_zero(self) :
        try :
            while True :
                point = self.points_tracked[0]
                print("Ctrl + C to interrupt when satisfied | Point's corrdinates", point)
                
        except KeyboardInterrupt:
            pass
        

    def update_points_tracked(self, L:list) :
        self.points_tracked = L
    
    def get_angles(self) -> np.array :
        d = self.width/(2*np.tan(self.fov/2))
        anglesT = np.zeros((len(self.get_points_tracked), 2))
        for i, point in enumerate(self.get_points_tracked) :
            x, y = point[0], point[1]
            anglesT[i, 0] = np.arctan(x/d)
            anglesT[i, 1] = np.arctan(y/d)
        return anglesT




