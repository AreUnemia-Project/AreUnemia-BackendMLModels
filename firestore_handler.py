from fastapi import FastAPI, HTTPException, File, UploadFile
from google.cloud import firestore, storage
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
import os
import uuid

firestore_credentials = "./config/areunemia-capstone-d3e5724eaec5.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = firestore_credentials
firestore_db = firestore.Client()

storage_credentials = "./config/areunemia-capstone-afc31e2de9ae.json"
storage_client = storage.Client.from_service_account_json(storage_credentials)
bucket_name = "model-ml-areunemia"
bucket = storage_client.bucket(bucket_name)

class Predictions(BaseModel):
    questionnaireAnswers: Dict[str, str]
    predictionResult: str

class PredictionsResponse(BaseModel):
    predictionID: str
    eyePhotoUrl: str
    questionnaireAnswers: Dict[str, str]
    predictionResult: str
    createdAt: datetime

async def save_prediction(user_id: str, prediction: Predictions, file: UploadFile = File(...)):
    try:
        if not user_id or not prediction or not file:
            raise HTTPException(status_code=400, detail="Missing required fields")
        unique_filename = f"image_uploads/{uuid.uuid4()}.jpg"

        blob = bucket.blob(unique_filename)
        blob.upload_from_file(file.file, content_type=file.content_type, rewind=True)

        eye_photo_url = blob.public_url

        predictions_ref =  predictions_ref = firestore_db.collection("users").document(user_id).collection("predictions")
        prediction_doc = predictions_ref.document()
        prediction_id = prediction_doc.id

        prediction_data = {
            "eyePhoto" : eye_photo_url,
            "questionnaireAnswers": prediction.questionnaireAnswers,
            "predictionResult": prediction.predictionResult,
            "createdAt": datetime.now(),
        }

        prediction_doc.set(prediction_data)
        return {"status": "success", "message": "Prediction added successfully", "predictionID": prediction_id}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to add prediction: {str(error)}")
    
async def retrieve_predictions_history(user_id: str, prediction_id: str):
    try:
        if not user_id or not prediction_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        predictions_ref = firestore_db.collection("users").document(user_id).collection("predictions").document(prediction_id)
        prediction_doc = predictions_ref.get()

        if not prediction_doc.exists:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        prediction_data = prediction_doc.to_dict()
        return prediction_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve prediction: {str(e)}")
    
async def retrieve_all_predictions_history(user_id: str):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        predictions_ref = firestore_db.collection("users").document(user_id).collection("predictions")
        prediction_docs = predictions_ref.stream()

        predictions = []
        for doc in prediction_docs:
            data = doc.to_dict()
            data['predictionID'] = doc.id
            predictions.append(data)
        
        return predictions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve prediction: {str(e)}")