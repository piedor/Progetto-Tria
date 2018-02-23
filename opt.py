#!/usr/bin/python
# -*- coding: utf-8 -*-

ValposOld = [0] * 24
CurrentX = 0                    # Coordinata X corrente
CurrentY = 0                    # Coordinata Y corrente
PosBloccoTriaU = []             # Posizione blocco tria utente
PosSvolgiTria = []              # Posizione completamento tria robot
Priorita = 0                    # Priorità mossa robot
AttaccoState = 0                # Stato strategia robot
ContatoreVPU = 0                # Contatore Valpos Update
PosPallineNuoveU = []           # Posizioni palline posizionate utente
PosDifesa = 0                   # Posizione difesa
Controllo = False               # Boolean controllo
TogliPallineR = False
TrieUtente = []
PosAttacco = []                 # Posizione attacco
PosTogliPallina = []            # Posizione togli pallina
PPTU=[]
