# Real-Time Object Counting System

A computer vision system that detects, tracks, and counts objects crossing a virtual line in real-time using YOLOv8 and ByteTrack.

## Features

- **Object Detection** using YOLOv8 (Nano/Small models)
- **Object Tracking** with ByteTrack algorithm (persistent ID assignment)
- **Line Crossing Counting** with configurable direction (up/down/both)
- **Live Dashboard** with FPS, count, and active objects overlay
- **Multi-Line Counting** support for complex scenarios
- **Streamlit Web Interface** for easy interaction
- **Video Export** with full annotations

## Architecture

```
Video Input → Frame Extraction → YOLOv8 Detection → ByteTrack Tracking → Line Crossing Logic → Counter Update → Visualization
```

## Tech Stack

- Python, OpenCV, YOLOv8 (Ultralytics), NumPy
- ByteTrack for object tracking
- Streamlit for web UI

## Installation

```bash
git clone <repo-url>
cd object-counting-project
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Process a video file
python app.py --video data/videos/traffic.mp4 --output data/outputs/result.mp4

# Webcam mode
python app.py

# Vehicle counting only
python app.py --video data/videos/traffic.mp4 --class-filter "2,3,5,7"

# Custom counting line
python app.py --video data/videos/traffic.mp4 --line-y 400 --direction down

# Multi-line counting
python app.py --video data/videos/traffic.mp4 --multi-line

# Skip frames for speed
python app.py --video data/videos/traffic.mp4 --skip-frames 1
```

### Web Interface

```bash
streamlit run streamlit_app.py
```

## Project Structure

```
object-counting-project/
├── data/
│   ├── videos/          # Input videos
│   └── outputs/         # Processed results
├── models/              # YOLO weights
├── trackers/
│   └── tracker.py       # ByteTrack implementation
├── utils/
│   ├── counter.py       # Line counting logic
│   ├── drawing.py       # Visualization utilities
│   └── helpers.py       # Helper functions
├── app.py               # CLI entry point
├── streamlit_app.py     # Web interface
├── requirements.txt
└── README.md
```

## Deployment

### Hugging Face Spaces

```bash
pip install streamlit ultralytics opencv-python numpy
streamlit run streamlit_app.py
```

## Use Cases

- Vehicle counting for traffic analytics
- People counting for retail/security
- Industrial object counting on conveyor belts
- Wildlife monitoring

## Future Improvements

- CSV logging for analytics
- Speed estimation
- Multi-camera support
- Direction-based lane counting
- Alerts and notifications
- Database integration

## License

MIT
