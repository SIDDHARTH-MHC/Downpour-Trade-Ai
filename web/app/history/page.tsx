"use client";

import useSWR from "swr";
import Link from "next/link";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function HistoryPage() {
  const { data, error, isLoading } = useSWR("history", () => api.history(undefined, 50), {
    refreshInterval: 120_000,
  });

  const wins = data?.verdicts.filter((v) => v.action !== "NO_TRADE").length ?? 0;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Verdict history</h1>
        <p className="text-sm text-muted">Past signals with outcomes when resolved</p>
      </div>
      <DataStamp label={data?.data_as_of_utc} />

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="card overflow-x-auto">
          <p className="mb-3 text-sm text-muted">
            {data.count} records · {wins} non-NO-TRADE · {data.open_outcomes} open outcomes
          </p>
          <table className="min-w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="pb-2">Time</th>
                <th className="pb-2">Pair</th>
                <th className="pb-2">TF</th>
                <th className="pb-2">Action</th>
                <th className="pb-2">Score</th>
                <th className="pb-2">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {data.verdicts.map((v, i) => (
                <tr key={i} className="border-t border-border/60">
                  <td className="py-2">{v.timestamp}</td>
                  <td className="py-2">
                    <Link href={`/pair/${encodeURIComponent(v.symbol)}`} className="text-sky-400 hover:underline">
                      {v.symbol}
                    </Link>
                  </td>
                  <td className="py-2">{v.timeframe}</td>
                  <td className="py-2">{v.action}</td>
                  <td className="py-2">{v.weighted_score.toFixed(1)}</td>
                  <td className="py-2">{v.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
