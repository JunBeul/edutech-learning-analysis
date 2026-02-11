# Technical Issues & Resolutions — Risk Prediction Project

본 문서는 위험군 예측 모델 개발 과정에서 발생한 주요 기술적 문제와 해결 과정을 기록한다.
실제 데이터 환경(학기 중간/말 혼재) 대응을 위해 설계 구조를 반복 개선하였다.

---

## 1. 점수 결측치로 인한 모델 입력 오류

### 문제

학기 중간 스냅샷 데이터에서 다음 컬럼이 전부 NaN 상태로 존재:

- final_score
- performance_score

Logistic Regression 입력 시 NaN 포함으로 학습/예측 실패.

### 원인

모델은 NaN 입력을 허용하지 않음.
또한 median/mean 계산도 all-NaN 컬럼에서는 작동하지 않음.

### 해결

전처리 단계에 fallback 로직 추가:

- all-NaN 컬럼은 0으로 채움
- 일반 결측은 median/mean 사용

---

## 2. 결측을 0으로 채울 때 발생한 의미 왜곡

### 문제

기말고사 미실시(결측) 학생과 실제 0점 학생이 동일 값으로 처리됨.

### 영향

모델이 결측을 “낮은 성적”으로 잘못 학습할 가능성 발생.

### 해결

결측 플래그 컬럼 추가:

- final_score_missing
- performance_score_missing
- midterm_score_missing

모델은 점수 + 결측 여부를 동시에 학습.

---

## 3. 단일 스키마 대응 문제

### 문제

학기 중간 데이터에는 다음이 아예 존재하지 않을 수 있음:

- performance_score

스키마 검증 단계에서 오류 발생.

### 해결

파이프라인에서 자동 생성 처리:

- 컬럼이 없으면 NaN 생성
- missing_flag = 1 부여

---

## 4. 모델 Feature 불일치 오류

### 문제

FEATURE_COLS 변경 후 기존 모델 사용 시:

- 입력 차원 불일치
- 예측 실패

### 해결

1. 모델 재학습 필수화
2. 예측 시 feature 정렬 코드 추가:

```python
feature_cols = getattr(model, "feature_names_in_", FEATURE_COLS)
X = df.reindex(columns=feature_cols)
```

---

## 5. 결측 채움 이후 사유 분석 오류

### 문제

fill_missing 이후에는 모든 점수가 존재.

따라서:

- “기말 성적 낮음” 사유가
- 실제 결측 학생에게도 표시됨

### 해결

결측 여부를 채우기 전 기준으로 보존:

- basic_cleaning 결과 사용
- missing_map 생성
- reason 생성 시 결측 제외

---

## 6. Participation 지표 해석 한계

### 문제

고정 임계값 기준은 학교별 편차 반영 불가.

### 해결

하위 15% 기반 상대 평가로 전환:

- 과제 제출
- 질문 횟수
- 참여도(상/중/하)

합산 점수 기반 risk flag 생성.

---

## 7. 회귀 테스트 필요성 인지

### 문제

전처리 변경 시 기존 기능이 무의식적으로 붕괴 가능.

### 해결

Smoke Test 스크립트 작성:

- 결측 채움 검증
- 라벨 생성 검증
- 플래그 생성 검증

---

# Summary

| 문제 유형      | 해결 전략      |
| -------------- | -------------- |
| 점수 결측      | fallback fill  |
| 결측 왜곡      | missing flag   |
| 컬럼 부재      | 자동 생성      |
| feature 불일치 | 재정렬         |
| 사유 오류      | 원본 기준 판정 |
| 참여도 편차    | 상대 평가      |
| 회귀 위험      | smoke test     |

---

본 문서는 데이터 불완전성 환경에서 ML 모델을 안정적으로 운영하기 위한 설계 개선 기록으로 활용된다.
