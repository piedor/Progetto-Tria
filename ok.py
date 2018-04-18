import Tria

Tria.TRIA=Tria.SplitList(Tria.TRIA,3)
Tria.opt.ValposOld=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Tria.Val=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

Pos=0
Pos2=0
PosOld=-1
i=0
while Pos!=23:
    Pos=Tria.PosSposta(Pos2)[i]
    while Pos==PosOld:
        i+=1
        Pos=Tria.PosSposta(Pos2)[i]
    i=0
    PosOld=Pos2
    Pos2=Pos
    print(Pos)

Pos=0
Pos2=0
PosOld=-1
i=0
