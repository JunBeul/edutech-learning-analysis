import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { predictCsv } from '../lib/api';

type Props = {
	onClose: () => void;
	onSuccessNavigateTo: string;
};

export default function UploadModal({ onClose, onSuccessNavigateTo }: Props) {
	const navigate = useNavigate();
	const [file, setFile] = useState<File | null>(null);

	// TODO: policy 입력 UI는 다음 단계에서 붙임(일단 기본값 고정)
	const defaultPolicy = {
		threshold: 0.4,
		midterm_max: 100,
		midterm_weight: 40,
		final_max: 100,
		final_weight: 40,
		performance_max: 100,
		performance_weight: 20,
		total_classes: 160
	};

	const onSubmit = async () => {
		if (!file) return;

		const result = await predictCsv({
			file,
			policyObj: defaultPolicy,
			mode: 'full'
		});

		onClose();
		navigate(onSuccessNavigateTo, { state: { result } });
	};

	return (
		<div
			style={{
				position: 'fixed',
				inset: 0,
				background: 'rgba(0,0,0,0.4)',
				display: 'grid',
				placeItems: 'center'
			}}
		>
			<div style={{ background: 'white', padding: 16, width: 'min(520px, 92vw)' }}>
				<h3>파일 업로드</h3>

				<input type='file' accept='.csv' onChange={(e) => setFile(e.target.files?.[0] ?? null)} />

				<div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
					<button onClick={onSubmit} disabled={!file}>
						업로드
					</button>
					<button onClick={onClose}>취소</button>
				</div>
			</div>
		</div>
	);
}
