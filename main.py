#!/usr/bin/python
# -*- coding: utf-8 -*-

from Settings import *
from tria import Tria
import cv2
import math

class Game():
    def __init__(self):
        self.ValElem=[0]*24
        self.Tria=Tria()
        self.elCamera=ElabCamImg(self.Tria)

    def run(self):
        self.elCamera.run(self.ValElem)

class ElabCamImg():
    def __init__(self,Tria):
        self.ValposCameraB = [0] * 24
        self.ValposCameraG = [0] * 24
        self.ValposCameraR = [0] * 24
        self.ValposCameraUpdateB=[0]*24
        self.ValposCameraUpdateG=[0]*24
        self.ValposCameraUpdateR=[0]*24
        self.cont=0
        self.Tria=Tria

    def ValposCameraReset(self):
        self.ValposCameraB = [self.RGBPosition(i)[0] for i in range(24)]
        self.ValposCameraG = [self.RGBPosition(i)[1] for i in range(24)]
        self.ValposCameraR = [self.RGBPosition(i)[2] for i in range(24)]

    def RGBPosition(self,Pos):
        img = cv2.imread(IMAGE_ALIGNED, 1)
        blue = 0
        green = 0
        red = 0
        for j in range(0, (STRATI * 2) + 1):
            for k in range(0, (STRATI * 2) + 1):
                b, g, r = img[YPOSIMG[Pos] + k, XPOSIMG[Pos] + j]
                blue += b
                green += g
                red += r
        return(blue,green,red)

    def MathDistance(self,p1,p2):
        return(math.sqrt(math.pow(p1-p2,2)))

    def isValposCameraHigher(self,Pos,Val):
        blue = self.RGBPosition(Pos)[0]
        green = self.RGBPosition(Pos)[1]
        red = self.RGBPosition(Pos)[2]
        if self.MathDistance(self.ValposCameraB[Pos],blue)+ self.MathDistance(self.ValposCameraG[Pos],green) + self.MathDistance(self.ValposCameraR[Pos],red) > Val:
            return True
        else:
            return False

    def CheckNewBallU(self):
        for i in range(0,24):
            if self.isValposCameraHigher(i,MINDISTNBU):
                if self.ValElem[i] == EMPTY:
                    self.ValElem[i] = USER
                    print("pallina blu nella posizione "), i

    def run(self,ValElem):
        self.ValElem=ValElem
        self.Tria.scrivi_img_camera()
        execfile("align_TXTCamImg.py",globals())
        if(self.cont==0):
            self.ValposCameraReset()
            print(self.ValposCameraB)
        else:
            self.CheckNewBallU()
        self.cont+=1

game=Game()
while True:
    game.run()
