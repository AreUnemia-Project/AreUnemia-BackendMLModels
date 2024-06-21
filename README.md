# AreUnemia-BackendMLModels
This is the API for AreUnemia Application Machine Learning API. It's a RESTful API that provides predictions and retrieve prediction histories based on users image input.

## Build
- Fast API
- Python
- JWT Token
- Google Cloud Firestore
- TensorFlow
- OpenCV

## Installation

Below is the first step consist of instructions on installing and setting up your app.

Clone Repository
```bash
  git clone https://github.com/AreUnemia-Project/AreUnemia-BackendMLModels.git
```

Create and activate .env file
```bash
  py -m venv env
  env\Scripts\activate.bat
```

Install Dependencies
```bash
  pip install -r requirements.txt
```

Make a config file and fill it with service accounts json for Google Cloud Storage & Google Cloud Firestore
```bash
  mkdir config
  # After created, fill it with json service accounts
```

Fill the .env file
```bash
  FIRESTORE_CREDENTIALS= # Path to json firestore service account
  STORAGE_CREDENTIALS= # Path to json cloud storage service account
  SECRET_KEY= # Provide JWT secret
```

Run in localhost
```bash
  fastapi dev main.py
```

## Configuration
Create a configuration folder named "config" that contains the following:

- Secret Key for JWT Token (the same secret key from the other AreUnemia API)
- Path to JSON Firestore Service Account
- Path to JSON Cloud Storage Service Account

## API Endpoints
Base URL: http://127.0.0.1:8000

Deployment URL: https://fastapi-app-3cv52zngvq-et.a.run.app

## Predictions
| Endpoint | Parameter | Body | Method    | Description                |
| :--------|:-------- | :------- |:------- | :------------------------- |
| /api/predict |`-`| eye_photo, questionnaire_answers| `POST` | Submit Prediction |
| /api/predict/history/{prediction_id} | prediction_id |`-`| `GET` | Retrieve Users' Prediction History from Prediction ID |
| /api/predict/history |`-`|`-`| `GET` | Retrieve Users' All Prediction Histories |