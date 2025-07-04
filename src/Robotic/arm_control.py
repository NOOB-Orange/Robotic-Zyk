import serial
import struct
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 115200

def float_to_bytes(f):
    return struct.pack('<f', f)  # 小端4字节float

def send_command(ser, cmd_list):
    cmd = bytearray(48)
    for i, val in enumerate(cmd_list):
        cmd[i] = val
    ser.write(cmd)
    print(f"[INFO] 已发送: {cmd.hex(' ')}")
    time.sleep(0.05)

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
    time.sleep(2)

    # ① 设定模式：六轴工业机器人 垂直手腕
    mode_cmd = [252, 30, 9, 0] + [0]*43 + [253]
    send_command(ser, mode_cmd)
    time.sleep(0.1)

    # ② 转动90度：Button8等效
    a = [0] * 48
    a[0] = 238
    a[1] = 3 + 48
    a[2] = 1  # G331

    # 假设轴3（a[11]~a[14]) 设为90度
    joint_angles = [0.0, -30.0, 90.0, 0.0, 0.0, 0.0]  # 6轴角度
    pmw = 1500.0
    at = 100.0
    spd = 36.0

    idx = 3
    for angle in joint_angles:
        b = float_to_bytes(angle)
        a[idx:idx+4] = list(b)
        idx += 4

    # PMW
    a[27:31] = list(float_to_bytes(pmw))
    # AT
    a[39:43] = list(float_to_bytes(at))
    # SPD
    a[43:47] = list(float_to_bytes(spd))

    a[47] = 239
    send_command(ser, a)

print("[INFO] 程序结束")
