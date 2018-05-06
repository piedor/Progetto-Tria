#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Modulo python opt.py il quale contiene tutte le variabili globali di Tria.py
"""

ValposOld = [0] * 24            # Array valori posizioni vecchie
CurrentX = 0                    # Coordinata X corrente
CurrentY = 0                    # Coordinata Y corrente
PosBloccoTriaU = []             # Posizione blocco tria utente
PosSvolgiTria = []              # Posizione completamento tria robot
Priorita = 0                    # Priorità mossa robot
AttaccoState = 0                # Stato strategia robot
ContatoreVPU = 0                # Contatore Valpos Update
PosPallineNuoveU = []           # Posizioni palline posizionate utente
PosDifesa = -1                  # Posizione difesa
Controllo = False               # Boolean controllo
TogliPallineR = False           # Boolean togli palline robot
TrieUtente = []                 # Array trie utente
TrieRobot = []                  # Array trie robot
PosAttacco = []                 # Posizione attacco
PosTogliPallina = []            # Posizione togli pallina
PosSpostaR = []                 # Posizioni possibili spostamento robot
PosSpostaU = []                 # Posizioni possibili spostamento utente
PosPallineRimosseU = []         # Array posizioni palline rimosse utente
PrioritaTR = False              # Boolean tria robot
PrioritaTU = False              # Boolean tria utente
Fase = 1                        # Variabile fase del gioco
User3F = False                  # Boolean utente 3 fase
PosTriaRSV = []                 # Array posizioni robot tria semi-vuota
TrieRSV = []                    # Array trie semi-vuote
