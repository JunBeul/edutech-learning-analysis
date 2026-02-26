# 개발/운영/재현 가이드 (README_DEV)

프로젝트를 로컬에서 실행하고, 운영 환경 기준으로 점검하고, 클린 클론 상태에서 재현하기 위한 문서입니다.
프로젝트 배경/성과 중심 설명은 루트 README를 참고하고, 상세 API/구조 문서는 본 문서 하단 링크를 참고하세요.

- 서비스 URL: https://maplight.onrender.com
- 루트 README: [`README.md`](README.md)

---

## INDEX

1. 실행 환경 준비
2. 환경변수 설정
3. 로컬 실행 방법
4. Docker/배포
5. API SPEC
6. 프로젝트 구조

---

## 1. 실행 환경 준비

### 요구 사항

- Python 3.11+
- Node.js 20+

### 가상환경 생성/활성화

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 패키지 설치

```bash
pip install -r requirements.txt
npm install
npm --prefix client install
```

> 참고:
>
> - 루트 `npm install`은 통합 개발 스크립트(`concurrently`) 실행에 필요합니다.
> - `client` 의존성은 별도로 설치해야 프론트가 실행됩니다.

---

## 2. 환경변수 설정

### 루트 `.env` (백엔드)

`.env.example` 기준

```env
APP_TITLE=EduTech Risk Prediction API
MODEL_PATH=models/logistic_model.joblib
REPORT_DIR=reports/tables
DUMMY_DATA_PATH=data/dummy/dummy_midterm_like_labeled.csv
FRONTEND_DIST=client/dist
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8000
```

파일 생성 예시:

Linux/macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### `client/.env` (프론트)

`client/.env.example` 기준

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
# VITE_DUMMY_CSV_URL=https://example.com/dummy_midterm_like_labeled.csv
```

파일 생성 예시:

Linux/macOS:

```bash
cp client/.env.example client/.env
```

Windows PowerShell:

```powershell
Copy-Item client/.env.example client/.env
```

> 설정 팁:
>
> - 로컬 개발에서는 `VITE_API_BASE_URL=http://127.0.0.1:8000` 권장
> - 배포/프록시 환경에서 same-origin으로 붙일 때는 빈 값 전략을 사용할 수 있음(빌드 구성 기준)

---

## 3. 로컬 실행 방법

### 모델 생성

`models/logistic_model.joblib`가 없으면 `POST /api/predict`에서 `500` 에러가 발생합니다.

```bash
python backend/scripts/train_model.py
```

### 통합 개발 서버 (백+프론트 동시 실행)

```bash
npm run dev
```

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

### 개별 실행

```bash
npm run dev:back
npm run dev:front
```

### 기본 동작 확인 (빠른 확인)

- 헬스체크: `GET http://127.0.0.1:8000/api/health`
- 샘플 CSV 다운로드: `GET http://127.0.0.1:8000/api/sample/dummy-midterm-like-labeled`
- 프론트 접속: `http://localhost:5173`

### 기능 재현 확인

1. `GET /api/health` 확인
2. 샘플 CSV 다운로드 확인
3. 프론트에서 더미 CSV 업로드 + 평가 정책 입력
4. 예측 결과 테이블 확인
5. 리포트 CSV 다운로드 확인

### 선택 검증 (전처리 스모크 테스트)

```bash
python backend/scripts/smoke_test_preprocessing.py
```

---

## 4. Docker/배포

### 4.1 Docker 이미지 빌드 (로컬 검증용)

```bash
docker build -t edutech-risk-prediction .
```

설명:

- Dockerfile은 멀티 스테이지 빌드입니다.
- 1단계에서 `client/`를 빌드해 `client/dist` 생성
- 2단계에서 Python 런타임 + FastAPI + 정적 파일 서빙 구성
- 빌드 중 기본 모델(`models/logistic_model.joblib`)을 생성합니다.

### 4.2 Docker 컨테이너 실행 (로컬)

```bash
docker run --rm -p 8000:8000 edutech-risk-prediction
```

접속:

- 앱/루트: `http://127.0.0.1:8000`
- 헬스체크: `http://127.0.0.1:8000/api/health`

### 4.3 배포 운영 체크포인트 (Render 기준)

- 단일 Web Service에서 FastAPI + 프론트 정적 파일(`client/dist`) 동시 서빙
- `PORT`는 플랫폼(Render) 주입값 사용
- 배포 후 최소 확인:
  - `GET /api/health`
  - 루트(`/`) 접속 시 프론트 로딩
  - `POST /api/predict` 동작
  - 리포트 다운로드(`GET /api/download/{filename}`) 동작

---

## 5. API SPEC (링크)

- 상세 API 문서: [`docs/dev_API_SPEC.md`](docs/dev_API_SPEC.md)

---

## 6. 프로젝트 구조 (링크)

- 상세 구조 문서: [`docs/dev_PROJECT_STRUCTURE.md`](docs/dev_PROJECT_STRUCTURE.md)

---
