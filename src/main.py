import cv2
import threading
import time
from Version.Detect_red import detect_red_target
from Robotic.arm_control_move import move_with_offset, initialize_serial, move_stop, query_current_position

# 摄像头中心
FRAME_CENTER_X = 320
FRAME_CENTER_Y = 240

# 固定Z轴高度
current_z = 417.4

# 控制参数
OFFSET_SCALE = 20
DEAD_ZONE = 0.5
MAX_STEP = 300
MOVE_INTERVAL = 3

# 🚨 安全范围（扩大 X轴 范围！）
X_MIN, X_MAX = 300.0, 380.0
Y_MIN, Y_MAX = -30.0, 30.0

# 控制线程锁和退出标志
move_lock = threading.Lock()
exit_flag = False  # ✅ 程序退出标志

def main():
    global exit_flag
    frame_count = 0

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ser = initialize_serial()
    print("[提示] 确保机械臂前方无障碍物。按 'q' 键退出。")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[警告] 无法读取摄像头")
                break

            frame_count += 1

            result = detect_red_target(frame)
            if result is not None:
                cx, cy = result
                print(f"[DEBUG] 检测到红点: {cx}, {cy}")

                dx = (cx - FRAME_CENTER_X) * OFFSET_SCALE
                dy = (cy - FRAME_CENTER_Y) * OFFSET_SCALE

                dx = max(min(dx, MAX_STEP), -MAX_STEP)
                dy = max(min(dy, MAX_STEP), -MAX_STEP)

                print(f"[INFO] 偏移 dx={dx:.2f}, dy={dy:.2f}")

                if abs(dx) < DEAD_ZONE and abs(dy) < DEAD_ZONE:
                    print("[DEBUG] 死区内，忽略移动")
                else:
                    if frame_count % MOVE_INTERVAL == 0:
                        try:
                            x_now, y_now, _ = query_current_position(ser)

                            target_x = max(min(x_now + dx, X_MAX), X_MIN)
                            target_y = max(min(y_now + dy, Y_MAX), Y_MIN)

                            print(f"[DEBUG] 当前: X={x_now:.2f}, Y={y_now:.2f}")
                            print(f"[DEBUG] 目标: X={target_x:.2f}, Y={target_y:.2f}")

                            def threaded_move(x, y, z):
                                if exit_flag:
                                    print("[THREAD] ❌ 程序退出中，跳过移动")
                                    return
                                print(f"[THREAD] 🚀 启动移动线程: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
                                with move_lock:
                                    if not exit_flag:
                                        move_with_offset(x, y, z, ser)

                            threading.Thread(target=threaded_move, args=(target_x, target_y, current_z)).start()

                        except Exception as e:
                            print(f"[WARN] 读取坐标失败，跳过一次移动。{e}")

            # 显示中心辅助线
            cv2.line(frame, (FRAME_CENTER_X - 50, FRAME_CENTER_Y), (FRAME_CENTER_X + 50, FRAME_CENTER_Y), (0, 255, 0), 1)
            cv2.line(frame, (FRAME_CENTER_X, FRAME_CENTER_Y - 50), (FRAME_CENTER_X, FRAME_CENTER_Y + 50), (0, 255, 0), 1)

            cv2.imshow("Red Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        print("[提示] 正在退出，终止线程中...")
        exit_flag = True  # ✅ 设退出标志，禁止新动作

        time.sleep(0.5)   # 给线程时间安全退出

        move_stop(ser)    # ✅ 强制停止指令
        cap.release()
        ser.close()
        cv2.destroyAllWindows()
        print("[提示] 程序已关闭，机械臂停止。")

if __name__ == "__main__":
    main()
