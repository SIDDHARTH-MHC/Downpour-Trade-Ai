"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { MetricTile } from "@/components/dashboard/MetricTile";
import { PortfolioPositionsTable } from "@/components/modules/portfolio/PortfolioPositionsTable";
import { Input } from "@/components/ui/input";

export default function PortfolioPage() {
  const [equity, setEquity] = useState(10_000);
  const { data, error, isLoading } = useSWR(["portfolio", equity], () => api.portfolioAnalytics(equity), {
    refreshInterval: 120_000,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Portfolio analytics"
        description="Risk heat from open tracked signals at assumed 1% risk per trade"
      />
      <label className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        Account equity (USD)
        <Input
          type="number"
          className="h-8 w-32"
          value={equity}
          onChange={(e) => setEquity(Number(e.target.value))}
        />
      </label>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <>
          <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
            <MetricTile label="Open trades" value={data.open_trades} />
            <MetricTile label="Long / Short" value={`${data.long_count} / ${data.short_count}`} />
            <MetricTile label="Total risk $" value={`$${data.total_risk_usd.toFixed(0)}`} />
            <MetricTile
              label="Heat"
              value={`${data.portfolio_heat_pct.toFixed(2)}%`}
              status={data.portfolio_heat_pct > 5 ? "warn" : "ok"}
            />
          </div>
          <PortfolioPositionsTable positions={data.positions} />
          <p className="text-xs text-muted-foreground">{data.disclaimer}</p>
        </>
      )}
    </div>
  );
}
