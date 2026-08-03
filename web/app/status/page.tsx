"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function StatusPage() {
  const { data, error, isLoading } = useSWR("engine-status", () => api.engineStatus(), {
    refreshInterval: 60_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Engine health</h1>
        <p className="text-sm text-muted">Live dependency checks for data feeds and calibration</p>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <>
          <p className="text-sm">
            Overall:{" "}
            <span className={data.status === "ok" ? "text-long" : "text-amber-400"}>{data.status}</span>
          </p>
          <div className="card grid gap-3 sm:grid-cols-2">
            {Object.entries(data.checks).map(([name, check]) => (
              <div key={name} className="rounded border border-border/60 p-3 text-sm">
                <div className="font-medium capitalize">{name.replace(/_/g, " ")}</div>
                <div className={check.status === "ok" ? "text-long" : "text-amber-400"}>{check.status}</div>
                <div className="text-xs text-muted">{check.detail}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
