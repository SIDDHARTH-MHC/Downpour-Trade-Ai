"use client";

import { useState } from "react";
import useSWR from "swr";
import { JournalEntry, api } from "@/lib/api";
import { LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";

const empty: JournalEntry = { title: "", body: "", symbol: "", tags: "" };

export default function NotebookPage() {
  const { data, isLoading, mutate } = useSWR("journal", () => api.journalList(50));
  const [draft, setDraft] = useState<JournalEntry>(empty);
  const [saving, setSaving] = useState(false);

  async function save() {
    if (!draft.title.trim() || !draft.body.trim()) return;
    setSaving(true);
    try {
      await api.journalSave(draft);
      setDraft(empty);
      await mutate();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Research notebook"
        description="Log what the engine said vs what you did — stored on the API server"
      />
      <div className="card space-y-2 text-sm">
        <input
          className="w-full rounded border border-border bg-slate-900 px-2 py-1"
          placeholder="Title"
          value={draft.title}
          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
        />
        <input
          className="w-full rounded border border-border bg-slate-900 px-2 py-1"
          placeholder="Symbol (optional)"
          value={draft.symbol}
          onChange={(e) => setDraft({ ...draft, symbol: e.target.value })}
        />
        <textarea
          className="w-full rounded border border-border bg-slate-900 px-2 py-1"
          rows={5}
          placeholder="Notes…"
          value={draft.body}
          onChange={(e) => setDraft({ ...draft, body: e.target.value })}
        />
        <button type="button" onClick={save} disabled={saving} className="rounded bg-sky-600 px-4 py-2 disabled:opacity-50">
          Save entry
        </button>
      </div>
      {isLoading && <LoadingCard />}
      {data && (
        <div className="space-y-3">
          {data.entries.map((e) => (
            <article key={e.id} className="card text-sm">
              <div className="flex justify-between gap-2">
                <h2 className="font-semibold">{e.title}</h2>
                <button
                  type="button"
                  className="text-xs text-red-400"
                  onClick={() => e.id && api.journalDelete(e.id).then(() => mutate())}
                >
                  Delete
                </button>
              </div>
              {e.symbol && <p className="text-muted">{e.symbol}</p>}
              <p className="mt-2 whitespace-pre-wrap">{e.body}</p>
              <p className="mt-2 text-xs text-muted">{e.created_at}</p>
            </article>
          ))}
          {data.entries.length === 0 && <p className="text-muted">No entries yet.</p>}
        </div>
      )}
    </div>
  );
}
