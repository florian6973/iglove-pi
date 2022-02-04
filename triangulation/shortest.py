from scipy import optimize as opt
import numpy as np
import time

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


            # trouver le vecteur directeur du point
            d = height/(2*np.tan(fovh/2))

            if dot != None :
                mx = dot["pos"][0] - width//2
                my = dot["pos"][1] - height//2

                theta = np.arctan(mx/d) # angle with the reference point along x axis 
                phi = np.arctan(my/d)

                u = np.array([np.cos(wiimote[5] + theta), np.sin(wiimote[5] + theta), np.sin(wiimote[6] + phi)]) 
                u = u/np.linalg.norm(u)
            self.U_list.append(u)


    def cost_function(self, X) :
        '''
        Function to optimize
        '''

        return Z(X, self.U_list, self.P0_list)

    def find_inter(self) :
        opt.minimize(self.cost_function, np.array[0, 0, 0]).x


wiimotes = connection.wiimotes

while True :
    DotsTS = np.array([(None, -1)]*len(wiimotes), dtype = object)
    ## recuperer des points avec date de peromption et n° de la wiimote qui l'a pris
    for i, wiimote in enumerate(wiimotes) :
        
        # enregistrer les points dans un tuple avec son timestampe
        TS = time.time()
        dot = wiimote[0].state['ir_src'][0] # ATTENTION on suppose qu'on a un seul point percu
        DotsTS[i] = (dot, TS)

        absolute_found = False
        close_dots = [(wiimotes[i], dot)]
        for j, DotTS in enumerate(DotTS) :
            if i != j and DotTS[1] > 0 :
                if abs(DotTS[1] - TS) < 1 : 
                    absolute_found = True

                    # on stocke les points proches temporellement
                    close_dots.append((wiimotes[j], DotsTS[0]))
                    
        
        if not absolute_found :
            # on integre la pos sur le capteur
            continue
        else :
            # ici on triangule
            triangulation = Triangulation(close_dots)
            X = triangulation.find_inter()
            print(X)

            
            






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


