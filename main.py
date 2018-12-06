#!/usr/bin/python
# -*- coding: utf-8 -*-

from settings import *
from tria import Tria
import cv2
import math
import random
import time
import pygame
from pygame.locals import *
import os
import sys

val_elem = [0] * 24
terne = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
         [21, 22, 23], [18, 19, 20],
         [15, 16, 17], [21, 9, 0], [18, 10, 3],
         [15, 11, 6], [2, 14, 23], [5, 13, 20],
         [8, 12, 17], [9, 10, 11], [
             16, 19, 22], [12, 13, 14],
         [1, 4, 7]]
vertici = [[0, 23], [2, 21], [3, 20],
           [5, 18], [6, 17], [8, 15]]
quadrati = [[0, 1, 2, 14, 23, 22, 21, 9], [
    3, 4, 5, 13, 20, 19, 18, 10], [6, 7, 8, 12, 17, 16, 15, 11]]
connettori = [[1, 4, 7], [14, 13, 12], [22, 19, 16], [9, 10, 11]]
pygame.init()
pygame.display.set_caption("Tria")
os.environ['SDL_VIDEO_CENTERED'] = '1'
clock = pygame.time.Clock()
infoDisplay = pygame.display.Info()
display_width, display_height = infoDisplay.current_w, infoDisplay.current_h


class Game():
    def __init__(self):
        self.tria = Tria()
        self.el_camera = ElabCamImg(self.tria)
        self.gui = Gui(self.tria)
        self.fase = 1
        self.partita_terminata = False
        self.val_terna1_mossa = 0
        self.val_terna2_mossa = 0
        self.val_terna1_mangiare = 0
        self.val_terna2_mangiare = 0
        self.pos_definited_mossa = -1
        self.pos_definited_mangiare = -1
        self.player = 0
        self.pos_libere = list()
        self.elem_robot = 8
        self.elem_user = 8
        self.trie_robot = list()
        self.trie_user = list()
        self.val_elem_precedente = [0] * 24
        self.user_can_mangia = False

    def set_init_player(self):
        self.tria.lamp.setLevel(OUTMAX)
        self.gui.set_init_player()
        self.player = self.gui.player
        self.tria.lamp.setLevel(OUTMIN)

    def change_turn(self):
        if self.player == ROBOT:
            self.player = USER
        elif self.player == USER:
            self.player = ROBOT

    def set_pos_libere(self):
        self.pos_libere = list()
        for i in range(0, 24):
            if val_elem[i] == EMPTY:
                self.pos_libere.append(i)

    def index_elements(self, arr, val):
        index_elements = list()
        for i in range(0, len(arr)):
            if arr[i] == val:
                index_elements.append(i)
        return(index_elements)

    def terne_pos(self, pos):
        t1 = list()
        t2 = list()
        for i in range(0, 16):
            if pos in terne[i]:
                if len(t1) == 0:
                    t1 = terne[i]
                else:
                    t2 = terne[i]
                    return(t1, t2)

    def valore_terna(self, t):
        val = list()
        val.extend(
            [val_elem[t[0]], val_elem[t[1]], val_elem[t[2]]])
        val.sort()
        return(val[0] * 100 + val[1] * 10 + val[2])

    def valori_terne_pos(self, pos):
        t1, t2 = self.terne_pos(pos)
        return(self.valore_terna(t1), self.valore_terna(t2))

    def vertice_opposto(self, v):
        index_v = -1
        for i in range(0, 6):
            if v in vertici[i]:
                index_v = vertici[i].index(v)
                if index_v == 0:
                    return(vertici[i][1])
                elif index_v == 1:
                    return(vertici[i][0])

    def b_common_element(self, arr1, arr2):
        if bool(set(arr1).intersection(arr2)):
            return(True)
        else:
            return(False)

    def vie_vertici_opposti(self, v, v_opp):
        t1v, t2v = self.terne_pos(v)
        t1v_opp, t2v_opp = self.terne_pos(v_opp)
        via1 = list()
        via2 = list()
        if self.b_common_element(t1v, t1v_opp):
            via1.append(t1v)
            via1.append(t1v_opp)
            via2.append(t2v)
            via2.append(t2v_opp)
        elif self.b_common_element(t1v, t2v_opp):
            via1.append(t1v)
            via1.append(t2v_opp)
            via2.append(t2v)
            via2.append(t1v_opp)
        return(via1, via2)

    def n_percorsi_liberi(self, v, v_opp):
        cont = 0
        via1, via2 = self.vie_vertici_opposti(
            v, v_opp)
        temp_val_v_opp = val_elem[v_opp]
        temp_val_v = val_elem[v]
        val_elem[v_opp] = 0
        val_elem[v] = 0
        if self.valore_terna(via1[0]) == 0 and self.valore_terna(via1[1]) == 0:
            cont += 1
        if self.valore_terna(via2[0]) == 0 and self.valore_terna(via2[1]) == 0:
            cont += 1
        val_elem[v_opp] = temp_val_v_opp
        val_elem[v] = temp_val_v
        return(cont)

    def b_tria_robot(self):
        if self.val_terna1_mossa == 111 or self.val_terna2_mossa == 111:
            return(True)
        else:
            return(False)

    def b_prevent_tria_user(self):
        if self.val_terna1_mossa == 122 or self.val_terna2_mossa == 122:
            return(True)
        else:
            return(False)

    def b_2_pairs_robot(self):
        if self.val_terna1_mossa == 11 and self.val_terna2_mossa == 11:
            return(True)
        else:
            return(False)

    def b_prevent_2_pairs_user(self):
        if self.val_terna1_mossa == 12 and self.val_terna2_mossa == 12:
            return(True)
        else:
            return(False)

    def b_vertice(self, pos):
        for i in range(0, 6):
            if pos in vertici[i]:
                return(True)
        return(False)

    def b_vertici_opposti_2_vie_robot(self, val_v_opp, npl):
        if val_v_opp == 1 and npl == 2:
            return(True)
        else:
            return(False)

    def b_prevent_vertici_opposti_2_vie_user(self, val_v_opp, npl):
        if val_v_opp == 2 and npl == 2:
            return(True)
        else:
            return(False)

    def b_vertici_opposti_1_via_robot(self, val_v_opp, npl):
        if val_v_opp == 1 and npl == 1:
            return(True)
        else:
            return(False)

    def b_prevent_vertici_opposti_1_via_user(self, val_v_opp, npl):
        if val_v_opp == 2 and npl == 1:
            return(True)
        else:
            return(False)

    def b_coppia_robot(self):
        if (self.val_terna1_mossa == 1 and self.val_terna2_mossa != 1) or (
                self.val_terna2_mossa == 1 and self.val_terna1_mossa != 1):
            return(True)
        else:
            return(False)

    def b_prevent_coppia_user(self):
        if (self.val_terna1_mossa == 2 and self.val_terna2_mossa != 2) or (
                self.val_terna2_mossa == 2 and self.val_terna1_mossa != 2):
            return(True)
        else:
            return(False)

    def val_mossa_fase_1(self, pos):
        val_elem[pos] = ROBOT
        self.val_terna1_mossa, self.val_terna2_mossa = self.valori_terne_pos(
            pos)
        val_elem[pos] = EMPTY
        if self.b_tria_robot():
            return(1000)
        elif self.b_prevent_tria_user():
            return(900)
        elif self.b_2_pairs_robot():
            return(800)
        elif self.b_prevent_2_pairs_user():
            return(700)
        elif self.b_vertice(pos):
            v_opp = self.vertice_opposto(pos)
            val_v_opp = val_elem[v_opp]
            npl = self.n_percorsi_liberi(
                pos, v_opp)
            if self.b_vertici_opposti_2_vie_robot(val_v_opp, npl):
                return(600)
            elif self.b_prevent_vertici_opposti_2_vie_user(val_v_opp, npl):
                return(500)
            elif self.b_vertici_opposti_1_via_robot(val_v_opp, npl):
                return(400)
            elif self.b_prevent_vertici_opposti_1_via_user(val_v_opp, npl):
                return(300)
        elif self.b_coppia_robot():
            return(200)
        elif self.b_prevent_coppia_user():
            return(100)
        return(50)

    def val_mosse_fase_1(self):
        self.set_pos_libere()
        val_mosse_pos = [0] * 24
        for i in self.pos_libere:
            val_mosse_pos[i] = self.val_mossa_fase_1(
                i)
        return(val_mosse_pos)

    def mossa_robot_fase_1(self):
        val_fase_1 = self.val_mosse_fase_1()
        val_max = max(val_fase_1)
        pos_max = self.index_elements(
            val_fase_1, val_max)
        self.pos_definited_mossa = random.choice(pos_max)
        self.tria.aggiungi_pallina(
            XPOS[self.pos_definited_mossa], YPOS[self.pos_definited_mossa])
        val_elem[self.pos_definited_mossa] = ROBOT

    def set_trie(self, trie):
        if self.player == ROBOT:
            self.trie_robot = trie
        else:
            self.trie_user = trie

    def b_new_tria(self):
        val_tria = 0
        terna1 = list()
        terna2 = list()
        trie = list()
        if self.player == ROBOT:
            terna1, terna2 = self.terne_pos(self.pos_definited_mossa)
            val_tria = VAL_TRIA_ROBOT
            trie = self.trie_robot
        else:
            terna1, terna2 = self.terne_pos(self.el_camera.pos_modified)
            val_tria = VAL_TRIA_USER
            trie = self.trie_user
        if self.valore_terna(terna1) == val_tria and terna1 not in trie:
            trie.append(terna1)
            self.set_trie(trie)
            return(True)
        elif self.valore_terna(terna1) != val_tria and terna1 in trie:
            trie.remove(terna1)
        elif self.valore_terna(terna2) == val_tria and terna2 not in trie:
            trie.append(terna2)
            self.set_trie(trie)
            return(True)
        elif self.valore_terna(terna2) != val_tria and terna2 in trie:
            trie.remove(terna2)
        self.set_trie(trie)
        return(False)

    def pos_adiacenti(self, pos):
        pos_x = -1
        pos_y = -1
        pos_adiacenti = list()
        for i in quadrati:
            if pos in i:
                pos_x = quadrati.index(i)
                pos_y = i.index(pos)
        if pos_y == 0:
            pos_adiacenti.append(quadrati[pos_x][7])
            pos_adiacenti.append(quadrati[pos_x][pos_y + 1])
        elif pos_y == 7:
            pos_adiacenti.append(quadrati[pos_x][pos_y - 1])
            pos_adiacenti.append(quadrati[pos_x][0])
        else:
            pos_adiacenti.append(quadrati[pos_x][pos_y - 1])
            pos_adiacenti.append(quadrati[pos_x][pos_y + 1])
        for i in connettori:
            if pos in i:
                index = i.index(pos)
                if index == 1:
                    pos_adiacenti.append(i[0])
                    pos_adiacenti.append(i[2])
                else:
                    pos_adiacenti.append(i[1])
        return(pos_adiacenti)

    def b_muovibile(self, pos):
        for i in self.pos_adiacenti(pos):
            if val_elem[i] == EMPTY:
                return(True)
        return(False)

    def b_bloccato(self, player):
        for i in range(0, 24):
            if val_elem[i] == player:
                if self.b_muovibile(i):
                    return(False)
        return(True)

    def b_pos_user_appartiene_a_una_tria(self, pos):
        if self.valori_terne_pos(pos)[0] == VAL_TRIA_USER or self.valori_terne_pos(pos)[
                1] == VAL_TRIA_USER:
            return(True)
        return(False)

    def elem_user_non_tria(self):
        elem = list()
        for i in range(0, 24):
            if val_elem[i] == USER and not self.b_pos_user_appartiene_a_una_tria(
                    i):
                elem.append(i)
        return(elem)

    def elem_user_mangiabili(self):
        return(self.elem_user_non_tria())

    def b_avoid_tria_user(self):
        if self.val_terna1_mangiare == 2 or self.val_terna2_mangiare == 2:
            return(True)
        return(False)

    def b_allow_tria_robot(self):
        if self.val_terna1_mangiare == 11 or self.val_terna2_mangiare == 11:
            return(True)
        return(False)

    def val_elem_mangiabile(self, pos):
        val_elem[pos] = EMPTY
        self.val_terna1_mangiare, self.val_terna2_mangiare = self.valori_terne_pos(
            pos)
        val_elem[pos] = USER
        if self.b_avoid_tria_user():
            return(1000)
        elif self.b_allow_tria_robot():
            return(900)
        return(50)

    def val_elem_mangiabili(self, vett):
        val = [0] * 24
        for i in vett:
            val[i] = self.val_elem_mangiabile(i)
        return(val)

    def mangia_elem_user(self):
        elem_mangiabili = self.elem_user_mangiabili()
        val_elem_mangiabili = self.val_elem_mangiabili(elem_mangiabili)
        val_max = max(val_elem_mangiabili)
        pos_max = self.index_elements(val_elem_mangiabili, val_max)
        self.pos_definited_mangiare = random.choice(pos_max)
        self.tria.rimuovi_pallina(
            XPOS[self.pos_definited_mangiare], YPOS[self.pos_definited_mangiare])
        val_elem[self.pos_definited_mangiare] = EMPTY

    def allow_user_mangia(self):
        print("Puoi mangiare una pallina del robot")
        self.tria.attendi_utente()
        self.user_can_mangia = True
        self.controlli_user()
        self.user_can_mangia = False

    def controlli_user(self):
        errore = False
        pos_new_user_elements = list()
        pos_removed_robot_elements = list()
        if self.fase == 1:
            pos_new_user_elements = self.el_camera.new_elements_user
            if len(pos_new_user_elements) == 0:
                self.gui.showInfo("Non hai posizionato alcuna pallina")
                print("Non hai posizionato alcuna pallina")
                errore = True
            elif len(pos_new_user_elements) > 1:
                self.gui.showInfo("Hai posizionato più palline")
                print(
                    "Hai posizionato",
                    len(pos_new_user_elements),
                    "palline nelle posizioni:",
                    pos_new_user_elements,
                    "rimuovine",
                    len(pos_new_user_elements) - 1)
                errore = True

            pos_removed_robot_elements = self.el_camera.removed_elements_robot
            if len(pos_removed_robot_elements) > 0 and not self.user_can_mangia:
                self.gui.showInfo("Hai rimosso delle palline del robot")
                print(
                    "Hai rimosso",
                    len(pos_removed_robot_elements),
                    "palline del robot nelle posizioni:",
                    pos_removed_robot_elements,
                    "rimettile a posto tutte")
                errore = True
            elif self.user_can_mangia:
                if len(pos_removed_robot_elements) == 0:
                    self.gui.showInfo(
                        "Non hai rimosso alcuna pallina del robot")
                    print("Non hai rimosso alcuna pallina del robot")
                    errore = True
                elif len(pos_removed_robot_elements) > 1:
                    self.gui.showInfo("Hai rimosso più palline del robot")
                    print(
                        "Hai rimosso",
                        len(pos_removed_robot_elements),
                        "palline del robot nelle posizioni:",
                        pos_removed_robot_elements,
                        "puoi rimuoverne solo 1 quindi rimetti a posto le altre")
                    errore = True
                elif len(pos_removed_robot_elements) == 1:
                    for i in self.trie_robot:
                        if pos_removed_robot_elements[0] in i:
                            self.gui.showInfo(
                                "Hai rimosso una pallina che fà parte di una tria del robot")
                            print(
                                "Hai rimosso una pallina del robot che fà parte di una tria")
                            errore = True
                            break
        if errore:
            self.tria.attendi_utente()
            self.el_camera.check_new_or_removed_elements()
            self.controlli_user()
        else:
            for i in pos_new_user_elements:
                val_elem[i] = USER
            for i in pos_removed_robot_elements:
                val_elem[i] = EMPTY
            for i in self.el_camera.removed_elements_user:
                val_elem[i] = EMPTY

    def change_fase(self):
        if self.fase == 1:
            if self.player == ROBOT:
                self.elem_robot -= 1
            else:
                self.elem_user -= 1
            if self.elem_robot == 0 and self.elem_user == 0:
                self.fase = 2
                print("Numero trie robot: ", len(self.trie_robot))
                print("Numero trie utente: ", len(self.trie_user))
                if(len(self.trie_robot) > len(self.trie_user)):
                    self.gui.showInfo("Ha vinto il robot")
                    print("Ha vinto il robot")
                else:
                    self.gui.showInfo("Ha vinto l'utente")
                    print("Ha vinto l'utente")
                time.sleep(2000)
                self.partita_terminata = True

    def set_partita_terminata(self, value):
        self._partita_terminata = value

    def get_partita_terminata(self):
        return(self._partita_terminata)
    partita_terminata = property(
        get_partita_terminata, set_partita_terminata)

    def run(self):
        while true:
            self.set_init_player()
            self.el_camera.val_pos_camera_update()
            self.gui.runBoard()
            while not self.partita_terminata:
                if self.player == ROBOT:
                    self.gui.showInfo("Robot sta effettuando mossa...")
                    if self.fase == 1:
                        self.mossa_robot_fase_1()
                elif self.player == USER:
                    self.gui.showInfo("Tocca a te!")
                    self.tria.attendi_utente()
                    self.el_camera.check_new_or_removed_elements()
                    self.controlli_user()
                if self.b_new_tria():
                    if self.player == ROBOT:
                        self.gui.showInfo("Il robot stà mangiando...")
                        self.mangia_elem_user()
                    else:
                        self.gui.showInfo(
                            "Puoi mangiare una pallina del robot")
                        self.allow_user_mangia()
                self.tria.reset()
                self.el_camera.val_pos_camera_update()
                self.change_fase()
                self.change_turn()
                for i in range(0, 24):
                    self.val_elem_precedente[i] = val_elem[i]


class ElabCamImg():
    def __init__(self, Tria):
        self.val_pos_camera_b = [0] * 24
        self.val_pos_camera_g = [0] * 24
        self.val_pos_camera_r = [0] * 24
        self.pos_modified = -1
        self.tria = Tria
        self.new_elements_user = list()
        self.removed_elements_user = list()
        self.removed_elements_robot = list()

    def val_pos_camera_update(self):
        self.tria.scrivi_img_camera()
        exec(
            open("align_TXTCamImg.py").read(), globals())
        self.val_pos_camera_b = [
            self.rgb_pos(i)[0] for i in range(24)]
        self.val_pos_camera_g = [
            self.rgb_pos(i)[1] for i in range(24)]
        self.val_pos_camera_r = [
            self.rgb_pos(i)[2] for i in range(24)]

    def rgb_pos(self, pos):
        img = cv2.imread(IMAGE_ALIGNED, 1)
        blue = 0
        green = 0
        red = 0
        for j in range(0, (STRATI * 2) + 1):
            for k in range(0, (STRATI * 2) + 1):
                b, g, r = img[int(YPOSIMG[pos] + k),
                              int(XPOSIMG[pos] + j)]
                blue += b
                green += g
                red += r
        return(blue, green, red)

    def math_distance(self, p1, p2):
        return(math.sqrt(math.pow(p1 - p2, 2)))

    def b_val_pos_camera_higher(self, pos, val):
        blue = self.rgb_pos(pos)[0]
        green = self.rgb_pos(pos)[1]
        red = self.rgb_pos(pos)[2]
        if self.math_distance(
                self.val_pos_camera_b[pos],
                blue) + self.math_distance(
                self.val_pos_camera_g[pos],
                green) + self.math_distance(
                self.val_pos_camera_r[pos],
                red) > val:
            return True
        else:
            return False

    def check_new_or_removed_elements(self):
        self.new_elements_user = list()
        self.removed_elements_user = list()
        self.removed_elements_robot = list()
        self.tria.scrivi_img_camera()
        exec(
            open("align_TXTCamImg.py").read(), globals())
        for i in range(0, 24):
            if self.b_val_pos_camera_higher(
                    i, MINDISTNBU) and val_elem[i] == EMPTY:
                self.new_elements_user.append(i)
                self.pos_modified = i
                print(
                    "pallina utente nella posizione ", i)
            elif self.b_val_pos_camera_higher(i, MINDISTNBU) and val_elem[i] == USER:
                self.removed_elements_user.append(i)
                print(
                    "pallina utente rimossa dalla posizione ", i)
            elif self.b_val_pos_camera_higher(
                    i, MINDISTRBR) and val_elem[i] == ROBOT:
                self.removed_elements_robot.append(i)
                print(
                    "pallina robot rimossa dalla posizione ", i)


class Gui():
    def __init__(self, tria):
        self.tria = tria
        self.bg = pygame.image.load("img/back.png")
        self.bgBoard = pygame.image.load("img/back2.png")
        self.bgBoard = pygame.transform.scale(self.bgBoard, (2000, 1000))
        self.bg_width, self.bg_height = self.bg.get_size()
        self.bgBoard_width, self.bgBoard_height = self.bgBoard.get_size()
        self.bg_center_x, self.bg_center_y = self.bg_width / 2, self.bg_height / 2
        self.bgBoard_center_x, self.bgBoard_center_y = self.bgBoard_width / \
            2, self.bgBoard_height / 2
        self.screen = pygame.display.set_mode(
            (display_width, display_height), 0, 32)
        self.surface = pygame.Surface(self.screen.get_size()).convert()
        self.menu = MAIN_MENU
        self.index = 0
        self.text_view_array = list()
        self.player = 0
        self.numeroTrieRobot = 0
        self.numeroTrieUtente = 0

    def incrementaTrieRobot(self):
        self.numeroTrieRobot += 1

    def incrementaTrieUtente(self):
        self.numeroTrieUtente += 1

    def show_menu(self, dict):
        TextView(self.surface, display_width /
                 2, 80, "impact", 80, (255, 0, 0), list(dict.keys())[0])
        self.text_view_array = list()
        nArgs = len(dict)
        if self.index > nArgs - 2:
            self.index = 0
        counter = 0

        for i in range(1, len(dict)):
            if list(dict.values())[i] != "BK":
                b = TextView(self.surface, display_width /
                             2, (display_height -
                                 (nArgs -
                                  1) *
                                 100) /
                             nArgs +
                             100 *
                             (counter +
                                 1), "Verdana", 40, (255, 255, 255), list(dict.keys())[i])
            else:
                b = TextView(self.surface, (display_width /
                                            2) +
                             300, (display_height -
                                   (nArgs -
                                    1) *
                                   100) /
                             nArgs +
                             100 *
                             (counter +
                              1) +
                             250, "Verdana", 40, (255, 255, 255), list(dict.keys())[i])
            if counter == self.index:
                b.set_hover()
            b.set_id(list(dict.values())[i])
            self.text_view_array.append(b)
            counter += 1

    def select_listener(self):
        if self.tria.in_select.state():
            self.index += 1
            pygame.time.wait(200)

    def start_listener(self):
        if self.tria.in_start.state():
            button_id = self.text_view_array[self.index].get_id()
            if button_id == "NP":
                self.menu = INIT_PLAYER_MENU
            elif button_id == "LN":
                self.menu = LANGUAGES_MENU
            elif button_id == "UT":
                self.player = USER
            elif button_id == "RT":
                self.player = ROBOT
            elif button_id == "BK":
                self.menu = MAIN_MENU
            pygame.time.wait(200)

    def set_init_player(self):
        while not self.player:
            self.runMenu()

    def showInfo(self, text):
        self.surface.fill((0, 0, 0))
        TextView(self.surface, display_width / 2, display_height /
                 2, "Verdana", 40, (255, 255, 255), text)
        self.updateScreen()

    def updateBoard(self):
        TextView(self.surface, 100, 50, "Verdana", 40, (0, 0, 255), "Robot")
        TextView(self.surface, 300, 50, "Verdana", 40, (0, 0, 255), "Utente")
        TextView(self.surface, 100, 100, "Verdana", 40,
                 (0, 0, 0), str(self.numeroTrieRobot))
        TextView(self.surface, 300, 100, "Verdana", 40,
                 (0, 0, 0), str(self.numeroTrieUtente))
        for i in range(0, 24):
            if val_elem[i] == ROBOT:
                pygame.draw.circle(
                    self.surface, (105, 105, 105), (XPOSBOARD[i], YPOSBOARD[i]), 20)
            elif val_elem[i] == USER:
                pygame.draw.circle(
                    self.surface, (0, 0, 255), (XPOSBOARD[i], YPOSBOARD[i]), 20)

    def runMenu(self):
        self.surface.fill((40, 40, 40))
        self.surface.blit(self.bg,
                          ((display_width / 2) - (self.bg_width - self.bg_center_x),
                           (display_height / 2) - (self.bg_height - self.bg_center_y)))

        self.show_menu(self.menu)
        self.select_listener()
        self.start_listener()
        self.updateScreen()

    def runBoard(self):
        self.surface.fill((255, 255, 255))
        self.surface.blit(self.bgBoard, ((display_width /
                                          2) -
                                         (self.bgBoard_width -
                                          self.bgBoard_center_x), (display_height /
                                                                   2) -
                                         (self.bgBoard_height -
                                          self.bgBoard_center_y)))

        self.surface.blit(self.bg,
                          ((display_width / 2) - (self.bg_width - self.bg_center_x),
                           (display_height / 2) - (self.bg_height - self.bg_center_y)))
        self.updateBoard()
        self.updateScreen()

    def updateScreen(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()
        clock.tick(30)


class TextView():
    def __init__(self, surface, posX, posY, font, size, color, text):
        self.posX = posX
        self.posY = posY
        self.font = pygame.font.SysFont(font, size)
        self.text = text
        self.color = color
        self.surface = surface
        self.id = ""
        self.show_on_surface(self.color)

    def show_on_surface(self, color):
        text = self.font.render(self.text, 1, color)
        textpos = text.get_rect()
        textpos.centerx = self.posX
        textpos.centery = self.posY
        self.surface.blit(text, textpos)

    def set_hover(self):
        self.show_on_surface((0, 0, 255))

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return(self.id)


game = Game()
game.run()
