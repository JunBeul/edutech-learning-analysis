# React 구조 학습 정리 (edutech-risk-prediction 기준)

이 문서는 이 프로젝트의 실제 코드 기준으로 React의 핵심 구조를 빠르게 복습하기 위한 가이드입니다.

## 1. React 앱 시작점

`client/src/main.tsx`에서 React 앱을 DOM에 마운트합니다.

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/index.scss';
import App from './App';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

핵심:
- `main.tsx`는 엔트리 포인트
- 실제 화면 구성은 `App.tsx`부터 시작

## 2. 폴더 구조 (client/src)

```txt
client/src
├─ main.tsx
├─ App.tsx
├─ pages/
│  ├─ LandingPage.tsx
│  └─ DashboardPage.tsx
├─ components/
│  ├─ common/
│  ├─ upload/
│  └─ dashboard/
├─ hooks/
│  ├─ useEscapeClose.ts
│  ├─ useBodyScrollLock.ts
│  ├─ useFixedTableHeader.ts
│  └─ useTableFilterPopover.ts
├─ shared/
│  ├─ api.ts
│  ├─ types.ts
│  └─ columnLabels.ts
└─ styles/
```

권장 읽는 순서:
1. `main.tsx`
2. `App.tsx`
3. `pages/*`
4. `components/*`
5. `hooks/*`

## 3. 라우팅 구조

`client/src/App.tsx`에서 URL 경로와 페이지 컴포넌트를 매핑합니다.

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route path='/dashboard' element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

핵심:
- `/` -> `LandingPage`
- `/dashboard` -> `DashboardPage`

## 4. 페이지 기본 구조

`pages`는 화면 단위 컴포넌트입니다. 보통 아래 순서로 구성합니다.

```tsx
import { useMemo, useState } from 'react';
import { useLocation, Navigate } from 'react-router-dom';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import DashboardTable from '../components/dashboard/DashboardTable';

export default function DashboardPage() {
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const result = (location.state as { result?: { data: Record<string, unknown>[] } } | null)?.result;
  const rows = useMemo(() => result?.data ?? [], [result]);

  if (!result) {
    return <Navigate to='/' replace />;
  }

  return (
    <div>
      <DashboardHeader onOpenUpload={() => setOpen(true)} onOpenColumns={() => {}} reportUrl='' />
      <DashboardTable
        visibleColumns={[]}
        rows={rows}
        fixedHeader={null}
        tableScrollRef={{ current: null }}
        tableRef={{ current: null }}
        overlayTableRef={{ current: null }}
        onHeaderClick={() => {}}
        onRowClick={() => {}}
      />
    </div>
  );
}
```

핵심:
- 페이지는 상태/훅/비즈니스 흐름을 관리
- UI 조각은 하위 컴포넌트로 분리

## 5. 페이지 이동하는 법

### 5-1. 코드로 이동: `useNavigate`

`client/src/components/upload/UploadModal.tsx`

```tsx
const navigate = useNavigate();

const onSubmit = async () => {
  const result = await predictCsv({ file, policyObj: policy, mode: 'full' });
  onClose();
  navigate('/dashboard', { state: { result } });
};
```

- 업로드 성공 후 `/dashboard`로 이동
- `state`로 결과 데이터 전달

### 5-2. 조건부 리다이렉트: `Navigate`

`client/src/pages/DashboardPage.tsx`

```tsx
if (!result) {
  return <Navigate to='/' replace />;
}
```

- 필요한 데이터가 없으면 홈으로 되돌림

## 6. Props 구조

부모가 데이터를 내려주고, 자식이 `Props` 타입으로 받습니다.

부모 (`DashboardPage`):

```tsx
<DashboardHeader
  onOpenUpload={() => setOpen(true)}
  onOpenColumns={() => setColModalOpen(true)}
  reportUrl={result.report_url}
/>
```

자식 (`DashboardHeader`):

```tsx
type Props = {
  onOpenUpload: () => void;
  onOpenColumns: () => void;
  reportUrl: string;
};

export default function DashboardHeader({ onOpenUpload, onOpenColumns, reportUrl }: Props) {
  // ...
}
```

핵심:
- Props는 "부모 -> 자식" 단방향
- 타입(`type Props`)을 명시하면 유지보수에 유리

## 7. `useState`

컴포넌트 내부에서 바뀌는 값을 저장할 때 사용합니다.

```tsx
const [open, setOpen] = useState(false);
const [selectedRow, setSelectedRow] = useState<Record<string, unknown> | null>(null);
```

사용 예:
- 모달 열림/닫힘
- 선택된 행 상태 저장

## 8. `useEffect`

렌더링 후 실행해야 하는 작업(이벤트 등록, 구독, 타이머, cleanup 등)에 사용합니다.

`client/src/components/dashboard/DashboardHeader.tsx`

```tsx
const [isScrolled, setIsScrolled] = useState(false);

useEffect(() => {
  const onScroll = () => setIsScrolled(window.scrollY > 0);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  return () => {
    window.removeEventListener('scroll', onScroll);
  };
}, []);
```

핵심:
- `[]` 의존성 배열: 마운트/언마운트 시점
- cleanup 함수에서 이벤트 해제 필수

## 9. `useMemo`

계산 비용이 있거나, 참조 안정성이 필요한 값을 메모이제이션할 때 사용합니다.

`client/src/pages/DashboardPage.tsx`

```tsx
const sourceData = useMemo(() => result?.data ?? [], [result]);

const allColumns = useMemo(() => {
  return Object.keys(sourceData[0] ?? {});
}, [sourceData]);

const defaultCols = useMemo(() => {
  return PRIORITY_COLUMNS.filter((column) => allColumns.includes(column));
}, [allColumns]);
```

핵심:
- 의존성이 바뀔 때만 재계산
- 불필요한 연산/재렌더 파급 감소

## 10. 빠른 기준표

- `Props`: 부모가 자식에게 값/함수 전달
- `useState`: UI 상태 저장
- `useEffect`: 외부 시스템과 동기화
- `useMemo`: 계산 결과 캐싱
- `useNavigate`: 코드에서 페이지 이동
- `Navigate`: 렌더링 단계 리다이렉트

## 11. 학습 순서 추천

1. `main.tsx`, `App.tsx`를 먼저 완전히 이해
2. `LandingPage`에서 `useState`와 이벤트 핸들러 흐름 확인
3. `UploadModal`에서 `useMemo`, `navigate` 흐름 확인
4. `DashboardPage`에서 페이지 조립 구조와 Props 전달 추적
5. `hooks/*`에서 `useEffect` cleanup 패턴 학습
