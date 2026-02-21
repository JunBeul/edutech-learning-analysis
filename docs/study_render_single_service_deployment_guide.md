# Render 단일 서비스 배포 가이드 (Docker 기준)

이 문서는 현재 프로젝트를 기준으로,  
`FastAPI + React 정적 파일`을 **Render 단일 서비스**로 배포하는 전 과정을 정리한 스터디 문서입니다.

---

## 1. 배포 목표

- 프론트/백엔드를 분리하지 않고 **하나의 컨테이너**로 배포
- 프론트는 FastAPI가 `client/dist`를 정적 서빙
- API는 `/api/*` 경로로 고정
- 업로드 -> 예측 -> 대시보드 이동까지 정상 동작 확인

---

## 2. 현재 프로젝트 배포 구조

### 백엔드
- FastAPI 엔드포인트
  - `GET /api/health`
  - `POST /api/predict`
  - `GET /api/download/{filename}`
  - `GET /api/sample/dummy-midterm-like-labeled`
- `GET /`은 React `index.html` 서빙
- SPA fallback(`/{full_path:path}`) 적용

### 프론트
- `buildApiUrl()`로 API URL 생성
- `VITE_API_BASE_URL`이 비어 있으면 상대경로(`/api/...`) 사용

### Dockerfile
- 멀티 스테이지 빌드
  - Node 스테이지: React 빌드
  - Python 스테이지: FastAPI 실행
- `EXPOSE 8000`
- 컨테이너 시작 시 `uvicorn` 실행

---

## 3. 배포 전 로컬 체크

### 3.1 Docker 빌드
```bash
docker build -t edutech-risk-prediction:local .
```

### 3.2 Docker 실행
```bash
docker run --rm -d -p 8000:8000 --name edutech-app edutech-risk-prediction:local
```

### 3.3 동작 확인
- 브라우저: `http://localhost:8000`
- 헬스체크: `http://localhost:8000/api/health`

예상 응답:
```json
{"status":"ok"}
```

### 3.4 종료
```bash
docker stop edutech-app
```

---

## 4. Render 배포 절차 (UI 기준)

## 4.1 준비
1. 변경사항 커밋
2. 원격 저장소 push
3. Render 계정 로그인

## 4.2 서비스 생성
1. `New +` -> `Web Service`
2. GitHub 저장소 연결
3. 브랜치 선택
4. Runtime은 Dockerfile 자동 인식 상태로 진행

## 4.3 주요 설정값
- `Name`: 원하는 서비스명
- `Region`: 가까운 리전 선택
- `Branch`: 배포 대상 브랜치
- `Instance Type`: Free(포트폴리오 용도)
- `Auto-Deploy`: 필요에 따라 On
- `Health Check Path`: `/api/health`

참고: Dockerfile 기반 배포에서는 별도 Build/Start Command 입력이 필요하지 않습니다.

## 4.4 환경변수
필수는 아니지만 필요 시 아래를 설정합니다.

- `APP_TITLE`
- `MODEL_PATH`
- `REPORT_DIR`
- `DUMMY_DATA_PATH`
- `FRONTEND_DIST`
- `ALLOWED_ORIGINS`

기본값으로도 동작하도록 코드가 구성되어 있습니다.

---

## 5. 배포 후 확인 순서

1. Render 배포 로그에서 `Deploy successful` 확인
2. `https://<서비스도메인>/api/health` 확인
3. `https://<서비스도메인>/` 접속 확인
4. 업로드 모달에서 CSV 업로드 후 대시보드 이동 확인
5. 보고서 다운로드 버튼 동작 확인

---

## 6. API Base URL 운영 규칙

### 개발
- `client/.env.local`
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 배포(단일 서비스)
- `VITE_API_BASE_URL`은 빈 값(또는 생략)
- 프론트가 같은 도메인의 `/api/*`로 호출

이 프로젝트의 Dockerfile은 배포 빌드 시 `VITE_API_BASE_URL` 기본값을 빈 값으로 처리합니다.

---

## 7. 자주 겪는 문제와 해결

### 7.1 업로드 후 대시보드로 안 넘어감
- 원인: 프론트 빌드 시 API base URL이 `127.0.0.1:8000`로 고정되어 교차 출처 문제 발생
- 해결: 배포 빌드에서 `VITE_API_BASE_URL`을 빈 값으로 사용

### 7.2 브라우저 접속이 안 됨
- 원인: 포트 매핑 누락
- 해결: `-p 8000:8000`으로 실행, Docker Desktop에서 포트 매핑 확인

### 7.3 Docker Desktop에 포트 입력이 안 보임
- 원인: 이미지 포트 노출 정보 없음
- 해결: Dockerfile에 `EXPOSE 8000` 추가

---

## 8. 재배포 체크리스트

- [ ] 코드 수정 후 commit/push 완료
- [ ] Render 배포 로그 에러 없음
- [ ] `/api/health` 정상 응답
- [ ] `/` 접속 시 프론트 렌더링
- [ ] 업로드 -> 대시보드 이동 정상
- [ ] 다운로드 링크 정상

