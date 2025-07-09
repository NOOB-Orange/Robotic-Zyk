import serial
import struct
import time

SERIAL_PORT = 'COM3'  # 修改为你的串口
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

# ✅ 改函数名为 move_rotate_90
def move_rotate_90():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)

        # 设定机械臂模式 → 六轴工业机器人模式
        mode_cmd = [252, 30, 9, 0] + [0]*43 + [253]
        send_command(ser, mode_cmd)
        time.sleep(0.1)

        # 指定关节动作（第三轴转到90度）
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
