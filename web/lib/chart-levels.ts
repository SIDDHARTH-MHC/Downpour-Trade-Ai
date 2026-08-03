import type { Verdict } from "@/lib/api";

export type ChartLevel = { label: string; price: number; kind?: "entry" | "sl" | "tp" | "structure" };

export function collectChartLevels(verdict: Verdict): ChartLevel[] {
  const out: ChartLevel[] = [];
  const structure = verdict.lanes.find((l) => l.name === "structure");
  const values = structure?.values ?? {};

  const push = (label: string, price: unknown, kind?: ChartLevel["kind"]) => {
    const n = typeof price === "number" ? price : Number(price);
    if (!Number.isFinite(n)) return;
    out.push({ label, price: n, kind });
  };

  push("POC", values.poc, "structure");
  push("Support", values.nearest_support, "structure");
  push("Resistance", values.nearest_resistance, "structure");

  for (const ev of verdict.structure_events || []) {
    if (ev.level != null) push(`${ev.type}`, ev.level, "structure");
  }

  const plan = verdict.trade_plan;
  if (plan) {
    push("Entry", plan.entry, "entry");
    push("SL", plan.stop_loss, "sl");
    push("TP1", plan.tp1, "tp");
    push("TP2", plan.tp2, "tp");
  }

  return out;
}

export function binanceSymbol(pair: string) {
  return pair.replace("/", "").toUpperCase();
}

export function binanceInterval(tf: string) {
  if (tf === "15m") return "15m";
  if (tf === "4h") return "4h";
  return "1h";
}
