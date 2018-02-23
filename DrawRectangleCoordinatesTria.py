import cv2

WHITE = [255, 255, 255]

# Coordinate posizioni immagine fotocamera
x_pos = [98,153,208,117,154,192,138,157,173,99,118,136,
         176,195,214,137,156,177,117,159,198,98,159,222]

y_pos = [70, 67, 64, 86, 82, 81, 102, 103, 100, 122, 122, 121,
         118, 116, 116, 139, 137, 136, 158, 157, 155, 180, 178, 172]

img = cv2.imread('img/TXTCamImg.jpg')
for x, y in zip(x_pos, y_pos):
    for x_off in range(0, 15):
        for y_off in range(0, 15):
            img[y + y_off, x + x_off] = WHITE

cv2.imshow("TXTCamImg", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
