from fastapi import FastAPI, File, UploadFile, HTTPException
from io import StringIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models/logistic_model.joblib"

import joblib
import pandas as pd
import numpy as np
from math import floor

from src.preprocessing import preprocess_pipeline
from src.config import FEATURE_COLS, EVALUATION_POLICY

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
    
    # 6) 모델 로드
    def assign_risk_level(p: float) -> str:
        if p >= 0.70:
            return "High"
        if p >= 0.40:
            return "Medium"
        return "Low"
    
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=500, detail="모델 파일이 존재하지 않습니다.")
    model = joblib.load(MODEL_PATH)
    
    # 7) 예측 수행
    risk_proba = model.predict_proba(X)[:, 1]
    df_result = df_processed.copy()
    df_result["risk_proba"] = risk_proba
    df_result["risk_level"] = df_result["risk_proba"].apply(assign_risk_level)
    
    # 8) 리포트 생성 로직
    # 8.1) 참여도 위험 점수 계산 (하위 15%)
    def assign_action(level: str) -> str:
        if level == "High":
            return "즉시 상담 및 보충학습 개입 필요"
        if level == "Medium":
            return "과제 참여 모니터링 및 사전 지도"
        return "일반 관찰 유지"

    df_result["action"] = df_result["risk_level"].apply(assign_action)
    
    # 8.2) 참여도 종합(하위 15% + 점수 합산)
    q_assign = df_result["assignment_count"].quantile(0.15)
    q_question = df_result["question_count"].quantile(0.15)

    df_result["participation_risk_score"] = 0
    df_result.loc[df_result["assignment_count"] <= q_assign, "participation_risk_score"] += 1
    df_result.loc[df_result["question_count"] <= q_question, "participation_risk_score"] += 1
    df_result.loc[df_result["participation_level"] == "하", "participation_risk_score"] += 2

    df_result["participation_flag"] = (df_result["participation_risk_score"] >= 2).astype(int)
    
    # 8.3) 결석 한도/남은 결석 여유일 계산
    total_classes = int(EVALUATION_POLICY["total_classes"])
    absence_limit = floor(total_classes / 3)

    df_result["absence_limit"] = absence_limit

    absn = pd.to_numeric(df_result.get("absence_count"), errors="coerce").fillna(0).astype(int)
    df_result["remaining_absence_allowance"] = absence_limit - absn
    
    # 8.4) 점수 역산
    def clamp_score(x: float, smax: float) -> float:
        # 필요한 점수가 0 미만이면 0, 만점 초과면 만점으로 클램프
        if x < 0:
            return 0.0
        if x > smax:
            return float(smax)
        return float(x)
    
    def to_w(pct: float) -> float:
        return float(pct) / 100.0
    
    T = float(EVALUATION_POLICY["threshold"])

    mmax = float(EVALUATION_POLICY["midterm_max"])
    fmax = float(EVALUATION_POLICY["final_max"])
    pmax = float(EVALUATION_POLICY["performance_max"])

    wm = to_w(EVALUATION_POLICY["midterm_weight"])
    wf = to_w(EVALUATION_POLICY["final_weight"])
    wp = to_w(EVALUATION_POLICY["performance_weight"])
    
    w_sum = wm + wf + wp
    if abs(w_sum - 1.0) > 1e-6:
        raise ValueError(f"가중치 합이 100%가 아닙니다: {w_sum*100:.2f}%")
    
    def score_guidance(row: pd.Series) -> str:
    # 원본 점수(채워진 값일 수 있으므로, missing flag로 결측 여부 판단)
        mid = pd.to_numeric(row.get("midterm_score"), errors="coerce")
        fin = pd.to_numeric(row.get("final_score"), errors="coerce")
        perf = pd.to_numeric(row.get("performance_score"), errors="coerce")

        mid_miss = int(row.get("midterm_score_missing", 0)) == 1
        fin_miss = int(row.get("final_score_missing", 0)) == 1
        perf_miss = int(row.get("performance_score_missing", 0)) == 1

        # 중간까지 결측인 데이터는 현실적으로 안내가 애매하므로 메시지 축소
        if mid_miss or pd.isna(mid):
            return "중간고사 점수 정보가 없어 성취율 역산 안내를 제공할 수 없습니다."

        # 현재 확보된 기여(결측 항목은 제외)
        base = (mid / mmax) * wm
        if (not fin_miss) and pd.notna(fin):
            base += (fin / fmax) * wf
        if (not perf_miss) and pd.notna(perf):
            base += (perf / pmax) * wp

        # 이미 기준 충족이면 안내 불필요
        if base >= T:
            return "현재 입력된 점수 기준으로 성취율 40% 기준을 충족합니다."

        needed = T - base  # 추가로 필요한 비율 기여

        # 케이스 분기
        if fin_miss and (not perf_miss):
            # 기말만 결측 -> 기말 최소 점수
            req_final = (needed / wf) * fmax if wf > 0 else float("inf")
            req_final = clamp_score(req_final, fmax)
            return f"기말고사에서 최소 {req_final:.1f}점(/{fmax:.0f}) 이상 필요합니다."

        if perf_miss and (not fin_miss):
            # 수행만 결측 -> 수행 최소 점수
            req_perf = (needed / wp) * pmax if wp > 0 else float("inf")
            req_perf = clamp_score(req_perf, pmax)
            return f"수행평가에서 최소 {req_perf:.1f}점(/{pmax:.0f}) 이상 필요합니다."

        if fin_miss and perf_miss:
            # 둘 다 결측 -> 시나리오 2줄(사용자 친화)
            # 1) 수행 만점 가정 시 기말 필요
            base_perf_full = base + (1.0 * wp)  # 수행 만점 기여
            needed_final = max(0.0, T - base_perf_full)
            req_final = (needed_final / wf) * fmax if wf > 0 else float("inf")
            req_final = clamp_score(req_final, fmax)

            # 2) 기말 만점 가정 시 수행 필요
            base_final_full = base + (1.0 * wf)  # 기말 만점 기여
            needed_perf = max(0.0, T - base_final_full)
            req_perf = (needed_perf / wp) * pmax if wp > 0 else float("inf")
            req_perf = clamp_score(req_perf, pmax)

            return (
                f"[시나리오] 수행 만점 가정 시 기말 최소 {req_final:.1f}점(/{fmax:.0f}) 필요 / "
                f"기말 만점 가정 시 수행 최소 {req_perf:.1f}점(/{pmax:.0f}) 필요"
            )

        # 결측이 없는데도 base<T인 경우: 단순 안내
        return "현재 입력된 점수 기준으로 성취율 40% 미달입니다."

    df_result["score_guidance"] = df_result.apply(score_guidance, axis=1)
    
    # 7.5) top_reasons 생성
    def build_reasons(row: pd.Series) -> str:
        reasons = []

        absn = pd.to_numeric(row.get("absence_count"), errors="coerce")
        mid = pd.to_numeric(row.get("midterm_score"), errors="coerce")
        fin = pd.to_numeric(row.get("final_score"), errors="coerce")
        perf = pd.to_numeric(row.get("performance_score"), errors="coerce")

        fin_miss = int(row.get("final_score_missing", 0)) == 1
        perf_miss = int(row.get("performance_score_missing", 0)) == 1

        if pd.notna(absn) and absn >= 5:
            reasons.append("결석 횟수 높음")

        if pd.notna(mid) and mid < 50:
            reasons.append("중간고사 성적 낮음")

        if (not fin_miss) and pd.notna(fin) and fin < 50:
            reasons.append("기말고사 성적 낮음")

        if (not perf_miss) and pd.notna(perf) and perf < 50:
            reasons.append("수행평가 성적 낮음")

        if int(row.get("participation_flag", 0)) == 1:
            reasons.append("학습 참여도 저하(과제/질문/참여)")

        return ", ".join(reasons[:3]) if reasons else "특이 요인 없음"

    df_result["top_reasons"] = df_result.apply(build_reasons, axis=1)
    
    # 7) NaN JSON 방어
    df_result = df_result.replace({np.nan: None})
    
    response_cols = [
        "student_id",                   # 학번
        "risk_proba",                   # 위험 확률
        "risk_level",                   # 위험 수준
        "top_reasons",                  # 주요 위험 요인
        "score_guidance",               # 점수 역산 안내
        "action",                       # 권고 조치
        "absence_limit",                # 결석 한도
        "remaining_absence_allowance",  # 남은 결석 여유일
        "participation_risk_score",     # 참여도 위험 점수
        "participation_flag",           # 참여도 위험 플래그
    ]

    return {
        "rows": int(df_result.shape[0]),
        "results": df_result[response_cols].to_dict(orient="records"),
    }
