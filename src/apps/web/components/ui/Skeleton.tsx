export default function Skeleton({ height = "1rem", width = "100%" }: { height?: string; width?: string }) {
	return <div aria-hidden="true" className="skeleton" style={{ height, width }} />;
}

export function PageSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading" style={{ display: "grid", gap: "0.8rem" }}>
			<div className="panel" style={{ display: "grid", gap: "0.6rem" }}>
				<Skeleton height="1.6rem" width="40%" />
				<Skeleton width="70%" />
			</div>
			<div className="panel" style={{ display: "grid", gap: "0.6rem" }}>
				<Skeleton />
				<Skeleton width="90%" />
				<Skeleton width="60%" />
			</div>
		</div>
	);
}
