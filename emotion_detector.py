import picamera
import cv2
import numpy as np
from deepface import DeepFace

# Initialize Pi Camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)

def capture_image():
    """Captures an image from the Pi camera and returns it as an OpenCV-compatible array."""
    image_path = "/home/pi/captured_image.jpg"
    camera.capture(image_path)
    image = cv2.imread(image_path)
    return image

def detect_emotion(image):
    """Detects emotion from the input image using DeepFace."""
    try:
        result = DeepFace.analyze(image, actions=['emotion'])
        emotion = result['dominant_emotion']
        return emotion
    except Exception as e:
        print(f"Error detecting emotion: {e}")
        return None

if __name__ == "__main__":
    print("Capturing image...")
    image = capture_image()
    print("Detecting emotion...")
    emotion = detect_emotion(image)

    if emotion:
        print(f"Detected emotion: {emotion}")
    else:
        print("Failed to detect emotion.")