import cv2

COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (128, 0, 0), (0, 128, 0), (0, 0, 128),
    (128, 128, 0), (128, 0, 128), (0, 128, 128),
]


def get_color(track_id):
    return COLORS[track_id % len(COLORS)]


def draw_bbox(frame, bbox, track_id, class_name, confidence, color=None):
    x1, y1, x2, y2 = map(int, bbox)
    if color is None:
        color = get_color(track_id)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = f"#{track_id} {class_name} {confidence:.2f}"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return frame


def draw_counting_line(frame, line_y, color=(0, 255, 255), label=None):
    h, w = frame.shape[:2]
    cv2.line(frame, (0, line_y), (w, line_y), color, 2)
    if label:
        cv2.putText(frame, label, (10, line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return frame


def draw_centroid(frame, centroid, color=(0, 255, 0)):
    cv2.circle(frame, centroid, 4, color, -1)
    return frame


def draw_dashboard(frame, counts, fps, line_y=None):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (250, 120), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    y_offset = 20
    if isinstance(counts, dict):
        for name, count in counts.items():
            cv2.putText(frame, f"{name}: {count}", (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 25
    else:
        cv2.putText(frame, f"Count: {counts}", (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        y_offset += 25

    cv2.putText(frame, f"FPS: {fps:.1f}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    y_offset += 25
    cv2.putText(frame, f"Active: {len(counts) if isinstance(counts, dict) else 0}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return frame
