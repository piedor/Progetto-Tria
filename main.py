#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Main program
"""

import sqlite3 as lite

if __name__ == "__main__":
    db = lite.connect("data.db")
    c = db.cursor()
    try:
        c.execute("SELECT val FROM Continue")
        rr = c.fetchall()
        for r in rr:
            if r[0] == "True":
                print("""E' stata riscontrata una partita non finita!
                      Vuoi continuare?Si->1 No->2""")
                r = input()
                if r == 2:
                    with db:
                        c.execute(
                            "UPDATE Continue SET val = 'False' WHERE val = 'True'")
    except BaseException:
        pass
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
