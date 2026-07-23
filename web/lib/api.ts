export type Verdict = {
  app: string;
  symbol: string;
  timeframe: string;
  timestamp: string;
  action: "LONG" | "SHORT" | "NO_TRADE";
  weighted_score: number;
  confidence: string;
  data_as_of_utc?: string;
  regime: {
    name: string;
    tradeable: boolean;
    lane_weights: Record<string, number>;
    evidence: string[];
  };
  lanes: Array<{
    name: string;
    score: number;
    evidence: string[];
    values: Record<string, number>;
    no_edge?: boolean;
  }>;
  reasons: string[];
  trade_plan: {
    entry: number;
    stop_loss: number;
    tp1: number;
    tp2: number;
    reward_risk: number;
    size_coin: number;
    size_usd: number;
    patient: boolean;
  } | null;
};

export type ScanResponse = {
  timeframe: string;
  data_as_of_utc: string;
  total: number;
  actionable_count: number;
  results: Verdict[];
  actionable: Verdict[];
};

export type HistoryResponse = {
  count: number;
  data_as_of_utc: string;
  verdicts: Verdict[];
  open_outcomes: number;
};

export type BacktestStatsResponse = {
  symbol: string;
  timeframe: string;
  data_as_of_utc: string;
  buckets: Record<
    string,
    {
      trade_count: number;
      win_rate: number;
      avg_r: number;
      profit_factor: number;
      max_drawdown_r?: number;
    }
  >;
};

export type PairsResponse = {
  data_as_of_utc: string;
  pairs: Array<{ symbol: string; volume?: number; updated_at?: string }>;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { next: { revalidate: 0 } });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  analyze: (symbol: string, tf = "1h") =>
    fetchJson<Verdict>(`/analyze?symbol=${encodeURIComponent(symbol)}&tf=${tf}`),
  scan: (tf = "1h") => fetchJson<ScanResponse>(`/scan?tf=${tf}`),
  history: (symbol?: string, limit = 50) =>
    fetchJson<HistoryResponse>(
      `/history?limit=${limit}${symbol ? `&symbol=${encodeURIComponent(symbol)}` : ""}`
    ),
  backtestStats: (symbol = "BTC/USDT", tf = "1h") =>
    fetchJson<BacktestStatsResponse>(
      `/backtest-stats?symbol=${encodeURIComponent(symbol)}&tf=${tf}`
    ),
  pairs: (limit = 50) => fetchJson<PairsResponse>(`/pairs?limit=${limit}`),
};
