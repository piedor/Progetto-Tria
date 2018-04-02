#!/usr/bin/python
# -*- coding: utf-8 -*-

if __name__ == "__main__":
    f = open("data.txt", "r")
    d = f.read()
    d = d.split()
    f.close()
    if d[0] == "False":
        print("""E' stata riscontrata una partita non finita!
              Vuoi continuare?Si->1 No->2""")
        r = input()
    try:
        import Tria.py
    except BaseException:
        stop = False
        while not stop:
            try:
                stop = True
                import Tria.py
            except BaseException:
                stop = False
