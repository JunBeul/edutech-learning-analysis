import '../../styles/loadingOverlay.scss';

type Props = {
	message?: string;
	ariaLabel?: string;
};

export default function LoadingOverlay({ message = 'Loading...', ariaLabel = 'Loading' }: Props) {
	return (
		<div className='modal_loading_overlay' role='status' aria-live='polite' aria-label={ariaLabel}>
			<div className='modal_loading_spinner' />
			<p>{message}</p>
		</div>
	);
}