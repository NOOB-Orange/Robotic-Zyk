# arm_control_move.py
import serial
import struct
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

# 工具函数

def float_to_bytes(f):
    return struct.pack('<f', f)


def send_command(ser, cmd_list):
    cmd = bytearray(48)
    for i, val in enumerate(cmd_list):
        cmd[i] = val
    ser.write(cmd)
    print(f"[INFO] 已发送: {cmd.hex(' ')}")
    time.sleep(0.05)

X_MIN, X_MAX = 340.0, 350.0
Y_MIN, Y_MAX = -10.0, 10.0
Z_MIN, Z_MAX = 0, 100

BASE_X = 344.1
BASE_Y = 0.7
BASE_Z = 417.4

current_x = BASE_X
current_y = BASE_Y
current_z = BASE_Z

THRESHOLD_MM = 0.2
MAX_STEP = 0.5

# 初始化

def initialize_serial():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    mode_cmd = [252, 30, 9, 0] + [0]*43 + [253]
    send_command(ser, mode_cmd)
    time.sleep(0.1)

    return ser


# 运动

def limit_position(x, y, z):
    x = max(X_MIN, min(X_MAX, x))
    y = max(Y_MIN, min(Y_MAX, y))
    z = max(Z_MIN, min(Z_MAX, z))
    return x, y, z


def move_with_offset(target_x, target_y, target_z, ser):
    global current_x, current_y, current_z

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
    spd = 30.0

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


# 查询实时坐标

def query_current_position(ser):
    cmd = [252, 30, 4, 0] + [0]*43 + [253]
    send_command(ser, cmd)

    response = ser.read(48)
    if len(response) != 48:
        print("[WARN] 未收到完整反馈")
        return None

    def bytes_to_float(b):
        return struct.unpack('<f', b)[0]

    x = bytes_to_float(response[3:7])
    y = bytes_to_float(response[7:11])
    z = bytes_to_float(response[11:15])

    print(f"[INFO] 📡 实时坐标: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
    return x, y, z


# 停止

def move_stop(ser):
    a = [0] * 48
    a[0] = 252
    a[1] = 12
    a[2] = 5
    a[47] = 253

    send_command(ser, a)
    print("[ACTION] 已发送停止")
