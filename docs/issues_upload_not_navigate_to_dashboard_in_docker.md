# Docker 환경에서 업로드 후 대시보드 미이동 이슈 정리

---

## 전체 요약

로컬 개발(`npm run dev`)에서는 업로드 후 대시보드로 정상 이동했지만, Docker 단일 서비스 환경에서는 업로드 이후 화면 전환이 멈추는 문제가 발생했습니다.  
핵심 원인은 프론트 빌드 시 API Base URL이 절대경로(`http://127.0.0.1:8000`)로 고정되어, 브라우저 접근 도메인(`http://localhost:8000`)과 출처가 달라지는 구성 충돌이었습니다.

최종적으로 Docker 빌드에서 `VITE_API_BASE_URL`을 빈 값으로 강제해 same-origin(`/api/*`) 호출로 통일했고, 업로드 에러 표시를 보강해 실패 시 즉시 원인 확인이 가능하도록 개선했습니다.

---

## 문제 정의

1. `npm run dev`에서는 업로드 후 `/dashboard`로 정상 이동했지만 Docker 실행 환경에서는 이동하지 않았습니다.
2. 서버 로그는 정상 기동 상태(`Uvicorn running`)였고, 단순 서버 다운 문제는 아니었습니다.
3. 업로드 실패 시 UI에 즉시 에러가 노출되지 않아 원인 파악이 지연되었습니다.

---

## 원인 파악

1. 프론트 빌드 시점 환경변수 고정.
- `client/.env.local`의 `VITE_API_BASE_URL=http://127.0.0.1:8000` 값이 Docker 빌드 산출물에 반영되었습니다.

2. 단일 서비스 도메인과 API 절대경로 간 출처 불일치.
- 브라우저는 `http://localhost:8000`으로 앱에 접속했는데, 프론트는 `http://127.0.0.1:8000/api/...`로 요청해 출처가 달라졌습니다.
- 이로 인해 CORS/요청 실패가 발생했고, 결과적으로 `navigate('/dashboard')` 단계까지 도달하지 못했습니다.

3. 실패 가시성 부족.
- 업로드 실패 메시지가 모달에서 충분히 표시되지 않아, 이동 실패가 라우팅 문제처럼 보였습니다.

---

## 해결 방안

1. Docker 빌드에서 API Base URL 기본값을 빈 값으로 고정했습니다.
- `Dockerfile` 프론트 빌드 스테이지에 아래를 추가:
  - `ARG VITE_API_BASE_URL=`
  - `ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}`
- 배포 빌드에서는 `buildApiUrl()`이 상대경로(`/api/...`)를 사용하도록 유도했습니다.

2. 프론트 URL 결합 규칙을 유지/검증했습니다.
- `client/src/shared/api.ts`의 `buildApiUrl()`에서 base URL이 비어 있으면 상대경로 반환.
- 예측 요청은 `/api/predict`, 샘플 다운로드는 `/api/sample/...`로 통일.

3. 업로드 실패 UX를 보강했습니다.
- `UploadModal`에 submit 에러 표시(`업로드 오류`)를 추가해 실패 시 즉시 메시지를 확인 가능하도록 개선했습니다.

---

## 결과

1. Docker 환경에서 업로드 후 대시보드 이동이 정상 동작하도록 복구되었습니다.
2. 배포 환경에서 API 호출이 same-origin(`/api/*`)으로 통일되어 URL 충돌/출처 문제 리스크가 감소했습니다.
3. 업로드 실패 시 모달 내에서 원인을 즉시 확인할 수 있어 디버깅 시간이 단축되었습니다.

---

## 관련 파일

- `Dockerfile`
- `client/src/shared/api.ts`
- `client/src/components/upload/UploadModal.tsx`
- `client/.env.local`
- `backend/api/main.py`
- `docs/issues_upload_not_navigate_to_dashboard_in_docker.md`
