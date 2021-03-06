"""
    Programma in Python per verificare le coordinate delle posizioni viste dalla fotocamera
"""

import cv2
from data import data
from settings import *

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = data.ReturnValue("XposIMG")
y_pos = data.ReturnValue("YposIMG")

img = cv2.imread('img/aligned.jpg')

for i in range(0, len(x_pos)):
    x_pos[i] -= STRATI
for i in range(0, len(y_pos)):
    y_pos[i] -= STRATI

for x, y in zip(x_pos, y_pos):
    for x_off in range(0, (STRATI * 2) + 1):
        for y_off in range(0, (STRATI * 2) + 1):
            img[int(y + y_off), int(x + x_off)] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
