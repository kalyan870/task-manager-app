import streamlit as st
import cv2
import tempfile
import os
import time
import numpy as np
from ultralytics import YOLO
from trackers.tracker import ByteTracker
from utils.counter import LineCounter
from utils.drawing import draw_bbox, draw_counting_line, draw_centroid, draw_dashboard
from utils.helpers import yolo_detections_to_list, resize_frame

st.set_page_config(page_title="Object Counting System", layout="wide")

st.title("Real-Time Object Counting System")
st.markdown("Upload a video or use webcam to detect, track, and count objects in real-time.")

with st.sidebar:
    st.header("Settings")

    input_source = st.radio("Input Source", ["Upload Video", "Webcam"])
    uploaded_file = None
    if input_source == "Upload Video":
        uploaded_file = st.file_uploader("Choose a video", type=["mp4", "avi", "mov", "mkv"])

    model_size = st.selectbox("YOLO Model", ["yolov8n (Nano)", "yolov8s (Small)"], index=0)
    model_map = {"yolov8n (Nano)": "yolov8n.pt", "yolov8s (Small)": "yolov8s.pt"}

    confidence_thresh = st.slider("Confidence Threshold", 0.1, 0.9, 0.3, 0.05)

    object_filter = st.multiselect(
        "Filter Objects",
        ["vehicles (car, truck, bus)", "persons", "all"],
        default=["all"],
    )

    counting_line_y = st.slider("Counting Line Position (%)", 10, 90, 50)

    col1, col2 = st.columns(2)
    with col1:
        direction = st.selectbox("Direction", ["down", "up", "both"])
    with col2:
        max_width = st.selectbox("Max Frame Width", [640, 854, 1280, 1920], index=2)

    run_button = st.button("Start Processing", type="primary")

st.sidebar.info(
    "**Controls**\n\n"
    "Press **q** to quit\n"
    "Press **r** to reset counter"
)

if "processing" not in st.session_state:
    st.session_state.processing = False
    st.session_state.count = 0
    st.session_state.fps = 0

placeholder = st.empty()
metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
metrics_col1.metric("Count", st.session_state.count)
metrics_col2.metric("FPS", st.session_state.fps)
metrics_col3.metric("Status", "Idle")

if run_button:
    st.session_state.processing = True
    st.session_state.count = 0

    model_path = model_map[model_size]
    with st.spinner("Loading model..."):
        model = YOLO(model_path)

    tracker = ByteTracker(track_high_thresh=confidence_thresh)

    class_filter = None
    if "vehicles (car, truck, bus)" in object_filter and "all" not in object_filter:
        class_filter = {2, 3, 5, 7}
    elif "persons" in object_filter and "all" not in object_filter:
        class_filter = {0}

    if input_source == "Webcam":
        cap = cv2.VideoCapture(0)
    elif uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
    else:
        st.error("Please upload a video or select webcam.")
        st.stop()

    if not cap.isOpened():
        st.error("Cannot open video source.")
        st.stop()

    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    line_y = int(frame_height * counting_line_y / 100)
    counter = LineCounter(line_y=line_y, direction=direction)

    prev_time = time.time()
    fps_display = 0
    frame_count = 0
    stop_btn = st.button("Stop")

    while cap.isOpened() and st.session_state.processing:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, max_width)
        h, w = frame.shape[:2]
        scaled_line_y = int(line_y * h / frame_height)

        frame_count += 1
        results = model(frame, verbose=False)
        detections = yolo_detections_to_list(results, class_filter=class_filter, conf_threshold=confidence_thresh)
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
            counter.update(track_id, centroid)

        draw_counting_line(frame, scaled_line_y, label="COUNTING LINE")

        current_time = time.time()
        elapsed = current_time - prev_time
        if elapsed > 0:
            fps_display = 0.9 * fps_display + 0.1 / elapsed if fps_display > 0 else 1.0 / elapsed
        prev_time = current_time

        frame = draw_dashboard(frame, counter.count, fps_display, scaled_line_y)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

        st.session_state.count = counter.count
        st.session_state.fps = fps_display

        metrics_col1.metric("Count", st.session_state.count)
        metrics_col2.metric("FPS", f"{st.session_state.fps:.1f}")
        metrics_col3.metric("Status", "Running")

        if stop_btn:
            st.session_state.processing = False
            break

    cap.release()
    st.session_state.processing = False
    metrics_col3.metric("Status", "Stopped")
    st.success(f"Processing complete! Total count: {counter.count}")
