"use client";

import useSWR from "swr";
import { api, ScanResponse } from "@/lib/api";
import { PairTable } from "@/components/PairTable";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function DashboardPage() {
  const { data, error, isLoading } = useSWR<ScanResponse>("scan-1h", () => api.scan("1h"), {
    refreshInterval: (latest) => (latest?.scan_running ? 10_000 : 60_000),
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted">
            Top-volume pairs scanned · NO-TRADE is the expected default
          </p>
        </div>
        <DataStamp label={data?.data_as_of_utc} />
      </div>

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && data.scan_running && (
        <p className="text-sm text-amber-400">
          Scan in progress… {data.scan_progress ? `(${data.scan_progress})` : ""} Full-depth scan running in parallel.
        </p>
      )}
      {data && data.total === 0 && !data.scan_running && (
        <p className="text-sm text-amber-400">
          No scan data yet. First scan runs automatically after deploy — refresh in 1–2 minutes.
        </p>
      )}
      {data && data.total > 0 && (
        <>
          <p className="text-sm text-muted">
            {data.total} pairs · {data.actionable_count} actionable signals
            {data.last_scan_utc ? ` · last scan ${data.last_scan_utc}` : ""}
          </p>
          <PairTable results={data.results} />
        </>
      )}
    </div>
  );
}
