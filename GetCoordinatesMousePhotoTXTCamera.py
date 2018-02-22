import cv2

SPACE_KEY = 1048608

nx = list()           # 'list' is easier to search than '[]'
ny = list()


def draw_circle(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        nx.append(x)
        ny.append(y)
        print(nx)
        print(ny)


img = cv2.imread("img/TXTCamImg.jpg")
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)

while True:
    cv2.imshow('image', img)
    k = cv2.waitKey(20)
    if k == SPACE_KEY:
        break
cv2.destroyAllWindows()
