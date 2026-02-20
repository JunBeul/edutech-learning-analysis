# 배포 전 환경변수/하드코딩 점검 가이드

## 1. 목표
- 배포 환경마다 달라지는 값(URL, 파일 경로, CORS origin)을 코드에서 분리한다.
- 프론트/백엔드 하드코딩을 줄여서 재배포 시 코드 수정 없이 환경변수만 바꿀 수 있게 만든다.

## 2. 이번 프로젝트에서 적용한 변경

### 백엔드 (`backend/api/main.py`)
- `APP_TITLE`, `MODEL_PATH`, `REPORT_DIR`, `DUMMY_DATA_PATH`, `ALLOWED_ORIGINS`를 환경변수로 받도록 변경
- 하드코딩된 모델 경로(`models/logistic_model.joblib`)를 `MODEL_PATH`로 치환
- 하드코딩된 리포트 경로(`reports/tables`)를 `REPORT_DIR`로 치환
- 하드코딩된 더미 파일 외부 URL 의존을 없애기 위해 `GET /sample/dummy-midterm-like-labeled` 엔드포인트 추가
- `/download/{filename}`에 디렉터리 이탈(path traversal) 방지 검증 추가

### 프론트엔드
- `client/src/shared/api.ts`
  - `buildApiUrl()` 유틸 추가 (base URL + path 결합 표준화)
  - `DUMMY_CSV_URL`을 환경변수(`VITE_DUMMY_CSV_URL`) 또는 백엔드 샘플 엔드포인트로 결정
- `client/src/pages/LandingPage.tsx`
  - GitHub raw URL 하드코딩 제거
- `client/src/components/dashboard/DashboardHeader.tsx`
  - 다운로드 URL 생성 시 `buildApiUrl(reportUrl)` 사용
- `client/src/components/dashboard/MobileFloatingNav.tsx`
  - 다운로드 URL 생성 시 `buildApiUrl(reportUrl)` 사용
- `client/src/vite-env.d.ts`
  - `VITE_DUMMY_CSV_URL` 타입 추가

### 환경변수 샘플 파일
- 루트 `.env.example` 추가 (백엔드용)
- `client/.env.example` 확장 (프론트용)

## 3. 환경변수 정의

### 백엔드 (`.env`)
```env
APP_TITLE=EduTech Risk Prediction API
MODEL_PATH=models/logistic_model.joblib
REPORT_DIR=reports/tables
DUMMY_DATA_PATH=data/dummy/dummy_midterm_like_labeled.csv
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 프론트 (`client/.env`)
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
# Optional
# VITE_DUMMY_CSV_URL=https://example.com/dummy_midterm_like_labeled.csv
```

## 4. 배포 전 점검 절차 (실전 순서)

1. 하드코딩 후보 검색
```bash
rg -n "(http://|https://|localhost|API_KEY|SECRET|PASSWORD|TOKEN|C:\\\\|D:\\\\)" backend/api client backend/src backend/scripts
```

2. 값 분류
- 환경별로 바뀌는 값: 환경변수로 분리
- 고정 비즈니스 규칙: 코드 상수 유지

3. 백엔드 분리
- 경로/Origin/앱 메타데이터를 env로 이동
- 파일 경로는 상대경로 입력 시 프로젝트 루트 기준으로 resolve

4. 프론트 분리
- API URL 결합을 공통 유틸 하나로 통일
- 외부 리소스 URL도 env override 가능하게 구성

5. 샘플 env 문서화
- `.env.example` 파일에 기본값/옵션값 정리
- 누락 시 실패하는 필수값 여부를 명시

6. 최소 검증
```bash
python - <<'PY'
import ast, pathlib
ast.parse(pathlib.Path("backend/api/main.py").read_text(encoding="utf-8"))
print("backend/api/main.py syntax ok")
PY

npm --prefix client run build
```

## 5. 배포 직전 체크리스트
- [ ] 민감정보(API 키, 비밀번호, 토큰)가 코드/리포지토리에 없는가
- [ ] `localhost`, 개인 PC 절대경로가 런타임 코드에 남아있지 않은가
- [ ] CORS origin이 실제 배포 도메인으로 설정되었는가
- [ ] 프론트 `VITE_API_BASE_URL`이 실제 백엔드를 가리키는가
- [ ] 모델/리포트 디렉터리 경로가 서버 파일시스템에서 유효한가
- [ ] 빌드/기본 실행이 성공하는가

## 6. 자주 하는 실수
- 프론트 `.env`를 바꿨지만 dev 서버 재시작을 안 해서 값이 반영되지 않음
- `ALLOWED_ORIGINS`를 쉼표 없이 넣어서 CORS 실패
- 백엔드 상대경로 기준이 실행 위치 기준이라고 착각 (프로젝트 루트 기준으로 통일 필요)
- 예시 파일 다운로드를 외부 URL에만 의존해서, 네트워크 정책에 따라 실패


