"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { CompareColumns } from "@/components/modules/compare/CompareColumns";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function ComparePage() {
  const [a, setA] = useState("BTC/USDT");
  const [b, setB] = useState("ETH/USDT");
  const [tf, setTf] = useState("1h");
  const key = ["compare", a, b, tf];
  const { data, error, isLoading, mutate } = useSWR(key, () => api.compare(a, b, tf));

  return (
    <div className="space-y-4">
      <ModuleHeader title="Compare signals" description="Side-by-side lane scores and verdicts" />
      <div className="flex flex-wrap items-center gap-2">
        <Input className="h-8 w-36" value={a} onChange={(e) => setA(e.target.value.toUpperCase())} aria-label="Symbol A" />
        <span className="text-sm text-muted-foreground">vs</span>
        <Input className="h-8 w-36" value={b} onChange={(e) => setB(e.target.value.toUpperCase())} aria-label="Symbol B" />
        {(["1h", "4h"] as const).map((t) => (
          <Button key={t} type="button" size="sm" variant={tf === t ? "default" : "outline"} onClick={() => setTf(t)}>
            {t}
          </Button>
        ))}
        <Button type="button" size="sm" variant="secondary" onClick={() => mutate()}>
          Refresh
        </Button>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && <CompareColumns a={data.a} b={data.b} />}
    </div>
  );
}
