import cv2
import numpy as np
import random as rd

k = 2





while True :
    img = np.zeros([768//k,1024//k])

    img[rd.randint(0, 768)//k:, rd.randint(0, 1024)//k:] = 1


    cv2.imshow("image", img)
    cv2.waitKey(10)