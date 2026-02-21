# Docker 사용 및 Dockerfile 작성 가이드

이 문서는 현재 프로젝트를 기준으로, Docker를 처음 사용하는 입장에서  
"왜 쓰는지 -> 어떻게 Dockerfile을 만들고 -> 어떻게 실행하는지"를 한 번에 정리한 스터디 문서입니다.

---

## 1. Docker를 사용하는 이유

1. 실행 환경을 고정할 수 있습니다.
- 내 PC에서는 되는데 배포 서버에서는 안 되는 문제를 줄일 수 있습니다.
- Python/Node 버전, 라이브러리, 시스템 패키지를 이미지에 함께 묶을 수 있습니다.

2. 배포와 로컬 검증 흐름을 맞출 수 있습니다.
- 로컬에서 Docker로 검증한 방식 그대로 Render 같은 배포 환경에 올릴 수 있습니다.

3. 실행/중지/재실행이 단순해집니다.
- 컨테이너 단위로 실행해서 정리하기 쉽고, 재현성이 높습니다.

---

## 2. Dockerfile 만드는 방법과 생성 규칙

## 2.1 만드는 방법
1. 프로젝트 루트에 `Dockerfile` 파일을 생성합니다.
2. 보통 아래 순서로 작성합니다.
- 베이스 이미지 선택
- 작업 디렉터리 설정
- 의존성 설치
- 소스 코드 복사
- 실행 명령 정의

## 2.2 작성 규칙(실무 기준)
1. 상단에 빌드 단계 목적을 주석으로 명확히 둡니다.
- 예: 프론트 빌드 단계 / 런타임 단계

2. 캐시를 고려해 `COPY` 순서를 설계합니다.
- `package.json`, `requirements.txt`를 먼저 복사하고 설치
- 소스 코드는 나중에 복사

3. 환경별로 바뀌는 값은 `ARG`/`ENV`로 분리합니다.
- 예: `VITE_API_BASE_URL`, `PORT`

4. 외부 접근 포트는 `EXPOSE`로 명시합니다.
- Docker Desktop UI 가시성과 운영 가독성이 좋아집니다.

5. 컨테이너 시작 명령은 하나의 책임으로 유지합니다.
- 예: `uvicorn backend.api.main:app ...`

---

## 3. Dockerfile 기본/필수 구조

아래는 현재 프로젝트(React + FastAPI 단일 서비스) 기준으로 이해하면 됩니다.

1. 빌드 스테이지
- `FROM node:20-alpine AS frontend-builder`
- React 앱 빌드 (`npm run build`)

2. 런타임 스테이지
- `FROM python:3.11-slim`
- FastAPI 실행에 필요한 패키지 설치
- 백엔드 코드/데이터 복사
- 프론트 빌드 산출물(`client/dist`) 복사

3. 환경변수 및 포트
- `ENV PORT=8000`
- `EXPOSE 8000`

4. 시작 명령
- `CMD ["sh", "-c", "python -m uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT}"]`

---

## 4. Docker 실행 방법 (실제 진행한 순서)

아래는 실제로 진행한 절차를 그대로 정리한 것입니다.

## 4.1 이미지 빌드
```bash
docker build -t edutech-risk-prediction:local .
```

## 4.2 Docker Desktop에서 실행
1. Docker Desktop `Images` 탭으로 이동
2. `edutech-risk-prediction:local` 이미지의 `Run` 클릭
3. 포트 설정 `8000`으로 실행
- 컨테이너 포트: `8000`
- 호스트 포트: `8000`

## 4.3 브라우저 확인
1. 컨테이너가 올라오면 브라우저 접속
2. `http://localhost:8000`

---

## 5. 자주 겪는 실수 체크리스트

- [ ] `docker build` 후 이전 컨테이너를 그대로 사용함(새 이미지 미반영)
- [ ] 포트 매핑(`8000:8000`) 누락
- [ ] `EXPOSE 8000` 미설정으로 Desktop UI에서 포트 확인 어려움
- [ ] 배포 빌드에서 `VITE_API_BASE_URL` 값이 절대경로로 고정됨

---

## 6. 관련 파일

- `Dockerfile`
- `backend/api/main.py`
- `client/src/shared/api.ts`
- `docs/study_docker_usage_and_dockerfile_guide.md`
