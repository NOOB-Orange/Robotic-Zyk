import cv2


def calibrate_visual_center():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[INFO] 请把机械臂移动到预期的中央位置，然后将红色目标放在该位置，按 's' 键记录坐标")

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
