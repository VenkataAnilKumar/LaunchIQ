import { STATUS_LABEL } from "@/lib/format";

export default function StatusPill({ status }: { status: string }) {
	return <span className={`status-pill status-${status}`}>{STATUS_LABEL[status] ?? status}</span>;
}
