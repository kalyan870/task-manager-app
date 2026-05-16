import cv2
import time
import os
import argparse
from ultralytics import YOLO
from trackers.tracker import ByteTracker
from utils.counter import LineCounter, MultiLineCounter
from utils.drawing import (
    draw_bbox,
    draw_counting_line,
    draw_centroid,
    draw_dashboard,
)
from utils.helpers import (
    yolo_detections_to_list,
    get_video_writer,
    resize_frame,
    VEHICLE_CLASSES,
    PERSON_CLASSES,
)


def process_video(
    video_path,
    output_path=None,
    model_path="yolov8n.pt",
    class_filter=None,
    line_y=None,
    direction="down",
    show=True,
    max_width=1280,
    skip_frames=0,
):
    model = YOLO(model_path)
    tracker = ByteTracker(track_high_thresh=0.5, track_low_thresh=0.1, match_thresh=0.8)
    counter = LineCounter(line_y=line_y, direction=direction)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if line_y is None:
        line_y = frame_height // 2
        counter.set_line(line_y)

    writer = None
    if output_path:
        writer = get_video_writer(output_path, max_width, int(frame_height * max_width / frame_width), int(fps))

    frame_count = 0
    prev_time = time.time()
    fps_display = 0

    print(f"Processing: {video_path}")
    print(f"Frames: {total_frames}, Resolution: {frame_width}x{frame_height}")
    print(f"Counting line at y={line_y}, direction={direction}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, max_width)
        current_h, current_w = frame.shape[:2]
        scaled_line_y = int(line_y * current_h / frame_height) if line_y else current_h // 2

        frame_count += 1
        if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:
            continue

        results = model(frame, verbose=False)
        detections = yolo_detections_to_list(results, class_filter=class_filter)

        tracked_objects = tracker.update(detections)

        for obj in tracked_objects:
            bbox = obj["bbox"]
            track_id = obj["track_id"]
            centroid = obj["centroid"]
            class_name = "object"

            matching_det = next(
                (d for d in detections if abs(d["confidence"] - obj["score"]) < 0.05),
                None,
            )
            if matching_det:
                class_name = matching_det["class_name"]

            draw_bbox(frame, bbox, track_id, class_name, obj["score"])
            draw_centroid(frame, centroid)

            counter.update(track_id, centroid)

        draw_counting_line(frame, scaled_line_y, label="COUNTING LINE")

        current_time = time.time()
        elapsed = current_time - prev_time
        if elapsed > 0:
            fps_display = 0.9 * fps_display + 0.1 / elapsed if fps_display > 0 else 1.0 / elapsed
        prev_time = current_time

        frame = draw_dashboard(frame, counter.count, fps_display, scaled_line_y)

        if writer:
            writer.write(frame)

        if show:
            cv2.imshow("Object Counting", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                counter.reset()
                print("Counter reset")

        if frame_count % 100 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"Progress: {progress:.1f}% | Count: {counter.count} | FPS: {fps_display:.1f}")

    cap.release()
    if writer:
        writer.release()
    if show:
        cv2.destroyAllWindows()

    print(f"\nDone! Total count: {counter.count}")
    if output_path:
        print(f"Output saved to: {output_path}")

    return counter.count


def process_video_multi(
    video_path,
    output_path=None,
    model_path="yolov8n.pt",
    show=True,
    max_width=1280,
    skip_frames=0,
):
    model = YOLO(model_path)
    tracker = ByteTracker()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    line1_y = frame_height // 3
    line2_y = 2 * frame_height // 3

    multi_counter = MultiLineCounter()
    multi_counter.add_line("Line 1 (Top)", line1_y, direction="down")
    multi_counter.add_line("Line 2 (Bottom)", line2_y, direction="up")

    writer = None
    if output_path:
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        writer = get_video_writer(output_path, max_width, int(frame_height * max_width / frame_width), int(fps))

    frame_count = 0
    prev_time = time.time()
    fps_display = 0

    print(f"Multi-line counting for: {video_path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, max_width)
        h, w = frame.shape[:2]

        frame_count += 1
        if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:
            continue

        results = model(frame, verbose=False)
        detections = yolo_detections_to_list(results)
        tracked_objects = tracker.update(detections)

        for obj in tracked_objects:
            bbox = obj["bbox"]
            track_id = obj["track_id"]
            centroid = obj["centroid"]

            matching_det = next(
                (d for d in detections if abs(d["confidence"] - obj["score"]) < 0.05),
                None,
            )
            class_name = matching_det["class_name"] if matching_det else "object"
            draw_bbox(frame, bbox, track_id, class_name, obj["score"])
            draw_centroid(frame, centroid)
            multi_counter.update(track_id, centroid)

        draw_counting_line(frame, line1_y, color=(0, 255, 255), label="LINE 1")
        draw_counting_line(frame, line2_y, color=(255, 0, 255), label="LINE 2")

        current_time = time.time()
        elapsed = current_time - prev_time
        if elapsed > 0:
            fps_display = 0.9 * fps_display + 0.1 / elapsed if fps_display > 0 else 1.0 / elapsed
        prev_time = current_time

        frame = draw_dashboard(frame, multi_counter.get_counts(), fps_display)

        if writer:
            writer.write(frame)

        if show:
            cv2.imshow("Multi-Line Counting", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if frame_count % 100 == 0:
            print(f"Frame {frame_count}/{total_frames} | Counts: {multi_counter.get_counts()}")

    cap.release()
    if writer:
        writer.release()
    if show:
        cv2.destroyAllWindows()

    print(f"Final counts: {multi_counter.get_counts()}")
    return multi_counter.get_counts()


def main():
    parser = argparse.ArgumentParser(description="Real-Time Object Counting System")
    parser.add_argument("--video", type=str, default=None,
                        help="Path to input video (uses webcam if not specified)")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save output video")
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="Path to YOLO model")
    parser.add_argument("--line-y", type=int, default=None,
                        help="Y coordinate of counting line")
    parser.add_argument("--direction", type=str, default="down",
                        choices=["down", "up", "both"],
                        help="Counting direction")
    parser.add_argument("--class-filter", type=str, default=None,
                        help="Comma-separated class IDs to track (e.g., '2,3,5,7' for vehicles)")
    parser.add_argument("--multi-line", action="store_true",
                        help="Enable multi-line counting")
    parser.add_argument("--no-show", action="store_true",
                        help="Disable video display")
    parser.add_argument("--max-width", type=int, default=1280,
                        help="Maximum frame width")
    parser.add_argument("--skip-frames", type=int, default=0,
                        help="Skip every N frames")
    args = parser.parse_args()

    class_filter = None
    if args.class_filter:
        class_filter = set(int(x.strip()) for x in args.class_filter.split(","))

    if args.video and not os.path.exists(args.video):
        print(f"Video not found: {args.video}")
        print("Download a sample video or use --video with webcam (omit --video)")
        return

    if args.multi_line:
        process_video_multi(
            video_path=args.video or 0,
            output_path=args.output,
            model_path=args.model,
            show=not args.no_show,
            max_width=args.max_width,
            skip_frames=args.skip_frames,
        )
    else:
        process_video(
            video_path=args.video or 0,
            output_path=args.output,
            model_path=args.model,
            class_filter=class_filter,
            line_y=args.line_y,
            direction=args.direction,
            show=not args.no_show,
            max_width=args.max_width,
            skip_frames=args.skip_frames,
        )


if __name__ == "__main__":
    main()
