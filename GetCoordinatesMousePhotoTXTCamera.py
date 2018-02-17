import cv2
import numpy as np


nx=[]
ny=[]
def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        nx.append(x)
        ny.append(y)
        print(nx)
        print(ny)

img=cv2.imread("img/TXTCamImg.jpg")
cv2.namedWindow('image')
cv2.setMouseCallback('image',draw_circle)

while(1):
    cv2.imshow('image',img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        break
cv2.destroyAllWindows()
