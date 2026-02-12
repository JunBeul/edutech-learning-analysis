from fastapi import FastAPI, File, UploadFile, HTTPException
from io import StringIO

import pandas as pd
import numpy as np

app = FastAPI(title="EduTech Risk Prediction API")

@app.get("/")
def root():
    return {"message": "EduTech Risk Prediction API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1) 확장자 최소 검증(엄격히 하려면 content-type도 같이 보지만 MVP에서는 확장자만)
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")

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

    preview_df = df.head(3).replace({np.nan: None})
    
    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "preview": preview_df.to_dict(orient="records"),
    }