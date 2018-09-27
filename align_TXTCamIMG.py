import time
import cv2
from vec import Vec2d
import numpy as np
import pickle


class Point(Vec2d):

    def __init__(self, x_or_pair, y=None):
        Vec2d.__init__(self, x_or_pair, y)

    def xy(self):
        return int(self.x), int(self.y)


SPACE_KEY = 1048608
VERBOSE = False
COLOR_RED = 0, 0, 255           # BGR !
COLOR_BLUE = 255, 0, 0
COLOR_GREEN = 0, 255, 0
POS_PICKLE_FILE = "data/pick_pos.txt"


def read_image(file):
    image = cv2.imread(file)
    return image


def show_image(image, title="main"):
    # Show image IMAGE in a window names (with title) TITLE
    cv2.imshow(title, image)


def write_image(image, file):
    cv2.imwrite(file, image)


def null_back(event, x, y, flags, param):
    # No-op mouse callback
    pass


def get_point(window):
    def back(event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN:
            out.append((x, y))
    out = list()
    cv2.setMouseCallback(window, back)
    while cv2.waitKey(10):
        if out:
            return Point(out[0])
    return None


def points_from_image(ima, count):
    for __ in range(count):
        show_image(ima, "main")
        p = get_point("main")
        yield p


def draw_dot(ima, center, radius=3, color=COLOR_RED):
    # Draw a filled circle on IMA at CENTER with radius RADIUS"
    cv2.circle(ima, center.xy(), radius, color, thickness=-1)


def pick_positions(ima, count):
    pp = list()
    if not count:
        return pp
    for i, p in enumerate(points_from_image(ima, count)):
        draw_dot(ima, p, radius=10, color=(0, 0, 255))
        show_image(ima)
        pp.append(p)
        if VERBOSE:
            print("Pos %d: %s" % (i, p))
    return pp


def middle_points(a, b, count=1):
    step = (b - a) / (count + 1)
    return [a + step * (i + 1) for i in range(count)]


def mid(a, b):
    return middle_points(a, b)[0]


def draw_points(image, pp, radius=5, color=COLOR_RED):
    for p in pp:
        draw_dot(image, p, radius=radius, color=color)


def inteporlate(tl, tr, bl, br):
    pp = list()
    pp.extend((mid(tl, tr),
               mid(tl, bl),
               mid(tr, br),
               mid(bl, br)))
    pp.extend(middle_points(tl, br, 5))
    pp.extend(middle_points(tr, bl, 5))
    return pp


def pp_to_array(pp):
    return np.array(pp, np.float32)


def make_matrix(pp, qq=None):
    if qq is None:
        qq = (Point(0, 0),
              Point(100, 0),
              Point(0, 100),
              Point(100, 100))

    return cv2.getPerspectiveTransform(
        pp_to_array(pp),
        pp_to_array(qq))


board = read_image("img/TXTCamImg.jpg")
try:
    with open(POS_PICKLE_FILE) as file:
        pp = pickle.load(file)
except Exception as e:
    print(e)
    with open(POS_PICKLE_FILE, "w") as file:
        pp = pick_positions(board, count=4)
        pickle.dump(pp, file)

tl, tr, bl, br = pp
qq = (tl,
      Point(tr.x, tl.y),
      Point(tl.x, bl.y),
      Point(tr.x, bl.y))
mat = make_matrix(pp, qq)

w = max(tr.x, br.x) + 100
h = max(bl.y, br.y) + 100
board = cv2.warpPerspective(board, mat, (w, h))

qq = pp_to_array(pp).dot(mat[:2, :2])
qq = [Point(p) for p in qq]
oo = inteporlate(*qq)

write_image(board, "img/aligned.jpg")
