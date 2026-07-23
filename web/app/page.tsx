"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { PairTable } from "@/components/PairTable";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function DashboardPage() {
  const { data, error, isLoading } = useSWR("scan-1h", () => api.scan("1h"), {
    refreshInterval: 60_000,
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
      {data && (
        <>
          <p className="text-sm text-muted">
            {data.total} pairs · {data.actionable_count} actionable signals
          </p>
          <PairTable results={data.results} />
        </>
      )}
    </div>
  );
}
