# main.py
import cv2
from Version.Detect_red import detect_red_target
from Robotic.arm_control_move import move_with_offset, initialize_serial, move_stop

# 1. 摄像头中心坐标
FRAME_CENTER_X = 320
FRAME_CENTER_Y = 240

# 2. 机械臂初始坐标（建议你根据实际位置调整）
current_x = 344.1
current_y = 0.7
current_z = 417.4  # 固定高度，防止撞到工作台

# 3. 灵敏度与死区
OFFSET_SCALE = 0.05  # 每像素偏移对应的坐标变化
DEAD_ZONE = 2.0      # 死区大小，防止抖动

# 4. 限定范围
X_MIN, X_MAX = 340.0, 350.0
Y_MIN, Y_MAX = -10.0, 10.0


def main():
    global current_x, current_y

    # 打开摄像头
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 初始化串口
    ser = initialize_serial()

    print("[提示] 确保机械臂前方无障碍物。按 'q' 键随时退出程序。")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[警告] 无法读取摄像头画面")
                break

            result = detect_red_target(frame)

            if result is not None:
                cx, cy = result

                dx = (cx - FRAME_CENTER_X) * OFFSET_SCALE
                dy = (cy - FRAME_CENTER_Y) * OFFSET_SCALE

                print(f"[INFO] 红色坐标: ({cx}, {cy}), 偏移: dx={dx:.2f}, dy={dy:.2f}")

                # 死区判断
                if abs(dx) < DEAD_ZONE and abs(dy) < DEAD_ZONE:
                    continue

                # ✅ 方向修正：红点向右，机械臂向右
                current_x += dx
                current_y += dy

                # 限制在安全工作范围
                current_x = max(min(current_x, X_MAX), X_MIN)
                current_y = max(min(current_y, Y_MAX), Y_MIN)

                # 执行移动
                move_with_offset(current_x, current_y, current_z, ser)

            # 显示检测画面
            cv2.imshow("Red Detection", frame)

            # 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        move_stop(ser)
        ser.close()
        cv2.destroyAllWindows()
        print("[提示] 已安全关闭程序。")


if __name__ == "__main__":
    main()
