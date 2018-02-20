#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Tria.py - Programma principale per la tria realizzata con fischertechnik
© 2018 Pietro Dorighi Riccardo Martinelli Gabriele Prada
"""

# Importazione librerie
import ftrobopy
import time
import random
import cv2
import logging
logging.basicConfig(level=logging.DEBUG)
debug = logging.debug


__author__ = "Pietro Dorighi"
__copyright__ = "Copyright 2018 by Pietro Dorighi"
__license__ = "MIT License"
__version__ = "2.0"
__maintainer__ = "Pietro Dorighi"
__email__ = "dorighipietro28@gmail.com"
__status__ = "development"
__date__ = "10/01/2018"


CAM_IMAGE = 'img/TXTCamImg.jpg'

WLAN = '192.168.8.2'
USB = '192.168.7.2'
txt = ftrobopy.ftrobopy(host=USB, port=65000) # Connessione al controller

M = [txt.C_MOTOR, txt.C_MOTOR, txt.C_MOTOR, txt.C_OUTPUT]

I = [(txt.C_SWITCH, txt.C_DIGITAL)] * 8

txt.setConfig(M, I)
txt.updateConfig()

#--------INIZIO DICHIARAZIONE VARIABILI---------------------

# Coordinate X e Y di ogni posizione in ordine numerico
Xpos = [970, 2635, 4211, 1580, 2635, 3690, 2180, 2635,
        3090, 970, 1580, 2180, 3090, 3690, 4211, 2180,
        2635, 3090, 1580, 2635, 3690, 970, 2635, 4211]

Ypos = [900, 900, 900, 1471, 1471, 1471, 2500, 2500, 2500,
        3200, 3200, 3200, 3200, 3200, 3200, 3926, 3926,
        3926, 4747, 4747, 4747, 5531, 5531, 5531]

# Valore posizione(0 = posizione vuota, 1 = pallina Robot, 10 = pallina User)
EMPTY = 0
ROBOT = 1
USER  = 10

VAL = [0] * 24
ValposOld = [0] * 24

# Coordinate X e Y dello scivolo su cui sono presenti le palline del Robot
scivoloPalline = [5025, 4308]
contenitorePVR = [0, 2903]      # Contenitore palline vinte robot
contenitorePVU = [2635, 0]      # Contenitore palline vinte user

Outmax = 512                    # Uscita massima pwm output
Outmin = 0                      # Uscita minima pwm output

ventosa = txt.output(7)
lamp = txt.output(8)

input_resety = txt.input(1)
input_resetx = txt.input(4)
input_downz = txt.input(5)
input_upz = txt.input(6)
input_finemossa = txt.input(7)
input_InizioR = txt.input(8)

asse_y = txt.motor(1)
asse_x = txt.motor(2)
asse_z = txt.motor(3)

# Combinazioni possibili delle trie
TRIA = [0, 1, 2, 3, 4, 5, 6, 7, 8,
        21, 22, 23, 18, 19, 20,
        15, 16, 17, 21, 9, 0, 18, 10, 3,
        15, 11, 6, 2, 14, 23, 5, 13, 20,
        8, 12, 17, 9, 10, 11, 16, 19, 22, 12, 13, 14,
        1, 4, 7]

CurrentX = 0                    # Coordinata X corrente
CurrentY = 0                    # Coordinata Y corrente
PosBloccoTriaU = []             # Posizione blocco tria utente
PosSvolgiTria = []              # Posizione completamento tria robot
Priorita = 0                    # Priorità mossa robot
angoli = [0, 3, 6, 23, 20, 17, 21, 18, 15, 2, 5, 8]  # Posizioni angoli tria
# Posizioni angoli quadrati tria
quadrati = [0, 21, 23, 2, 3, 18, 20, 5, 6, 15, 17, 8]
collegamenti = [9, 10, 11, 22, 19, 16, 14, 13,
                12, 1, 4, 7]         # Posizioni collegamenti tria
centroCollegamenti = [4, 10, 19, 13] # Posizioni centro dei collegamenti tria
AttaccoState = 0                     # Stato strategia robot
ContatoreVPU = 0                     # Contatore Valpos Update
PosPallineNuoveU = []           # Posizioni palline posizionate utente
PosDifesa = 0                   # Posizione difesa
Controllo = False               # Boolean controllo
PosAttacco = []                 # Posizione attacco
PosTogliPallina = []            # Posizione togli pallina
ValposCamera = [0] * 24 # Valori posizioni fotocamera rilevamento somma blu

# Coordinate posizioni immagine fotocamera
XposIMG = [101, 156, 213, 121, 157, 195, 139, 157,
           178, 101, 122, 139, 179, 198, 217, 139,
           160, 180, 121, 162, 200, 101, 160, 223]
YposIMG = [72, 70, 66, 87, 84, 83, 104, 104,
           103, 124, 124, 123, 121, 119, 118, 140,
           140, 138, 161, 160, 156, 182, 180, 176]
User = False                    # Boolean inizio utente
Robot = False                   # Boolean inizio robot

#------------INIZIO FORMALIZZAZIONE CLASSI------------------

def reset():
    "Reset del Robot nelle cordinate (0, 0)."
    asse_x.setSpeed(-Outmax)
    asse_x.setDistance(20000)
    asse_y.setSpeed(Outmax)
    asse_y.setDistance(20000)
    asse_z.setSpeed(-Outmax)
    asse_z.setDistance(20000)
    while True:
        if (input_resetx.state() == 1 and
            input_resety.state() == 1 and
            input_upz.state() == 1):
            asse_x.setSpeed(Outmin)
            asse_y.setSpeed(Outmin)
            asse_z.setSpeed(Outmin)
            break


def catch():
    "Presa delle palline."
    asse_z.setSpeed(Outmax)
    asse_z.setDistance(20000)
    while True:
    	if(input_downz.state()==1):
    		asse_z.stop()
    		ventosa.setLevel(Outmax)
    		break
    asse_z.setSpeed(-Outmax)
    asse_z.setDistance(20000)
    while True:
    	if(input_upz.state()==1):
    		asse_z.stop()
    		break


def release():
    "Rilascio delle palline."
    asse_z.setSpeed(Outmax)
    asse_z.setDistance(20000)
    while True:
    	if(input_downz.state()==1):
    		asse_z.stop()
    		ventosa.setLevel(Outmin)
    		break
    asse_z.setSpeed(-Outmax)
    asse_z.setDistance(20000)
    while True:
    	if(input_upz.state()==1):
    		asse_z.stop()
    		break


def fromto(x1, y1, x2, y2):
    "Spostamento da (x1, y1) a (x2, y2)."
    global CurrentX
    global CurrentY
    CurrentX = x2
    CurrentY = y2
    diffx = x2-x1
    diffy = y2-y1
    distx = abs(diffx)
    disty = abs(diffy)
    if diffx != 0:
        if diffx > 0:
            asse_x.setSpeed(Outmax)
        else:
            asse_x.setSpeed(-Outmax)
        asse_x.setDistance(distx)

    if diffy != 0:
        if diffy > 0:
            asse_y.setSpeed(-Outmax)
        else:
            asse_y.setSpeed(Outmax)
        asse_y.setDistance(disty)

    while not(asse_y.finished() and asse_x.finished()):
        txt.updateWait()


def ValposReset():
    "Rilevamento somme blu posizioni fotocamera all'inizio."
    global ValposOld
    for i in range(0, 50):
        frameCamera = txt.getCameraFrame()
        with open(CAM_IMAGE, 'wb') as f:
            f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE, 1)
    for i in range(0, 24):
        blue = 0
        for j in range(0, 15):
            for k in range(0, 15):
                b, _, _ = img[YposIMG[i] + k, XposIMG[i] + j]
                blue = blue + b
        ValposCamera[i] = blue
    ValposOld = VAL


def ValposUpdate():
    "Riconoscimento palline blu."
    global ContatoreVPU
    global PosPallineNuoveU
    global ValposOld
    PosPallineNuoveU = []
    ContatoreVPU += 1
    frameCamera = txt.getCameraFrame()
    with open(CAM_IMAGE, 'wb') as f:
        f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE, 1)
    if ContatoreVPU > 2:
        ValposOld = VAL
    for i in range(0, 24):
        blue = 0
        for j in range(0, 15):
            for k in range(0, 15):
                b, _, _ = img[YposIMG[i] + k, XposIMG[i] + j]
                blue = blue + b
        if blue - ValposCamera[i] > 3000:
            if VAL[i] == EMPTY:
                VAL[i] = USER
                PosPallineNuoveU.append(i)
                print("pallina blu nella posizione "), i
        if((blue - ValposCamera[i] > -1000) and (blue - ValposCamera[i] < 1000)):
            if(VAL[i]==1):
                VAL[i]=0
                print("pallina Robot rimossa dalla posizione "),i


def Lampeggio(seconds):
    "Lampeggio lampadina dati i secondi."
    start = time.time()
    while True:
        lamp.setLevel(Outmin)
        time.sleep(0.5)
        lamp.setLevel(Outmax)
        time.sleep(0.5)
        if (time.time() - start) >= seconds:
            lamp.setLevel(Outmin)
            break


def AttendUser():
    "Attend input fine mossa."
    while True:
        if input_finemossa.state() == 1:
            break


def Strategia():
    "Strategia robot."
    global PosAttacco
    global AttaccoState
    global PosSvolgiTria
    PosAttacco = []
    V = centroCollegamenti
    if (VAL[V[0]] == EMPTY or
        VAL[V[1]] == EMPTY or
        VAL[V[2]] == EMPTY or
        VAL[V[3]] == EMPTY):

        N = random.choice(V)
        while VAL[N] != EMPTY:
            N = random.choice(V)
        fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
        catch()
        fromto(scivoloPalline[0], scivoloPalline[1], Xpos[N], Ypos[N])
        release()
        VAL[N] = ROBOT
    else:
        for i in quadrati:
            for j in collegamenti:
                if VAL[i] == EMPTY and VAL[j] == EMPTY:
                    if j not in V:
                        VAL[i] = ROBOT
                        VAL[j] = ROBOT
                        FPossibiliTria()
                        VAL[i] = EMPTY
                        VAL[j] = EMPTY
                        if len(PosSvolgiTria) > 1:
                            fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
                            catch()
                            fromto(scivoloPalline[0], scivoloPalline[1],
                                   Xpos[i], Ypos[i])
                            release()
                            VAL[i] = ROBOT
                            PosAttacco = [j]
                            AttaccoState = 1


def FPossibiliTria():
    "Controllo possibili trie utente e robot."
    global Priorita
    global PosSvolgiTria
    global PosBloccoTriaU
    global PosTogliPallina
    Priorita = 0
    PosBloccoTriaU = []
    PosSvolgiTria = []
    for i in range(0, 48, 3):
        if (VAL[TRIA[i]] +
            VAL[TRIA[i+1]] +
            VAL[TRIA[i+2]]) == 20:
            Priorita = 2
            if VAL[TRIA[i]] == EMPTY:
                PosBloccoTriaU.append(TRIA[i])
            elif VAL[TRIA[i]] == USER:
                PosTogliPallina = TRIA[i]
            if VAL[TRIA[i+1]] == EMPTY:
                PosBloccoTriaU.append(TRIA[i+1])
            elif VAL[TRIA[i+1]] == USER:
                PosTogliPallina = TRIA[i+1]
            if VAL[TRIA[i+2]] == EMPTY:
                PosBloccoTriaU.append(TRIA[i+2])
            elif VAL[TRIA[i+2]] == USER:
                PosTogliPallina = TRIA[i+2]

    for i in range(0, 48, 3):
        if (VAL[TRIA[i]] +
            VAL[TRIA[i+1]] +
            VAL[TRIA[i+2]]) == 2:
            Priorita = 3
            if VAL[TRIA[i]] == EMPTY:
                PosSvolgiTria.append(TRIA[i])
            if VAL[TRIA[i+1]] == EMPTY:
                PosSvolgiTria.append(TRIA[i+1])
            if VAL[TRIA[i+2]] == EMPTY:
                PosSvolgiTria.append(TRIA[i+2])
    if not Controllo:
        for i in range(0, 48, 3):
            if (VAL[TRIA[i]] +
                VAL[TRIA[i+1]] +
                VAL[TRIA[i+2]]) == 30:
                if (ValposOld[TRIA[i]] +
                    ValposOld[TRIA[i+1]] +
                    ValposOld[TRIA[i+2]]) != 30:
                    print("Hai formalizzato una Tria.")
                    print("Puoi eliminare una pallina avversaria!")
                    lamp.setLevel(256)
                    AttendUser()
                    lamp.setLevel(0)
                    ValposUpdate()


def ControlloAttacco():
    "Controllo possibili mosse fortunate"
    global Priorita
    for i in range(0, 23):
        if VAL[i] == EMPTY:
            VAL[i] = ROBOT
            FPossibiliTria()
            Priorita = 0
            VAL[i] = EMPTY
            if len(PosSvolgiTria) > 1:
                fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
                catch()
                fromto(scivoloPalline[0], scivoloPalline[1], Xpos[i], Ypos[i])
                release()
                Priorita = 3
                VAL[i] = ROBOT
                break


def Attacco():
    "Procedura attacco."
    global AttaccoState
    p = PosAttacco
    if AttaccoState == 0:
        Strategia()
    else:
        VAL[p[0]] = ROBOT
        FPossibiliTria()
        if PosSvolgiTria > 1:
            fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
            catch()
            fromto(scivoloPalline[0], scivoloPalline[1],
                   Xpos[p[0]], Ypos[p[0]])
            release()
            AttaccoState = 0
        else:
            VAL[p[0]] = EMPTY
            AttaccoState = 0
            Strategia()


def BloccoTriaU():
    "Blocco tria utente."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1],
           Xpos[PosBloccoTriaU[0]], Ypos[PosBloccoTriaU[0]])
    release()
    VAL[PosBloccoTriaU[0]] = ROBOT


def SvolgiTria():
    "Svolgi tria."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1],
           Xpos[PosSvolgiTria[0]], Ypos[PosSvolgiTria[0]])
    release()
    VAL[PosSvolgiTria[0]] = ROBOT


def Controlli():
    "Procedura controlli mosse utente non valide."
    global ContatoreVPU
    global PosPallineNuoveU
    LenPNU = len(PosPallineNuoveU)
    stop = False
    ContatorePos = -1
    if LenPNU == 0 or LenPNU > 1:
        while LenPNU > 1:
            for i in range(0, LenPNU):
                VAL[PosPallineNuoveU[i-1]] = EMPTY
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            SONO STATE POSIZIONATE PIU' PALLINE!!!
            LASCIANE SOLTANTO UNA""")
            lamp.setLevel(Outmax)
            AttendUser()
            lamp.setLevel(Outmin)
            ValposUpdate()
            LenPNU = len(PosPallineNuoveU)
        while LenPNU == 0:
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            NON HAI POSIZIONATO LA PALLINA!""")
            lamp.setLevel(Outmax)
            AttendUser()
            lamp.setLevel(Outmin)
            ValposUpdate()
            LenPNU = len(PosPallineNuoveU)
    while not stop:
        stop = True
        for i1, i2 in zip(ValposOld, VAL):
            ContatorePos = ContatorePos+1
            if i1 == 10 or i1 == 1:
                if i2 == 0:
                    stop = False
                    ContatoreVPU = -1
                    print("""\
                    MOSSA UTENTE NON VALIDA!!!
                    HAI SPOSTATO O RIMOSSO UNA PALLINA DALLA POSIZIONE %d""" %
                          ContatorePos)
                    lamp.setLevel(Outmax)
                    AttendUser()
                    lamp.setLevel(Outmin)
                    ValposUpdate()
                    ContatorePos = 3


def ControlloDifesa():
    "Difesa da possibili strategie utente."
    global Priorita
    global PosDifesa
    global Controllo
    Controllo = True
    for i in range(0, 23):
        if VAL[i] == EMPTY:
            VAL[i] = USER
            FPossibiliTria()
            Priorita = 0
            VAL[i] = EMPTY
            if len(PosBloccoTriaU) > 1:
                print(i)
                Priorita = 1
                PosDifesa = i
                break
    if Priorita != 1:
        for i in range(0, 12):
            if VAL[angoli[i]] == USER:
                if angoli[i] in [0, 3, 6, 21, 18, 15]:
                    if VAL[angoli[i+3]] == EMPTY:
                        Priorita = 1
                        PosDifesa = angoli[i+3]
                elif angoli[i] in [23, 20, 17, 2, 5, 8]:
                    if VAL[angoli[i-3]] == EMPTY:
                        Priorita = 1
                        PosDifesa = angoli[i-3]
    Controllo = False


def Difesa():
    "Esecuzione difesa."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1],
           Xpos[PosDifesa], Ypos[PosDifesa])
    release()
    VAL[PosDifesa] = ROBOT


def TogliPallina():
    "Togliere pallina utente quando robot esegue tria."
    FPossibiliTria()
    if Priorita == 2:
        fromto(CurrentX, CurrentY,
               Xpos[PosTogliPallina], Ypos[PosTogliPallina])
        catch()
        fromto(Xpos[PosTogliPallina], Ypos[PosTogliPallina],
               contenitorePVR[0], contenitorePVR[1])
        release()
        VAL[PosTogliPallina] = EMPTY
    else:
        contatore = -1
        for i in VAL:
            contatore += 1
            if i == 10:
                fromto(CurrentX, CurrentY, Xpos[contatore], Ypos[contatore])
                catch()
                fromto(Xpos[contatore], Ypos[contatore],
                       contenitorePVR[0], contenitorePVR[1])
                release()
                VAL[contatore] = EMPTY
                return

#-----INIZIO PROGRAMMA------------------------------------------------


reset()
txt.startCameraOnline()
Lampeggio(2.5)
ValposReset()
lamp.setLevel(Outmax)
User = False
Robot = False

while True:
    if input_InizioR.state() == 1:
        Robot = True
        break
    if input_finemossa.state() == 1:
        User = True
        break

lamp.setLevel(Outmin)
if (Robot):
    #-------------------- Inizio prima fase gioco---------------------
    for i in range(0, 9):
        debug("Controllo Possibili Trie...")
        FPossibiliTria()
        if Priorita == 2 or Priorita == 3:
            if Priorita == 2:
                debug("Blocco Tria nemica...")
                BloccoTriaU()
            elif Priorita == 3:
                debug("Svolgitura Tria...")
                SvolgiTria()
                TogliPallina()
        else:
            debug("Controllo Attacco")
            ControlloAttacco()
            if Priorita != 3:
                debug("Controllo Difesa...")
                ControlloDifesa()
        if Priorita == 1:
            debug("Difesa...")
            Difesa()
        elif Priorita == 0:
            debug("Strategia...")
            Attacco()
        reset()
        lamp.setLevel(Outmax)
        AttendUser()
        lamp.setLevel(Outmin)
        time.sleep(0.5)
        ValposUpdate()
        Controlli()

if (User):
    for i in range(0, 9):
        #-------------------- Inizio prima fase gioco-----------------
        ValposUpdate()
        Controlli()
        debug("Controllo Possibili Trie...")
        FPossibiliTria()
        if Priorita == 2 or Priorita == 3:
            if Priorita == 2:
                debug("Blocco Tria nemica...")
                BloccoTriaU()
            elif Priorita == 3:
                debug("Svolgitura Tria...")
                SvolgiTria()
                TogliPallina()
        else:
            debug("Controllo Attacco")
            ControlloAttacco()
            if Priorita != 3:
                debug("Controllo Difesa...")
                ControlloDifesa()
        if Priorita == 1:
            debug("Difesa...")
            Difesa()
        elif Priorita == 0:
            debug("Strategia...")
            Attacco()
        reset()
        lamp.setLevel(Outmax)
        AttendUser()
        lamp.setLevel(Outmin)
        time.sleep(0.5)
