export function DisclaimerFooter() {
  return (
    <footer className="mt-10 border-t border-border pt-4 text-xs text-muted">
      Downpour Trade AI is for informational and educational purposes only. It is not financial advice
      and is not registered with SEBI or any regulatory body. Markets are probabilistic — risk only
      what you can afford to lose.
    </footer>
  );
}

export function DataStamp({ label }: { label?: string }) {
  if (!label) return null;
  return <p className="text-xs text-muted">Data as of {label}</p>;
}

export function LoadingCard() {
  return (
    <div className="card space-y-3">
      <div className="skeleton h-6 w-1/3" />
      <div className="skeleton h-4 w-full" />
      <div className="skeleton h-4 w-2/3" />
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="card border-short/40 text-short">
      <p className="font-medium">Failed to load data</p>
      <p className="text-sm">{message}</p>
    </div>
  );
}
