"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { ScannerHeatmap } from "@/components/ScannerHeatmap";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function HeatmapPage() {
  const { data, error, isLoading } = useSWR("scan-heatmap", () => api.scan("1h"), {
    refreshInterval: 60_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Scanner heatmap</h1>
        <p className="text-sm text-muted">Latest scan — color by verdict</p>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && data.results.length > 0 && (
        <div className="card">
          <ScannerHeatmap results={data.results} />
        </div>
      )}
    </div>
  );
}
