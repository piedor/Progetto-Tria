"""
    Programma in Python per verificare le coordinate delle posizioni viste dalla fotocamera
"""

import cv2
import data

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = data.ReturnValue("XposIMG")

y_pos = data.ReturnValue("YposIMG")
img = cv2.imread('img/aligned.jpg')
strati = 3

for i in range(0, len(x_pos)):
    x_pos[i] -= strati
for i in range(0, len(y_pos)):
    y_pos[i] -= strati

for x, y in zip(x_pos, y_pos):
    for x_off in range(0, (strati * 2) + 1):
        for y_off in range(0, (strati * 2) + 1):
            img[y + y_off, x + x_off] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
