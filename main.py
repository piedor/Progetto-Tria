#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Main program
"""

import data

if __name__ == "__main__":
    if not (data.ReturnValue("XposIMG") or data.ReturnValue("YposIMG")):
        import GetCoordinatesMousePhotoTXTCamera
    if data.ReturnValue("Continue") == "True":
        print("""E' stata riscontrata una partita non finita!
              Vuoi continuare?Si->1 No->2""")
        r = input()
        if r == 2:
            data.Insert("Continue", 'False')
    try:
        import Tria
    except BaseException:
        stop = False
        while not stop:
            try:
                stop = True
                import Tria
            except BaseException:
                stop = False
