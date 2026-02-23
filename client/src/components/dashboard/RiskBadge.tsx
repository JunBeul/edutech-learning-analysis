type Props = {
	level: string;
};

export default function RiskBadge({ level }: Props) {
	const colorMap: Record<string, string> = {
		High: '#ef4444',
		Medium: '#f59e0b',
		Low: '#22c55e'
	};

	return (
		<div
			style={{
				background: colorMap[level] ?? '#ccc',
				color: 'white',
				padding: '2px 8px',
				borderRadius: '100dvh',
				fontSize: 12,
				fontWeight: 'bold',
				width: '100%',
				textAlign: 'center'
			}}
		>
			{level}
		</div>
	);
}
