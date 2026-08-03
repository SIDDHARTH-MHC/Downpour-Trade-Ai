"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";

function pct(v: number | null | undefined, digits = 2) {
  if (v == null || Number.isNaN(v)) return "—";
  return `${(v * 100).toFixed(digits)}%`;
}

export default function MacroPage() {
  const { data, error, isLoading } = useSWR("macro", () => api.macroSnapshot(), { refreshInterval: 300_000 });
  const { data: risk, error: riskErr, isLoading: riskLoading } = useSWR("macro-risk", () => api.macroRisk(), {
    refreshInterval: 300_000,
  });
  const { data: etf } = useSWR("etf", () => api.contextEtf(), { refreshInterval: 600_000 });
  const { data: onchain, error: chainErr } = useSWR("onchain", () => api.contextOnchain(), {
    refreshInterval: 300_000,
  });

  const m = data?.macro;
  const r = risk?.risk;
  const chain = onchain?.onchain;

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Macro snapshot"
        description="Global crypto context (CoinGecko), DXY risk (Stooq), ETF/on-chain reference — not mixed into lane scores except optional DXY regime nudge"
      />
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {m?.error && <ErrorState message={m.error} />}
      {m && !m.error && (
        <dl className="card grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-muted">BTC dominance</dt>
            <dd className="text-xl font-semibold">{m.btc_dominance?.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted">ETH dominance</dt>
            <dd className="text-xl font-semibold">{m.eth_dominance?.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted">Total market cap</dt>
            <dd className="text-xl font-semibold">${((m.total_market_cap_usd ?? 0) / 1e12).toFixed(2)}T</dd>
          </div>
          <div>
            <dt className="text-muted">24h mcap change</dt>
            <dd className="text-xl font-semibold">{m.market_cap_change_24h_pct?.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted">24h volume</dt>
            <dd className="text-xl font-semibold">${((m.total_volume_usd ?? 0) / 1e9).toFixed(1)}B</dd>
          </div>
        </dl>
      )}

      <section className="card space-y-3 text-sm">
        <h2 className="font-semibold text-sky-300">DXY risk (regime context)</h2>
        {riskLoading && <p className="text-muted">Loading DXY…</p>}
        {riskErr && <ErrorState message={(riskErr as Error).message} />}
        {r && (
          <>
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div>
                <dt className="text-muted">DXY last</dt>
                <dd className="text-lg font-semibold">{r.dxy_last?.toFixed(3) ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted">24h change</dt>
                <dd className="text-lg font-semibold">{pct(r.dxy_24h_pct)}</dd>
              </div>
              <div>
                <dt className="text-muted">Risk-off flag</dt>
                <dd className="text-lg font-semibold">{r.risk_off ? "Yes" : "No"}</dd>
              </div>
              <div>
                <dt className="text-muted">Regime gate</dt>
                <dd className="text-lg font-semibold">{r.regime_gate_enabled ? "On" : "Off"}</dd>
              </div>
            </dl>
            <p className="text-xs text-muted">{r.disclaimer}</p>
          </>
        )}
      </section>

      {etf?.etf && (
        <div className="card space-y-3 text-sm">
          <h2 className="font-semibold text-sky-300">ETF context (reference)</h2>
          <p className="text-muted">{etf.etf.message}</p>
          {etf.etf.proxies && etf.etf.proxies.length > 0 && (
            <ul className="grid gap-2 sm:grid-cols-3">
              {etf.etf.proxies.map((p) => (
                <li key={p.ticker} className="rounded-md border border-border/40 p-2">
                  <span className="font-medium">{p.ticker}</span>
                  {p.error ? (
                    <p className="text-xs text-muted">{p.error}</p>
                  ) : (
                    <>
                      <p className="text-lg font-semibold">${p.last_close_usd?.toFixed(2)}</p>
                      <p className="text-muted">1d {pct(p.daily_change_pct ?? null)}</p>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
          <p className="text-xs text-muted">{etf.etf.disclaimer}</p>
        </div>
      )}

      <section className="card space-y-3 text-sm">
        <h2 className="font-semibold text-sky-300">On-chain context (BTC)</h2>
        {chainErr && <ErrorState message={(chainErr as Error).message} />}
        {chain && (
          <>
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div>
                <dt className="text-muted">Spot (chain index)</dt>
                <dd className="text-lg font-semibold">
                  {chain.market_price_usd ? `$${Number(chain.market_price_usd).toLocaleString()}` : "—"}
                </dd>
              </div>
              <div>
                <dt className="text-muted">Mempool txs</dt>
                <dd className="text-lg font-semibold">{chain.mempool_tx_count?.toLocaleString() ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted">Fast fee (sat/vB)</dt>
                <dd className="text-lg font-semibold">{chain.fees_sat_vb?.fastest ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted">Hash rate</dt>
                <dd className="text-lg font-semibold">
                  {chain.hash_rate ? `${(Number(chain.hash_rate) / 1e18).toFixed(2)} EH/s` : "—"}
                </dd>
              </div>
            </dl>
            <p className="text-xs text-muted">{chain.disclaimer}</p>
          </>
        )}
      </section>
    </div>
  );
}
