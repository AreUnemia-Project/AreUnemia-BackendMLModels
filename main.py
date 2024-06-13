from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from predictions import segmentation_crop_image, get_prediction
from firestore_handler import save_prediction, Predictions
import uuid
import base64
import json

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/predict")
async def predict(
    userId: str = Form(...), 
    eyePhoto: UploadFile = File(...),
    questionnaireAnswers: str = Form(...)):

    if eyePhoto is None:
        raise HTTPException(status_code=400, detail="No image provided")
    
    questionnaireAnswers_dict = json.loads(questionnaireAnswers)
    
    eyePhoto.filename = f"{uuid.uuid4()}.jpg"
    image = await eyePhoto.read()

    # Encode the image to base64
    b64imgstr = base64.b64encode(image).decode('utf-8')

    # Call the prediction function
    cropped_image = segmentation_crop_image(b64imgstr)
    prediction_res = get_prediction(cropped_image)

    prediction_data = Predictions (
        questionnaireAnswers=questionnaireAnswers_dict,
        predictionResult=prediction_res
    )

    response = await save_prediction(userId, prediction_data, eyePhoto)

    return response