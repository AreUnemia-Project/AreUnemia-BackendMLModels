from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from predictions import segmentation_crop_image, get_prediction
from firestore_handler import *
import uuid
import base64
import json

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/api/predict")
async def predict(
    user_id: str = Form(...), 
    eye_photo: UploadFile = File(...),
    questionnaire_answers: str = Form(...)):

    if eye_photo is None:
        raise HTTPException(status_code=400, detail="No image provided")
    
    questionnaireAnswers_dict = json.loads(questionnaire_answers)
    
    eye_photo.filename = f"{uuid.uuid4()}.jpg"
    image = await eye_photo.read()

    b64imgstr = base64.b64encode(image).decode('utf-8')

    cropped_image = segmentation_crop_image(b64imgstr)
    prediction_res = get_prediction(cropped_image)

    prediction_data = Predictions (
        questionnaireAnswers=questionnaireAnswers_dict,
        predictionResult=prediction_res
    )

    response = await save_prediction(user_id, prediction_data, eye_photo)

    return response

@app.get("/api/predict/history/{user_id}")
async def get_all_predictions_history(user_id:str):

    if not user_id:
        raise HTTPException(status_code=400, detail="No Id provided")
    
    predictions = await retrieve_all_predictions_history(user_id)
    return predictions

@app.get("/api/predict/history/{user_id}/{predict_id}")
async def get_predictions_history(user_id: str, predict_id: str):

    if not predict_id or not user_id:
        raise HTTPException(status_code=400, detail="No Id provided")
    
    prediction = await retrieve_predictions_history(user_id, predict_id)
    return prediction