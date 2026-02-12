from fastapi import FastAPI, File, UploadFile, HTTPException
from io import StringIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models/logistic_model.joblib"

import joblib
import pandas as pd
import numpy as np

from src.preprocessing import preprocess_pipeline
from src.config import FEATURE_COLS

app = FastAPI(title="EduTech Risk Prediction API")

@app.get("/")
def root():
    return {"message": "EduTech Risk Prediction API"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =====================================
# main prediction logic
# =====================================

def assign_risk_level(p: float) -> str:
    if p >= 0.70:
        return "High"
    if p >= 0.40:
        return "Medium"
    return "Low"

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1) 확장자 최소 검증(엄격히 하려면 content-type도 같이 보지만 MVP에서는 확장자만)
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")     # raise <- 강제로 에러 발생시킴

    # 2) 업로드 파일 읽기(UTF-8-SIG 우선)
    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        # 학교 현장 CSV는 cp949 가능성이 있어 fallback, 복잡한 인코딩 탐지는 생략
        text = raw.decode("cp949", errors="replace")

    # 3) DataFrame 파싱
    try:
        df = pd.read_csv(StringIO(text))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV 파싱 실패: {e}")

    # 4) 전처리
    df_processed = preprocess_pipeline(df)
    
    # 5) 모델 입력 feature 구성
    try:
        X = df_processed[FEATURE_COLS]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"필수 컬럼 누락: {e}")
    
    # 6) 모델 로드 및 예측
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=500, detail="모델 파일이 존재하지 않습니다.")
    model = joblib.load(MODEL_PATH)
    
    risk_proba = model.predict_proba(X)[:, 1]
    df_result = df_processed.copy()
    df_result["risk_proba"] = risk_proba
    df_result["risk_level"] = df_result["risk_proba"].apply(assign_risk_level)
    
    # 7) NaN JSON 방어
    df_result = df_result.replace({np.nan: None})

    return {
        "rows": int(df_result.shape[0]),
        "results": df_result[
            ["student_id", "risk_proba", "risk_level"]
        ].to_dict(orient="records"),
    }