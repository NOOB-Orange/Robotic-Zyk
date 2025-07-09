import cv2
from Version.Detect_red import detect_red_target
from Robotic.arm_control_move import move_with_offset

# 1️⃣ 设置摄像头中心坐标（校准后填入）
FRAME_CENTER_X = 320
FRAME_CENTER_Y = 240

# 2️⃣ 机械臂初始位置（mm）
current_x = 100.0
current_y = 100.0

# 3️⃣ 每次偏移比例（调节灵敏度）
OFFSET_SCALE = 0.05  # 越小越平滑

# 4️⃣ 限制活动范围
X_MIN, X_MAX = 90.0, 110.0
Y_MIN, Y_MAX = 90.0, 110.0

def main():
    global current_x, current_y

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = detect_red_target(frame)

        if result is not None:
            cx, cy = result

            dx = (cx - FRAME_CENTER_X) * OFFSET_SCALE
            dy = (cy - FRAME_CENTER_Y) * OFFSET_SCALE

            print(f"[INFO] 检测到红色：X={cx}, Y={cy}, 偏移 dx={dx:.2f}, dy={dy:.2f}")

            # 更新目标坐标
            current_x -= dx
            current_y -= dy

            # 限定在安全活动范围
            current_x = max(min(current_x, X_MAX), X_MIN)
            current_y = max(min(current_y, Y_MAX), Y_MIN)

            move_with_offset(current_x, current_y)

        cv2.imshow("Red Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
