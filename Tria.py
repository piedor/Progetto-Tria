#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
*********************************************************************************************
Tria.py - Programma principale per la tria realizzata con fischertechnik
© 2018 Pietro Dorighi Riccardo Martinelli Gabriele Prada
*********************************************************************************************
"""

#Importazione librerie
import ftrobopy
import time
import random
import cv2
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
debug=logging.debug


__author__      = "Pietro Dorighi"
__copyright__   = "Copyright 2018 by Pietro Dorighi"
__license__     = "MIT License"
__version__     = "2.0"
__maintainer__  = "Pietro Dorighi"
__email__       = "dorighi@developer.org"
__status__      = "development"
__date__        = "10/01/2018"


CAM_IMAGE = 'img/TXTCamImg.jpg'

WLAN = '192.168.8.2'
USB = '192.168.7.2'
txt = ftrobopy.ftrobopy(host=USB, port=65000) # Connessione al controller

M = [ txt.C_MOTOR, txt.C_MOTOR, txt.C_MOTOR, txt.C_OUTPUT ]

I = [ (txt.C_SWITCH, txt.C_DIGITAL ) ] * 8

txt.setConfig(M, I)
txt.updateConfig()

#--------INIZIO DICHIARAZIONE VARIABILI--------------------------------------------------------------------------------

# Coordinate X e Y di ogni posizione in ordine numerico
Xpos = [970,2635,4211,1580,2635,3690,2180,2635,
        3090,970,1580,2180,3090,3690,4211,2180,
        2635,3090,1580,2635,3690,970,2635,4211]

Ypos = [900,900,900,1471,1471,1471,2500,2500,2500,
        3200,3200,3200,3200,3200,3200,3926,3926,
        3926,4747,4747,4747,5531,5531,5531]

# Valore posizione(0 = posizione vuota, 1 = pallina Robot, 10 = pallina User)
Valpos=[0] * 24
ValposOld=[0] * 24

scivoloPalline = [5025,4308]  # Coordinate X e Y dello scivolo su cui sono presenti le palline del Robot
contenitorePVR = [0,2903]     # Contenitore palline vinte robot
contenitorePVU = [2635,0]     # Contenitore palline vinte user

Outmax=512 #Uscita massima pwm output
Outmin=0 #Uscita minima pwm output

ventosa=txt.output(7)
lamp=txt.output(8)

inputresety=txt.input(1)
inputresetx=txt.input(4)
inputdownz=txt.input(5)
inputupz=txt.input(6)
inputfinemossa=txt.input(7)
inputInizioR=txt.input(8)

assey=txt.motor(1)
assex=txt.motor(2)
assez=txt.motor(3)
PossibiliTria = [0,1,2, 3,4,5, 6,7,8,
                 21,22,23, 18,19,20,
                 15,16,17, 21,9,0, 18,10,3,
                 15,11,6, 2,14,23, 5,13,20,
                 8,12,17, 9,10,11, 16,19,22, 12,13,14,
                 1,4,7] #Combinazioni possibili delle trie
CurrentX=0 #Coordinata X corrente
CurrentY=0 #Coordinata Y corrente
PosBloccoTriaU=[] #Posizione blocco tria utente
PosSvolgiTria=[] #Posizione completamento tria robot
Priorita=0 #Priorità mossa robot
angoli=[0,3,6, 23,20,17, 21,18,15, 2,5,8] #Posizioni angoli tria
quadrati=[0,21,23,2, 3,18,20,5, 6,15,17,8] #Posizioni angoli quadrati tria
collegamenti=[9,10,11, 22,19,16, 14,13,12, 1,4,7] #Posizioni collegamenti tria
centroCollegamenti=[4,10,19,13] #Posizioni centro dei collegamenti tria
AttaccoState=0 #Stato strategia robot
ContatoreVPU=0 #Contatore Valpos Update
PosPallineNuoveU=[] #Posizioni palline posizionate utente
PosDifesa=0 #Posizione difesa
Controllo=False #Boolean controllo
PosAttacco=[] #Posizione attacco
PosTogliPallina=[] #Posizione togli pallina
ValposCamera = [0] * 24 #Valori posizioni fotocamera rilevamento somma blu
XposIMG=[101, 156, 213, 121, 157, 195, 139, 157,
         178, 101, 122, 139, 179, 198, 217, 139,
         160, 180, 121, 162, 200, 101, 160, 223] #Coordinate X posizioni immagine fotocamera
YposIMG=[72, 70, 66, 87, 84, 83, 104, 104,
         103, 124, 124, 123, 121, 119, 118, 140,
         140, 138, 161, 160, 156, 182, 180, 176] #Coordinate Y posizioni immagine fotocamera
User=False #Boolean inizio utente
Robot=False #Boolean inizio robot

#------------INIZIO FORMALIZZAZIONE CLASSI-----------------------------------------------------------------------------

def reset():
    "Reset del Robot nelle cordinate (0, 0)."
    assex.setSpeed(-Outmax)
    assey.setSpeed(Outmax)
    assez.setSpeed(-Outmax)
    while True:
        if((inputresetx.state() == 1) and (inputresety.state()==1) and (inputupz.state()==1)):
            assex.setSpeed(Outmin)
            assey.setSpeed(Outmin)
            assez.setSpeed(Outmin)
            break

def catch():
    "Presa delle palline."
	assez.setSpeed(Outmax)
    while True:
    	if(inputdownz.state()==1):
    		assez.setSpeed(Outmin)
    		ventosa.setLevel(Outmax)
    		break
	assez.setSpeed(-Outmax)
    while True:
    	if(inputupz.state()==1):
    		assez.setSpeed(Outmin)
    		break

def release():
    "Rilascio delle palline."
	assez.setSpeed(Outmax)
    while True:
    	if(inputdownz.state()==1):
    		assez.setSpeed(Outmin)
    		ventosa.setLevel(Outmin)
    		break
	assez.setSpeed(-Outmax)
    while True:
    	if(inputupz.state()==1):
    		assez.setSpeed(Outmin)
    		break

def fromto(x1,y1,x2,y2):
    "Spostamento da (x1, y1) a (x2, y2)."
    global CurrentX
    global CurrentY
    CurrentX=x2
    CurrentY=y2
    diffx=x2-x1
    diffy=y2-y1
    distx=abs(diffx)
    disty=abs(diffy)
    if(diffx != 0):
        if(diffx > 0):
            assex.setSpeed(Outmax)
        else:
            assex.setSpeed(-Outmax)
        assex.setDistance(distx)

    if(diffy != 0):
        if(diffy > 0):
            assey.setSpeed(-Outmax)
        else:
            assey.setSpeed(Outmax)
        assey.setDistance(disty)

    while not(assey.finished() and assex.finished()):
        txt.updateWait()

def ValposReset():
    "Rilevamento somme blu posizioni fotocamera all'inizio."
    for i in range(0,50):
        frameCamera = txt.getCameraFrame()
        with open(CAM_IMAGE, 'wb') as f:
            f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE,1)
    for i in range(0,24):
        blue = 0
        for j in range(0,15):
            for k in range(0,15):
                b, _, _ = img[YposIMG[i] + k, XposIMG[i] + j]
                blue = blue + b
        ValposCamera[i] = blue
    ValposOld=Valpos

def ValposUpdate():
    "Riconoscimento palline blu."
    global ContatoreVPU
    global PosPallineNuoveU
    PosPallineNuoveU=[]
    ContatoreVPU+=1
    frameCamera = txt.getCameraFrame()
    with open(CAM_IMAGE, 'wb') as f:
        f.write(bytearray(frameCamera))
    img = cv2.imread(CAM_IMAGE,1)
    if(ContatoreVPU>2):
        ValposOld=Valpos
    for i in range(0,24):
        blue = 0
        for j in range(0,15):
            for k in range(0,15):
                b, _, _ = img[YposIMG[i] + k, XposIMG[i] + j]
                blue = blue + b
        if(blue - ValposCamera[i] > 3000):
            if(Valpos[i]  ==  0):
                Valpos[i] = 10
                PosPallineNuoveU.append(i)
                print("pallina blu nella posizione "),i
        # if((blue - ValposCamera[i] > -1000) and (blue - ValposCamera[i] < 1000)):
        #     if(Valpos[i]==1):
        #         Valpos[i]=0
        #         print("pallina Robot rimossa dalla posizione "),i

def Lampeggio(seconds):
    "Lampeggio lampadina dati i secondi."
    start = time.time()
    while True:
        lamp.setLevel(Outmin)
        time.sleep(0.5)
        lamp.setLevel(Outmax)
        time.sleep(0.5)
        if((time.time() - start) >= seconds):
            lamp.setLevel(Outmin)
            break

def AttendUser():
    "Attend input fine mossa."
    while True:
        if(inputfinemossa.state()==1):
            break

def Strategia():
    "Strategia robot."
    global PosAttacco
    global AttaccoState
    global PosSvolgiTria
    PosAttacco=[]
    V=centroCollegamenti
    if(Valpos[V[0]]==0 or Valpos[V[1]]==0 or Valpos[V[2]]==0 or Valpos[V[3]]==0):
        N=random.choice(V)
        while(Valpos[N]!=0):
            N=random.choice(V)
        fromto(0,0,scivoloPalline[0],scivoloPalline[1])
        catch()
        fromto(scivoloPalline[0],scivoloPalline[1],Xpos[N],Ypos[N])
        release()
        Valpos[N]=1
    else:
        for i in quadrati:
            for j in collegamenti:
                if(Valpos[i]==0 and Valpos[j]==0):
                    if(j!=V[0] and j!=V[1] and j!=V[2] and j!=V[3]):
                        Valpos[i]=1
                        Valpos[j]=1
                        FPossibiliTria()
                        Valpos[i]=0
                        Valpos[j]=0
                        if(len(PosSvolgiTria)>1):
                            fromto(0,0,scivoloPalline[0],scivoloPalline[1])
                            catch()
                            fromto(scivoloPalline[0],scivoloPalline[1],Xpos[i],Ypos[i])
                            release()
                            Valpos[i]=1
                            PosAttacco=[j]
                            AttaccoState=1

def FPossibiliTria():
    "Controllo possibili trie utente e robot."
    global Priorita
    global PosSvolgiTria
    global PosBloccoTriaU
    global PosTogliPallina
    Priorita=0
    PosBloccoTriaU=[]
    PosSvolgiTria=[]
    for i in range(0,48,3):
        if((Valpos[PossibiliTria[i]]+Valpos[PossibiliTria[i+1]]+Valpos[PossibiliTria[i+2]])==20):
            Priorita=2
            if(Valpos[PossibiliTria[i]]==0):
                PosBloccoTriaU.append(PossibiliTria[i])
            elif(Valpos[PossibiliTria[i]]==1):
                PosTogliPallina=PossibiliTria[i]
            if(Valpos[PossibiliTria[i+1]]==0):
                PosBloccoTriaU.append(PossibiliTria[i+1])
            elif(Valpos[PossibiliTria[i+1]]==1):
                PosTogliPallina=PossibiliTria[i+1]
            if(Valpos[PossibiliTria[i+2]]==0):
                PosBloccoTriaU.append(PossibiliTria[i+2])
            elif(Valpos[PossibiliTria[i+2]]==1):
                PosTogliPallina=PossibiliTria[i+2]

    for i in range(0,48,3):
        if((Valpos[PossibiliTria[i]]+Valpos[PossibiliTria[i+1]]+Valpos[PossibiliTria[i+2]])==2):
            Priorita=3
            if(Valpos[PossibiliTria[i]]==0):
                PosSvolgiTria.append(PossibiliTria[i])
            if(Valpos[PossibiliTria[i+1]]==0):
                PosSvolgiTria.append(PossibiliTria[i+1])
            if(Valpos[PossibiliTria[i+2]]==0):
                PosSvolgiTria.append(PossibiliTria[i+2])
    if(Controllo==False):
        for i in range(0,48,3):
            if((Valpos[PossibiliTria[i]]+Valpos[PossibiliTria[i+1]]+Valpos[PossibiliTria[i+2]])==30):
                if((ValposOld[PossibiliTria[i]]+ValposOld[PossibiliTria[i+1]]+ValposOld[PossibiliTria[i+2]])!=30):
                    print("Hai formalizzato una Tria.\nPuoi eliminare una pallina avversaria!")
                    lamp.setLevel(256)
                    AttendUser()
                    lamp.setLevel(0)
                    ValposUpdate()

def ControlloAttacco:
    "Controllo possibili mosse fortunate"
    global Priorita
    for i in range(0,23):
        if(Valpos[i]==0):
            Valpos[i]=1
            FPossibiliTria()
            Priorita=0
            Valpos[i]=0
            if(len(PosSvolgiTria)>1):
                fromto(0,0,scivoloPalline[0],scivoloPalline[1])
                catch()
                fromto(scivoloPalline[0],scivoloPalline[1],Xpos[i],Ypos[i])
                release()
                Priorita=3
                Valpos[i]=1
                break

def Attacco():
    "Procedura attacco."
    global AttaccoState
    p=PosAttacco
    if(AttaccoState==0):
        Strategia()
    else:
        Valpos[p[0]]=1
        FPossibiliTria()
        if(PosSvolgiTria>1):
            fromto(0,0,scivoloPalline[0],scivoloPalline[1])
            catch()
            fromto(scivoloPalline[0],scivoloPalline[1],Xpos[p[0]],Ypos[p[0]])
            release()
            AttaccoState=0
        else:
            Valpos[p[0]]=0
            AttaccoState=0
            Strategia()

def BloccoTriaU():
    "Blocco tria utente."
    fromto(0,0,scivoloPalline[0],scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0],scivoloPalline[1],Xpos[PosBloccoTriaU[0]],Ypos[PosBloccoTriaU[0]])
    release()
    Valpos[PosBloccoTriaU[0]]=1

def SvolgiTria():
    "Svolgi tria."
    fromto(0,0,scivoloPalline[0],scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0],scivoloPalline[1],Xpos[PosSvolgiTria[0]],Ypos[PosSvolgiTria[0]])
    release()
    Valpos[PosSvolgiTria[0]]=1

def Controlli():
    "Procedura controlli mosse utente non valide."
    global ContatoreVPU
    global PosPallineNuoveU
    LenPNU=len(PosPallineNuoveU)
    stop=False
    ContatorePos=-1
    if(LenPNU==0 or LenPNU>1):
        while(LenPNU>1):
            for i in range(0,LenPNU):
                Valpos[PosPallineNuoveU[i-1]]=0
            print("MOSSA UTENTE NON VALIDA!!!\nSONO STATE POSIZIONATE PIU' PALLINE!!!\nLASCIANE SOLTANTO UNA")
            lamp.setLevel(Outmax)
            AttendUser()
            lamp.setLevel(Outmin)
            ValposUpdate()
            LenPNU=len(PosPallineNuoveU)
        while(LenPNU==0):
            print("MOSSA UTENTE NON VALIDA!!!\nNON HAI POSIZIONATO LA PALLINA!")
            lamp.setLevel(Outmax)
            AttendUser()
            lamp.setLevel(Outmin)
            ValposUpdate()
            LenPNU=len(PosPallineNuoveU)
    while(stop==False):
        stop=True
        for i1,i2 in zip(ValposOld, Valpos):
            ContatorePos=ContatorePos+1
            if(i1==10 or i1==1):
                if(i2==0):
                    stop=False
                    ContatoreVPU=-1
                    print("MOSSA UTENTE NON VALIDA!!!\nHAI SPOSTATO O RIMOSSO UNA PALLINA DALLA POSIZIONE "),ContatorePos
                    lamp.setLevel(Outmax)
                    AttendUser()
                    lamp.setLevel(Outmin)
                    ValposUpdate()
                    ContatorePos=3

def ControlloDifesa():
    "Difesa da possibili strategie utente."
    global Priorita
    global PosDifesa
    global Controllo
    Controllo=True
    for i in range(0,23):
        if(Valpos[i]==0):
            Valpos[i]=10
            FPossibiliTria()
            Priorita=0
            Valpos[i]=0
            if(len(PosBloccoTriaU)>1):
                print(i)
                Priorita=1
                PosDifesa=i
                break
    if(Priorita!=1):
        for i in range(0,12):
            if(Valpos[angoli[i]]==10):
                if(angoli[i]==0 or angoli[i]==3 or angoli[i]==6 or angoli[i]==21 or angoli[i]==18 or angoli[i]==15):
                    if(Valpos[angoli[i+3]]==0):
                        Priorita=1
                        PosDifesa=angoli[i+3]
                elif(angoli[i]==23 or angoli[i]==20 or angoli[i]==17 or angoli[i]==2 or angoli[i]==5 or angoli[i]==8):
                    if(Valpos[angoli[i-3]]==0):
                        Priorita=1
                        PosDifesa=angoli[i-3]
    Controllo=False

def Difesa():
    "Esecuzione difesa."
    fromto(0, 0, scivoloPalline[0], scivoloPalline[1])
    catch()
    fromto(scivoloPalline[0], scivoloPalline[1], Xpos[PosDifesa], Ypos[PosDifesa])
    release()
    Valpos[PosDifesa]=1

def TogliPallina():
    "Togliere pallina utente quando robot esegue tria."
    FPossibiliTria()
    if(Priorita==2):
        fromto(CurrentX,CurrentY,Xpos[PosTogliPallina],Ypos[PosTogliPallina])
        catch()
        fromto(Xpos[PosTogliPallina],Ypos[PosTogliPallina],contenitorePVR[0],contenitorePVR[1])
        release()
        Valpos[PosTogliPallina]=0
    else:
        contatore=-1
        for i in Valpos:
            contatore+=1
            if(i==10):
                fromto(CurrentX,CurrentY,Xpos[contatore],Ypos[contatore])
                catch()
                fromto(Xpos[contatore],Ypos[contatore],contenitorePVR[0],contenitorePVR[1])
                release()
                Valpos[contatore]=0
                return

#-----INIZIO PROGRAMMA------------------------------------------------------------------------------------------------

reset()
txt.startCameraOnline()
Lampeggio(2.5)
ValposReset()
lamp.setLevel(Outmax)
User=False
Robot=False

while True:
    if(inputInizioR.state()==1):
        Robot=True
        break
    if(inputfinemossa.state()==1):
        User=True
        break

lamp.setLevel(Outmin)
if (Robot):
    #-------------------- Inizio prima fase gioco--------------------------------------------------------------------------------------
    for i in range(0,9):
        debug("Controllo Possibili Trie...")
        FPossibiliTria()
        if(Priorita==2 or Priorita==3):
            if(Priorita==2):
                debug("Blocco Tria nemica...")
                BloccoTriaU()
            elif(Priorita==3):
                debug("Svolgitura Tria...")
                SvolgiTria()
                TogliPallina()
        else:
            debug("Controllo Attacco")
            ControlloAttacco()
            if(Priorita!=3):
                debug("Controllo Difesa...")
                ControlloDifesa()
        if(Priorita==1):
            debug("Difesa...")
            Difesa()
        elif(Priorita==0):
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
    for i in range(0,9):
        #-------------------- Inizio prima fase gioco--------------------------------------------------------------------------------------
        ValposUpdate()
        Controlli()
        debug("Controllo Possibili Trie...")
        FPossibiliTria()
        if(Priorita==2 or Priorita==3):
            if(Priorita==2):
                debug("Blocco Tria nemica...")
                BloccoTriaU()
            elif(Priorita==3):
                debug("Svolgitura Tria...")
                SvolgiTria()
                TogliPallina()
        else:
            debug("Controllo Attacco")
            ControlloAttacco()
            if(Priorita!=3):
                debug("Controllo Difesa...")
                ControlloDifesa()
        if(Priorita==1):
            debug("Difesa...")
            Difesa()
        elif(Priorita==0):
            debug("Strategia...")
            Attacco()
        reset()
        lamp.setLevel(Outmax)
        AttendUser()
        lamp.setLevel(Outmin)
        time.sleep(0.5)
