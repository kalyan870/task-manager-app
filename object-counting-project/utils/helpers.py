import os
import cv2
import numpy as np

CLASS_NAMES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle",
    4: "airplane", 5: "bus", 6: "train", 7: "truck",
    8: "boat", 9: "traffic light", 10: "fire hydrant",
    11: "stop sign", 12: "parking meter", 13: "bench",
    14: "bird", 15: "cat", 16: "dog", 17: "horse",
    18: "sheep", 19: "cow", 20: "elephant",
}

VEHICLE_CLASSES = {2, 3, 5, 7}
PERSON_CLASSES = {0}


def get_class_name(class_id):
    return CLASS_NAMES.get(class_id, f"class_{class_id}")


def is_vehicle(class_id):
    return class_id in VEHICLE_CLASSES


def is_person(class_id):
    return class_id in PERSON_CLASSES


def yolo_detections_to_list(results, class_filter=None, conf_threshold=0.3):
    detections = []
    if results is None or len(results) == 0:
        return detections

    boxes = results[0].boxes
    if boxes is None:
        return detections

    for box in boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        if confidence < conf_threshold:
            continue
        if class_filter is not None and class_id not in class_filter:
            continue
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        detections.append({
            "bbox": [x1, y1, x2, y2],
            "class_id": class_id,
            "class_name": get_class_name(class_id),
            "confidence": confidence,
        })
    return detections


def get_video_writer(output_path, frame_width, frame_height, fps=30):
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))


def resize_frame(frame, max_width=1280):
    h, w = frame.shape[:2]
    if w > max_width:
        scale = max_width / w
        new_w = max_width
        new_h = int(h * scale)
        return cv2.resize(frame, (new_w, new_h))
    return frame
