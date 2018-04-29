"""
    Programma in Python per calibrare le coordinate delle posizioni viste dalla fotocamera
"""

import cv2
import data

nx = list()           # 'list' is easier to search than '[]'
ny = list()
XposIMG = [0] * 24
YposIMG = [0] * 24


def draw_circle(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        nx.append(x)
        ny.append(y)


def CalCoordinatesQ(nQ):
    i = nQ * 8
    XposIMG[0 + i], XposIMG[2 + i], XposIMG[5 + i], XposIMG[7 + i] = nx
    XposIMG[4 + i] = XposIMG[7 + i]
    XposIMG[3 + i] = XposIMG[0 + i]
    YposIMG[0 + i], YposIMG[2 + i], YposIMG[5 + i], YposIMG[7 + i] = ny
    YposIMG[1 + i] = YposIMG[0 + i]
    YposIMG[6 + i] = YposIMG[7 + i]
    XposIMG[1 + i] = ((XposIMG[2 + i] - XposIMG[0 + i]) / 2) + XposIMG[0 + i]
    XposIMG[6 + i] = ((XposIMG[7 + i] - XposIMG[5 + i]) / 2) + XposIMG[5 + i]
    YposIMG[3 + i] = ((YposIMG[5 + i] - YposIMG[0 + i]) / 2) + YposIMG[0 + i]
    YposIMG[4 + i] = ((YposIMG[7 + i] - YposIMG[2 + i]) / 2) + YposIMG[2 + i]


def ReorderPos():
    x = [0] * 24
    y = [0] * 24
    p = [0, 1, 2, 8, 9, 10, 16, 17, 18, 3, 11, 19,
         20, 12, 4, 21, 22, 23, 13, 14, 15, 5, 6, 7]
    for i in range(0, 24):
        x[i], y[i] = XposIMG[p[i]], YposIMG[p[i]]
    return(x, y)


img = cv2.imread("img/aligned.jpg")
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)
c = 0

while True:
    cv2.imshow('image', img)
    if (len(nx) and len(ny)) == 4:
        CalCoordinatesQ(c)
        nx = []
        ny = []
        c += 1
    if c == 3:
        XposIMG, YposIMG = ReorderPos()
        data.Insert("XposIMG", XposIMG)
        data.Insert("YposIMG", YposIMG)
        import DrawRectangleCoordinatesTria
        break
    cv2.waitKey(33)
cv2.destroyAllWindows()
