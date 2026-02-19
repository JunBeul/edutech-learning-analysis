import { useEffect, useRef } from 'react';

type EscapeHandlerEntry = {
	id: number;
	onClose: () => void;
};

const escapeStack: EscapeHandlerEntry[] = [];
let listenerAttached = false;
let nextEntryId = 1;

function handleEscapeKeydown(event: KeyboardEvent): void {
	if (event.key !== 'Escape') return;

	const top = escapeStack[escapeStack.length - 1];
	if (!top) return;

	event.preventDefault();
	event.stopPropagation();
	top.onClose();
}

function ensureEscapeListener(): void {
	if (listenerAttached) return;

	window.addEventListener('keydown', handleEscapeKeydown);
	listenerAttached = true;
}

export function useEscapeClose(onClose: () => void): void {
	const onCloseRef = useRef(onClose);

	useEffect(() => {
		onCloseRef.current = onClose;
	}, [onClose]);

	useEffect(() => {
		ensureEscapeListener();

		const entryId = nextEntryId++;
		const entry: EscapeHandlerEntry = {
			id: entryId,
			onClose: () => onCloseRef.current()
		};
		escapeStack.push(entry);

		return () => {
			const index = escapeStack.findIndex((x) => x.id === entryId);
			if (index >= 0) {
				escapeStack.splice(index, 1);
			}
			if (escapeStack.length === 0 && listenerAttached) {
				window.removeEventListener('keydown', handleEscapeKeydown);
				listenerAttached = false;
			}
		};
	}, []);
}
