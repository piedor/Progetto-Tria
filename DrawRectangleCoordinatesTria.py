import cv2
import numpy as np

XposIMG=[101, 156, 213, 121, 157, 195, 139, 157,
         178, 101, 122, 139, 179, 198, 217, 139,
         160, 180, 121, 162, 200, 101, 160, 223] #Coordinate X posizioni immagine fotocamera
YposIMG=[72, 70, 66, 87, 84, 83, 104, 104,
         103, 124, 124, 123, 121, 119, 118, 140,
         140, 138, 161, 160, 156, 182, 180, 176] #Coordinate Y posizioni immagine fotocamera

img=cv2.imread('img/TXTCamImg.jpg',1)
for indice in range(0,24):
    for indice2 in range(0,15):
        for indice3 in range(0,15):
            img[YposIMG[indice]+indice3,XposIMG[indice]+indice2]=[255,255,255]
cv2.imshow("TXTCamImg",img)
cv2.waitKey(0)
