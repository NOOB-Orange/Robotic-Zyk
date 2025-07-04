import cv2
import numpy as np

# 摄像头初始化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 红色HSV阈值
lower_red1 = np.array([0, 120, 150])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 120, 150])
upper_red2 = np.array([180, 255, 255])

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    target_center = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000 and area > max_area:  # 只取最大面积
            max_area = area
            x, y, w, h = cv2.boundingRect(cnt)
            center_x, center_y = x + w // 2, y + h // 2
            target_center = (center_x, center_y)

    if target_center:
        cv2.circle(frame, target_center, 10, (0, 255, 0), -1)
        cv2.putText(frame, f"Center: {target_center}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        print(f"Detected Red Target at: {target_center}")

    cv2.imshow('Target Detection', frame)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
