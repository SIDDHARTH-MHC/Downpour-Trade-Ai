"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function IntegrationsPage() {
  const { data, error, isLoading, mutate } = useSWR("integrations", () => api.integrationsGet());
  const [discord, setDiscord] = useState("");
  const [slack, setSlack] = useState("");
  const [saved, setSaved] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (data && !hydrated) {
      setDiscord(data.discord_webhook_url || "");
      setSlack(data.slack_webhook_url || "");
      setHydrated(true);
    }
  }, [data, hydrated]);

  async function save() {
    await api.integrationsSave({ discord_webhook_url: discord, slack_webhook_url: slack });
    setSaved(true);
    await mutate();
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Integrations</h1>
        <p className="text-sm text-muted">Discord &amp; Slack webhooks for actionable scan alerts</p>
      </div>
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="card space-y-3 text-sm">
          <p className="text-muted">{data.note}</p>
          <p>Telegram: {data.telegram_configured ? "configured via server env" : "not configured"}</p>
          <label className="block">
            Discord webhook URL
            <input
              className="mt-1 w-full rounded border border-border bg-slate-900 px-2 py-1"
              value={discord}
              onChange={(e) => setDiscord(e.target.value)}
            />
          </label>
          <label className="block">
            Slack webhook URL
            <input
              className="mt-1 w-full rounded border border-border bg-slate-900 px-2 py-1"
              value={slack}
              onChange={(e) => setSlack(e.target.value)}
            />
          </label>
          <button type="button" onClick={save} className="rounded bg-sky-600 px-4 py-2">
            Save
          </button>
          {saved && <p className="text-long">Saved.</p>}
        </div>
      )}
    </div>
  );
}
