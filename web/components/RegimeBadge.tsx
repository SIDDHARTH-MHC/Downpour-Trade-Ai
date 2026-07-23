export function RegimeBadge({ regime, tradeable }: { regime: string; tradeable: boolean }) {
  const color =
    regime === "SHOCK"
      ? "bg-red-900 text-red-200"
      : regime === "COMPRESSION"
        ? "bg-amber-900 text-amber-200"
        : regime.startsWith("TRENDING")
          ? "bg-blue-900 text-blue-200"
          : "bg-slate-700 text-slate-200";
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {regime} {tradeable ? "" : "· blocked"}
    </span>
  );
}
