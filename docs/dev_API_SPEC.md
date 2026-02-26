# API 스펙 (dev_API_SPEC)

이 문서는 `backend/api/main.py` 기준의 실제 서버 API 동작을 상세하게 정리한 문서입니다.

---

- 루트
  - 서비스 안내: [README.md](../README.md)
  - 개발/운영/재현 가이드: [README_DEV.md](../README_DEV.md)

---

## 1. 개요

### Base URL

- 로컬 개발: `http://127.0.0.1:8000`
- 배포 환경: 서비스 도메인 기준 (예: `https://maplight.onrender.com`)

### 기술 스택

- Backend Framework: FastAPI
- 응답 형식: JSON (`/api/*` 대부분), CSV 파일 다운로드 (`/api/sample/*`, `/api/download/*`)
- 업로드 형식: `multipart/form-data` (`POST /api/predict`)

### 자동 문서(OpenAPI)

FastAPI 기본 설정을 사용하므로 아래 엔드포인트도 사용 가능합니다.

- `GET /docs` (Swagger UI)
- `GET /redoc`
- `GET /openapi.json`

단, `/{full_path:path}` 프론트 서빙 라우트는 `include_in_schema=False`로 OpenAPI에 노출되지 않습니다.

---

## 2. 공통 규칙

### 2.1 CORS

`ALLOWED_ORIGINS` 환경변수(쉼표 구분) 또는 기본값으로 CORS 허용 Origin을 설정합니다.

- 기본값
  - `http://localhost:5173`
  - `http://localhost:3000`

### 2.2 에러 응답 형식

FastAPI `HTTPException`을 사용하므로 기본적으로 아래 형태를 반환합니다.

```json
{
  "detail": "에러 메시지"
}
```

주의:

- `POST /api/predict` 내부에서 발생한 일부 검증 오류(`policy` 파싱/정책 검증 등)는 현재 구현상 `500`으로 래핑되어 반환됩니다.
- FastAPI 레벨의 파라미터 검증 실패(필수 form 누락 등)는 `422 Unprocessable Entity` 형식으로 반환됩니다.

### 2.3 인코딩 / 파일 저장

- 서버가 생성하는 예측 리포트 CSV는 `utf-8-sig` 인코딩으로 저장됩니다.
- 리포트 저장 경로는 `REPORT_DIR` 환경변수(기본값 `reports/tables`)를 사용합니다.

---

## 3. 데이터 계약 (업로드 CSV)

`POST /api/predict`의 `file`은 CSV 파일이어야 하며, 아래 컬럼을 기준으로 처리됩니다.

### 3.1 필수 컬럼

- `student_id`
- `midterm_score` (권장, 컬럼 자체 누락도 현재 구현상 허용)
- `final_score` (권장, 컬럼 자체 누락도 현재 구현상 허용)
- `performance_score` (권장, 컬럼 자체 누락도 현재 구현상 허용)
- `assignment_count`
- `participation_level`
- `question_count`
- `night_study`
- `absence_count`
- `behavior_score`

### 3.2 컬럼별 의미 / 타입

| 컬럼명                | 타입(권장)      | 설명                      |
| --------------------- | --------------- | ------------------------- |
| `student_id`          | string / int    | 학생 식별자               |
| `midterm_score`       | number or empty | 중간고사 점수 (결측 허용) |
| `final_score`         | number or empty | 기말고사 점수 (결측 허용) |
| `performance_score`   | number or empty | 수행평가 점수 (결측 허용) |
| `assignment_count`    | number          | 과제 제출/수행 횟수       |
| `participation_level` | string          | 수업 참여도(문자열)       |
| `question_count`      | number          | 질문 횟수                 |
| `night_study`         | number (0/1)    | 야간 학습 여부            |
| `absence_count`       | number          | 결석 횟수                 |
| `behavior_score`      | number          | 행동/태도 점수            |

### 3.3 처리 시 참고 동작

- 숫자형 컬럼은 `pd.to_numeric(..., errors="coerce")`로 변환되며, 변환 실패 값은 `NaN` 처리됩니다.
- 점수 컬럼(`midterm/final/performance`)은 결측 플래그(`*_missing`)가 생성됩니다.
- 점수 컬럼이 아예 없으면 내부에서 해당 컬럼을 생성(`NaN`)하고 `*_missing = 1`로 처리합니다.
- `participation_level`은 문자열 trim 후 숫자형 보조 컬럼(`participation_level_num`)으로 인코딩됩니다.
- 중복 행은 제거됩니다.

---

## 4. 평가 정책(`policy`) 스펙

`POST /api/predict`에서 `policy`는 `multipart/form-data`의 문자열 필드이며, JSON 문자열이어야 합니다.

### 4.1 JSON 스키마

```json
{
  "threshold": 0.4,
  "midterm_max": 100,
  "midterm_weight": 40,
  "final_max": 100,
  "final_weight": 40,
  "performance_max": 100,
  "performance_weight": 20,
  "total_classes": 160
}
```

### 4.2 필수 키

- `threshold`
- `midterm_max`
- `midterm_weight`
- `final_max`
- `final_weight`
- `performance_max`
- `performance_weight`
- `total_classes`

### 4.3 검증 규칙 (현재 구현)

- `0 < threshold < 1`
- `*_max > 0`
- `midterm_weight + final_weight + performance_weight == 100`
- 모든 `*_weight >= 0`
- `total_classes >= 1` (정수 변환 후 검증)

주의:

- 검증 실패 시 내부적으로 `ValueError`가 발생하고, 현재 API 구현에서는 `500`으로 반환됩니다.

---

## 5. 엔드포인트 상세

### 5.1 `GET /`

#### 설명

- 프론트엔드 빌드 산출물(`client/dist/index.html`)이 있으면 해당 HTML을 반환합니다.
- 없으면 API 식별용 JSON 메시지를 반환합니다.

#### 응답 (프론트 빌드 없음)

`200 OK`

```json
{
  "message": "EduTech Risk Prediction API"
}
```

#### 응답 (프론트 빌드 있음)

- `200 OK`
- `text/html` (`FileResponse`)

---

### 5.2 `GET /api/health`

#### 설명

서버 상태 확인용 헬스체크 엔드포인트입니다.

#### 응답

`200 OK`

```json
{
  "status": "ok"
}
```

---

### 5.3 `GET /api/sample/dummy-midterm-like-labeled`

#### 설명

업로드 스키마 예시용 더미 CSV 파일을 다운로드합니다.

#### 성공 응답

- `200 OK`
- `Content-Type: text/csv`
- 첨부 파일명: `DUMMY_DATA_PATH`의 파일명

#### 실패 응답

`404 Not Found`

```json
{
  "detail": "Dummy CSV file not found."
}
```

---

### 5.4 `POST /api/predict`

#### 설명

CSV 업로드 + 평가 정책(`policy`)을 받아 전처리/모델 추론/리포트 확장을 수행하고:

- 결과 JSON 반환
- 서버에 리포트 CSV 저장
- 다운로드 URL 제공

#### 요청

##### Query Parameters

| 이름   | 타입   | 필수 | 기본값 | 설명                                                    |
| ------ | ------ | ---- | ------ | ------------------------------------------------------- |
| `mode` | string | 선택 | `full` | 응답 `data` 배열 컬럼 범위 제어 (`compact`면 축약 응답) |

현재 구현 기준:

- `mode == "compact"`일 때만 compact 응답
- 그 외 모든 값은 `full`처럼 동작

##### Body (`multipart/form-data`)

| 필드명   | 타입          | 필수 | 설명                  |
| -------- | ------------- | ---- | --------------------- |
| `file`   | file (CSV)    | 필수 | 업로드 CSV            |
| `policy` | string (JSON) | 필수 | 평가 정책 JSON 문자열 |

##### 요청 예시 (cURL)

```bash
curl -X POST "http://127.0.0.1:8000/api/predict?mode=compact" \
  -F "file=@data/dummy/dummy_midterm_like_labeled.csv;type=text/csv" \
  -F "policy={\"threshold\":0.4,\"midterm_max\":100,\"midterm_weight\":40,\"final_max\":100,\"final_weight\":40,\"performance_max\":100,\"performance_weight\":20,\"total_classes\":160}"
```

#### 처리 흐름 (서버 내부)

1. 업로드 파일 `content_type`이 정확히 `text/csv`인지 검사
2. CSV 로드 (`pandas.read_csv`)
3. 전처리 파이프라인 수행 (`preprocess_pipeline`)
4. 모델 파일 로드 (`joblib.load`)
5. `FEATURE_COLS` 기준으로 위험 확률 예측 (`predict_proba`)
6. 위험 등급 / 액션 / 사유 / 점수 가이드 / 결석 허용치 등 리포트 컬럼 확장
7. 전체 결과를 CSV로 저장 (`reports/tables/...`)
8. JSON 응답 반환 (`data`, `report_url` 포함)

#### 성공 응답 (공통 메타)

`200 OK`

```json
{
  "rows": 100,
  "report_filename": "prediction_report_20260226_235959_ab12cd34.csv",
  "report_url": "/api/download/prediction_report_20260226_235959_ab12cd34.csv",
  "data": [
    {
      "student_id": "S001",
      "risk_level": "Medium",
      "risk_proba": 0.5231
    }
  ]
}
```

##### 응답 필드 설명

| 필드명            | 타입          | 설명                               |
| ----------------- | ------------- | ---------------------------------- |
| `rows`            | integer       | 전체 결과 행 수 (`len(df_result)`) |
| `report_filename` | string        | 서버에 저장된 CSV 파일명           |
| `report_url`      | string        | 리포트 다운로드 API 상대 경로      |
| `data`            | array<object> | `mode`에 따른 결과 행 배열         |

#### `mode=compact` 응답 스키마 (`data[*]`)

`compact` 모드에서는 아래 핵심 컬럼만 반환합니다.

- `student_id`
- `risk_level`
- `risk_proba`
- `top_reasons`
- `score_guidance`
- `action`
- `remaining_absence_allowance`

예시:

```json
{
  "student_id": "S001",
  "risk_level": "High",
  "risk_proba": 0.8123,
  "top_reasons": "위험 사유 문자열",
  "score_guidance": "점수 가이드 문구",
  "action": "개입 권고 문구",
  "remaining_absence_allowance": 3
}
```

#### `mode=full` 응답 스키마 (`data[*]`)

`full` 모드에서는 전처리 결과 + 추론 결과 + 리포트 확장 컬럼 전체를 반환합니다.
실제 컬럼(현재 코드 기준)은 다음과 같습니다.

##### 원본/전처리 컬럼

- `student_id`
- `midterm_score`
- `final_score`
- `performance_score`
- `assignment_count`
- `participation_level`
- `question_count`
- `night_study`
- `absence_count`
- `behavior_score`
- `at_risk` (입력 CSV에 존재하면 유지됨)
- `midterm_score_missing`
- `final_score_missing`
- `performance_score_missing`
- `participation_level_num`
- `achievement_rate`

##### 추론/리포트 확장 컬럼

- `risk_proba`
- `risk_level`
- `action`
- `participation_risk_score`
- `participation_flag`
- `absence_limit`
- `remaining_absence_allowance`
- `score_guidance`
- `top_reasons`

#### 주요 파생 컬럼 규칙

##### `risk_level`

- `High`: `risk_proba >= 0.70`
- `Medium`: `0.40 <= risk_proba < 0.70`
- `Low`: `risk_proba < 0.40`

##### `absence_limit`, `remaining_absence_allowance`

- `absence_limit = floor(total_classes / 3)`
- `remaining_absence_allowance = absence_limit - absence_count`

##### `top_reasons` (최대 3개)

아래 조건을 기준으로 사유 문자열을 조합합니다.

- 결석 횟수 높음 (`absence_count >= 5`)
- 중간고사 점수 낮음 (`midterm_score < 50`)
- 기말고사 점수 낮음 (`final_score < 50`, 결측 제외)
- 수행평가 점수 낮음 (`performance_score < 50`, 결측 제외)
- 참여위험 플래그(`participation_flag == 1`)

##### `score_guidance`

`policy`의 만점/반영비율/기준치(`threshold`)를 사용해 학생별 점수 달성 가이드를 문자열로 생성합니다.
결측 상태(기말/수행 없음)에 따라 안내 문구가 달라집니다.

#### 실패 응답

##### `400 Bad Request`

CSV 이외 파일 업로드 시

```json
{
  "detail": "Only CSV files are supported."
}
```

##### `422 Unprocessable Entity`

예시:

- `file` form 필드 누락
- `policy` form 필드 누락

FastAPI 기본 검증 오류 형식으로 반환됩니다.

##### `500 Internal Server Error`

예시 원인:

- 모델 파일 없음 (`MODEL_PATH`)
- CSV 파싱 실패
- 전처리 스키마 검증 실패(필수 컬럼 누락 등)
- `policy` JSON 파싱/검증 실패 (현재 구현상 500으로 래핑)
- 예측/리포트 생성 중 예외

응답 예시:

```json
{
  "detail": "Model file not found: D:\\workSpace\\edutech-risk-prediction\\models\\logistic_model.joblib"
}
```

#### 부수효과 (Side Effects)

- 서버가 `REPORT_DIR`에 리포트 CSV를 생성합니다.
- 파일명 패턴: `prediction_report_{YYYYMMDD_HHMMSS}_{8자리토큰}.csv`

---

### 5.5 `GET /api/download/{filename}`

#### 설명

`POST /api/predict`로 생성된 리포트 CSV를 다운로드합니다.

#### Path Parameters

| 이름       | 타입   | 필수 | 설명                     |
| ---------- | ------ | ---- | ------------------------ |
| `filename` | string | 필수 | 다운로드할 리포트 파일명 |

#### 보안 제약 (경로 이탈 방지)

서버는 `(REPORT_DIR / filename).resolve()` 결과가 실제로 `REPORT_DIR` 바로 아래 파일인지 검증합니다.
따라서 `../` 경로 이탈 시도는 허용되지 않습니다.

#### 성공 응답

- `200 OK`
- `Content-Type: text/csv`
- 첨부 파일명: 요청한 `filename`

#### 실패 응답

`404 Not Found`

```json
{
  "detail": "Report file not found."
}
```

---

### 5.6 `GET /{full_path:path}` (프론트엔드 정적/SPA 서빙, 문서 비노출)

#### 설명

프론트 빌드 산출물이 있을 때 SPA 라우팅/정적 파일 서빙을 처리하는 fallback 라우트입니다.

동작 규칙:

1. `client/dist/index.html`이 없으면 `404`
2. 요청 경로가 `/api` 또는 `/api/...`이면 fallback으로 처리하지 않고 `404`
3. `client/dist/{full_path}`가 실제 파일이면 해당 파일 반환
4. 그 외는 `index.html` 반환 (SPA 클라이언트 라우팅용)

#### 실패 응답 예시

프론트 빌드 미존재:

```json
{
  "detail": "Frontend build not found."
}
```

API 경로 오타:

```json
{
  "detail": "API endpoint not found."
}
```

---

## 6. 환경변수와 API 동작 영향

| 환경변수          | 기본값                                      | API 영향                           |
| ----------------- | ------------------------------------------- | ---------------------------------- |
| `APP_TITLE`       | `EduTech Risk Prediction API`               | `GET /` 메시지, FastAPI title      |
| `MODEL_PATH`      | `models/logistic_model.joblib`              | `POST /api/predict` 모델 로딩 경로 |
| `REPORT_DIR`      | `reports/tables`                            | 리포트 저장/다운로드 대상 폴더     |
| `DUMMY_DATA_PATH` | `data/dummy/dummy_midterm_like_labeled.csv` | 샘플 CSV 다운로드 대상             |
| `FRONTEND_DIST`   | `client/dist`                               | 루트/SPA 정적 파일 서빙 기준 경로  |
| `ALLOWED_ORIGINS` | 로컬 기본 2개                               | CORS 허용 Origin 목록              |

---

## 7. 프론트엔드 연동 메모

`client/src/shared/api.ts` 기준 현재 프론트는 다음 방식으로 호출합니다.

- `POST /api/predict`
  - `multipart/form-data`
  - `policy`는 객체를 `JSON.stringify`한 문자열로 전송
  - `mode` 쿼리 파라미터 사용 (`full`/`compact`)
- `report_url`은 상대 경로(`/api/download/...`)로 받아 프론트에서 base URL과 결합
- 더미 CSV 다운로드는 `GET /api/sample/dummy-midterm-like-labeled`

---

## 8. 개선 포인트

현재 구현 기준으로 확인된 동작이며, 필요 시 향후 개선 대상입니다.

- `policy` 파싱/검증 실패를 `400`으로 명확히 구분 반환
- CSV MIME 타입 허용 범위 확대 (`application/vnd.ms-excel` 등)
- `mode` 허용값 검증 (`full|compact` 외 값 400 처리)
- `POST /api/predict` 요청/응답 Pydantic 스키마화(OpenAPI 품질 개선)
