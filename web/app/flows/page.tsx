"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { FlowsTable } from "@/components/modules/flows/FlowsTable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const DEFAULT_SYMBOLS = "BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT";
const LIQ_SYMBOL = "BTC/USDT";

export default function FlowsPage() {
  const [symbols, setSymbols] = useState(DEFAULT_SYMBOLS);
  const { data, error, isLoading, mutate } = useSWR(["flows", symbols], () => api.flowsSnapshot(symbols), {
    refreshInterval: 120_000,
  });
  const { data: liq, error: liqErr } = useSWR(["liq", LIQ_SYMBOL], () => api.contextLiquidations(LIQ_SYMBOL), {
    refreshInterval: 120_000,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Funding & flow snapshot"
        description="Live funding rate and OI change from Binance USD-M (same inputs as flow lane)"
      />
      <div className="flex flex-wrap gap-2">
        <Input
          className="min-w-[280px] flex-1"
          value={symbols}
          onChange={(e) => setSymbols(e.target.value)}
          aria-label="Symbol list"
        />
        <Button type="button" variant="secondary" onClick={() => mutate()}>
          Refresh
        </Button>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && <FlowsTable rows={data.rows} />}
      {liq?.liquidations && (
        <div className="card space-y-2 text-sm">
          <h2 className="font-semibold text-sky-300">Liquidation stress (estimated)</h2>
          <p>{liq.liquidations.message}</p>
          {liq.liquidations.elevated_forced_flow && (
            <p className="text-amber-400/90">Elevated taker sell flow — use as cascade context only.</p>
          )}
          {liqErr && <ErrorState message={(liqErr as Error).message} />}
          <p className="text-xs text-muted">{liq.liquidations.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
