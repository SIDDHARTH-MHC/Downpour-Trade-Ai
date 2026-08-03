"use client";

import Link from "next/link";
import type { ScanResponse } from "@/lib/api";
import type { CalibrateStatusResponse } from "@/lib/api";
import type { PortfolioAnalyticsResponse } from "@/lib/api";
import { MetricTile } from "@/components/dashboard/MetricTile";

type KPIRowProps = {
  scan?: ScanResponse;
  portfolio?: PortfolioAnalyticsResponse;
  calibration?: CalibrateStatusResponse;
  scanLoading?: boolean;
};

function formatLastScan(utc?: string) {
  if (!utc) return "—";
  return utc.replace("T", " ").replace(/:\d{2}(\.\d+)?Z?$/, " UTC");
}

export function KPIRow({ scan, portfolio, calibration, scanLoading }: KPIRowProps) {
  const actionable = scan?.actionable_count ?? (scanLoading ? "…" : "—");
  const total = scan?.total ?? 0;
  const scanStatus = scan?.scan_running ? "Running" : total > 0 ? "Ready" : scanLoading ? "Loading" : "Waiting";
  const scanStatusKind = scan?.scan_running ? "scan" : total > 0 ? "ok" : "warn";

  const heat = portfolio?.portfolio_heat_pct;
  const heatHint =
    portfolio != null
      ? `${portfolio.open_trades} open · $${portfolio.total_risk_usd.toFixed(0)} at risk`
      : undefined;

  const wf = calibration?.walk_forward ?? [];
  const wfPassed = wf.length > 0 && wf.every((w) => w.accepted);
  let calLabel = "—";
  let calHint = "Run backtests for confidence labels";
  let calStatus: "ok" | "warn" | "neutral" | "scan" = "neutral";
  if (calibration?.running) {
    calLabel = "Running";
    calHint = calibration.progress || "Calibration in progress";
    calStatus = "scan";
  } else if (wf.length > 0) {
    calLabel = wfPassed ? "WF pass" : "WF fail";
    calHint =
      calibration?.last_calibrated_utc && calibration.last_calibrated_utc !== "never"
        ? `Updated ${calibration.last_calibrated_utc}`
        : "Walk-forward OOS";
    calStatus = wfPassed ? "ok" : "warn";
  } else if (calibration?.last_calibrated_utc && calibration.last_calibrated_utc !== "never") {
    calLabel = "Stale";
    calHint = calibration.last_calibrated_utc;
    calStatus = "warn";
  }

  return (
    <div className="grid grid-cols-2 gap-2 lg:grid-cols-4 xl:grid-cols-5">
      <MetricTile
        label="Actionable"
        value={actionable}
        hint={total > 0 ? `${total} pairs scanned (1h)` : "Awaiting first scan"}
        status={typeof actionable === "number" && actionable > 0 ? "ok" : "neutral"}
      />
      <MetricTile
        label="Scan"
        value={scanStatus}
        hint={scan?.scan_progress || formatLastScan(scan?.last_scan_utc)}
        status={scanStatusKind as "ok" | "warn" | "scan"}
      />
      <MetricTile
        label="Data as of"
        value={scan?.data_as_of_utc ? scan.data_as_of_utc.split("T")[0] : "—"}
        hint={scan?.data_as_of_utc?.includes("T") ? scan.data_as_of_utc.split("T")[1]?.replace("Z", " UTC") : undefined}
        status="neutral"
      />
      <MetricTile
        label="Portfolio heat"
        value={heat != null ? `${heat.toFixed(2)}%` : "—"}
        hint={heatHint}
        status={heat != null && heat > 5 ? "warn" : heat != null ? "ok" : "neutral"}
      />
      <Link href="/backtests" className="col-span-2 lg:col-span-1">
        <MetricTile
          label="Calibration"
          value={calLabel}
          hint={calHint}
          status={calStatus}
          className="h-full transition-colors hover:border-primary/40"
        />
      </Link>
    </div>
  );
}
