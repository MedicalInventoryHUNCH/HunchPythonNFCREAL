import cv2

cap = cv2.VideoCapture(0)


ret, frame = cap.read()
if not ret:
    exit(":(")

cv2.imwrite("pictures/face7.jpg", frame)
exit()
