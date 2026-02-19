import { useMemo } from 'react';
import { labelOf } from '../../shared/columnLabels';
import '../../styles/filterPopover.scss';
import { useEscapeClose } from '../../hooks/useEscapeClose';

type SortDir = 'asc' | 'desc';

type Props = {
	colKey: string;
	anchorRect: DOMRect;
	values: string[];
	hiddenValues: Set<string>;
	onToggleValue: (v: string) => void;
	onSort: (dir: SortDir) => void;
	onHideColumn: () => void;
	onClose: () => void;
};

export default function FilterPopover({ colKey, anchorRect, values, hiddenValues, onToggleValue, onSort, onHideColumn, onClose }: Props) {
	useEscapeClose(onClose);

	const style = useMemo(() => {
		const top = anchorRect.bottom + window.scrollY + 6;
		const left = anchorRect.left + window.scrollX;
		return {
			position: 'absolute' as const,
			top,
			left
		};
	}, [anchorRect]);

	return (
		<div className='filter_wapper' style={style}>
			<div className='fillter_header'>
				<h4>{labelOf(colKey)}</h4>
				<button onClick={onClose}>
					<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='currentColor'>
						<path d='M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708' />
					</svg>
				</button>
			</div>

			<div className='filter_srot'>
				<button onClick={() => onSort('asc')}>오름차순</button>
				<button onClick={() => onSort('desc')}>내림차순</button>
			</div>

			<div className='filter_rowDel'>
				<div className='filter_rowDel_header'>값 숨기기</div>
				<div className='filter_rowDel_content'>
					{values.map((v) => {
						const checked = !hiddenValues.has(v);
						return (
							<label key={v} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
								<input type='checkbox' checked={checked} onChange={() => onToggleValue(v)} />
								<span style={{ fontSize: 13 }}>{v === '' ? '(빈값)' : v}</span>
							</label>
						);
					})}
				</div>
			</div>

			<div className='filter_colDel'>
				<button onClick={onHideColumn}>
					<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' className='bi bi-trash3-fill' viewBox='0 0 16 16'>
						<path d='M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5m-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5M4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06m6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528M8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5' />
					</svg>
				</button>
			</div>
		</div>
	);
}
