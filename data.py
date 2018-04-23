#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Modulo python data.py per lavorare con i database composto da due funzioni Insert e ReturnValue
"""

import sqlite3 as lite

db = lite.connect("data.db")
with db:
    c = db.cursor()


def Insert(name, val):
    "Inserisce un dato nel database dato il nome(str) e il valore(int,str,list)."
    with db:
        try:
            c.execute("DELETE FROM %s" % (name))
        except BaseException:
            pass
        c.execute("CREATE TABLE if not exists %s (val)" % (name))
        if isinstance(val, list):
            db.executemany(
                "INSERT INTO %s (val) VALUES (?)" %
                (name), [
                    (x,) for x in val])
        elif isinstance(val, str):
            val = (val,)
            db.execute("INSERT INTO %s (val) VALUES (?)" % (name), val)
        else:
            db.execute("INSERT INTO %s (val) VALUES (%d)" % (name, val))


def ReturnValue(name):
    "Ritorna i valori della tabella già esistente dato il nome."
    v = list()
    with db:
        c.execute("SELECT val FROM %s" % (name))
        rr = c.fetchall()
        if(len(rr) > 1):
            for r in rr:
                v.append(r[0])
            return(v)
        else:
            return([j for r in rr for j in r][0])
