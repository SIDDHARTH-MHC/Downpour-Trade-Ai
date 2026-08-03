"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { ScannerHeatmap } from "@/components/ScannerHeatmap";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { EmptyState } from "@/components/shell/EmptyState";
import { Card, CardContent } from "@/components/ui/card";
import { Grid3x3 } from "lucide-react";

export default function HeatmapPage() {
  const { data, error, isLoading } = useSWR("scan-heatmap", () => api.scan("1h"), {
    refreshInterval: 60_000,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader title="Scanner heatmap" description="Latest scan — color by verdict" />
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && data.results.length === 0 && (
        <EmptyState
          icon={Grid3x3}
          title="No heatmap data"
          description="Run a scan from the dashboard or wait for the next scheduled pass."
        />
      )}
      {data && data.results.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <ScannerHeatmap results={data.results} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
