import cv2

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = [100, 155, 211, 119, 157, 195, 138, 157, 177, 101, 119, 140, 177,
           196, 215, 139, 160, 178, 120, 161, 203, 100, 163, 222]

y_pos = [67, 62, 60, 81, 79, 76, 99, 98, 97, 118, 118, 118, 115, 114, 113,
           135, 135, 133, 155, 154, 151, 175, 175, 169]

img = cv2.imread('img/TXTCamImg.jpg')
for x, y in zip(x_pos, y_pos):
    for x_off in range(0, 15):
        for y_off in range(0, 15):
            img[y + y_off, x + x_off] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
