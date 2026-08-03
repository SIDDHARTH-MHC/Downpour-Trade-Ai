import Link from "next/link";
import type { ReactNode } from "react";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

function TermTable({ rows }: { rows: [string, string][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <tbody>
          {rows.map(([term, meaning]) => (
            <tr key={term} className="border-t border-border/60 first:border-t-0">
              <td className="py-2 pr-4 align-top font-medium text-sky-300 whitespace-nowrap">{term}</td>
              <td className="py-2 text-muted">{meaning}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">{children}</CardContent>
    </Card>
  );
}

export default function GlossaryPage() {
  return (
    <div className="space-y-6">
      <ModuleHeader
        title="Glossary"
        description="What every label on Downpour Trade AI means — deterministic math on live Binance data, no LLM."
      />

      <Section title="Keyboard shortcuts">
        <p className="text-sm text-muted">
          Press <strong className="text-slate-200">?</strong> anywhere in the app for the full list. Examples:{" "}
          <strong className="text-slate-200">⌘K</strong> command palette, <strong className="text-slate-200">G then D</strong>{" "}
          dashboard, <strong className="text-slate-200">⌘B</strong> toggle sidebar.
        </p>
      </Section>

      <Section title="Core idea">
        <p className="text-sm text-muted">
          The engine reads live market data, scores four independent{" "}
          <strong className="text-slate-200">lanes</strong>, and outputs a{" "}
          <strong className="text-slate-200">verdict</strong>: LONG, SHORT, or NO-TRADE.{" "}
          <strong className="text-slate-200">NO-TRADE is the expected default</strong> — the system only
          signals when strict multi-lane rules align. Every evidence line cites an actual number from the
          exchange.
        </p>
      </Section>

      <Section title="Pages">
        <TermTable
          rows={[
            ["Dashboard", "Latest batch scan of top-volume USDT pairs."],
            ["History", "Past verdicts saved by the API, with outcomes when resolved."],
            ["Backtests", "Historical win-rate tables that power confidence labels."],
            ["Pair detail", "Full breakdown for one symbol — lanes, score, trade plan, chart."],
          ]}
        />
      </Section>

      <Section title="Dashboard columns">
        <TermTable
          rows={[
            ["Pair", "Trading symbol, e.g. BTC/USDT (coin priced in USDT)."],
            ["Regime", "Current market 'weather' — see Regime types below."],
            ["Score", "Weighted score from −100 (bearish) to +100 (bullish)."],
            ["Verdict", "Final action: LONG, SHORT, or NO_TRADE."],
            ["Actionable signals", "Pairs where verdict is not NO-TRADE."],
            ["Scan in progress", "Background analysis running (every ~15 minutes)."],
            ["Data as of", "Timestamp (UTC) when this data was computed."],
          ]}
        />
      </Section>

      <Section title="Verdicts">
        <TermTable
          rows={[
            [
              "LONG",
              "Bullish setup passed all rules: weighted score ≥ +35, at least 2 lanes aligned, no major conflict, regime tradeable.",
            ],
            ["SHORT", "Bearish mirror of LONG (score ≤ −35)."],
            [
              "NO_TRADE",
              "Default — insufficient alignment, bad reward:risk, regime block, conflicting lanes, or structure has no edge.",
            ],
          ]}
        />
      </Section>

      <Section title="The four lanes">
        <p className="text-sm text-muted">
          Each lane scores −100 to +100. Evidence lines always include the measured value.
        </p>
        <div className="space-y-4 text-sm">
          <div>
            <h3 className="font-medium text-slate-200">Technical</h3>
            <p className="text-muted">
              Chart indicators: EMA stack, RSI, MACD, ADX, higher-timeframe alignment.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-slate-200">Flow</h3>
            <p className="text-muted">
              Derivatives positioning: funding rate, open interest (OI), taker buy/sell imbalance, funding
              z-score.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-slate-200">Structure</h3>
            <p className="text-muted">
              Support/resistance, order-book walls, volume profile (POC, HVN, LVN), breakouts.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-slate-200">Regime</h3>
            <p className="text-muted">
              Not a scored lane on the pair page — it gates whether any signal is trusted and adjusts lane
              weights. Shown as a badge.
            </p>
          </div>
        </div>
      </Section>

      <Section title="Regime types">
        <TermTable
          rows={[
            ["TRENDING_UP", "4h uptrend — technical lane weighted higher."],
            ["TRENDING_DOWN", "4h downtrend."],
            ["RANGING", "Sideways — structure / S&R weighted higher."],
            ["COMPRESSION", "Very low volatility — breakout setups favored."],
            ["SHOCK", "Extreme volatility — forced NO-TRADE."],
            ["· blocked", "Regime prevents trading (SHOCK, or BTC moving hard during alt analysis)."],
          ]}
        />
      </Section>

      <Section title="Confidence labels">
        <p className="text-sm text-muted">Only shown for LONG/SHORT. Based on backtested history, never guessed.</p>
        <TermTable
          rows={[
            ["HIGH", "Backtest: ≥55% win rate, ≥100 trades, profit factor ≥1.4."],
            ["MODERATE", "≥48% win rate, ≥50 trades, profit factor ≥1.15."],
            ["LOW", "Passed verdict rules but weaker historical edge."],
            ["INSUFFICIENT_DATA", "Not enough backtest trades in this score bucket."],
            ["N/A", "NO-TRADE or regime blocked."],
          ]}
        />
      </Section>

      <Section title="Trade plan">
        <p className="text-sm text-muted">Only appears when verdict is LONG or SHORT.</p>
        <TermTable
          rows={[
            ["Entry", "Suggested entry (mid of bid/ask)."],
            ["SL", "Stop loss — exit if wrong (~1.5× ATR beyond nearest level)."],
            ["TP1", "First target at nearest opposing support/resistance."],
            ["TP2", "Second target at ~2× risk from entry."],
            ["R:R", "Reward:Risk to TP1 — must be ≥1.2 or trade is rejected."],
            ["Size / USD", "Position size assuming ~1% account risk."],
          ]}
        />
      </Section>

      <Section title="History page">
        <TermTable
          rows={[
            ["Records", "Past verdicts stored by the server."],
            ["Non-NO-TRADE", "Signals that were LONG or SHORT."],
            ["Open outcomes", "Signals still waiting — did TP1 or SL hit?"],
            ["TF", "Timeframe the signal was generated on (15m, 1h, 4h)."],
            ["Outcome", "TP1 = target hit first; SL = stop hit first."],
          ]}
        />
      </Section>

      <Section title="Backtests page">
        <TermTable
          rows={[
            ["Calibration", "Replaying the engine on months of history to measure win rates."],
            ["Run calibration", "Starts a long job (10–30+ min) on major pairs."],
            ["Bucket", "Score-range group, e.g. 35–50 or 50+."],
            ["Win rate", "% of trades where TP1 hit before SL."],
            ["Avg R", "Average profit/loss in R units (1R = one stop distance)."],
            ["Profit factor", "Gross wins ÷ gross losses — above 1.0 is net positive in backtest."],
          ]}
        />
      </Section>

      <Section title="Common abbreviations">
        <TermTable
          rows={[
            ["ATR", "Average True Range — volatility measure for distances."],
            ["EMA", "Exponential Moving Average."],
            ["RSI", "Relative Strength Index — momentum."],
            ["MACD", "Moving Average Convergence Divergence."],
            ["OI", "Open Interest on futures."],
            ["POC", "Point of Control — price with most volume."],
            ["HVN / LVN", "High / Low Volume Node — acceptance vs rejection zones."],
            ["HTF", "Higher timeframe (e.g. 4h when primary is 1h)."],
            ["PF", "Profit factor."],
          ]}
        />
      </Section>

      <Section title="Evidence examples">
        <ul className="space-y-2 text-sm text-muted">
          <li>
            <span className="text-slate-200">RSI(14)=36.2 → bearish (−10)</span> — RSI below 40 adds bearish
            points.
          </li>
          <li>
            <span className="text-slate-200">OI +6.2% w/ price +1.8% → new longs (+15)</span> — rising open
            interest with rising price = new long positions.
          </li>
          <li>
            <span className="text-slate-200">bid wall $9.5M @ 65431 (+20)</span> — large buy orders near price
            (capped influence — walls can be spoofed).
          </li>
          <li>
            <span className="text-slate-200">no_edge</span> — price mid-range, far from support and
            resistance → usually NO-TRADE.
          </li>
        </ul>
      </Section>

      <Alert className="border-amber-900/40 bg-amber-950/20">
        <AlertTitle className="text-amber-200">Disclaimer</AlertTitle>
        <AlertDescription className="text-muted">
          <p>
            Downpour Trade AI is for informational and educational purposes only. It is not financial advice
            and is not registered with SEBI or any regulatory body. Past backtest win rates do not guarantee
            future results. Risk only what you can afford to lose.
          </p>
          <p className="mt-3">
            Ready to explore?{" "}
            <Link href="/" className="text-primary hover:underline">
              Open Dashboard
            </Link>
          </p>
        </AlertDescription>
      </Alert>
    </div>
  );
}
