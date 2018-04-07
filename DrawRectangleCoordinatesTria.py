import cv2

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = [105, 159, 217, 125, 161, 199, 144, 163, 181, 105, 123, 144, 183, 201,
          220, 144, 164, 184, 123, 162, 203, 105, 165, 226]

y_pos = [69, 67, 64, 84, 82, 81, 101, 102, 100, 121, 121, 121, 118, 118, 117, 139,
         139, 137, 159, 158, 156, 179, 177, 173]

img = cv2.imread('img/TXTCamImg.jpg')
for x, y in zip(x_pos, y_pos):
    for x_off in range(0, 15):
        for y_off in range(0, 15):
            img[y + y_off, x + x_off] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
