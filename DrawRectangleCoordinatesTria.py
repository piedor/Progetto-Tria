import cv2

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = [101, 156, 213, 121, 157, 195, 139, 157,
         178, 101, 122, 139, 179, 198, 217, 139,
         160, 180, 121, 162, 200, 101, 160, 223]

y_pos = [72, 70, 66, 87, 84, 83, 104, 104,
         103, 124, 124, 123, 121, 119, 118, 140,
         140, 138, 161, 160, 156, 182, 180, 176]

img = cv2.imread('img/TXTCamImg.jpg')
for x, y in zip(x_pos, y_pos):
    for x_off in range(0, 15):
        for y_off in range(0, 15):
            img[y + y_off, x + x_off] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
