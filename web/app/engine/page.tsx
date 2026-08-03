import Link from "next/link";

const LANES = [
  {
    id: "technical",
    title: "Technical lane",
    measures: "Trend, momentum, and HTF alignment on OHLCV (EMA stack, RSI, ADX-style strength).",
    strengths: "Clear rules on trending markets; fast to compute.",
    weaknesses: "Lags in compression; can conflict with flow in shocks.",
    ignored: "When regime is SHOCK or BTC gate blocks alts.",
    weighted: "Higher in TRENDING_UP/DOWN per config regime weights.",
  },
  {
    id: "flow",
    title: "Flow / derivatives lane",
    measures: "Funding rate, funding z-score, OI vs price, taker buy ratio.",
    strengths: "Crowding and positioning edge; complements spot technicals.",
    weaknesses: "Needs futures data; degraded in backtest without history.",
    ignored: "Light scans may skip taker; neutral funding → zero contribution.",
    weighted: "Often elevated in RANGING/COMPRESSION regimes.",
  },
  {
    id: "structure",
    title: "Structure lane",
    measures: "Swing S/R clusters, breakouts, order-book walls (capped), volume profile POC/HVN/LVN.",
    strengths: "Location-based risk; NO_EDGE when mid-range.",
    weaknesses: "Book walls can be spoofed — influence is capped.",
    ignored: "no_edge=True blocks LONG/SHORT even if other lanes agree.",
    weighted: "Higher when price sits near levels in trending regimes.",
  },
  {
    id: "regime",
    title: "Regime gate (not scored)",
    measures: "4h trend class, ATR percentile shock/compression, BTC 1h move gate for alts.",
    strengths: "Honest NO-TRADE default; scales lane weights.",
    weaknesses: "Binary gates can feel conservative.",
    ignored: "Never adds points — only weights and blocks.",
    weighted: "Applies lane_weights map; SHOCK forces NO-TRADE.",
  },
];

export default function EnginePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Explain the engine</h1>
        <p className="text-sm text-muted">
          Deterministic lanes → synthesizer → calibration. See also{" "}
          <Link href="/glossary" className="text-sky-400 hover:underline">
            Glossary
          </Link>
          .
        </p>
      </div>
      {LANES.map((lane) => (
        <article key={lane.id} className="card space-y-2 text-sm">
          <h2 className="text-lg font-semibold text-sky-300">{lane.title}</h2>
          <p>
            <span className="text-muted">What it measures: </span>
            {lane.measures}
          </p>
          <p>
            <span className="text-muted">Strengths: </span>
            {lane.strengths}
          </p>
          <p>
            <span className="text-muted">Weaknesses: </span>
            {lane.weaknesses}
          </p>
          <p>
            <span className="text-muted">When ignored: </span>
            {lane.ignored}
          </p>
          <p>
            <span className="text-muted">How weighted: </span>
            {lane.weighted}
          </p>
        </article>
      ))}
    </div>
  );
}
