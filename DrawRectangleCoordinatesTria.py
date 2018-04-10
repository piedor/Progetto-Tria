import cv2

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = [101, 156, 213, 122, 160, 198, 143, 159, 179, 103, 120, 139, 179,
            200, 217, 141, 161, 180, 120, 163, 200, 101, 162, 223]

y_pos = [66, 62, 60, 80, 79, 78, 97, 97, 97, 119, 114, 117, 114, 112, 113,
           134, 134, 133, 155, 154, 152, 174, 172, 169]

img = cv2.imread('img/TXTCamImg.jpg')
for x, y in zip(x_pos, y_pos):
    for x_off in range(0, 15):
        for y_off in range(0, 15):
            img[y + y_off, x + x_off] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
