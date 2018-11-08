#!/usr/bin/python
# -*- coding: utf-8 -*-

from settings import *
from tria import Tria
import cv2
import math
import random
import time

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


class Game():
    def __init__(self):
        self.Tria = Tria()
        self.el_camera = ElabCamImg(self.Tria)
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
        print("Chi comincia? Tu(down) Robot(up)")
        self.Tria.lamp.setLevel(OUTMAX)
        while True:
            if self.Tria.in_finemossa.state():
                self.player = USER
                break
            elif self.Tria.in_inizioR.state():
                self.player = ROBOT
                break
        self.Tria.lamp.setLevel(OUTMIN)
        time.sleep(1)

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
        self.Tria.aggiungi_pallina(
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
        self.Tria.rimuovi_pallina(
            XPOS[self.pos_definited_mangiare], YPOS[self.pos_definited_mangiare])
        val_elem[self.pos_definited_mangiare] = EMPTY

    def allow_user_mangia(self):
        print("Puoi mangiare una pallina del robot")
        self.Tria.attendi_utente()
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
                print("Non hai posizionato alcuna pallina")
                errore = True
            elif len(pos_new_user_elements) > 1:
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
                print(
                    "Hai rimosso",
                    len(pos_removed_robot_elements),
                    "palline del robot nelle posizioni:",
                    pos_removed_robot_elements,
                    "rimettile a posto tutte")
                errore = True
            elif self.user_can_mangia:
                if len(pos_removed_robot_elements) == 0:
                    print("Non hai rimosso alcuna pallina del robot")
                    errore = True
                elif len(pos_removed_robot_elements) > 1:
                    print(
                        "Hai rimosso",
                        len(pos_removed_robot_elements),
                        "palline del robot nelle posizioni:",
                        pos_removed_robot_elements,
                        "puoi rimuoverne solo 1 quindi rimetti a posto le altre")
                    errore = True
        if errore:
            self.Tria.attendi_utente()
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
                print("fase 2")

    def set_partita_terminata(self, value):
        self._partita_terminata = value

    def get_partita_terminata(self):
        return(self._partita_terminata)
    partita_terminata = property(
        get_partita_terminata, set_partita_terminata)

    def run(self):
        self.set_init_player()
        self.el_camera.val_pos_camera_update()
        while not self.partita_terminata:
            if self.player == ROBOT:
                if self.fase == 1:
                    self.mossa_robot_fase_1()
            elif self.player == USER:
                self.Tria.attendi_utente()
                self.el_camera.check_new_or_removed_elements()
                self.controlli_user()
            if self.b_new_tria():
                if self.player == ROBOT:
                    self.mangia_elem_user()
                else:
                    self.allow_user_mangia()
            self.Tria.reset()
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
        self.Tria = Tria
        self.new_elements_user = list()
        self.removed_elements_user = list()
        self.removed_elements_robot = list()

    def val_pos_camera_update(self):
        self.Tria.scrivi_img_camera()
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
        self.Tria.scrivi_img_camera()
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


game = Game()
while True:
    game.run()
