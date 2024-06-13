from fastapi import FastAPI, HTTPException, File, UploadFile
from google.cloud import firestore, storage
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
import os
import uuid

# Initialize Firestore
firestore_credentials = "./config/areunemia-capstone-d3e5724eaec5.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = firestore_credentials
firestore_db = firestore.Client()

# Initialize Google Cloud Storage
storage_credentials = "./config/areunemia-capstone-afc31e2de9ae.json"
storage_client = storage.Client.from_service_account_json(storage_credentials)
bucket_name = "model-ml-areunemia"
bucket = storage_client.bucket(bucket_name)

class Predictions(BaseModel):
    questionnaireAnswers: Dict[str, str]
    predictionResult: str

async def save_prediction(user_id: str, prediction: Predictions, file: UploadFile = File(...)):
    try:
        # Generate a unique file name with the desired path
        unique_filename = f"image_uploads/{uuid.uuid4()}.jpg"

        # Upload the file to Google Cloud Storage
        blob = bucket.blob(unique_filename)
        blob.upload_from_file(file.file, content_type=file.content_type, rewind=True)

        # Get the public URL of the uploaded file
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
        print(error)
        raise HTTPException(status_code=500, detail="Failed to add prediction")