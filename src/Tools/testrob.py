import cv2
import serial
import struct
import time
import sys
import os

# 添加搜索路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Version.Detect_red import detect_red_target

# 串口配置
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

# 摄像头参数
FRAME_CENTER_X = 320
FRAME_CENTER_Y = 240

# 灵敏度与控制参数
ANGLE_SCALE = 0.15
ANGLE_SPEED = 50.0  # 提升速度
DEAD_ZONE = 1.0
MIN_ANGLE_DELTA = 0.3
MAX_ANGLE_DELTA = 10.0  # 限幅，避免飞出
MOVE_INTERVAL = 0.15  # 更快响应

def move_single_axis(axis_number, angle_delta, speed, ser):
    cmd = [0] * 48
    cmd[0] = 0xEE
    cmd[1] = ord('5')
    cmd[2] = 0
    cmd[3:7] = list(struct.pack('<f', float(axis_number)))
    cmd[7:11] = list(struct.pack('<f', float(angle_delta)))
    cmd[27:31] = list(struct.pack('<f', 1500.0))
    cmd[43:47] = list(struct.pack('<f', float(speed)))
    cmd[47] = 0xEF
    ser.write(bytearray(cmd))
    print(f"[ACTION] 轴 {axis_number} 增量 {angle_delta:.2f}° 速度 {speed:.1f}")

def initialize_serial():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    cmd = [252, 30, 9, 0] + [0]*43 + [253]
    ser.write(bytearray(cmd))
    time.sleep(0.1)
    return ser

def move_stop(ser):
    cmd = [0] * 48
    cmd[0] = 252
    cmd[1] = 12
    cmd[2] = 5
    cmd[47] = 253
    ser.write(bytearray(cmd))
    print("[ACTION] 已发送停止")

def draw_grid(frame):
    h, w, _ = frame.shape
    color = (0, 255, 0)
    thickness = 1
    cv2.line(frame, (w // 3, 0), (w // 3, h), color, thickness)
    cv2.line(frame, (2 * w // 3, 0), (2 * w // 3, h), color, thickness)
    cv2.line(frame, (0, h // 3), (w, h // 3), color, thickness)
    cv2.line(frame, (0, 2 * h // 3), (w, 2 * h // 3), color, thickness)
    cv2.circle(frame, (w // 2, h // 2), 3, (0, 0, 255), -1)

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    ser = initialize_serial()
    last_move_time = time.time()

    print("[提示] 确保机械臂安全，按 'q' 退出。")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result = detect_red_target(frame)
            draw_grid(frame)

            if result is not None:
                cx, cy = result
                dx = cx - FRAME_CENTER_X
                dy = cy - FRAME_CENTER_Y

                print(f"[INFO] 红色坐标: ({cx}, {cy}), 偏移: dx={dx}, dy={dy}")

                now = time.time()
                if now - last_move_time > MOVE_INTERVAL:
                    # 左右
                    if abs(dx) > DEAD_ZONE:
                        angle_delta_x = dx * ANGLE_SCALE
                        if abs(angle_delta_x) < MIN_ANGLE_DELTA:
                            angle_delta_x = MIN_ANGLE_DELTA if angle_delta_x > 0 else -MIN_ANGLE_DELTA
                        if abs(angle_delta_x) > MAX_ANGLE_DELTA:
                            angle_delta_x = MAX_ANGLE_DELTA if angle_delta_x > 0 else -MAX_ANGLE_DELTA
                        move_single_axis(0, angle_delta_x, ANGLE_SPEED, ser)

                    # 上下
                    if abs(dy) > DEAD_ZONE:
                        angle_delta_y = -dy * ANGLE_SCALE
                        if abs(angle_delta_y) < MIN_ANGLE_DELTA:
                            angle_delta_y = MIN_ANGLE_DELTA if angle_delta_y > 0 else -MIN_ANGLE_DELTA
                        if abs(angle_delta_y) > MAX_ANGLE_DELTA:
                            angle_delta_y = MAX_ANGLE_DELTA if angle_delta_y > 0 else -MAX_ANGLE_DELTA
                        move_single_axis(2, angle_delta_y, ANGLE_SPEED, ser)  # 修正为 axis=2

                    last_move_time = now

            cv2.imshow("Red Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        move_stop(ser)
        ser.close()
        cv2.destroyAllWindows()
        print("[提示] 已退出程序。")

if __name__ == "__main__":
    main()
