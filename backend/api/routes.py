from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from backend.core.application_controller import ApplicationController
import shutil
import os
import json
import uuid

router = APIRouter()
controller = ApplicationController()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process the initial Excel file."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")

    # Save the file temporarily
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process with the controller
    result = controller.load_and_transform_data(file_path)

    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Failed to process file'))

    return {"message": "File processed successfully", "stats": result.get('stats')}

@router.get("/years/{season_type}")
def get_years(season_type: str):
    """Get available years for a specific season type (dry or rainy)."""
    if season_type not in ['dry', 'rainy']:
        raise HTTPException(status_code=400, detail="Invalid season type")



    years = controller.get_available_years(season_type)
    return {"years": years}

@router.get("/analyze")
def analyze_data(season_type: str, year: str = None):
    """Analyze flows for a given season and optional year."""
    if season_type not in ['dry', 'rainy']:
        raise HTTPException(status_code=400, detail="Invalid season type")



    result = controller.analyze_flows(season_type, year)

    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Failed to analyze flows'))

    # We need to sanitize the results for JSON (convert DataFrames/Series to dicts if any exist at the top level,
    # but based on the codebase, it seems to return dictionaries of primitives and lists/dicts)
    return {"results": result.get('results')}

@router.post("/predict")
def predict_data(season_type: str, year: str, model_name: str):
    """Predict flows."""
    if season_type not in ['dry', 'rainy']:
        raise HTTPException(status_code=400, detail="Invalid season type")

    model_map = {
        'random_forest': 'Random Forest',
        'xgboost': 'XGBoost',
        'linear_regression': 'Régression Linéaire',
        'sarima': 'SARIMA',
        'adaboost': 'AdaBoost'
    }
    actual_model_name = model_map.get(model_name, 'Random Forest')



    result = controller.predict_flows(season_type, year, actual_model_name)

    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('message', 'Prediction failed'))

    metrics = result.get('metrics', {})

    # Prepare predictions data for frontend chart
    # Predictions in results are often pandas Series or DataFrames which aren't JSON serializable directly
    predictions_test = result['results']['predictions']['test']

    actual = predictions_test['actual'].tolist() if hasattr(predictions_test['actual'], 'tolist') else list(predictions_test['actual'])
    predicted = predictions_test['predicted'].tolist() if hasattr(predictions_test['predicted'], 'tolist') else list(predictions_test['predicted'])
    # Get index for x-axis if possible
    index = predictions_test['actual'].index.astype(str).tolist() if hasattr(predictions_test['actual'], 'index') else list(range(len(actual)))

    return {
        "metrics": metrics,
        "chart_data": {
            "dates": index,
            "actual": actual,
            "predicted": predicted
        }
    }
