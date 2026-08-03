import { Verdict } from "@/lib/api";
import { ScanTable } from "@/components/dashboard/ScanTable";

/** @deprecated Prefer ScanTable — kept for heatmap-adjacent imports */
export function PairTable({ results }: { results: Verdict[] }) {
  return <ScanTable results={results} />;
}
