# FastAPI 구조 정리 (CORS, GET, POST)

이 문서는 현재 프로젝트의 `api/main.py`를 기준으로 FastAPI의 기본 구조를 공부하기 쉽게 정리한 문서입니다.

---

## 1. 전체 구조 한눈에 보기

FastAPI 앱은 보통 아래 순서로 구성합니다.

1. 모듈 import
2. 전역 상수/경로 설정
3. `app = FastAPI(...)` 생성
4. 미들웨어 등록 (`CORS` 등)
5. 라우터 정의 (`@app.get`, `@app.post`)
6. 예외 처리 (`HTTPException`)

현재 프로젝트도 이 흐름을 따릅니다.

---

## 2. FastAPI 앱 생성

```python
app = FastAPI(title="EduTech Risk Prediction API")
```

- `title`은 Swagger 문서(`/docs`) 상단에 표시됩니다.
- FastAPI 객체가 라우팅, 문서화, 요청/응답 처리를 담당합니다.

---

## 3. CORS 설정

브라우저에서 React(예: `http://localhost:5173`)가 FastAPI 서버로 요청할 때, 출처(origin)가 다르면 CORS 허용이 필요합니다.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 핵심 옵션

- `allow_origins`: 허용할 프론트엔드 주소 목록
- `allow_credentials=True`: 쿠키/인증 헤더 허용
- `allow_methods=["*"]`: GET/POST 등 모든 메서드 허용
- `allow_headers=["*"]`: 모든 헤더 허용

### 현재 프로젝트 포인트

- 기본 localhost origin 목록을 두고,
- `ALLOWED_ORIGINS` 환경변수가 있으면 그것을 우선 사용하도록 되어 있습니다.
- 배포 환경에서는 `*`보다 명시적 origin 화이트리스트를 권장합니다.

---

## 4. GET 엔드포인트

GET은 주로 조회/상태 확인에 사용합니다.

```python
@app.get("/")
def root():
    return {"message": "EduTech Risk Prediction API"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

### GET 특징

- 서버 상태 확인, 데이터 조회에 적합
- 보통 요청 본문(body) 없이 사용
- path/query parameter를 통해 값을 전달

예시:

- `GET /download/{filename}`: 경로 변수(`filename`)를 받아 파일 응답 반환

---

## 5. POST 엔드포인트

POST는 서버에 데이터를 전송해 처리(생성/예측/업로드)할 때 사용합니다.

현재 프로젝트의 대표 예시는 `/predict` 입니다.

```python
@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    policy: str = Form(...),
    mode: str = "full",
):
    ...
```

### 파라미터 해석

- `file: UploadFile = File(...)`
  - multipart/form-data의 파일 필드
  - 필수값(`...`)
- `policy: str = Form(...)`
  - multipart/form-data의 일반 텍스트 필드
  - 필수값
- `mode: str = "full"`
  - 기본값이 있는 선택 파라미터

### 왜 `File()`/`Form()`을 쓰는가?

- 파일 업로드 요청은 일반 JSON body와 달리 `multipart/form-data`를 사용
- 따라서 파일/폼 필드를 명시적으로 구분해야 FastAPI가 올바르게 파싱합니다.

---

## 6. 예외 처리 패턴

```python
if file.content_type != "text/csv":
    raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")
```

- 잘못된 요청은 `HTTPException`으로 명확한 상태코드와 메시지를 반환
- 예:
  - `400`: 잘못된 입력
  - `404`: 리소스 없음
  - `500`: 서버 내부 오류

프로젝트에서는 전체 로직을 `try/except`로 감싸 예외를 `500`으로 반환합니다.

---

## 7. 학습용 최소 예제 (GET + POST + CORS)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

class PredictRequest(BaseModel):
    score: float
    absences: int

@app.post("/predict")
def predict(req: PredictRequest):
    if req.score < 0:
        raise HTTPException(status_code=400, detail="score must be >= 0")
    risk = "high" if req.score < 60 or req.absences > 10 else "low"
    return {"risk": risk}
```

---

## 8. 빠른 복습 체크리스트

1. FastAPI 객체 생성 후 미들웨어를 먼저 등록했는가?
2. 브라우저 연동 시 CORS origin을 정확히 설정했는가?
3. 조회는 GET, 처리/생성은 POST로 분리했는가?
4. 파일/폼 요청에서 `File()`/`Form()`을 사용했는가?
5. 실패 케이스에 `HTTPException` 상태코드를 명확히 정의했는가?

