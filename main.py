#!/usr/bin/python
# -*- coding: utf-8 -*-

from settings import *
from tria import Tria
import cv2
import math

val_elem = [0]*24


class Game():
    def __init__(self):
        self.Tria = Tria()
        self.el_camera = ElabCamImg(self.Tria)
        self.el_camera.run()

    def run(self):
        self.el_camera.run()


class ElabCamImg():
    def __init__(self, Tria):
        self.val_pos_camera_b = [0] * 24
        self.val_pos_camera_g = [0] * 24
        self.val_pos_camera_r = [0] * 24
        self.val_pos_camera_updated_b = [0]*24
        self.val_pos_camera_updated_g = [0]*24
        self.val_pos_camera_updated_r = [0]*24
        self.cont = 0
        self.Tria = Tria

    def valPosCameraReset(self):
        self.val_pos_camera_b = [self.rgbPosition(i)[0] for i in range(24)]
        self.val_pos_camera_g = [self.rgbPosition(i)[1] for i in range(24)]
        self.val_pos_camera_r = [self.rgbPosition(i)[2] for i in range(24)]

    def valPosCameraUpdate(self):
        self.val_pos_camera_updated_b = [self.rgbPosition(i)[0] for i in range(24)]
        self.val_pos_camera_updated_g = [self.rgbPosition(i)[1] for i in range(24)]
        self.val_pos_camera_updated_r = [self.rgbPosition(i)[2] for i in range(24)]

    def rgbPosition(self, pos):
        img = cv2.imread(IMAGE_ALIGNED, 1)
        blue = 0
        green = 0
        red = 0
        for j in range(0, (STRATI * 2) + 1):
            for k in range(0, (STRATI * 2) + 1):
                b, g, r = img[int(YPOSIMG[pos] + k), int(XPOSIMG[pos] + j)]
                blue += b
                green += g
                red += r
        return(blue, green, red)

    def mathDistance(self, p1, p2):
        return(math.sqrt(math.pow(p1-p2, 2)))

    def newElement(self, pos, val):
        blue = self.rgbPosition(pos)[0]
        green = self.rgbPosition(pos)[1]
        red = self.rgbPosition(pos)[2]
        if self.mathDistance(self.val_pos_camera_b[pos], blue) + self.mathDistance(self.val_pos_camera_g[pos], green) + self.mathDistance(self.val_pos_camera_r[pos], red) > val:
            return True
        else:
            return False

    def removedElement(self, pos, val):
        blue = self.rgbPosition(pos)[0]
        green = self.rgbPosition(pos)[1]
        red = self.rgbPosition(pos)[2]
        if self.mathDistance(self.val_pos_camera_updated_b[pos], blue) + self.mathDistance(self.val_pos_camera_updated_g[pos], green) + self.mathDistance(self.val_pos_camera_updated_r[pos], red) > val:
            return True
        else:
            return False

    def checkNewOrRemovedElement(self):
        for i in range(0, 24):
            if self.newElement(i, MINDISTNBU) and val_elem[i] == EMPTY:
                val_elem[i] = USER
                print("pallina utente nella posizione ", i)
            elif self.removedElement(i, MINDISTNBU) and val_elem[i] == USER:
                val_elem[i] = EMPTY
                print("pallina utente rimossa dalla posizione ", i)
            if(self.cont > 1):
                if self.removedElement(i, MINDISTRBR) and val_elem[i] == ROBOT:
                    val_elem[i] = EMPTY
                    print("pallina robot rimossa dalla posizione ", i)

    def run(self):
        self.Tria.scrivi_img_camera()
        exec(open("align_TXTCamImg.py").read(), globals())
        if(self.cont == 0):
            self.valPosCameraReset()
        else:
            self.checkNewOrRemovedElement()
            self.valPosCameraUpdate()
        self.cont += 1


game = Game()
while True:
    game.run()
