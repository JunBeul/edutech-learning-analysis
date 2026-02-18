import { useLocation, useNavigate } from 'react-router-dom';
import { useMemo, useState } from 'react';
import UploadModal from '../components/UploadModal';

type PredictResponse = {
	rows: number;
	report_filename: string;
	report_url: string;
	data: Record<string, unknown>[];
};

export default function DashboardPage() {
	const location = useLocation();
	const navigate = useNavigate();
	const [open, setOpen] = useState(false);

	const result = (location.state as any)?.result as PredictResponse | undefined;

	// 새로고침 등으로 state가 없으면 홈으로
	if (!result) {
		navigate('/', { replace: true });
		return null;
	}

	const columns = useMemo(() => {
		// 기본 표시 컬럼 + 추천 4개
		const preferred = ['student_id', 'risk_proba', 'risk_level', 'top_reasons', 'action', 'score_guidance', 'remaining_absence_allowance'];
		const existing = preferred.filter((c) => result.data?.[0]?.hasOwnProperty(c));
		return existing;
	}, [result]);

	return (
		<div>
			<header style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
				<h2 style={{ marginRight: 'auto' }}>대시보드</h2>

				{/* PC: 헤더 버튼 / Mobile: 나중에 하단바로 분기 */}
				<button onClick={() => setOpen(true)}>파일 업로드</button>

				<a href={`http://127.0.0.1:8000${result.report_url}`} download>
					CSV 다운로드
				</a>
			</header>

			<section>
				<p>rows: {result.rows}</p>

				<table>
					<thead>
						<tr>
							{columns.map((c) => (
								<th key={c}>{c}</th>
							))}
						</tr>
					</thead>
					<tbody>
						{result.data.map((row, i) => (
							<tr key={i}>
								{columns.map((c) => (
									<td key={c}>{String((row as any)[c] ?? '')}</td>
								))}
							</tr>
						))}
					</tbody>
				</table>
			</section>

			{open && <UploadModal onClose={() => setOpen(false)} onSuccessNavigateTo='/dashboard' />}
		</div>
	);
}
