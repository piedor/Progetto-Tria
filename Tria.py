import ftrobopy
from Settings import *
import time


class Tria:
    def __init__(self):
        self.txt = ftrobopy.ftrobopy('auto')
        time.sleep(2)
        self.asse_y = self.txt.motor(1)
        self.asse_x = self.txt.motor(2)
        self.asse_z = self.txt.motor(3)
        self.ventosa = self.txt.output(7)
        self.lamp = self.txt.output(8)
        self.in_resety = self.txt.input(1)
        self.in_resetx = self.txt.input(4)
        self.in_downz = self.txt.input(5)
        self.in_upz = self.txt.input(6)
        self.in_finemossa = self.txt.input(7)
        self.in_inizioR = self.txt.input(8)
        self.reset()

    def muovi_asse(self, asse, verso, dist):
        if verso:
            asse.setSpeed(OUTMAX)
        else:
            asse.setSpeed(-OUTMAX)
        asse.setDistance(dist)

    def aspetta_input(self, input):
        while True:
            if input.state() == 1:
                break
        if(input == self.asse_x):
            self.asse_x.stop()
        elif(input == self.asse_y):
            self.asse_y.stop()
        elif(input == self.asse_z):
            self.asse_z.stop()

    def reset(self):
        self.muovi_asse(self.asse_x, 0, 20000)
        self.muovi_asse(self.asse_y, 1, 20000)
        self.muovi_asse(self.asse_z, 0, 20000)
        self.aspetta_input(self.in_resetx)
        self.aspetta_input(self.in_resety)
        self.aspetta_input(self.in_upz)

    def catch(self):
        self.muovi_asse(self.asse_z, 1, 20000)
        self.aspetta_input(self.in_downz)
        self.ventosa.setLevel(OUTMAX)
        self.muovi_asse(self.asse_z, 0, 20000)
        self.aspetta_input(self.in_upz)

    def release(self):
        self.muovi_asse(self.asse_z, 1, 20000)
        self.aspetta_input(self.in_downz)
        self.ventosa.setLevel(OUTMIN)
        self.muovi_asse(self.asse_z, 0, 20000)
        self.aspetta_input(self.in_upz)

    def fromto(self, x1, y1, x2, y2):
        start = time.time()
        diffx = x2 - x1
        diffy = y2 - y1
        distx = abs(diffx)
        disty = abs(diffy)
        if diffx != 0:
            if diffx > 0:
                self.asse_x.setSpeed(OUTMAX)
            else:
                self.asse_x.setSpeed(-OUTMAX)
            self.asse_x.setDistance(distx)
        if diffy != 0:
            if diffy > 0:
                self.asse_y.setSpeed(-OUTMAX)
            else:
                self.asse_y.setSpeed(OUTMAX)
            self.asse_y.setDistance(disty)
        while not(self.asse_y.finished() and self.asse_x.finished()):
            if time.time() - start >= 30:
                break
            self.txt.updateWait()

    def lampeggio(self, seconds, vel):
        start = time.time()
        while True:
            self.lamp.setLevel(OUTMIN)
            time.sleep(vel)
            self.lamp.setLevel(OUTMAX)
            time.sleep(vel)
            if time.time() - start >= seconds:
                self.lamp.setLevel(OUTMIN)
                break

    def attendi_utente(self):
        self.lamp.setLevel(OUTMAX)
        self.aspetta_input(self.in_finemossa)
        self.lamp.setLevel(OUTMIN)

    def aggiungi_pallina(self, x, y):
        self.fromto(0, 0, SCIVOLOPALLINE[0], SCIVOLOPALLINE[1])
        self.catch()
        self.fromto(SCIVOLOPALLINE[0], SCIVOLOPALLINE[1], x, y)
        self.release()

    def rimuovi_pallina(self, x, y):
        self.fromto(self.txt.getMotorDistance(
            2), self.txt.getMotorDistance(1), x, y)
        self.catch()
        self.fromto(Xpos[Pos], Ypos[Pos], CONTENITOREPVR[0], CONTENITOREPVR[1])
        self.ventosa.setLevel(OUTMIN)

    def muovi_pallina(self, x1, y1, x2, y2):
        self.fromto(0, 0, x1, y1)
        self.catch()
        self.fromto(x1, y1, x2, y2)
        self.release()

    def scrivi_img_camera(self):
        self.txt.startCameraOnline()
        time.sleep(2.5)
        fc = self.txt.getCameraFrame()
        with open(CAM_IMAGE, 'wb') as f:
            f.write(bytearray(fc))
        self.txt.stopCameraOnline()
