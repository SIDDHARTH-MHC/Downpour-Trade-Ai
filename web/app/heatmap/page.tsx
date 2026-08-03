"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { ScannerHeatmap } from "@/components/ScannerHeatmap";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { Card, CardContent } from "@/components/ui/card";

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
