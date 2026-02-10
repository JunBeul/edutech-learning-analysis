"""
Generate Risk Prediction Report

Usage:
python -m scripts.generate_prediction_report
"""

from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import pandas as pd

from src.config import FEATURE_COLS, REASON_THRESHOLDS, PARTICIPATION_LOW_MAX
from src.preprocessing import load_csv, preprocess_pipeline

DATA_PATH = PROJECT_ROOT / "data/dummy/dummy_midterm_like_labeled.csv"
MODEL_PATH = PROJECT_ROOT / "models/logistic_model.joblib"

OUTPUT_DIR = PROJECT_ROOT / "reports/tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def assign_risk_level(p: float) -> str:
    if p >= 0.70:
        return "High"
    if p >= 0.40:
        return "Medium"
    return "Low"


def assign_action(level: str) -> str:
    if level == "High":
        return "즉시 상담 및 보충학습 개입 필요"
    if level == "Medium":
        return "과제 참여 모니터링 및 사전 지도"
    return "일반 관찰 유지"

def build_reasons(row) -> str:
    reasons = []

    # 결석
    if pd.notna(row.get("absence_count")) and row["absence_count"] >= REASON_THRESHOLDS["absence_count_high"]:
        reasons.append("결석 횟수 높음")

    # 과제
    if pd.notna(row.get("assignment_count")) and row["assignment_count"] <= REASON_THRESHOLDS["assignment_count_low"]:
        reasons.append("과제 제출 부족")

    # 참여도
    if pd.notna(row.get("participation_level_num")) and row["participation_level_num"] <= PARTICIPATION_LOW_MAX:
        reasons.append("수업 참여도 낮음")

    # 중간/수행 성적
    if pd.notna(row.get("midterm_score")) and row["midterm_score"] < REASON_THRESHOLDS["midterm_score_low"]:
        reasons.append("중간고사 성적 낮음")

    if pd.notna(row.get("performance_score")) and row["performance_score"] < REASON_THRESHOLDS["performance_score_low"]:
        reasons.append("수행평가 성적 낮음")

    # 최대 3개만
    return ", ".join(reasons[:3]) if reasons else "특이 요인 없음"

def main() -> pd.DataFrame:
    df = load_csv(DATA_PATH)
    df_processed = preprocess_pipeline(df)

    X = df_processed[FEATURE_COLS]

    model = joblib.load(MODEL_PATH)
    risk_proba = model.predict_proba(X)[:, 1]

    df_result = df.copy()
    df_result["risk_proba"] = risk_proba
    df_result["risk_level"] = df_result["risk_proba"].apply(assign_risk_level)
    df_result["action"] = df_result["risk_level"].apply(assign_action)
    df_result["top_reasons"] = df_result.apply(build_reasons, axis=1)
    
    preferred_cols = [
        "student_id",
        "risk_proba",
        "risk_level",
        "top_reasons",
        "action",
    ]

    # 존재하는 컬럼만 유지 (입력 스키마 차이 방어)
    save_cols = [c for c in preferred_cols if c in df_result.columns] + [c for c in df_result.columns if c not in preferred_cols]
    df_result = df_result[save_cols]


    today = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"prediction_report_{today}.csv"
    df_result.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Saved: {output_path}")
    return df_result


if __name__ == "__main__":
    main()
