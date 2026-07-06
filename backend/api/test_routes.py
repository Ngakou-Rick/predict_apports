import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
import os
import shutil
import pandas as pd
import numpy as np

client = TestClient(app)

def test_fastapi_endpoints():
    # Make a dummy excel file using pandas
    dates = pd.date_range("2020-01-01", "2021-12-31")
    df = pd.DataFrame({
        "Date": dates,
        "Débits": np.random.uniform(50, 150, len(dates)),
        "Pluie": np.random.uniform(0, 20, len(dates)),
        "Tmax": np.random.uniform(25, 35, len(dates)),
        "Tmin": np.random.uniform(15, 25, len(dates)),
        "ETP": np.random.uniform(3, 8, len(dates))
    })

    os.makedirs("test_data", exist_ok=True)
    df.to_excel("test_data/dummy.xlsx", index=False)

    # Upload the file
    with open("test_data/dummy.xlsx", "rb") as f:
        response = client.post("/api/upload", files={"file": ("dummy.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})

    assert response.status_code == 200

    # Get years
    response = client.get("/api/years/dry")
    assert response.status_code == 200
    assert "years" in response.json()
    years = response.json()["years"]

    if len(years) > 0:
        year = years[0]
        # Analyze
        response = client.get(f"/api/analyze?season_type=dry&year={year}")
        assert response.status_code == 200

        # Predict
        response = client.post(f"/api/predict?season_type=dry&year={year}&model_name=random_forest")
        assert response.status_code == 200

    # Cleanup
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
