import { useMemo, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { labelOf } from '../shared/columnLabels';
import { useBodyScrollLock } from '../hooks/useBodyScrollLock';
import UploadModal from '../components/upload/UploadModal';
import ColumnSelectorModal from '../components/dashboard/ColumnSelectorModal';
import DetailDrawer from '../components/dashboard/DetailDrawer';
import RiskBadge from '../components/dashboard/RiskBadge';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import MobileFloatingNav from '../components/dashboard/MobileFloatingNav';
import FilterPopover from '../components/dashboard/FilterPopover';

import '../styles/table.scss';

type PredictResponse = {
	rows: number;
	report_filename: string;
	report_url: string;
	data: Record<string, unknown>[];
};

type DashboardLocationState = {
	result?: PredictResponse;
};

const PRIORITY_COLUMNS = ['student_id', 'risk_proba', 'risk_level', 'top_reasons', 'remaining_absence_allowance'];

export default function DashboardPage() {
	const location = useLocation();
	const [UploadModalOpen, setOpen] = useState(false);
	const [colModalOpen, setColModalOpen] = useState(false);
	const [columnState, setColumnState] = useState<{ reportKey: string; cols: string[] }>({
		reportKey: '',
		cols: []
	});
	const [selectedRow, setSelectedRow] = useState<Record<string, unknown> | null>(null);
	const [activeCol, setActiveCol] = useState<string | null>(null);
	const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);

	// column key -> hidden values
	const [hiddenMap, setHiddenMap] = useState<Record<string, Set<string>>>({});
	const [sortState, setSortState] = useState<{ key: string; dir: 'asc' | 'desc' } | null>(null);

	const result = (location.state as DashboardLocationState | null)?.result;
	const sourceData = result?.data ?? [];

	const allColumns = useMemo(() => {
		return Object.keys(sourceData[0] ?? {});
	}, [sourceData]);

	const filteredRows = useMemo(() => {
		let rows = [...sourceData];

		// hidden value filter
		rows = rows.filter((row) => {
			for (const [col, hiddenSet] of Object.entries(hiddenMap)) {
				const v = String((row as any)[col] ?? '');
				if (hiddenSet?.has(v)) return false;
			}
			return true;
		});

		// sorting
		if (sortState) {
			const { key, dir } = sortState;
			rows.sort((a, b) => {
				const av = String((a as any)[key] ?? '');
				const bv = String((b as any)[key] ?? '');
				if (av === bv) return 0;
				return dir === 'asc' ? (av > bv ? 1 : -1) : av < bv ? 1 : -1;
			});
		}

		return rows;
	}, [sourceData, hiddenMap, sortState]);

	const activeValues = useMemo(() => {
		if (!activeCol) return [];
		const s = new Set<string>();
		for (const row of sourceData) {
			s.add(String((row as any)[activeCol] ?? ''));
		}
		return Array.from(s).sort();
	}, [activeCol, sourceData]);

	const defaultCols = useMemo(() => {
		return PRIORITY_COLUMNS.filter((column) => allColumns.includes(column));
	}, [allColumns]);

	const reportKey = result?.report_filename ?? '';
	const visibleColumns = columnState.reportKey === reportKey ? columnState.cols : defaultCols;
	const isScrollLockOpen = UploadModalOpen || colModalOpen;

	useBodyScrollLock(isScrollLockOpen);

	const handleColumnsChange = (cols: string[]) => {
		setColumnState({ reportKey, cols });
	};

	if (!result) {
		return <Navigate to='/' replace />;
	}

	return (
		<div>
			<DashboardHeader onOpenUpload={() => setOpen(true)} onOpenColumns={() => setColModalOpen(true)} reportUrl={result.report_url} />

			<section>
				<p>rows: {filteredRows.length}</p>
				<div className='table-wrapper'>
					<table className='dashboard-table'>
						<thead>
							<tr>
								{visibleColumns.map((c) => (
									<th
										key={c}
										onClick={(e) => {
											const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
											setActiveCol(c);
											setAnchorRect(rect);
										}}
										style={{ cursor: 'pointer' }}
									>
										{labelOf(c)}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{filteredRows.map((row, i) => (
								<tr key={i} onClick={() => setSelectedRow(row)} style={{ cursor: 'pointer' }}>
									{visibleColumns.map((c) => {
										const value = row[c];

										if (c === 'risk_level') {
											return (
												<td key={c}>
													<RiskBadge level={String(value)} />
												</td>
											);
										}

										if (c === 'risk_proba') {
											return <td key={c}>{(Number(value) * 100).toFixed(1)}%</td>;
										}

										return <td key={c}>{String(value ?? '')}</td>;
									})}
								</tr>
							))}
						</tbody>
					</table>
				</div>
			</section>
			<MobileFloatingNav onOpenUpload={() => setOpen(true)} onOpenColumns={() => setColModalOpen(true)} reportUrl={result.report_url} />
			{UploadModalOpen && <UploadModal onClose={() => setOpen(false)} onSuccessNavigateTo='/dashboard' />}
			{colModalOpen && <ColumnSelectorModal allColumns={allColumns} visibleColumns={visibleColumns} onChange={handleColumnsChange} onClose={() => setColModalOpen(false)} />}
			{selectedRow && <DetailDrawer row={selectedRow} onClose={() => setSelectedRow(null)} />}
			{activeCol && anchorRect && (
				<FilterPopover
					colKey={activeCol}
					anchorRect={anchorRect}
					values={activeValues}
					hiddenValues={hiddenMap[activeCol] ?? new Set()}
					onToggleValue={(v) => {
						if (!activeCol) return;
						setHiddenMap((prev) => {
							const next = { ...prev };
							const set = new Set(next[activeCol] ?? []);
							if (set.has(v)) set.delete(v);
							else set.add(v);
							next[activeCol] = set;
							return next;
						});
					}}
					onSort={(dir) => {
						if (!activeCol) return;
						setSortState({ key: activeCol, dir });
					}}
					onHideColumn={() => {
						if (!activeCol) return;
						setColumnState((prev) => {
							const currentCols = prev.reportKey === reportKey ? prev.cols : defaultCols;
							return { reportKey, cols: currentCols.filter((x) => x !== activeCol) };
						});
						setActiveCol(null);
						setAnchorRect(null);
					}}
					onClose={() => {
						setActiveCol(null);
						setAnchorRect(null);
					}}
				/>
			)}
		</div>
	);
}
