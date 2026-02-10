from __future__ import annotations

FEATURE_COLS = [
    "midterm_score",
    "performance_score",
    "assignment_count",
    "question_count",
    "night_study",
    "absence_count",
    "behavior_score",
    "participation_level_num",
]

# 위험 사유 생성용 임계값 (더미 기준, 실제 데이터에 맞게 조정 가능)
REASON_THRESHOLDS = {
    "absence_count_high": 5,
    "assignment_count_low": 2,
    "midterm_score_low": 50,
    "performance_score_low": 50,
    "question_count_low": 1,
    "behavior_score_low": -5,   # 상벌점 체계에 따라 조정
}

# participation_level_num 매핑이 3=상,2=중,1=하 라고 가정
PARTICIPATION_LOW_MAX = 1