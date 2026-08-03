"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { EngineHealthGrid } from "@/components/modules/status/EngineHealthGrid";

export default function StatusPage() {
  const { data, error, isLoading } = useSWR("engine-status", () => api.engineStatus(), {
    refreshInterval: 60_000,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Engine health"
        description="Live dependency checks for data feeds and calibration"
      />
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && <EngineHealthGrid data={data} />}
    </div>
  );
}
