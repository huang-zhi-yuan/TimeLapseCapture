# camera_utils.py
import cv2
import logging

def list_cameras():
    cams = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            cams.append((i, f"Camera {i}"))
            cap.release()
    return cams

def open_camera_properties(index):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_SETTINGS, 0)
        cv2.waitKey(500)
        cap.release()

def find_best_resolution(index):
    resolutions = [(3840, 2160), (3264, 2448), (2592, 1944), (2048, 1536),
                   (1920, 1080), (1280, 720), (640, 480)]
    best_w, best_h = 640, 480
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if cap.isOpened():
        for w, h in resolutions:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            aw = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            ah = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if aw >= w * 0.95 and ah >= h * 0.95:
                best_w, best_h = w, h
                break
        cap.release()
    logging.info(f"最佳分辨率: {best_w}x{best_h}")
    return best_w, best_h

def create_default_baseline():
    return {
        "brightness": 128.0,
        "avg_r": 128.0,
        "avg_g": 128.0,
        "avg_b": 128.0,
        "rg_ratio": 1.0,
        "bg_ratio": 1.0
    }