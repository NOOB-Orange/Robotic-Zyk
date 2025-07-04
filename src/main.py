import cv2
from Detect_red import detect_red_target
from robotic.arm_control_move import move_rotate_90


def main():
    cap = cv2.VideoCapture(0)
    detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = detect_red_target(frame)

        if result is not None and not detected:
            cx, cy = result
            print(f"[INFO] 检测到红色：X={cx}, Y={cy}")
            move_rotate_90()
            detected = True

        cv2.imshow("Red Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
