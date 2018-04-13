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


def ReturnValue(name):
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
