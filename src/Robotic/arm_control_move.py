import serial
import struct
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

# 工具函数：float转4字节小端bytes
def float_to_bytes(f):
    return struct.pack('<f', f)

# 发送48字节指令
def send_command(ser, cmd_list):
    cmd = bytearray(48)
    for i, val in enumerate(cmd_list):
        cmd[i] = val
    ser.write(cmd)
    print(f"[INFO] 已发送: {cmd.hex(' ')}")
    time.sleep(0.05)

# 限制工作台坐标范围
X_MIN, X_MAX = 80, 120
Y_MIN, Y_MAX = 80, 120
Z_MIN, Z_MAX = 0, 100

def limit_position(x, y, z):
    x = max(X_MIN, min(X_MAX, x))
    y = max(Y_MIN, min(Y_MAX, y))
    z = max(Z_MIN, min(Z_MAX, z))
    return x, y, z

BASE_X = 100
BASE_Y = 100
BASE_Z = 50

current_x = BASE_X
current_y = BASE_Y
current_z = BASE_Z

THRESHOLD_MM = 0.5
MAX_STEP = 1.5

# 改为接受串口对象
def import cv2


def calibrate_visual_center():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[INFO] 请把机械臂移动到预期的中央位置，
           然后将红色目标放在该位置，按 's' 键记录坐标")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Calibration Window", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            h, w = frame.shape[:2]
            center_x = w // 2
            center_y = h // 2
            print(f"[INFO] 当前画面大小: {w}x{h}")
            print(f"[INFO] 当前视觉中心坐标: X={center_x}, Y={center_y}")
            print("[INFO] 你可以把这个值填入 main.py 作为 frame_center_x, frame_center_y")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    calibrate_visual_center()
move_with_offset(dx, dy, ser):
    global current_x, current_y, current_z

    step_x = max(-MAX_STEP, min(MAX_STEP, dx))
    step_y = max(-MAX_STEP, min(MAX_STEP, dy))

    target_x = current_x + step_x
    target_y = current_y + step_y
    target_z = current_z

    target_x, target_y, target_z = limit_position(target_x, target_y, target_z)

    if abs(target_x - current_x) < THRESHOLD_MM and abs(target_y - current_y) < THRESHOLD_MM:
        return

    current_x = target_x
    current_y = target_y

    print(f"[ACTION] 移动到: X={current_x:.2f} mm, Y={current_y:.2f} mm")

    a = [0] * 48
    a[0] = 251
    a[1] = ord('2')
    a[2] = 1

    joint_values = [current_x, current_y, current_z, 0.0, 0.0, 0.0]
    pmw = 1500.0
    at = 100.0
    spd = 6000.0

    idx = 3
    for val in joint_values:
        b = float_to_bytes(val)
        a[idx:idx+4] = list(b)
        idx += 4

    a[27:31] = list(float_to_bytes(pmw))
    a[39:43] = list(float_to_bytes(at))
    a[43:47] = list(float_to_bytes(spd))
    a[47] = 252

    send_command(ser, a)

# 原有单次动作函数保留
def move_rotate_90():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)

        mode_cmd = [252, 30, 9, 0] + [0]*43 + [253]
        send_command(ser, mode_cmd)
        time.sleep(0.1)

        a = [0] * 48
        a[0] = 238
        a[1] = 3 + 48
        a[2] = 1

        joint_angles = [0.0, -30.0, 90.0, 0.0, 0.0, 0.0]
        pmw = 1500.0
        at = 100.0
        spd = 36.0

        idx = 3
        for angle in joint_angles:
            b = float_to_bytes(angle)
            a[idx:idx+4] = list(b)
            idx += 4

        a[27:31] = list(float_to_bytes(pmw))
        a[39:43] = list(float_to_bytes(at))
        a[43:47] = list(float_to_bytes(spd))
        a[47] = 239

        send_command(ser, a)

if __name__ == "__main__":
    move_rotate_90()
    print("[INFO] 程序结束")
