# edutech-risk-prediction

정보·컴퓨터 교과에서 **최소성취수준 보장지도(최성보) 대상 학생을 학기 중간 시점에 사전 예측**하기 위한  
EduTech 데이터 분석 및 AI 예측 프로젝트입니다.

본 프로젝트는 교사가 예방지도를 위한 예비군을 선별해야 하는  
현장 업무 부담을 데이터 기반으로 경감하는 것을 목표로 합니다.

---

# 1. 프로젝트 배경

2022 개정 교육과정에서는 최소성취수준 보장지도가 도입되었습니다.

다음 조건에 해당하는 학생은 보충지도를 의무적으로 실시해야 합니다.

- 성취율 40% 미만
- 결석률 1/3 이상

문제는 학기 종료 후 성취율이 확정되기 때문에  
학기 중간 시점에는 위험군 선별 기준이 부재하다는 점입니다.

특히 정보·컴퓨터 교과는

- 모의고사 없음
- 수행평가 비중 높음
- 과정 중심 평가 구조

로 인해 사전 선별이 더욱 어렵습니다.

---

# 2. 프로젝트 목표

학기 중간 시점의 학습·행동 데이터를 기반으로  
최소성취수준 미도달 위험군을 조기 예측합니다.

---

# 3. 데이터 스키마 (Single Schema)

| Column              | Description               |
| ------------------- | ------------------------- |
| midterm_score       | 중간고사 성적             |
| final_score         | 기말고사 성적 (결측 허용) |
| performance_score   | 수행평가 성적             |
| assignment_count    | 과제 제출 횟수            |
| participation_level | 수업 참여도               |
| question_count      | 질문 횟수                 |
| night_study         | 야간자율학습 참여         |
| absence_count       | 결석 횟수                 |
| behavior_score      | 상벌점                    |

---

# 4. 더미 데이터 구성

경로:

```
data/dummy/
```

생성 파일:

- dummy_full.csv → 학기 말 가정 데이터
- dummy_midterm_like.csv → 학기 중간 가정 데이터
- dummy_full_labeled.csv
- dummy_midterm_like_labeled.csv
- data_dictionary.csv

---

# 5. 전처리 파이프라인

경로:

```
src/preprocessing.py
```

주요 기능:

- 단일 스키마 검증
- 결측 점수 자동 반영
- 참여도 인코딩
- 성취율 계산
- 위험군 라벨 생성

---

# 6. 탐색적 데이터 분석 (EDA)

노트북:

```
notebook/01_eda.ipynb
```

분석 내용:

1. 데이터 품질 점검
2. 결측 데이터 영향 분석
3. 위험군 분포 분석
4. 변수별 위험군 차이 분석
5. 조기 탐지 후보 변수 도출

---

# 7. 주요 발견점

위험군 학생은 다음 특성을 보였습니다.

- 결석 횟수 높음
- 과제 제출 횟수 낮음
- 수행평가 점수 낮음
- 참여도 낮음

→ 학기 중간 시점에서도 위험군 조기 탐지 가능

---

# 8. 산출물

## Figures

```
reports/figures/
├─ risk_rate_comparison.png
├─ achievement_rate_distribution.png
├─ eda_absence_vs_risk.png
├─ eda_assignment_vs_risk.png
├─ eda_performance_vs_risk.png
└─ eda_participation_vs_risk.png
```

## Tables

```
reports/tables/
├─ data_quality_report.csv
├─ desc_dummy_full_processed.csv
└─ desc_dummy_midterm_like_processed.csv
```

---

# 9. 향후 계획

- 위험군 분류 모델 구축
- 예측 정확도 평가
- 예방지도 자동 선별 시스템 구현

---

# 10. 개인정보 처리

- 실제 학생 데이터 비공개
- 더미 데이터만 저장소 포함
- 분석 결과는 집계·익명화하여 보고
