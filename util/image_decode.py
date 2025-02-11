import numpy as np
import cv2
import base64

def process_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    height, width = image.shape[:2]

    if height > width:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    max_dimension = 1000
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def get_image(uploaded_file):
    return cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
    