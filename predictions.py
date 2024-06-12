import base64, numpy as np
import cv2
from ultralytics import YOLO
from shapely.geometry import Polygon

def segmentation_crop_image(b64imgstr):
    # Decode base64 string to image
    image_bytes = base64.b64decode(b64imgstr)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Get predictions
    model=YOLO("./model/best.pt")
    results = model.predict(source=image)
    masks=results[0].masks.xy

    for mask in masks:
        # Example polygon coordinates (replace with actual polygon coordinates)
        polygon_coords = mask

        # Create a mask image with the same shape as the original image
        mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)

        # Draw the filled polygon on the mask
        cv2.fillPoly(mask, [np.array(polygon_coords, dtype=np.int32)], color=255)

        # Bitwise AND operation to get the cropped region
        cropped_image = cv2.bitwise_and(image, image, mask=mask)

        # Display the result
        cv2.imwrite('crop_mask.jpg',cropped_image)
    
    return {
        "fire": "bruh",
    }