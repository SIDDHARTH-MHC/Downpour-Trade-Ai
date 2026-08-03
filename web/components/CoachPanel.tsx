"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function CoachPanel({ symbol, action }: { symbol?: string; action?: string }) {
  const [message, setMessage] = useState("I keep entering before confirmation. Help me.");
  const [reply, setReply] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function send() {
    setLoading(true);
    try {
      const data = await api.coachChat(message, symbol, action);
      setReply(data.markdown);
    } catch (e) {
      setReply((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card space-y-3">
      <div>
        <h3 className="text-sm font-semibold">AI Coach</h3>
        <p className="text-xs text-muted">Education &amp; process — not trading advice</p>
      </div>
      <textarea
        className="w-full rounded border border-border bg-slate-900 p-2 text-sm"
        rows={3}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button
        type="button"
        onClick={send}
        disabled={loading}
        className="rounded bg-violet-700 px-3 py-1 text-sm disabled:opacity-50"
      >
        {loading ? "Thinking…" : "Ask coach"}
      </button>
      {reply && (
        <pre className="max-h-80 overflow-auto whitespace-pre-wrap rounded bg-slate-950 p-3 text-xs">{reply}</pre>
      )}
    </div>
  );
}
