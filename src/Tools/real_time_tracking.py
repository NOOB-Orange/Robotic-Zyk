import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Version.Detect_red import detect_red_target
from Robotic.arm_control_move import move_with_offset, initialize_serial, move_stop, query_current_position

import cv2
import threading
import time

# 中心
FRAME_CENTER_X = 320
FRAME_CENTER_Y = 240

# 固定 Z 高度
current_z = 417.4

# 控制参数
OFFSET_SCALE = 8       # 平滑偏移比例
DEAD_ZONE = 1.0         # 死区避免抖动
MAX_STEP = 50           # 每次最大移动 50mm

# 控制标志
exit_flag = False
latest_target = [None, None]
move_lock = threading.Lock()

def tracking_thread(ser):
    global latest_target, exit_flag

    while not exit_flag:
        if latest_target[0] is None:
            time.sleep(0.01)
            continue

        try:
            with move_lock:
                x_now, y_now, _ = query_current_position(ser)

                dx = (latest_target[0] - FRAME_CENTER_X) * OFFSET_SCALE
                dy = (latest_target[1] - FRAME_CENTER_Y) * OFFSET_SCALE

                if abs(dx) < DEAD_ZONE and abs(dy) < DEAD_ZONE:
                    continue

                dx = max(min(dx, MAX_STEP), -MAX_STEP)
                dy = max(min(dy, MAX_STEP), -MAX_STEP)

                # ✅ 无限制直接累加
                target_x = x_now + dx
                target_y = y_now + dy

                print(f"[跟踪] 当前: ({x_now:.2f}, {y_now:.2f}) → 目标: ({target_x:.2f}, {target_y:.2f})")

                move_with_offset(target_x, target_y, current_z, ser)

        except Exception as e:
            print(f"[错误] 追踪失败: {e}")

        time.sleep(0.05)

def main():
    global exit_flag, latest_target

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ser = initialize_serial()
    print("[提示] 启动成功。按 'q' 退出程序。")

    tracker = threading.Thread(target=tracking_thread, args=(ser,))
    tracker.start()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[错误] 摄像头读取失败")
                break

            result = detect_red_target(frame)
            if result:
                cx, cy = result
                latest_target = [cx, cy]
                cv2.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)

            # 中心辅助线
            cv2.line(frame, (FRAME_CENTER_X - 50, FRAME_CENTER_Y), (FRAME_CENTER_X + 50, FRAME_CENTER_Y), (0, 255, 0), 1)
            cv2.line(frame, (FRAME_CENTER_X, FRAME_CENTER_Y - 50), (FRAME_CENTER_X, FRAME_CENTER_Y + 50), (0, 255, 0), 1)

            cv2.imshow("Red Tracker", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        print("[提示] 正在退出...")
        exit_flag = True
        time.sleep(0.3)
        move_stop(ser)
        cap.release()
        ser.close()
        cv2.destroyAllWindows()
        print("[提示] 已安全退出。")

if __name__ == "__main__":
    main()
