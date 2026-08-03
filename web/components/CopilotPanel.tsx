"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function CopilotPanel({ symbol, tf }: { symbol: string; tf: string }) {
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function explain() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.copilotExplain(symbol, tf);
      setMarkdown(res.markdown);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold">Explain-only Copilot</h3>
          <p className="text-xs text-muted">Paraphrases engine JSON — never changes the verdict</p>
        </div>
        <button
          type="button"
          onClick={explain}
          disabled={loading}
          className="rounded bg-slate-700 px-3 py-1 text-sm disabled:opacity-50"
        >
          {loading ? "Explaining…" : "Why this verdict?"}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      {markdown && (
        <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap rounded bg-slate-950 p-3 text-xs text-slate-200">
          {markdown}
        </pre>
      )}
    </div>
  );
}
