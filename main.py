from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from predictions import segmentation_crop_image, get_prediction
from firestore_handler import *
from jwt_utils import decode_jwt
import uuid
import base64
import json

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_jwt(token)
    if user_id is None:
        raise credentials_exception
    return user_id

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/api/predict")
async def predict(
    eye_photo: UploadFile = File(...),
    questionnaire_answers: str = Form(...),
    token: str = Depends(oauth2_scheme)):

    current_user = get_current_user(token)
    user_id = current_user["userId"]

    if not eye_photo or not questionnaire_answers:
        raise HTTPException(status_code=400, detail="Missing fields required")
    
    try:
        questionnaireAnswers_dict_raw = json.loads(questionnaire_answers)
        questionnaireAnswers_dict = dict(sorted(questionnaireAnswers_dict_raw.items(), key=lambda item: int(item[0].replace('question', ''))))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid questionnaire answers format")
    
    eye_photo.filename = f"{uuid.uuid4()}.jpg"
    image = await eye_photo.read()

    b64imgstr = base64.b64encode(image).decode('utf-8')

    try:
        cropped_image = segmentation_crop_image(b64imgstr)
        prediction_res = get_prediction(cropped_image, questionnaireAnswers_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction processing failed: {str(e)}")
    
    prediction_data = Predictions (
        questionnaireAnswers=questionnaireAnswers_dict,
        predictionResult=prediction_res
    )

    try:
        response = await save_prediction(user_id, prediction_data, eye_photo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Saving prediction failed: {str(e)}")
    return response

@app.get("/api/predict/history")
async def get_all_predictions_history(token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token)
    user_id = current_user["userId"]
        
    list_predictions = await retrieve_all_predictions_history(user_id)
    return list_predictions

@app.get("/api/predict/history/{predict_id}")
async def get_predictions_history(predict_id: str, token: str = Depends(oauth2_scheme)):
    current_user = get_current_user(token)
    user_id = current_user["userId"]

    if not predict_id:
        raise HTTPException(status_code=400, detail="No Predict Id provided")
        
    prediction = await retrieve_predictions_history(user_id, predict_id)
    return prediction