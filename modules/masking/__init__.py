import cv2
import numpy as np
import os
import io

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Paths to the Haar cascade XML files
face_cascade_path = os.path.join(
    current_dir, "models", "haarcascade_frontalface_default.xml"
)
eye_cascade_path = os.path.join(current_dir, "models", "haarcascade_eye.xml")
eyeglass_cascade_path = os.path.join(
    current_dir, "models", "haarcascade_eye_tree_eyeglasses.xml"
)


def detect_and_mask_eyes(image_bytes):

    npimg = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Error: Could not load image")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the pre-trained face, eye, and eyeglass detectors from OpenCV
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    eyeglass_cascade = cv2.CascadeClassifier(eyeglass_cascade_path)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) == 0:
        print("Error: No faces detected")
        return

    (fx, fy, fw, fh) = faces[0]

    roi_gray = gray[fy : fy + fh, fx : fx + fw]
    eyes = eye_cascade.detectMultiScale(
        roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(eyes) == 0:
        print("Error: No eyes detected within the face region")
        return

    # Detect eyeglasses within the detected face region
    eyeglasses = eyeglass_cascade.detectMultiScale(
        roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(eyeglasses) > 0:
        eyes = eyeglasses
        print("Eyeglasses detected")
    else:
        print("No eyeglasses detected")

    mask = np.zeros_like(gray)

    y_min = fy + min([y for (x, y, w, h) in eyes])
    y_max = fy + max([y + h for (x, y, w, h) in eyes])

    y_offset = int((y_max - y_min) * 0.2)

    head_center_x = fx + fw // 2

    head_x_offset = int(fw * 0.15)

    top_left = (fx - head_x_offset, y_min - y_offset - 100)
    bottom_right = (fx + fw + head_x_offset, y_max + y_offset)

    top_left = (max(top_left[0], 0), max(top_left[1], 0))
    bottom_right = (
        min(bottom_right[0], image.shape[1]),
        min(bottom_right[1], image.shape[0]),
    )

    cv2.rectangle(mask, top_left, bottom_right, 255, -1)

    image_with_line = image.copy()
    cv2.line(
        image_with_line,
        (head_center_x, 0),
        (head_center_x, image.shape[0]),
        (0, 0, 255),
        2,
    )

    # FOR DEV ONLY TO SHOW MASKING POSITION AND FACE CENTER
    combined = cv2.addWeighted(
        image_with_line, 0.5, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 0.5, 0
    )

    # Convert the combined image to bytes
    _, img_encoded = cv2.imencode(".png", mask)
    return io.BytesIO(img_encoded.tobytes())


# HOME = os.getcwd()
# assets_path = os.path.join(HOME, 'assets')
# ASSETS = os.listdir(assets_path)

# def main():
#     print('Running eyes detection')
#     for idx, item in enumerate(ASSETS):
#         detect_and_mask_eyes(os.path.join(HOME, 'assets', item), os.path.join(HOME, 'output', f'result-{idx + 1}.jpg'))
#     print('Finish running eyes detection')


# if __name__ == '__main__':
#     main()
