# requirements.txt 사용하는 이유와 사용법

## 1. `requirements.txt`란?

파이썬 프로젝트에서 필요한 패키지 목록(이름 + 버전)을 기록해 두는 파일입니다.

예시:

```txt
fastapi==0.116.1
uvicorn==0.35.0
pandas==2.3.1
scikit-learn==1.7.1
```

이 파일이 있으면 다른 개발자나 배포 서버에서 같은 의존성 환경을 재현하기 쉬워집니다.

## 2. 왜 사용하는가? (필요한 이유)

### 2.1 개발 환경 재현성

- 내 PC에서는 되는데 다른 PC/서버에서는 안 되는 문제를 줄일 수 있음
- 같은 버전의 패키지를 설치하도록 맞출 수 있음

### 2.2 협업 효율

- 팀원이 프로젝트를 받을 때 한 번에 필요한 라이브러리를 설치 가능
- 문서로 패키지 목록을 따로 관리할 필요가 줄어듦

### 2.3 배포/운영 안정성

- 서버 배포 시 동일한 패키지 버전을 설치해 예기치 않은 동작 변경 방지
- CI/CD 환경에서도 설치 명령을 표준화할 수 있음

### 2.4 의존성 관리 추적

- Git으로 변경 이력을 확인할 수 있어 패키지 추가/업데이트 내역 추적 가능

## 3. 기본 사용법

### 3.1 가상환경 생성 및 활성화 (권장)

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

가상환경을 사용하는 이유:

- 프로젝트별로 패키지 충돌을 방지
- 시스템 전역 Python 환경 오염 방지

### 3.2 `requirements.txt`로 패키지 설치

```powershell
python -m pip install -r requirements.txt
```

설명:

- `-r` 옵션은 파일에 적힌 패키지 목록을 읽어서 설치하라는 의미

### 3.3 현재 설치된 패키지로 `requirements.txt` 생성/최신화

```powershell
python -m pip freeze > requirements.txt
```

설명:

- 현재 가상환경에 설치된 패키지 목록을 버전 포함 형태로 저장
- 기존 파일이 있으면 덮어씀

주의:

- 반드시 **프로젝트 가상환경 활성화 후** 실행하는 것이 안전함
- 불필요한 패키지까지 함께 기록될 수 있으므로 확인이 필요함

## 4. 자주 쓰는 작업 흐름 (실무 기준)

### 4.1 새 프로젝트 시작

1. 가상환경 생성/활성화
2. 필요한 패키지 설치 (`pip install fastapi uvicorn ...`)
3. `pip freeze > requirements.txt`
4. Git에 커밋

### 4.2 기존 프로젝트 실행

1. 가상환경 생성/활성화
2. `pip install -r requirements.txt`
3. 애플리케이션 실행

### 4.3 패키지 추가 후 반영

1. `pip install <package-name>`
2. 동작 확인
3. `pip freeze > requirements.txt`
4. 변경된 `requirements.txt` 커밋

## 5. 버전 표기 방식 이해

### 5.1 고정 버전 (`==`)

```txt
pandas==2.3.1
```

- 가장 재현성이 높음
- 협업/배포에서 가장 많이 사용

### 5.2 범위 지정 (`>=`, `<`) - 상황에 따라 사용

```txt
fastapi>=0.110,<1.0
```

- 유연하지만 환경별 설치 버전이 달라질 수 있음
- 라이브러리 개발이나 특정 정책이 있을 때 사용

일반적인 서비스 프로젝트에서는 운영 안정성을 위해 `==` 고정 버전을 선호하는 경우가 많습니다.

## 6. 자주 발생하는 문제와 팁

### 6.1 `pip freeze` 결과가 너무 많음

원인:

- 전역 환경 또는 다른 프로젝트용 패키지가 섞여 있음

해결:

- 새 가상환경을 만들고 필요한 패키지만 설치 후 다시 `freeze`

### 6.2 설치 오류 발생 (`pip install -r requirements.txt`)

확인할 것:

- Python 버전이 프로젝트 요구사항과 맞는지
- OS별 패키지 호환성 문제는 없는지
- 네트워크/사내 프록시 제한이 있는지

### 6.3 패키지 버전 충돌

증상:

- 특정 패키지 설치 시 다른 패키지 버전이 내려가거나 충돌 발생

대응:

- 최근에 추가/업데이트한 패키지 확인
- 충돌 패키지 버전 조정 후 `requirements.txt` 재생성

## 7. 권장 습관 (팀 협업)

- 항상 가상환경에서 작업하기
- 패키지 설치/업데이트 후 `requirements.txt` 즉시 반영하기
- 이유 없는 대규모 버전 업그레이드는 한 번에 하지 않기
- `requirements.txt` 변경 시 PR/커밋 메시지에 변경 이유 남기기

## 8. 이 프로젝트에서 바로 쓰는 명령 예시

설치:

```powershell
python -m pip install -r requirements.txt
```

최신화:

```powershell
python -m pip freeze > requirements.txt
```

---

필요하면 다음 단계로 `requirements-dev.txt` 분리(개발용/배포용 의존성 분리)까지 정리할 수 있습니다.
