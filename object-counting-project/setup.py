import subprocess
import sys
import os


def install_requirements():
    print("Installing dependencies...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )
    print("Dependencies installed!")


def download_model():
    model_path = os.path.join("models", "yolov8n.pt")
    if not os.path.exists(model_path):
        print("Downloading YOLOv8n model...")
        from ultralytics import YOLO
        YOLO("yolov8n.pt")
        print("Model downloaded!")
    else:
        print("Model already exists.")


def download_sample_video():
    video_path = os.path.join("data", "videos", "sample.mp4")
    if not os.path.exists(video_path):
        print("To download sample videos:")
        print("  1. YouTube: search 'traffic camera footage'")
        print("  2. Kaggle: search 'traffic videos dataset'")
        print("  3. Place video in data/videos/ folder")
    else:
        print("Sample video found.")


if __name__ == "__main__":
    install_requirements()
    download_model()
    download_sample_video()
    print("\nSetup complete! Run:")
    print("  python app.py --help")
    print("  streamlit run streamlit_app.py")
