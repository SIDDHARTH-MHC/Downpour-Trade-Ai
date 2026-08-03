"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { CorrelationHeatmap } from "@/components/modules/correlation/CorrelationHeatmap";
import { Input } from "@/components/ui/input";

const DEFAULT = "BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,BNB/USDT";

export default function CorrelationPage() {
  const [symbols, setSymbols] = useState(DEFAULT);
  const { data, error, isLoading } = useSWR(["corr", symbols], () => api.correlationMatrix(symbols), {
    refreshInterval: 300_000,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Correlation explorer"
        description="Rolling correlation & beta vs BTC (context only)"
      />
      <Input value={symbols} onChange={(e) => setSymbols(e.target.value)} aria-label="Symbol list" />
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && <CorrelationHeatmap data={data} />}
    </div>
  );
}
