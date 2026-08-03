"use client";

import { useState } from "react";
import useSWR from "swr";
import { AlertRule, api } from "@/lib/api";
import { ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

const emptyRule: AlertRule = {
  name: "Actionable signals",
  enabled: true,
  actions: "LONG,SHORT",
  min_score: 35,
  confidence_contains: "",
  telegram: true,
  webhook_url: "",
};

export default function AlertsPage() {
  const { data, error, isLoading, mutate } = useSWR("alert-rules", () => api.alertRules());
  const [draft, setDraft] = useState<AlertRule>(emptyRule);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await api.saveAlertRule(draft);
      setDraft(emptyRule);
      await mutate();
    } catch (e) {
      alert((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  async function remove(id: number) {
    await api.deleteAlertRule(id);
    await mutate();
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Alert builder</h1>
        <p className="text-sm text-muted">
          Rules run after each scan. With no rules, default Telegram alerts apply for all LONG/SHORT.
        </p>
      </div>

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}

      <div className="card space-y-3 text-sm">
        <h2 className="font-semibold">New rule</h2>
        <input
          className="w-full rounded border border-border bg-slate-900 px-2 py-1"
          placeholder="Name"
          value={draft.name}
          onChange={(e) => setDraft({ ...draft, name: e.target.value })}
        />
        <label className="flex items-center gap-2">
          Min |score|
          <input
            type="number"
            className="w-24 rounded border border-border bg-slate-900 px-2 py-1"
            value={draft.min_score}
            onChange={(e) => setDraft({ ...draft, min_score: Number(e.target.value) })}
          />
        </label>
        <input
          className="w-full rounded border border-border bg-slate-900 px-2 py-1"
          placeholder="Confidence contains (optional, e.g. HIGH)"
          value={draft.confidence_contains}
          onChange={(e) => setDraft({ ...draft, confidence_contains: e.target.value })}
        />
        <input
          className="w-full rounded border border-border bg-slate-900 px-2 py-1"
          placeholder="Webhook URL (optional)"
          value={draft.webhook_url}
          onChange={(e) => setDraft({ ...draft, webhook_url: e.target.value })}
        />
        <button
          type="button"
          disabled={saving}
          onClick={save}
          className="rounded bg-sky-600 px-4 py-2 disabled:opacity-50"
        >
          Save rule
        </button>
      </div>

      {data && (
        <div className="card overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="pb-2">Name</th>
                <th className="pb-2">Min score</th>
                <th className="pb-2">Confidence</th>
                <th className="pb-2">Telegram</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {data.rules.map((r) => (
                <tr key={r.id} className="border-t border-border/60">
                  <td className="py-2">{r.name}</td>
                  <td className="py-2">{r.min_score}</td>
                  <td className="py-2">{r.confidence_contains || "—"}</td>
                  <td className="py-2">{r.telegram ? "yes" : "no"}</td>
                  <td className="py-2">
                    <button type="button" className="text-red-400" onClick={() => r.id && remove(r.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.rules.length === 0 && <p className="text-muted">No custom rules yet.</p>}
        </div>
      )}
    </div>
  );
}
