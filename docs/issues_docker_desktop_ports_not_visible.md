# Docker Desktop 포트 입력 미노출 이슈 정리

---

## 전체 요약

Docker Desktop의 `Run` 화면에서 `Ports: No ports exposed in this image`가 표시되어 포트 입력 UI가 보이지 않는 문제가 발생했습니다.  
이 상태에서 컨테이너를 실행하면 브라우저에서 서비스 접근이 되지 않아, 서버는 정상인데 화면 접속이 불가능한 상황으로 이어졌습니다.

핵심 원인은 이미지 메타데이터에 노출 포트 정보(`EXPOSE`)가 없고, 실행 시 포트 매핑(`-p`)이 누락된 조합이었습니다.  
`EXPOSE 8000` 추가와 `-p 8000:8000` 실행 규칙으로 문제를 해결했습니다.

---

## 문제 정의

1. Docker Desktop `Images -> Run`에서 포트 설정 입력이 보이지 않았습니다.
2. 컨테이너 로그는 정상(`Uvicorn running on 0.0.0.0:8000`)인데 브라우저 접속이 되지 않았습니다.
3. `docker inspect` 기준 `PortBindings`가 비어 있어 외부 접근 포트가 열리지 않은 상태였습니다.

---

## 원인 파악

1. Docker 이미지 포트 노출 메타정보 부재.
- `Dockerfile`에 `EXPOSE 8000`이 없으면 Desktop UI에서 포트 항목이 제한적으로 표시될 수 있습니다.

2. 컨테이너 실행 시 포트 매핑 누락.
- `docker run`에서 `-p 8000:8000`을 지정하지 않으면 호스트에서 컨테이너 포트로 접근할 수 없습니다.

3. 상태 확인 절차 부족.
- 실행 직후 `docker ps`/`docker inspect`로 포트 바인딩을 확인하지 않아 원인 파악이 지연되었습니다.

---

## 해결 방안

1. Dockerfile에 노출 포트를 명시했습니다.
```dockerfile
EXPOSE 8000
```

2. 컨테이너 실행 시 포트 매핑을 강제했습니다.
```bash
docker run --rm -d -p 8000:8000 --name maplight edutech-risk-prediction:local
```

3. 실행 상태를 명령어로 검증했습니다.
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker inspect -f "{{json .HostConfig.PortBindings}}" <container_name>
```

---

## 결과

1. Docker Desktop에서 포트 설정 인지성이 개선되었습니다.
2. 컨테이너 실행 시 `0.0.0.0:8000->8000/tcp` 바인딩이 정상 확인되었습니다.
3. 브라우저(`http://localhost:8000`) 및 헬스체크(`http://localhost:8000/api/health`) 접근이 정상화되었습니다.

---

## 관련 파일

- `Dockerfile`
- `backend/api/main.py`
- `docs/issues_docker_desktop_ports_not_visible.md`
