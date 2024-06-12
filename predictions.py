import base64, numpy as np
import cv2
from ultralytics import YOLO
from shapely.geometry import Polygon
from keras.models import load_model

def segmentation_crop_image(b64imgstr):
    # Decode base64 string to image
    image_bytes = base64.b64decode(b64imgstr)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Get predictions
    model=YOLO("./model/best.pt")
    results = model.predict(source=image)
    masks=results[0].masks.xy

    if masks:
        polygon_coords = masks[-1]

        # Create a mask image with the same shape as the original image
        mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)

        # Draw the filled polygon on the mask
        cv2.fillPoly(mask, [np.array(polygon_coords, dtype=np.int32)], color=255)

        # Bitwise AND operation to get the cropped region
        cropped_image_region = cv2.bitwise_and(image, image, mask=mask)

        # Convert cropped_image_region to base64
        _, buffer = cv2.imencode('.jpg', cropped_image_region)
        cropped_image_base64 = base64.b64encode(buffer).decode('utf-8')

        return cropped_image_base64

def get_prediction(cropped_imageb64):
    # Decode base64 string to image
    cropped_image_bytes = base64.b64decode(cropped_imageb64)
    cropped_image_array = np.frombuffer(cropped_image_bytes, dtype=np.uint8)
    cropped_image = cv2.imdecode(cropped_image_array, cv2.IMREAD_COLOR)

    # Resize the image to the size expected by the model
    input_image = cv2.resize(cropped_image, (64, 64))  # Resize to 64x64
    input_image = input_image / 255.0  # Normalize
    input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension

    # Load the model and get predictions
    predict_model = load_model("./model/my_model.h5")
    predict_result = predict_model.predict(input_image)
    result = predict_result.argmax(axis=1)

    # 1: Not Anemia (default), 0: Anemia
    prediction = "Not Anemia"
    if not result:
        prediction = "Anemia"
    
    return {"status": "Successful", "prediction": prediction}