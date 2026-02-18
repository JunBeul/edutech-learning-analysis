type Props = {
	allColumns: string[];
	visibleColumns: string[];
	onChange: (cols: string[]) => void;
	onClose: () => void;
};

export default function ColumnSelectorModal({ allColumns, visibleColumns, onChange, onClose }: Props) {
	const toggle = (col: string) => {
		if (visibleColumns.includes(col)) {
			onChange(visibleColumns.filter((c) => c !== col));
			return;
		}

		onChange([...visibleColumns, col]);
	};

	return (
		<div
			style={{
				position: 'fixed',
				inset: 0,
				background: 'rgba(0,0,0,0.4)',
				display: 'grid',
				placeItems: 'center',
				zIndex: 1000
			}}
			onClick={onClose}
		>
			<div
				style={{ background: 'white', padding: 16, width: 'min(560px, 92vw)', maxHeight: '80vh', overflow: 'auto' }}
				onClick={(e) => e.stopPropagation()}
			>
				<h3>컬럼 선택</h3>

				<div style={{ display: 'grid', gap: 8 }}>
					{allColumns.map((col) => (
						<label key={col} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
							<input type='checkbox' checked={visibleColumns.includes(col)} onChange={() => toggle(col)} />
							{col}
						</label>
					))}
				</div>

				<div style={{ marginTop: 12 }}>
					<button onClick={onClose}>닫기</button>
				</div>
			</div>
		</div>
	);
}
