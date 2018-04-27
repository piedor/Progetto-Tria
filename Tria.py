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
import data
import sys
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

txt.play_sound(1, 50)

M = [txt.C_MOTOR, txt.C_MOTOR, txt.C_MOTOR, txt.C_OUTPUT]

I = [(txt.C_SWITCH, txt.C_DIGITAL)] * 8

txt.setConfig(M, I)
txt.updateConfig()

#--------INIZIO DICHIARAZIONE VARIABILI---------------------

# Coordinate X e Y di ogni posizione in ordine numerico
Xpos = [1000, 2665, 4241, 1610, 2590, 3720, 2210, 2665, 3120, 1000, 1530,
 2210, 3120, 3720, 4241, 2080, 2665, 3120, 1610, 2665, 3720, 1000, 2665, 4241]

Ypos = [760, 760, 760, 1331, 1530, 1331, 2360, 2360, 2360, 3060, 3060, 3060,
        3060, 3060, 3060, 3786, 3786, 3786, 4607, 4607, 4607, 5391, 5391, 5391]

# Coordinate posizioni immagine fotocamera
XposIMG = [101, 156, 213, 122, 160, 198, 143, 159, 179, 103, 120, 139, 179,
           200, 217, 141, 161, 180, 120, 163, 200, 101, 162, 223]
YposIMG = [66, 62, 60, 80, 79, 78, 97, 97, 97, 119, 114, 117, 114, 112, 113,
           134, 134, 133, 155, 154, 152, 174, 172, 169]
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
scivoloPalline = [120, 4140]
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

Val = [0] * 24  # Valori posizioni(0=Vuota,1=Robot,10=Utente)
ValposCameraB = [0] * 24  # Valori posizioni fotocamera rilevamento somma blu
ValposCameraUpdatedB = [0] * 24  # Valori blue delle posizioni
ValposCameraUpdatedG = [0] * 24  # Valori green delle posizioni
ValposCameraUpdatedR = [0] * 24  # Valori red delle posizioni

User = False                    # Boolean inizio utente
Robot = False                   # Boolean inizio robot
Fase = 1  # Variabile fase del gioco

#------------INIZIO FORMALIZZAZIONE CLASSI------------------


def SplitList(L, step):
    "Divisione in sublists dato il numero di step di una lista."
    return[L[i:i + step]for i in range(0, len(L), step)]


def GetItems(V, I):
    "Elementi in V dato l'indice I."
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
    start = time.time()
    opt.CurrentX = x2
    opt.CurrentY = y2
    data.Insert("CurrentX", opt.CurrentX)
    data.Insert("CurrentY", opt.CurrentY)
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
        if time.time() - start >= 30:
            return
        txt.updateWait()


def ValposReset():
    "Rilevamento somme blu posizioni fotocamera all'inizio."
    global TRIA
    try:
        for i in range(0, 50):
            frameCamera = txt.getCameraFrame()
            with open(CAM_IMAGE, 'wb') as f:
                f.write(bytearray(frameCamera))
    except BaseException:
        sys.exit(0)
    img = cv2.imread(CAM_IMAGE, 1)
    for i in range(0, 24):
        blue = 0
        for j in range(0, 15):
            for k in range(0, 15):
                b, _, _ = img[YposIMG[i] + k, XposIMG[i] + j]
                blue += b
        ValposCameraB[i] = blue
    data.Insert("ValposOld", opt.ValposOld)
    TRIA = SplitList(TRIA, 3)


def ValposUpdate():
    "Riconoscimento palline blu."
    opt.ContatoreVPU += 1
    frameCamera = txt.getCameraFrame()
    with open(CAM_IMAGE, 'wb') as f:
        f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE, 1)
    if opt.ContatoreVPU > 1:
        opt.ValposOld = data.ReturnValue("Val")
    for i in range(0, 24):
        blue = 0
        green = 0
        red = 0
        for j in range(0, 15):
            for k in range(0, 15):
                b, g, r = img[YposIMG[i] + k, XposIMG[i] + j]
                blue += b
                green += g
                red += r
        if blue - ValposCameraB[i] > 3000:
            if Val[i] == EMPTY:
                Val[i] = USER
                opt.PosPallineNuoveU.append(i)
                print("pallina blu nella posizione "), i
        if (ValposCameraUpdatedB[i] -
            blue > 5000) and (ValposCameraUpdatedG[i] -
                              green > 3000) and (ValposCameraUpdatedR[i] -
                                                 red > 1000):
            if Val[i] == ROBOT:
                if opt.TogliPallineR:
                    flag = 0
                    for j in opt.TrieRobot:
                        if i in j:
                            flag = 1
                    if flag == 1:
                        txt.play_sound(3, 1)
                        print("""\
                        MOSSA UTENTE NON VALIDA!!!
                        NON PUOI TOGLIERE UNA PALLINA DA UNA TRIA DEL ROBOT.
                        RIMETTI A POSTO!""")
                        AttendUser()
                        ValposUpdate()
                    else:
                        Val[i] = EMPTY
                        opt.PosPallineRimosseU.append(i)
                        print("pallina Robot rimossa dalla posizione "), i
                else:
                    txt.play_sound(3, 1)
                    print("""\
                    MOSSA UTENTE NON VALIDA!!!
                    NON HAI IL PERMESSO DI TOGLIERE LE PALLINE DEL ROBOT.
                    RIMETTI A POSTO!""")
                    AttendUser()
                    ValposUpdate()
        if (ValposCameraUpdatedB[i] -
                blue > 5000):
            if Fase == 2:
                if Val[i] == USER:
                    Val[i] = EMPTY
                    debug("Pallina Utente rimossa dalla posizione %d" % (i))
    data.Insert("Val", Val)
    data.Insert("ValposOld", opt.ValposOld)


def ValposCameraUpdate():
    "Aggiornamento valori RGB delle posizioni."
    frameCamera = txt.getCameraFrame()
    with open(CAM_IMAGE, 'wb') as f:
        f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE, 1)
    for i in range(0, 24):
        blue = 0
        green = 0
        red = 0
        for j in range(0, 15):
            for k in range(0, 15):
                b, g, r = img[YposIMG[i] + k, XposIMG[i] + j]
                blue += b
                green += g
                red += r
        ValposCameraUpdatedB[i] = blue
        ValposCameraUpdatedG[i] = green
        ValposCameraUpdatedR[i] = red


def Lampeggio(seconds, vel):
    "Lampeggio lampadina dati i secondi e la velocità(valore più basso,lampeggio più veloce)."
    start = time.time()
    while True:
        lamp.setLevel(OUTMIN)
        time.sleep(vel)
        lamp.setLevel(OUTMAX)
        time.sleep(vel)
        if time.time() - start >= seconds:
            lamp.setLevel(OUTMIN)
            return


def AttendUser():
    "Attend input fine mossa."
    lamp.setLevel(OUTMAX)
    while True:
        if input_finemossa.state() == 1:
            lamp.setLevel(OUTMIN)
            return


def AddPallina(Pos):
    "Posizionamento nuova pallina del Robot data la posizione."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1], Xpos[Pos], Ypos[Pos])
    release()
    Val[Pos] = 1
    data.Insert("Val", Val)


def RemovePallina(Pos):
    "Rimozione pallina data la posizione."
    fromto(opt.CurrentX, opt.CurrentY,
           Xpos[Pos], Ypos[Pos])
    catch()
    fromto(Xpos[Pos], Ypos[Pos],
           contenitorePVR[0], contenitorePVR[1])
    ventosa.setLevel(OUTMIN)
    Val[Pos] = EMPTY
    data.Insert("Val", Val)


def MovePallina(Pos1, Pos2):
    "Spostamento pallina data la posizione di partenza e di arrivo."
    fromto(0, 0, Xpos[Pos1], Ypos[Pos1])
    catch()
    fromto(Xpos[Pos1],
           Ypos[Pos1],
           Xpos[Pos2],
           Ypos[Pos2])
    release()
    Val[Pos1] = 0
    Val[Pos2] = 1
    data.Insert("Val", Val)


def Return2TPos(Pos):
    "Ritorna le 2 trie di cui fà parte Pos."
    T1 = []
    T2 = []
    for i in TRIA:
        if Pos in i:
            if len(T1) == 0:
                T1 = i
            else:
                T2 = i
    return(T1, T2)


def Strategia():
    "Strategia robot."
    opt.PosAttacco = []
    V = POS_CENTRALI
    random.shuffle(V)
    if (Val[V[0]] == EMPTY or
        Val[V[1]] == EMPTY or
        Val[V[2]] == EMPTY or
            Val[V[3]] == EMPTY):
        for j in V:
            ritorno = True
            for i in TRIA:
                if j in i:
                    if Val[i[0]] != 0 or Val[i[1]] != 0 or Val[i[2]] != 0:
                        ritorno = False
                        break
            if ritorno:
                AddPallina(j)
                return
    for i in ANG_QUADRATI:
        for j in COLLEGAMENTI:
            if Val[i] == EMPTY and Val[j] == EMPTY:
                if j not in V:
                    opt.Controllo = True
                    Val[i] = ROBOT
                    Val[j] = ROBOT
                    FPossibiliTria()
                    Val[i] = EMPTY
                    Val[j] = EMPTY
                    opt.Controllo = False
                    if len(opt.PosSvolgiTria) > 1:
                        AddPallina(i)
                        opt.PosAttacco = [j]
                        opt.AttaccoState = 1
                        return
    for i in range(0, 24):
        if Val[i] == EMPTY:
            AddPallina(i)
            return


def FPossibiliTria():
    "Controllo possibili trie utente e robot."
    opt.Priorita = EMPTY
    opt.PosBloccoTriaU = []
    opt.PosSvolgiTria = []
    opt.PosTogliPallina = []
    opt.PrioritaTR = False
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
            for j in i:
                if Val[j] == USER:
                    opt.PosTogliPallina.append(j)
        if sum(s) == 20:
            opt.Priorita = BLOCCOTRIA
            opt.PosBloccoTriaU.append(posEmpty)
        elif sum(s) == 2:
            opt.PosSvolgiTria.append(posEmpty)
            pRobot = True
        elif sum(s) == 3:
            opt.PrioritaTR = True
            if not opt.Controllo:
                if i not in opt.TrieRobot:
                    opt.TrieRobot.append(i)
                    txt.play_sound(5, 1)
                    Lampeggio(1, 0.002)
                    TogliPallina()
                    opt.Controllo = False
                    return
        elif sum(s) == 30:
            if not opt.Controllo:
                if i not in opt.TrieUtente:
                    opt.TrieUtente.append(i)
                    txt.play_sound(4, 1)
                    print("Hai formalizzato una Tria.")
                    print("Puoi eliminare una pallina avversaria!")
                    Lampeggio(1, 0.02)
                    AttendUser()
                    opt.TogliPallineR = True
                    ValposUpdate()
                    Controlli()
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
    "Controllo se il Robot può aprirsi 2 trie."
    for i in range(0, 24):
        if Val[i] == EMPTY:
            opt.Controllo = True
            Val[i] = ROBOT
            FPossibiliTria()
            opt.Controllo = False
            opt.Priorita = 0
            Val[i] = EMPTY
            if len(opt.PosSvolgiTria) > 1:
                AddPallina(i)
                opt.Priorita = 3
                return


def Attacco():
    "Procedura attacco."
    p = opt.PosAttacco
    if opt.AttaccoState == 0:
        Strategia()
    else:
        if p[0] == EMPTY:
            opt.Controllo = True
            Val[p[0]] = ROBOT
            FPossibiliTria()
            opt.Controllo = False
            if opt.PosSvolgiTria > 1:
                AddPallina(p[0])
                opt.AttaccoState = 0
            else:
                Val[p[0]] = EMPTY
                opt.AttaccoState = 0
                Strategia()
        else:
            opt.AttaccoState = 0
            Strategia()


def BloccoTriaU():
    "Blocco tria utente."
    AddPallina(opt.PosBloccoTriaU[0])


def SvolgiTria():
    "Svolgi tria."
    AddPallina(opt.PosSvolgiTria[0])


def Controlli():
    "Controllo mosse utente non valide."
    LenPNU = len(opt.PosPallineNuoveU)
    LenPRU = len(opt.PosPallineRimosseU)
    if not opt.TogliPallineR:
        while LenPNU > 1:
            for i in range(0, LenPNU):
                Val[opt.PosPallineNuoveU[i]] = EMPTY
            txt.play_sound(3, 1)
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            SONO STATE POSIZIONATE PIU' PALLINE!!!
            LASCIANE SOLTANTO UNA""")
            opt.PosPallineNuoveU = []
            AttendUser()
            ValposUpdate()
            LenPNU = len(opt.PosPallineNuoveU)
        while LenPNU == 0:
            txt.play_sound(3, 1)
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            NON HAI POSIZIONATO LA PALLINA!""")
            opt.PosPallineNuoveU = []
            AttendUser()
            ValposUpdate()
            LenPNU = len(opt.PosPallineNuoveU)
    if opt.TogliPallineR:
        while LenPRU > 1:
            for i in range(0, LenPRU):
                Val[opt.PosPallineRimosseU[i]] = EMPTY
            txt.play_sound(3, 1)
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            HAI RIMOSSO PIU' PALLINE DEL ROBOT!!!
            """)
            opt.PosPallineRimosseU = []
            AttendUser()
            ValposUpdate()
            LenPRU = len(opt.PosPallineRimosseU)
        while LenPRU == 0:
            txt.play_sound(3, 1)
            print("""\
            MOSSA UTENTE NON VALIDA!!!
            NON HAI RIMOSSO UNA PALLINA DEL ROBOT!""")
            opt.PosPallineRimosseU = []
            AttendUser()
            ValposUpdate()
            LenPRU = len(opt.PosPallineRimosseU)
    opt.PosPallineNuoveU = []
    opt.PosPallineRimosseU = []


def ControlloDifesa():
    "Difesa da possibili strategie utente."
    a = ANGOLI
    opt.Controllo = True
    for i in range(0, 24):
        if Val[i] == EMPTY:
            opt.Controllo = True
            Val[i] = USER
            FPossibiliTria()
            opt.Controllo = False
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
                                opt.Controllo = True
                                Val[a[j]] = USER
                                FPossibiliTria()
                                opt.Controllo = False
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
                                opt.Controllo = True
                                Val[a[j]] = USER
                                FPossibiliTria()
                                opt.Controllo = False
                                Val[a[j]] = EMPTY
                                if len(opt.PosBloccoTriaU) > 1:
                                    opt.Priorita = DIFESA
                                    opt.PosDifesa = a[i - 3]
                                    break
                        Val[a[i - 3]] = EMPTY
    opt.Controllo = False


def Difesa():
    "Esecuzione difesa."
    AddPallina(opt.PosDifesa)


def TogliPallina():
    "Togliere pallina utente quando il Robot esegue tria."
    opt.Controllo = True
    FPossibiliTria()
    if len(opt.PosBloccoTriaU) > 1:
        for i in range(0, 24):
            flag = 0
            for j in opt.TrieUtente:
                if i in j:
                    flag = 1
            if flag == 0:
                if Val[i] == USER:
                    opt.Controllo = True
                    Val[i] = EMPTY
                    FPossibiliTria()
                    opt.Controllo = False
                    Val[i] = USER
                    if len(opt.PosBloccoTriaU) == 0:
                        RemovePallina(i)
                        return

    for i in range(0, 24):
        flag = 0
        for j in opt.TrieUtente:
            if i in j:
                flag = 1
        if flag == 0:
            if Val[i] == EMPTY:
                opt.Controllo = True
                Val[i] = USER
                FPossibiliTria()
                opt.Controllo = False
                Val[i] = EMPTY
            if len(opt.PosTogliPallina) > 0:
                for k in opt.PosTogliPallina:
                    if Val[k] == USER:
                        RemovePallina(k)
                        return

    for i in range(0, 24):
        flag = 0
        for j in opt.TrieUtente:
            if i in j:
                flag = 1
        if flag == 0:
            if Val[i] == 10:
                RemovePallina(i)
                return


def ReturnValUS():
    "Ritorna le 2 posizioni dello spostamento da parte dell'utente."
    Pos1 = []
    Pos2 = []
    ContatorePos = -1
    for i1, i2 in zip(opt.ValposOld, Val):
        ContatorePos = ContatorePos + 1
        if i1 == 10:
            if i2 == 0:
                Pos1.append(ContatorePos)
        if i1 == 0:
            if i2 == 10:
                Pos2.append(ContatorePos)
    return(Pos1, Pos2)


def Controlli2F():
    "Controlli mosse utente non valide nella seconda fase."
    Pos1, Pos2 = ReturnValUS()
    while len(Pos1) + len(Pos2) > 2:
        print("""
        MOSSA UTENTE NON VALIDA!!!
        HAI SPOSTATO PIU' PALLINE""")
        for i in Pos1:
            Val[i] = 10
        for i in Pos2:
            Val[i] = 0
        AttendUser()
        ValposUpdate()
        Pos1, Pos2 = ReturnValUS()
    while len(Pos1) + len(Pos2) == 0:
        print("""
        MOSSA UTENTE NON VALIDA!!!
        NON HAI SPOSTATO NESSUNA PALLINA""")
        AttendUser()
        ValposUpdate()
        Pos1, Pos2 = ReturnValUS()
    Val[Pos1[0]] = 10
    Val[Pos2[0]] = 0
    while Pos2[0] not in PosSposta(Pos1[0]):
        print("""
        MOSSA UTENTE NON VALIDA!!!
        NON PUOI SPOSTARE LA PALLINA DALLA POSIZIONE """, Pos1[0], """ ALLA POSIZIONE """,
              Pos2[0])
        Val[Pos1[0]] = 10
        Val[Pos2[0]] = 0
        AttendUser()
        ValposUpdate()
        Pos1, Pos2 = ReturnValUS()
    Val[Pos1[0]] = 0
    Val[Pos2[0]] = 10
    debug(
        "Pallina utente spostata dalla posizione %d alla posizione %d" %
        (Pos1[0], Pos2[0]))


def PosSposta(pos):
    "Procedura data una posizione rilascia le posizioni dove può spostarsi VUOTE."
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
    "Aggiorna PosSpostaR e PosSpostaU."
    opt.PosSpostaR = []
    opt.PosSpostaU = []
    for i in range(0, 24):
        if Val[i] == 1:
            opt.PosSpostaR.append(PosSposta(i))
        elif Val[i] == 10:
            opt.PosSpostaU.append(PosSposta(i))


def TrovaPosSposta(pos):
    "Trova la pedina del robot che può spostarsi nella posizione pos."
    p=[]
    for i in range(0, 24):
        if Val[i] == 1:
            if pos in PosSposta(i):
                p.append(i)
    return p


def Spostamento():
    "Mossa Robot 2 fase."
    PosSpostaUpdate()
    FPossibiliTria()
    if opt.Priorita == SVOLGITRIA:
        for i in opt.PosSvolgiTria:
            for j in opt.PosSpostaR:
                if i in j:
                    Pos = TrovaPosSposta(i)
                    for k in Pos:
                        if k:
                            opt.Controllo = True
                            Val[k] = 0
                            Val[i] = 1
                            FPossibiliTria()
                            Val[k] = 1
                            Val[i] = 0
                            opt.Controllo = False
                            if opt.PrioritaTR:
                                MovePallina(k, i)
                                return
    if opt.Priorita == BLOCCOTRIA:
        for i in opt.PosBloccoTriaU:
            for j in opt.PosSpostaR:
                if i in j:
                    Pos = TrovaPosSposta(opt.PosBloccoTriaU)
                    for k in Pos:
                        if k:
                            MovePallina(k, i)
                            return
    if len(opt.TrieRobot) > 0:
        for i in opt.TrieRobot:
            for j in i:
                if len(PosSposta(j)) > 0:
                    Val[j] = 0
                    PosSpostaUpdate()
                    Val[j] = 1
                    if j not in opt.PosSpostaU:
                        for k in PosSposta(j):
                            if k:
                                MovePallina(j, k)
                                return
    r = range(0, 24)
    random.shuffle(r)
    for i in r:
        if Val[i] == 0:
            Pos = TrovaPosSposta(i)
            for k in Pos:
                if k:
                    MovePallina(k, i)
                    return


def ControlloFine():
    "Controllo fine partita"
    PosSpostaUpdate()
    if len(opt.PosSpostaR) == 0:
        print("""HAI VINTO!!! NESSUNA MOSSA POSSIBILE PER IL ROBOT""")
        sys.exit(0)
    if Val.count(1) == 2:
        print("""HAI VINTO!!! IL ROBOT E' RIMASTO SOLO CON 2 PALLINE""")
        sys.exit(0)
    if len(opt.PosSpostaU) == 0:
        print("""HA VINTO IL ROBOT! NON HAI NESSUNA MOSSA POSSIBILE""")
        sys.exit(0)
    if Val.count(10) == 2:
        print("""HA VINTO IL ROBOT! SEI RIMASTO SOLO CON 2 PALLINE""")
        sys.exit(0)

# -----INIZIO PROGRAMMA------------------------------------------------


reset()
txt.startCameraOnline()
Lampeggio(2, 0.2)
ValposReset()
data.Insert("Continue", 'True')
txt.stop_sound()
lamp.setLevel(OUTMAX)
User = False
Robot = False

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
        data.Insert("i", i)
        data.Insert("player", 'Robot')
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
        if opt.Priorita == EMPTY:
            debug("Strategia...")
            Attacco()
        debug("Reset...")
        reset()
        ValposCameraUpdate()
        debug("Attend Utente...")
        AttendUser()
        ValposUpdate()
        Controlli()
        ValposCameraUpdate()
        data.Insert("player", 'Utente')
    #------------- Inizio seconda parte gioco---------------

    data.Insert("Continue", 'False')
    print("___2 parte___")
    Fase = 2
    while True:
        data.Insert("player", 'Robot')
        ControlloFine()
        Spostamento()
        FPossibiliTria()
        reset()
        ValposCameraUpdate()
        ControlloFine()
        PosSpostaUpdate()
        AttendUser()
        ValposUpdate()
        Controlli2F()
        ValposCameraUpdate()
        data.Insert("player", 'Utente')
        FPossibiliTria()


if (User):
    for i in range(0, 9):
        #-------------------- Inizio prima fase gioco-----------------
        data.Insert("player", 'Utente')
        if i == 0:
            ValposUpdate()
        else:
            debug("Attend Utente...")
            AttendUser()
            ValposUpdate()
        Controlli()
        ValposCameraUpdate()
        data.Insert("player", 'Robot')
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
        if opt.Priorita == EMPTY:
            debug("Strategia...")
            Attacco()
        debug("Reset...")
        reset()
        ValposCameraUpdate()
    #------------- Inizio seconda parte gioco---------------

    data.Insert("Continue", 'False')
    print("___2 parte___")
    Fase = 2
    while True:
        ControlloFine()
        data.Insert("player", 'Utente')
        PosSpostaUpdate()
        AttendUser()
        ValposUpdate()
        Controlli2F()
        ValposCameraUpdate()
        ControlloFine()
        data.Insert("player", 'Robot')
        FPossibiliTria()
        Spostamento()
        FPossibiliTria()
        reset()
        ValposCameraUpdate()
