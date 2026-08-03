export type Verdict = {
  app: string;
  symbol: string;
  timeframe: string;
  timestamp: string;
  action: "LONG" | "SHORT" | "NO_TRADE";
  weighted_score: number;
  confidence: string;
  data_as_of_utc?: string;
  attribution?: Record<string, number>;
  structure_events?: Array<{
    type: string;
    direction: string;
    level?: number;
    label: string;
  }>;
  trust?: TrustMetrics;
  replay_events?: ReplayEvent[];
  lifecycle?: LifecycleState;
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
  status?: string;
  message?: string;
  last_scan_utc?: string;
  scan_running?: boolean;
  scan_progress?: string;
  total: number;
  actionable_count: number;
  results: Verdict[];
  actionable: Verdict[];
  scan_report?: ScanReport | null;
};

export type ScanReport = {
  total_scanned: number;
  actionable_count: number;
  rejected_count: number;
  rejection_reasons: Record<string, number>;
};

export type ReplayEvent = { step: string; category: string; label: string };

export type LifecycleStep = { id: string; label: string; status: "done" | "current" | "upcoming" };

export type LifecycleState = {
  stage: string;
  label: string;
  steps: LifecycleStep[];
  outcome?: string | null;
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

export type CalibrateStatusResponse = {
  status?: string;
  running: boolean;
  progress: string;
  last_calibrated_utc: string;
  last_error?: string;
  bucket_count?: number;
  buckets?: BacktestStatsResponse["buckets"];
  message?: string;
  data_as_of_utc: string;
  walk_forward?: Array<{
    symbol?: string;
    accepted?: boolean;
    out_of_sample_profit_factor?: number;
    out_of_sample_trades?: number;
  }> | null;
};

export type PairsResponse = {
  data_as_of_utc: string;
  pairs: Array<{ symbol: string; volume?: number; updated_at?: string }>;
};

export type TrustMetrics = {
  confidence: string;
  score_bucket: string | null;
  historical_win_rate?: number | null;
  backtested_trades?: number | null;
  profit_factor?: number | null;
  average_r?: number | null;
  max_drawdown_r?: number | null;
  walk_forward_passed: boolean | null;
  walk_forward: {
    passed: boolean | null;
    symbols: number;
    detail: Array<{ symbol?: string; accepted?: boolean; out_of_sample_profit_factor?: number }>;
  };
  last_calibrated_utc: string;
  data_as_of_utc: string;
};

export type TrustResponse = {
  symbol: string;
  timeframe: string;
  trust: TrustMetrics;
};

export type ConfidencePoint = {
  timestamp: string;
  symbol: string;
  timeframe: string;
  action: string;
  weighted_score: number;
  confidence: string;
  outcome: string | null;
};

export type ConfidenceHistoryResponse = {
  symbol: string | null;
  count: number;
  points: ConfidencePoint[];
  data_as_of_utc: string;
};

export type FlowsSnapshotResponse = {
  symbols: string[];
  rows: Array<{
    symbol: string;
    funding_rate: number | null;
    funding_rate_pct: number | null;
    open_interest_usd: number | null;
    oi_change_1bar: number | null;
  }>;
  data_as_of_utc: string;
};

export type MacroSnapshotResponse = {
  macro: {
    btc_dominance?: number;
    eth_dominance?: number;
    total_market_cap_usd?: number;
    total_volume_usd?: number;
    market_cap_change_24h_pct?: number;
    updated_at?: string;
    error?: string;
  };
  data_as_of_utc: string;
};

export type MacroRiskResponse = {
  risk: {
    updated_at_utc: string;
    dxy_last?: number;
    dxy_24h_pct?: number | null;
    risk_off: boolean;
    risk_off_threshold_pct?: number;
    regime_gate_enabled?: boolean;
    source: string;
    disclaimer?: string;
  };
  data_as_of_utc: string;
};

export type LiquidationsContextResponse = {
  liquidations: {
    status: string;
    symbol: string;
    updated_at_utc: string;
    message: string;
    elevated_forced_flow?: boolean;
    disclaimer: string;
    stress?: Record<string, unknown>;
  };
  data_as_of_utc: string;
};

export type OnchainContextResponse = {
  onchain: {
    updated_at_utc: string;
    asset: string;
    status: string;
    disclaimer: string;
    market_price_usd?: number;
    hash_rate?: number;
    mempool_tx_count?: number;
    fees_sat_vb?: Record<string, number | undefined>;
  };
  data_as_of_utc: string;
};

export type BatchAnalyzeResponse = {
  timeframe: string;
  results: Verdict[];
  errors: Record<string, string>;
  data_as_of_utc: string;
};

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const url = `${API_URL}${path}`;
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
      throw new Error(`API ${path} failed: ${res.status} (${API_URL})`);
    }
    return res.json() as Promise<T>;
  } catch (err) {
    if (err instanceof Error && err.message.startsWith("API")) throw err;
    throw new Error(
      `Cannot reach API at ${API_URL}. Set NEXT_PUBLIC_API_URL on Vercel and ALLOWED_ORIGINS on Render, then redeploy both.`
    );
  }
}

async function fetchInternalJson<T>(path: string, init?: RequestInit): Promise<T | null> {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, { cache: "no-store", ...init });
  if (res.status === 404) return null;
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
  calibrateStatus: () => fetchJson<CalibrateStatusResponse>("/calibrate"),
  startCalibrate: (months = 6, symbols = "BTC/USDT,ETH/USDT", tf = "1h") =>
    fetch(`${API_URL}/calibrate?months=${months}&symbols=${encodeURIComponent(symbols)}&tf=${tf}`, {
      method: "POST",
      cache: "no-store",
    }).then(async (res) => {
      const body = (await res.json()) as CalibrateStatusResponse;
      if (!res.ok) throw new Error(body.message || `Calibration failed: ${res.status}`);
      return body;
    }),
  pairs: (limit = 50) => fetchJson<PairsResponse>(`/pairs?limit=${limit}`),
  trust: (symbol: string, tf = "1h") =>
    fetchJson<TrustResponse>(`/trust?symbol=${encodeURIComponent(symbol)}&tf=${tf}`),
  confidenceHistory: (symbol?: string, limit = 30) =>
    fetchJson<ConfidenceHistoryResponse>(
      `/confidence-history?limit=${limit}${symbol ? `&symbol=${encodeURIComponent(symbol)}` : ""}`
    ),
  flowsSnapshot: (symbols: string) =>
    fetchJson<FlowsSnapshotResponse>(`/flows/snapshot?symbols=${encodeURIComponent(symbols)}`),
  macroSnapshot: () => fetchJson<MacroSnapshotResponse>("/macro/snapshot"),
  macroRisk: () => fetchJson<MacroRiskResponse>("/macro/risk"),
  contextLiquidations: (symbol = "BTC/USDT") =>
    fetchJson<LiquidationsContextResponse>(`/context/liquidations?symbol=${encodeURIComponent(symbol)}`),
  contextOnchain: () => fetchJson<OnchainContextResponse>("/context/onchain"),
  analyzeBatch: (symbols: string[], tf = "1h") =>
    fetchJson<BatchAnalyzeResponse>(
      `/analyze/batch?symbols=${encodeURIComponent(symbols.join(","))}&tf=${tf}`
    ),
  engineStatus: () => fetchJson<EngineStatusResponse>("/status"),
  copilotExplain: (symbol: string, tf = "1h") =>
    fetch(`${API_URL}/copilot/explain?symbol=${encodeURIComponent(symbol)}&tf=${tf}`, {
      method: "POST",
      cache: "no-store",
    }).then(async (res) => {
      const body = (await res.json()) as CopilotResponse;
      if (!res.ok) throw new Error("Copilot explain failed");
      return body;
    }),
  alertRules: () => fetchJson<AlertRulesResponse>("/alerts/rules"),
  saveAlertRule: (rule: AlertRule) =>
    fetch(`${API_URL}/alerts/rules`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(rule),
      cache: "no-store",
    }).then(async (res) => {
      if (!res.ok) throw new Error("Save alert rule failed");
      return res.json();
    }),
  deleteAlertRule: (id: number) =>
    fetch(`${API_URL}/alerts/rules/${id}`, { method: "DELETE", cache: "no-store" }),
  contextNews: (symbol: string, limit = 12, category?: string) => {
    const params = new URLSearchParams({ symbol, limit: String(limit) });
    if (category) params.set("category", category);
    return fetchJson<NewsContextResponse>(`/context/news?${params.toString()}`);
  },
  contextEtf: () => fetchJson<EtfContextResponse>("/context/etf"),
  liquiditySnapshot: (symbol: string) =>
    fetchJson<LiquiditySnapshotResponse>(`/structure/liquidity?symbol=${encodeURIComponent(symbol)}`),
  correlationMatrix: (symbols: string, tf = "1h") =>
    fetchJson<CorrelationMatrixResponse>(
      `/correlation/matrix?tf=${tf}&symbols=${encodeURIComponent(symbols)}`
    ),
  runScenario: (body: ScenarioRequest) =>
    fetch(`${API_URL}/scenarios/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    }).then(async (res) => {
      const data = (await res.json()) as ScenarioResponse;
      if (!res.ok) throw new Error("Scenario run failed");
      return data;
    }),
  compare: (a: string, b: string, tf = "1h") =>
    fetchJson<CompareResponse>(`/compare?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}&tf=${tf}`),
  coachChat: (message: string, symbol?: string, action?: string) =>
    fetch(`${API_URL}/coach/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, symbol, action }),
      cache: "no-store",
    }).then(async (res) => {
      const data = (await res.json()) as CoachChatResponse;
      if (!res.ok) throw new Error("Coach request failed");
      return data;
    }),
  journalList: (limit = 50) => fetchJson<JournalListResponse>(`/journal?limit=${limit}`),
  journalSave: (entry: JournalEntry) =>
    fetch(`${API_URL}/journal`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entry),
      cache: "no-store",
    }).then(async (res) => {
      if (!res.ok) throw new Error("Save journal failed");
      return res.json();
    }),
  journalDelete: (id: number) => fetch(`${API_URL}/journal/${id}`, { method: "DELETE", cache: "no-store" }),
  portfolioAnalytics: (equity = 10_000) =>
    fetchJson<PortfolioAnalyticsResponse>(`/portfolio/analytics?equity=${equity}`),
  integrationsGet: () => fetchJson<IntegrationsResponse>("/integrations"),
  integrationsSave: (body: { discord_webhook_url: string; slack_webhook_url: string }) =>
    fetch(`${API_URL}/integrations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    }).then(async (res) => {
      if (!res.ok) throw new Error("Save integrations failed");
      return res.json();
    }),
  researchDashboard: () =>
    fetchInternalJson<ResearchDashboardResponse>("/internal/research/v1/dashboard"),
  researchPromotionDecide: (
    runId: string,
    body: {
      decision: "PROMOTED" | "REJECTED" | "DEFERRED";
      reason: string;
      approved_by: string;
      promotion_class?: string;
    }
  ) =>
    fetchInternalJson<{ run_id: string; decision: string; note: string }>(
      `/internal/research/v1/promotion-queue/${encodeURIComponent(runId)}/decide`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }
    ).then((data) => {
      if (data === null) throw new Error("Internal research API is disabled (404)");
      return data;
    }),
};

export type EngineStatusResponse = {
  status: string;
  checks: Record<string, { status: string; detail: string }>;
  last_scan_report?: ScanReport | null;
  data_as_of_utc: string;
};

export type CopilotResponse = {
  markdown: string;
  disclaimer: string;
  action?: string;
};

export type AlertRule = {
  id?: number;
  name: string;
  enabled: boolean;
  actions: string;
  min_score: number;
  confidence_contains: string;
  telegram: boolean;
  webhook_url: string;
};

export type AlertRulesResponse = { rules: AlertRule[] };

export type NewsHeadline = {
  title?: string;
  url?: string | null;
  source?: string;
  category?: string;
  published?: string | null;
  symbols?: string[];
  sentiment?: string;
};

export type NewsContextResponse = {
  symbol: string;
  base: string;
  aggregated_at_utc?: string;
  feed_count?: number;
  headlines: NewsHeadline[];
  disclaimer: string;
};

export type EtfContextResponse = {
  etf: {
    status: string;
    message: string;
    reference_tickers: string[];
    disclaimer: string;
    updated_at_utc?: string;
    proxies?: Array<{
      ticker: string;
      last_close_usd?: number;
      daily_change_pct?: number | null;
      error?: string;
    }>;
  };
};

export type LiquiditySnapshotResponse = {
  symbol: string;
  mid_price: number;
  walls: Array<{ side: string; price: number; notional_usd: number }>;
  bids: Array<{ price: number; amount: number; notional_usd: number }>;
  asks: Array<{ price: number; amount: number; notional_usd: number }>;
  disclaimer: string;
};

export type CorrelationMatrixResponse = {
  timeframe: string;
  benchmark: string;
  data_as_of_utc?: string;
  rows: Array<{
    symbol: string;
    correlation: number | null;
    beta_vs_btc: number | null;
    error?: string;
  }>;
};

export type ScenarioRequest = { shock_pct: number; shock_asset?: string; tf?: string };

export type ScenarioResponse = {
  shock_pct: number;
  shock_asset: string;
  open_positions: number;
  positions: Array<{
    symbol: string;
    action: string;
    move_pct: number;
    shocked_price: number;
    sl_hit: boolean;
    tp1_hit: boolean;
  }>;
  disclaimer: string;
};

export type CompareSide = {
  symbol: string;
  action: string;
  weighted_score: number;
  confidence: string;
  regime: string;
  lanes: Record<string, number>;
};

export type CompareResponse = {
  timeframe: string;
  data_as_of_utc?: string;
  a: CompareSide;
  b: CompareSide;
};

export type CoachChatResponse = {
  topic: string;
  markdown: string;
  disclaimer: string;
};

export type JournalEntry = {
  id?: number;
  symbol?: string;
  title: string;
  body: string;
  tags?: string;
};

export type JournalListResponse = {
  entries: Array<JournalEntry & { created_at?: string; updated_at?: string }>;
};

export type PortfolioAnalyticsResponse = {
  equity_usd: number;
  open_trades: number;
  long_count: number;
  short_count: number;
  total_risk_usd: number;
  portfolio_heat_pct: number;
  avg_reward_risk: number | null;
  positions: Array<{
    symbol: string;
    action: string;
    risk_usd: number;
    reward_risk: number;
  }>;
  config_risk: {
    account_risk_pct: number;
    min_reward_risk: number;
    default_equity_usd: number;
  };
  disclaimer: string;
  data_as_of_utc?: string;
};

export type IntegrationsResponse = {
  discord_webhook_url: string;
  slack_webhook_url: string;
  telegram_configured: boolean;
  note: string;
};

export type ResearchDashboardResponse = {
  data_as_of_utc: string;
  internal_api_enabled: boolean;
  research_db_enabled: boolean;
  research_scheduler_enabled: boolean;
  promotion_policy: string;
  database: Record<string, unknown>;
  scheduler: { running: boolean; jobs: Array<{ id: string; next_run_utc: string | null; trigger: string }> };
  automation: Record<string, unknown>;
  collector: { last_run: Record<string, unknown> | null; watermarks: Array<Record<string, unknown>> };
  data_quality: {
    enabled: boolean;
    summary: Record<string, number>;
    reports: Array<Record<string, unknown>>;
  };
  datasets: Array<Record<string, unknown>>;
  storage: {
    filesystem: { bytes_by_path: Record<string, number>; total_bytes: number };
    timescale: Record<string, unknown>;
  };
  walk_forward: { last: Record<string, unknown> | null; recent_runs: Array<Record<string, unknown>> };
  calibration: Record<string, unknown>;
  promotion_queue: Array<Record<string, unknown>>;
  promotion_history: Array<Record<string, unknown>>;
  experiments: Array<Record<string, unknown>>;
  logs: Array<{ kind: string; at: string; status?: string; detail?: unknown }>;
};

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  if (n < 1024 * 1024 * 1024) return `${(n / (1024 * 1024)).toFixed(1)} MB`;
  return `${(n / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
