import { API_BASE_URL } from '../../shared/api';
import { useEffect, useState } from 'react';
import '../../styles/dashboardHeader.scss';

type Props = {
	onOpenUpload: () => void;
	onOpenColumns: () => void;
	reportUrl: string;
};

export default function DashboardHeader({ onOpenUpload, onOpenColumns, reportUrl }: Props) {
	const [isScrolled, setIsScrolled] = useState(false);
	useEffect(() => {
		const onScroll = () => setIsScrolled(window.scrollY > 0); // 1px라도 움직이면 true
		window.addEventListener('scroll', onScroll, { passive: true });
		onScroll();
		return () => window.removeEventListener('scroll', onScroll);
	}, []);

	const handleDownload = () => {
		const link = document.createElement('a');
		link.href = `${API_BASE_URL}${reportUrl}`;
		link.setAttribute('download', '');
		document.body.appendChild(link);
		link.click();
		link.remove();
	};

	return (
		<header className={`dashboard_header ${isScrolled ? 'is-scrolled' : ''}`}>
			<h2 style={{ marginRight: 'auto' }}>최소성취수준 보장지도 예측 AI</h2>

			<button onClick={onOpenUpload}>파일 업로드</button>
			<button onClick={onOpenColumns}>컬럼 필터</button>
			<button onClick={handleDownload}>CSV 다운로드</button>
		</header>
	);
}
