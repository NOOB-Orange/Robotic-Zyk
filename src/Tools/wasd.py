import serial
import struct
from pynput import keyboard

# 串口配置
SERIAL_PORT = 'COM3'  # 根据你的实际端口修改
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

# 当前位置初始化（建议用机械臂实际初始坐标）
current_x = 350.0
current_y = 0.0
current_z = 100.0  # 固定高度，防止撞台

step = 5.0  # 每次移动的步长（毫米）
speed = 5000.0  # 移动速度

# 浮点数转4字节
def float_to_bytes(f):
    return struct.pack('<f', f)

# 发送G1直线插补指令
def send_move_command(x, y, z):
    cmd = bytearray(48)
    cmd[0] = 0xEE  # 帧头
    cmd[1] = ord('1')  # G1指令

    # 写入目标坐标
    cmd[3:7] = float_to_bytes(x)
    cmd[7:11] = float_to_bytes(y)
    cmd[11:15] = float_to_bytes(z)

    # 姿态角（保持不变）
    cmd[15:19] = float_to_bytes(0.0)  # B0
    cmd[19:23] = float_to_bytes(0.0)  # B1
    cmd[23:27] = float_to_bytes(0.0)  # W

    # PWM（不控制）
    cmd[27:31] = float_to_bytes(1500.0)

    # 速度
    cmd[43:47] = float_to_bytes(speed)

    cmd[47] = 0xEF  # 帧尾

    ser.write(cmd)
    print(f"[INFO] 发送坐标：X={x:.1f}, Y={y:.1f}, Z={z:.1f}")

# 按键事件处理
def on_press(key):
    global current_x, current_y, current_z
    try:
        if key.char == 'w':
            current_y += step
        elif key.char == 's':
            current_y -= step
        elif key.char == 'a':
            current_x -= step
        elif key.char == 'd':
            current_x += step
        elif key.char == 'q':
            print("[INFO] 退出程序")
            return False  # 停止监听

        send_move_command(current_x, current_y, current_z)
    except AttributeError:
        pass

# 主程序
print("按 W/A/S/D 控制机械臂，Q 退出")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
