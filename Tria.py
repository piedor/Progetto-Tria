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
import opt
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
txt = ftrobopy.ftrobopy('auto')  # Connessione al controller

M = [txt.C_MOTOR, txt.C_MOTOR, txt.C_MOTOR, txt.C_OUTPUT]

I = [(txt.C_SWITCH, txt.C_DIGITAL)] * 8

txt.setConfig(M, I)
txt.updateConfig()

#--------INIZIO DICHIARAZIONE VARIABILI---------------------

# Coordinate X e Y di ogni posizione in ordine numerico
Xpos = [970, 2635, 4211, 1580, 2560, 3690, 2180, 2635,
        3090, 970, 1500, 2180, 3090, 3690, 4211, 2050,
        2635, 3090, 1580, 2635, 3690, 970, 2635, 4211]

Ypos = [900, 900, 900, 1471, 1670, 1471, 2500, 2500, 2500,
        3200, 3200, 3200, 3200, 3200, 3200, 3926, 3926,
        3926, 4747, 4747, 4747, 5531, 5531, 5531]

# Coordinate posizioni immagine fotocamera
XposIMG = [100, 155, 211, 119, 157, 195, 138, 157, 177, 101, 119, 140, 177,
           196, 215, 139, 160, 178, 120, 161, 203, 100, 163, 222]
YposIMG = [67, 62, 60, 81, 79, 76, 99, 98, 97, 118, 118, 118, 115, 114, 113,
           135, 135, 133, 155, 154, 151, 175, 175, 169]

# Valore posizione(0 = posizione vuota, 1 = pallina Robot, 10 = pallina User)
EMPTY = 0
ROBOT = 1
USER = 10
BLOCCOTRIA = 2
SVOLGITRIA = 3
DIFESA = 1
OUTMAX = 512                    # Uscita massima pwm output
OUTMIN = 0                      # Uscita minima pwm output

# Combinazioni possibili delle trie
TRIA = [0, 1, 2, 3, 4, 5, 6, 7, 8,
        21, 22, 23, 18, 19, 20,
        15, 16, 17, 21, 9, 0, 18, 10, 3,
        15, 11, 6, 2, 14, 23, 5, 13, 20,
        8, 12, 17, 9, 10, 11, 16, 19, 22, 12, 13, 14,
        1, 4, 7]

ANGOLI = [0, 3, 6, 23, 20, 17, 21, 18, 15, 2, 5, 8]  # Posizioni angoli tria
# Posizioni angoli quadrati tria
ANG_QUADRATI = [0, 21, 23, 2, 3, 18, 20, 5, 6, 15, 17, 8]
QUADRATI = [[0, 1, 2, 14, 23, 22, 21, 9], [
    3, 4, 5, 13, 20, 19, 18, 10], [6, 7, 8, 12, 17, 16, 15, 11]]
SPOSTAMENTI = [0, 1, 0, 1, 0, 1, 0, 1]
COLLEGAMENTI = [9, 10, 11, 22, 19, 16, 14, 13,
                12, 1, 4, 7]         # Posizioni collegamenti tria
POS_CENTRALI = [4, 10, 19, 13]  # Posizioni centro dei collegamenti tria

# Coordinate X e Y dello scivolo su cui sono presenti le palline del Robot
scivoloPalline = [80, 4280]
contenitorePVR = [5025, 4308]      # Contenitore palline vinte robot
contenitorePVU = [2635, 0]      # Contenitore palline vinte user

asse_y = txt.motor(1)
asse_x = txt.motor(2)
asse_z = txt.motor(3)
ventosa = txt.output(7)
lamp = txt.output(8)

input_resety = txt.input(1)
input_resetx = txt.input(4)
input_downz = txt.input(5)
input_upz = txt.input(6)
input_finemossa = txt.input(7)
input_InizioR = txt.input(8)

Val = [0] * 24
ValposCamera = [0] * 24  # Valori posizioni fotocamera rilevamento somma blu

User = False                    # Boolean inizio utente
Robot = False                   # Boolean inizio robot

#------------INIZIO FORMALIZZAZIONE CLASSI------------------


def SplitList(L, step):
    "Divisione in sublists dato il numero di step di una lista"
    return[L[i:i + step]for i in range(0, len(L), step)]


def GetItems(V, I):
    "Elementi in V dato l'indice I"
    return[V[i]for i in I]


def reset():
    "Reset del Robot nelle cordinate (0, 0)."
    asse_x.setSpeed(-OUTMAX)
    asse_x.setDistance(20000)
    asse_y.setSpeed(OUTMAX)
    asse_y.setDistance(20000)
    asse_z.setSpeed(-OUTMAX)
    asse_z.setDistance(20000)
    while True:
        if (input_resetx.state() == 1 and
            input_resety.state() == 1 and
                input_upz.state() == 1):
            asse_x.stop()
            asse_y.stop()
            asse_z.stop()
            return


def catch():
    "Presa delle palline."
    asse_z.setSpeed(OUTMAX)
    asse_z.setDistance(20000)
    while True:
        if(input_downz.state() == 1):
            asse_z.stop()
            ventosa.setLevel(OUTMAX)
            break
    asse_z.setSpeed(-OUTMAX)
    asse_z.setDistance(20000)
    while True:
        if(input_upz.state() == 1):
            asse_z.stop()
            break


def release():
    "Rilascio delle palline."
    asse_z.setSpeed(OUTMAX)
    asse_z.setDistance(20000)
    while True:
        if(input_downz.state() == 1):
            asse_z.stop()
            ventosa.setLevel(OUTMIN)
            break
    asse_z.setSpeed(-OUTMAX)
    asse_z.setDistance(20000)
    while True:
        if(input_upz.state() == 1):
            asse_z.stop()
            break


def fromto(x1, y1, x2, y2):
    "Spostamento da (x1, y1) a (x2, y2)."
    start=time.time()
    opt.CurrentX = x2
    opt.CurrentY = y2
    diffx = x2 - x1
    diffy = y2 - y1
    distx = abs(diffx)
    disty = abs(diffy)
    if diffx != 0:
        if diffx > 0:
            asse_x.setSpeed(OUTMAX)
        else:
            asse_x.setSpeed(-OUTMAX)
        asse_x.setDistance(distx)
        txt.incrMotorCmdId(1)
    if diffy != 0:
        if diffy > 0:
            asse_y.setSpeed(-OUTMAX)
        else:
            asse_y.setSpeed(OUTMAX)
        asse_y.setDistance(disty)
        txt.incrMotorCmdId(0)
    while not(asse_y.finished() and asse_x.finished()):
        if time.time()-start >= 30:
            return
        txt.updateWait()


def ValposReset():
    global TRIA
    "Rilevamento somme blu posizioni fotocamera all'inizio."
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
    opt.ValposOld = Val
    TRIA = SplitList(TRIA, 3)


def ValposUpdate():
    "Riconoscimento palline blu."
    opt.PosPallineNuoveU = []
    opt.ContatoreVPU += 1
    frameCamera = txt.getCameraFrame()
    with open(CAM_IMAGE, 'wb') as f:
        f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE, 1)
    if opt.ContatoreVPU > 2:
        opt.ValposOld = Val
    for i in range(0, 24):
        blue = 0
        for j in range(0, 15):
            for k in range(0, 15):
                b, _, _ = img[YposIMG[i] + k, XposIMG[i] + j]
                blue = blue + b
        if blue - ValposCamera[i] > 3000:
            if Val[i] == EMPTY:
                Val[i] = USER
                opt.PosPallineNuoveU.append(i)
                print("pallina blu nella posizione "), i
        if((blue - ValposCamera[i] > -2500) and (blue - ValposCamera[i] < 2000)):
            if(Val[i] == ROBOT):
                if opt.TogliPallineR:
                    Val[i] = EMPTY
                    print("pallina Robot rimossa dalla posizione "), i
                else:
                    print("""\
                    MOSSA UTENTE NON VALIDA!!!
                    NON HAI IL PERMESSO DI TOGLIERE LE PALLINE DEL ROBOT.
                    RIMETTI A POSTO!""")
                    AttendUser()
                    ValposUpdate()


def Lampeggio(seconds,vel):
    "Lampeggio lampadina dati i secondi."
    start = time.time()
    while True:
        lamp.setLevel(OUTMIN)
        time.sleep(vel)
        lamp.setLevel(OUTMAX)
        time.sleep(vel)
        if (time.time() - start) >= seconds:
            lamp.setLevel(OUTMIN)
            return


def AttendUser():
    "Attend input fine mossa."
    lamp.setLevel(OUTMAX)
    while True:
        if input_finemossa.state() == 1:
            lamp.setLevel(OUTMIN)
            return


def Strategia():
    "Strategia robot."
    opt.PosAttacco = []
    V = POS_CENTRALI
    ritorno = True
    if (Val[V[0]] == EMPTY or
        Val[V[1]] == EMPTY or
        Val[V[2]] == EMPTY or
            Val[V[3]] == EMPTY):
        for j in POS_CENTRALI:
            ritorno = True
            for i in TRIA:
                if j in i:
                    if Val[i[0]] != 0 or Val[i[1]] != 0 or Val[i[2]] != 0:
                        ritorno = False
                        break
            if ritorno:
                fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
                catch()
                fromto(scivoloPalline[0], scivoloPalline[1], Xpos[j], Ypos[j])
                release()
                Val[j] = ROBOT
                return
    for i in ANG_QUADRATI:
        for j in COLLEGAMENTI:
            if Val[i] == EMPTY and Val[j] == EMPTY:
                if j not in V:
                    Val[i] = ROBOT
                    Val[j] = ROBOT
                    FPossibiliTria()
                    Val[i] = EMPTY
                    Val[j] = EMPTY
                    if len(opt.PosSvolgiTria) > 1:
                        fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
                        catch()
                        fromto(scivoloPalline[0], scivoloPalline[1],
                               Xpos[i], Ypos[i])
                        release()
                        Val[i] = ROBOT
                        opt.PosAttacco = [j]
                        opt.AttaccoState = 1
                        return


def FPossibiliTria():
    "Controllo possibili trie utente e robot."
    opt.Priorita = EMPTY
    opt.PosBloccoTriaU = []
    opt.PosSvolgiTria = []
    opt.PosTogliPallina = []
    posEmpty = -1
    posUser = -1
    pRobot = False
    s = 0
    for i in TRIA:
        s = GetItems(Val, i)
        if 0 in s:
            posEmpty = i[s.index(0)]
        if 10 in s:
            posUser = i[s.index(10)]
        if sum(s) == 20:
            opt.Priorita = BLOCCOTRIA
            opt.PosBloccoTriaU.append(posEmpty)
            opt.PosTogliPallina.append(posUser)
        elif sum(s) == 2:
            opt.PosSvolgiTria.append(posEmpty)
            pRobot = True
        elif sum(s) == 3:
            if i not in opt.TrieRobot:
                opt.TrieRobot.append(i)
                Lampeggio(1,0.002)
                TogliPallina()
                opt.Controllo=False
                return
        elif sum(s) == 30:
            if not opt.Controllo:
                if i not in opt.TrieUtente:
                    opt.TrieUtente.append(i)
                    print("Hai formalizzato una Tria.")
                    print("Puoi eliminare una pallina avversaria!")
                    Lampeggio(1,0.02)
                    AttendUser()
                    opt.TogliPallineR = True
                    ValposUpdate()
                    opt.TogliPallineR = False
                    FPossibiliTria()
                    return
        if sum(s) != 30:
            if i in opt.TrieUtente:
                opt.TrieUtente.remove(i)
        if sum(s) != 3:
            if i in opt.TrieRobot:
                opt.TrieRobot.remove(i)
    if pRobot:
        opt.Priorita = SVOLGITRIA


def ControlloAttacco():
    "Controllo possibili mosse fortunate"
    for i in range(0, 24):
        if Val[i] == EMPTY:
            Val[i] = ROBOT
            FPossibiliTria()
            opt.Priorita = EMPTY
            Val[i] = EMPTY
            if len(opt.PosSvolgiTria) > 1:
                fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
                catch()
                fromto(scivoloPalline[0], scivoloPalline[1], Xpos[i], Ypos[i])
                release()
                opt.Priorita = 3
                Val[i] = ROBOT
                return


def Attacco():
    "Procedura attacco."
    p = opt.PosAttacco
    if opt.AttaccoState == 0:
        Strategia()
    else:
        Val[p[0]] = ROBOT
        FPossibiliTria()
        if opt.PosSvolgiTria > 1:
            fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
            catch()
            fromto(scivoloPalline[0], scivoloPalline[1],
                   Xpos[p[0]], Ypos[p[0]])
            release()
            opt.AttaccoState = 0
        else:
            Val[p[0]] = EMPTY
            opt.AttaccoState = 0
            Strategia()


def BloccoTriaU():
    "Blocco tria utente."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1],
           Xpos[opt.PosBloccoTriaU[0]], Ypos[opt.PosBloccoTriaU[0]])
    release()
    Val[opt.PosBloccoTriaU[0]] = ROBOT


def SvolgiTria():
    "Svolgi tria."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1],
           Xpos[opt.PosSvolgiTria[0]], Ypos[opt.PosSvolgiTria[0]])
    release()
    Val[opt.PosSvolgiTria[0]] = ROBOT


def Controlli():
    "controllo mosse utente non valide."
    LenPNU = len(opt.PosPallineNuoveU)
    stop = False
    ContatorePos = -1
    if LenPNU == 0 or LenPNU > 1:
        while LenPNU > 1:
            for i in range(0, LenPNU):
                Val[opt.PosPallineNuoveU[i - 1]] = EMPTY
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            SONO STATE POSIZIONATE PIU' PALLINE!!!
            LASCIANE SOLTANTO UNA""")
            AttendUser()
            ValposUpdate()
            LenPNU = len(opt.PosPallineNuoveU)
        while LenPNU == 0:
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            NON HAI POSIZIONATO LA PALLINA!""")
            AttendUser()
            ValposUpdate()
            LenPNU = len(opt.PosPallineNuoveU)
    while not stop:
        stop = True
        for i1, i2 in zip(opt.ValposOld, Val):
            ContatorePos = ContatorePos + 1
            if i1 == USER or i1 == ROBOT:
                if i2 == EMPTY:
                    stop = False
                    opt.ContatoreVPU = -1
                    print("""\
                    MOSSA UTENTE NON VALIDA!!!
                    HAI SPOSTATO O RIMOSSO UNA PALLINA DALLA POSIZIONE %d"""), ContatorePos
                    AttendUser()
                    ValposUpdate()
                    ContatorePos = 3


def ControlloDifesa():
    "Difesa da possibili strategie utente."
    a = ANGOLI
    opt.Controllo = True
    for i in range(0, 24):
        if Val[i] == EMPTY:
            Val[i] = USER
            FPossibiliTria()
            opt.Priorita = EMPTY
            Val[i] = EMPTY
            if len(opt.PosBloccoTriaU) > 1:
                opt.Priorita = DIFESA
                opt.PosDifesa = i
                break
    if opt.Priorita != DIFESA:
        for i in range(0, 12):
            if Val[a[i]] == USER:
                if a[i] in [0, 3, 6, 21, 18, 15]:
                    if Val[a[i + 3]] == EMPTY:
                        Val[a[i + 3]] = USER
                        for j in range(0, 12):
                            if Val[a[j]] == EMPTY:
                                Val[a[j]] = USER
                                FPossibiliTria()
                                Val[a[j]] = EMPTY
                                if len(opt.PosBloccoTriaU) > 1:
                                    opt.Priorita = DIFESA
                                    opt.PosDifesa = a[i + 3]
                                    break
                        Val[a[i + 3]] = EMPTY
                elif a[i] in [23, 20, 17, 2, 5, 8]:
                    if Val[a[i - 3]] == EMPTY:
                        Val[a[i - 3]] = USER
                        for j in range(0, 12):
                            if Val[a[j]] == EMPTY:
                                Val[a[j]] = USER
                                FPossibiliTria()
                                Val[a[j]] = EMPTY
                                if len(opt.PosBloccoTriaU) > 1:
                                    opt.Priorita = DIFESA
                                    opt.PosDifesa = a[i - 3]
                                    break
                        Val[a[i - 3]] = EMPTY
    opt.Controllo = False


def Difesa():
    "Esecuzione difesa."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1],
           Xpos[opt.PosDifesa], Ypos[opt.PosDifesa])
    release()
    Val[opt.PosDifesa] = ROBOT


def TogliPallina():
    "Togliere pallina utente quando robot esegue tria."
    opt.Controllo=True
    FPossibiliTria()
    if len(opt.PosBloccoTriaU) > 1:
        for i in range(0, 24):
            if Val[i] == USER:
                Val[i] = EMPTY
                FPossibiliTria()
                if len(opt.PosBloccoTriaU) == 0:
                    fromto(opt.CurrentX, opt.CurrentY,
                           Xpos[i], Ypos[i])
                    catch()
                    fromto(Xpos[i], Ypos[i],
                           contenitorePVR[0], contenitorePVR[1])
                    ventosa.setLevel(OUTMIN)
                    return
                else:
                    Val[i] = USER
    for i in range(0, 24):
        if Val[i] == EMPTY:
            Val[i] = USER
            FPossibiliTria()
            Val[i] = EMPTY
            if len(opt.PosBloccoTriaU) > 1:
                fromto(opt.CurrentX,
                       opt.CurrentY,
                       Xpos[opt.PosTogliPallina[0]],
                       Ypos[opt.PosTogliPallina[0]])
                catch()
                fromto(Xpos[opt.PosTogliPallina[0]],
                       Ypos[opt.PosTogliPallina[0]],
                       contenitorePVR[0],
                       contenitorePVR[1])
                ventosa.setLevel(OUTMIN)
                Val[opt.PosTogliPallina[0]]=EMPTY
                return
    for i in range(0, 24):
        if Val[i] == 10:
            fromto(
                opt.CurrentX,
                opt.CurrentY,
                Xpos[i],
                Ypos[i])
            catch()
            fromto(Xpos[i], Ypos[i],
                   contenitorePVR[0], contenitorePVR[1])
            Val[i] = EMPTY
            ventosa.setLevel(OUTMIN)
            return

def Controlli2F():
    Pos1=-1
    Pos2=-1
    for i1, i2 in zip(opt.ValposOld, Val):
        ContatorePos = ContatorePos + 1
        if Val[i1]==10:
            if Val[i2]==0:
                Pos1=ContatorePos
        if Val[i1]==0:
            if Val[i2]==10:
                Pos2=ContatorePos

    while Pos2 not in opt.PosSpostaU[Pos1]:
        print("""
        MOSSA UTENTE NON VALIDA!!!
        NON PUOI SPOSTARE LA PALLINA NELLA POSIZIONE """,Pos1,""" ALLA POSIZIONE """,
        Pos2)
        Val[Pos1]=10
        Val[Pos2]=0
        AttendUser()
        ValposUpdate()
        for i1, i2 in zip(opt.ValposOld, Val):
            ContatorePos = ContatorePos + 1
            if Val[i1]==10:
                if Val[i2]==0:
                    Pos1=ContatorePos
            if Val[i1]==0:
                if Val[i2]==10:
                    Pos2=ContatorePos

def PosSposta(pos):
    "Procedura data una posizione rilascia le posizioni dove può spostarsi VUOTE"
    Pos = []
    for i in QUADRATI:
        i2 = QUADRATI.index(i)
        if pos in i:
            i3 = i.index(pos)
            if SPOSTAMENTI[i3] == 1:
                if(i2 == 0):
                    i4 = QUADRATI[i2 + 1]
                    if Val[i4[i3]] not in [1, 10]:
                        Pos.append(i4[i3])
                elif(i2 == 1):
                    i4 = QUADRATI[i2 + 1]
                    if Val[i4[i3]] not in [1, 10]:
                        Pos.append(i4[i3])
                    i4 = QUADRATI[i2 - 1]
                    if Val[i4[i3]] not in [1, 10]:
                        Pos.append(i4[i3])
                elif(i2 == 2):
                    i4 = QUADRATI[i2 - 1]
                    if Val[i4[i3]] not in [1, 10]:
                        Pos.append(i4[i3])
            i2 = i3 + 1
            if i2 > 7:
                i2 = 0
            if Val[i[i2]] not in [1, 10]:
                Pos.append(i[i2])
            i2 = i3 - 1
            if i2 < 0:
                i2 = 7
            if Val[i[i2]] not in [1, 10]:
                Pos.append(i[i2])
    return(Pos)


def PosSpostaUpdate():
    "Aggiorna PosSpostaR e PosSpostaU"
    for i in range(0, 24):
        if Val[i] == 1:
            opt.PosSpostaR.append(PosSposta(i))
        elif Val[i] == 10:
            opt.PosSpostaU.append(PosSposta(i))


def TrovaPosSposta(pos):
    "Trova la pedina del robot che può spostarsi nella posizione pos"
    for i in range(0, 24):
        if Val[i] == 1:
            if pos in PosSposta(i):
                return i


def Spostamento():
    "Funzione principale per lo spostamento delle palline del robot"
    PosSpostaUpdate()
    FPossibiliTria()
    if opt.Priorita == SVOLGITRIA:
        if opt.PosSvolgiTria in opt.PosSpostaR:
            Pos = TrovaPosSposta(opt.PosSvolgiTria[0])
            fromto(0, 0, Xpos[Pos], Ypos[Pos])
            catch()
            fromto(Xpos[Pos],
                   Ypos[Pos],
                   Xpos[opt.PosSvolgiTria[0]],
                   Ypos[opt.PosSvolgiTria[0]])
            release()
    elif opt.Priorita == BLOCCOTRIA:
        if opt.PosBloccoTriaU in opt.PosSpostaR:
            Pos = TrovaPosSposta(opt.PosBloccoTriaU)
            fromto(0, 0, Xpos[Pos], Ypos[Pos])
            catch()
            fromto(Xpos[Pos],
                   Ypos[Pos],
                   Xpos[opt.PosBloccoTriaU[0]],
                   Ypos[opt.PosBloccoTriaU[0]])
            release()
    else:
        for i in opt.PosSpostaR:
            Pos = TrovaPosSposta(i)
            fromto(0, 0, Xpos[Pos], Ypos[Pos])
            catch()
            fromto(Xpos[Pos], Ypos[Pos], Xpos[i], Ypos[i])
            release()
#-----INIZIO PROGRAMMA------------------------------------------------


reset()
txt.startCameraOnline()
Lampeggio(2.5,0.2)
ValposReset()
lamp.setLevel(OUTMAX)
User = False
Robot = False
Fine = False

while True:
    if input_InizioR.state() == 1:
        Robot = True
        break
    if input_finemossa.state() == 1:
        User = True
        break

lamp.setLevel(OUTMIN)
if (Robot):
    #-------------------- Inizio prima fase gioco---------------------
    for i in range(0, 9):
        debug("Controllo Possibili Trie...")
        FPossibiliTria()
        if opt.Priorita == BLOCCOTRIA:
            debug("Blocco Tria nemica...")
            BloccoTriaU()
        elif opt.Priorita == SVOLGITRIA:
            debug("Svolgitura Tria...")
            SvolgiTria()
            FPossibiliTria()
            opt.Priorita = 3
        else:
            debug("Controllo Attacco")
            ControlloAttacco()
            if opt.Priorita != 3:
                debug("Controllo Difesa...")
                ControlloDifesa()
        if opt.Priorita == DIFESA:
            debug("Difesa...")
            Difesa()
        elif opt.Priorita == EMPTY:
            debug("Strategia...")
            Attacco()
        debug("Reset...")
        reset()
        debug("Attend Utente...")
        AttendUser()
        ValposUpdate()
        Controlli()
    #------------- Inizio seconda parte gioco---------------

    while not Fine:
        print("___2 parte___")
        Spostamento()
        FPossibiliTria()
        reset()
        if len(opt.PosSpostaU) == 0 or Val.count(10) == 3:
            Fine = True
            print("Ha vinto il robot")
        PosSpostaUpdate()
        AttendUser()
        ValposUpdate()
        Controlli2F()
        FPossibiliTria()
        if len(opt.PosSpostaR) == 0 or Val.count(1) == 3:
            Fine = True
            print("Hai vinto!!")


if (User):
    for i in range(0, 9):
        #-------------------- Inizio prima fase gioco-----------------
        if i==0:
            ValposUpdate()
        else:
            debug("Attend Utente...")
            AttendUser()
            ValposUpdate()
        Controlli()
        debug("Controllo Possibili Trie...")
        FPossibiliTria()
        if opt.Priorita == BLOCCOTRIA:
            debug("Blocco Tria nemica...")
            BloccoTriaU()
        elif opt.Priorita == SVOLGITRIA:
            debug("Svolgitura Tria...")
            SvolgiTria()
            FPossibiliTria()
            opt.Priorita = 3
        else:
            debug("Controllo Attacco")
            ControlloAttacco()
            if opt.Priorita != 3:
                debug("Controllo Difesa...")
                ControlloDifesa()
        if opt.Priorita == DIFESA:
            debug("Difesa...")
            Difesa()
        elif opt.Priorita == EMPTY:
            debug("Strategia...")
            Attacco()
        debug("Reset...")
        reset()
    #------------- Inizio seconda parte gioco---------------

    while not Fine:
        print("___2 parte___")
        PosSpostaUpdate()
        AttendUser()
        ValposUpdate()
        FPossibiliTria()
        if len(opt.PosSpostaR) == 0 or Val.count(1) == 3:
            Fine = True
            print("Hai vinto!!")
        Spostamento()
        FPossibiliTria()
        reset()
        if len(opt.PosSpostaU) == 0 or Val.count(10) == 3:
            Fine = True
            print("Ha vinto il robot")
