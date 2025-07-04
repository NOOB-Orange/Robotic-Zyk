import cv2

# 打开摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("摄像头无法打开")
    exit()

# 创建跟踪器对象（KCF、CSRT、MOSSE 等可选）
tracker = cv2.TrackerKCF_create()

# 初始化状态
initBB = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 如果已经初始化了目标 → 开始跟踪
    if initBB is not None:
        success, box = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            center_x, center_y = x + w // 2, y + h // 2

            # 绘制跟踪框
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)

            cv2.putText(frame, f"Target: ({center_x}, {center_y})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Tracking", frame)

    key = cv2.waitKey(1) & 0xFF

    # 按 's' 键选择目标
    if key == ord('s'):
        initBB = cv2.selectROI("Tracking", frame, fromCenter=False, showCrosshair=True)
        tracker.init(frame, initBB)

    # 按 'q' 退出
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
