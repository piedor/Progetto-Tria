import sqlite3 as lite

db = lite.connect("data.db")
with db:
    c = db.cursor()


def Insert(name, val):
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


def Print(name):
    with db:
        c.execute("SELECT val FROM %s" % (name))
        rr = c.fetchall()
        for r in rr:
            print(r[0])
