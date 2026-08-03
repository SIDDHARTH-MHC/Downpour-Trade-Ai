"use client";

import useSWR from "swr";
import { api, ScanResponse } from "@/lib/api";
import { WatchlistPanel } from "@/components/WatchlistPanel";
import { ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { KPIRow } from "@/components/dashboard/KPIRow";
import { ScanTable } from "@/components/dashboard/ScanTable";
import { ScanRejectionChart } from "@/components/dashboard/ScanRejectionChart";
import { DashboardHeatmapStrip } from "@/components/dashboard/DashboardHeatmapStrip";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function DashboardPage() {
  const { data, error, isLoading } = useSWR<ScanResponse>("scan-1h", () => api.scan("1h"), {
    refreshInterval: (latest) => (latest?.scan_running ? 10_000 : 60_000),
  });

  const { data: portfolio } = useSWR("dashboard-portfolio", () => api.portfolioAnalytics(10_000), {
    refreshInterval: 120_000,
    revalidateOnFocus: false,
  });

  const { data: calibration } = useSWR("dashboard-calibrate", () => api.calibrateStatus(), {
    refreshInterval: (latest) => (latest?.running ? 15_000 : 180_000),
    revalidateOnFocus: false,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Dashboard"
        description="Top-volume pairs · 1h scan · NO-TRADE is the expected default"
      />

      <KPIRow scan={data} portfolio={portfolio} calibration={calibration} scanLoading={isLoading && !data} />

      {isLoading && !data && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}

      {data?.scan_running && (
        <Alert className="border-warning/30 bg-warning/5 py-2">
          <AlertDescription className="text-sm text-warning">
            Scan in progress… {data.scan_progress ? `(${data.scan_progress})` : ""} Full-depth scan running in
            parallel.
          </AlertDescription>
        </Alert>
      )}

      {data && data.total === 0 && !data.scan_running && (
        <Alert className="border-warning/30 bg-warning/5 py-2">
          <AlertDescription className="text-sm text-warning">
            No scan data yet. First scan runs automatically after deploy — refresh in 1–2 minutes.
          </AlertDescription>
        </Alert>
      )}

      {data && data.total > 0 && (
        <>
          <DashboardHeatmapStrip results={data.results} />
          <div className="grid gap-4 xl:grid-cols-[1fr_min(22rem,32%)]">
            <ScanTable results={data.results} />
            <ScanRejectionChart report={data.scan_report} />
          </div>
        </>
      )}

      <WatchlistPanel />
    </div>
  );
}
