from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models/logistic_model.joblib"

import pandas as pd
import joblib

from src.config import FEATURE_COLS
from src.preprocessing import preprocess_pipeline
from src.report_logic import (
    parse_policy_json,
    enrich_report,
    assign_risk_level,
    assign_action,
    safe_json_df,
)

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

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),   # '...'는 필수 항목임을 나타냄, Ellipsis는 한국어로 '생략'이라는 뜻
    policy: str = Form(...),   # multipart JSON 문자열
):
    try:
        # 1. CSV → DataFrame
        df_raw = pd.read_csv(file.file)

        # 2. 전처리
        df_processed = preprocess_pipeline(df_raw)

        # 3. 모델 로드
        model_path = PROJECT_ROOT / "models/logistic_model.joblib"
        model = joblib.load(model_path)

        X = df_processed[FEATURE_COLS]
        risk_proba = model.predict_proba(X)[:, 1]

        # 4. policy 파싱 + 검증
        policy_obj = parse_policy_json(policy)

        # 5. 리포트 생성
        df_result = df_processed.copy()

        df_result["risk_proba"] = risk_proba
        df_result["risk_level"] = df_result["risk_proba"].apply(assign_risk_level)
        df_result["action"] = df_result["risk_level"].apply(assign_action)

        # 공통 로직 호출
        df_result = enrich_report(df_result, policy_obj)

        # 6. JSON 안전 변환
        df_result = safe_json_df(df_result)

        return {
            "rows": len(df_result),
            "data": df_result.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
