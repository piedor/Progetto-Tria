from data import data

OUTMAX = 512
OUTMIN = 0
XPOS = [
    1000,
    2665,
    4241,
    1610,
    2590,
    3720,
    2210,
    2665,
    3120,
    1000,
    1530,
    2210,
    3120,
    3720,
    4241,
    2080,
    2665,
    3120,
    1610,
    2665,
    3720,
    1000,
    2665,
    4241]
YPOS = [760, 760, 760, 1331, 1530, 1331, 2360, 2360, 2360, 3060, 3060, 3060,
        3060, 3060, 3060, 3786, 3786, 3786, 4607, 4607, 4607, 5391, 5391, 5391]
XPOSIMG = data.ReturnValue("XposIMG")
YPOSIMG = data.ReturnValue("YposIMG")
CAM_IMAGE = 'img/TXTCamImg.jpg'
IMAGE_ALIGNED = 'img/aligned.jpg'
SCIVOLOPALLINE = [120, 4140]
CONTENITOREPVR = [5025, 4308]
CONTENITOREPVU = [2635, 0]
STRATI = 4
EMPTY = 0
ROBOT = 1
USER = 2
for i in range(0, len(XPOSIMG)):
    XPOSIMG[i] -= STRATI
for i in range(0, len(YPOSIMG)):
    YPOSIMG[i] -= STRATI
MINDISTNBU = 6000
MINDISTRBR = 9000
VAL_TRIA_ROBOT = 111
VAL_TRIA_USER = 222
