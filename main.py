#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite

if __name__ == "__main__":
    db = lite.connect("data.db")
    c = db.cursor()
    c.execute("SELECT interrupt FROM Continue")
    rr = c.fetchall()
    for r in rr:
        if r[0] == "True":
            print("""E' stata riscontrata una partita non finita!
                  Vuoi continuare?Si->1 No->2""")
            r = input()
            if r == 2:
                with db:
                    c.execute(
                        "UPDATE Continue SET interrupt = 'False' WHERE interrupt = 'True'")
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
