from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from predictions import segmentation_crop_image, get_prediction
import uuid
import base64 

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    if file is None:
        return {"status" : "No image provided"}
    
    file.filename = f"{uuid.uuid4()}.jpg"
    image = await file.read()

    # Encode the image to base64
    b64imgstr = base64.b64encode(image).decode('utf-8')

    # Call the prediction function
    cropped_image = segmentation_crop_image(b64imgstr)
    return get_prediction(cropped_image)