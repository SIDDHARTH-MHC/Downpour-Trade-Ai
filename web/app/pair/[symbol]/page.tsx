"use client";

import { useState } from "react";
import useSWR from "swr";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { SignalHero } from "@/components/modules/pair/SignalHero";
import { PairDetailTabs } from "@/components/modules/pair/PairDetailTabs";
import { useRecentSymbol } from "@/hooks/use-recent-symbols";

const PriceChart = dynamic(() => import("@/components/modules/pair/PriceChart").then((m) => m.PriceChart), {
  ssr: false,
  loading: () => <div className="skeleton h-[420px] w-full rounded-xl" />,
});

export default function PairPage({ params }: { params: { symbol: string } }) {
  const symbol = decodeURIComponent(params.symbol);
  const [tf, setTf] = useState("1h");
  useRecentSymbol(symbol);

  const { data, error, isLoading } = useSWR(["analyze", symbol, tf], () => api.analyze(symbol, tf), {
    refreshInterval: 60_000,
  });
  const { data: confHist } = useSWR(["conf-hist", symbol], () => api.confidenceHistory(symbol, 20), {
    refreshInterval: 120_000,
  });

  return (
    <div className="space-y-4">
      {isLoading && !data && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <>
          <SignalHero verdict={data} tf={tf} onTfChange={setTf} />
          <DataStamp label={data.data_as_of_utc || data.timestamp} />
          <PriceChart symbol={symbol} tf={tf} verdict={data} />
          <PairDetailTabs symbol={symbol} tf={tf} verdict={data} confHist={confHist} />
        </>
      )}
    </div>
  );
}
