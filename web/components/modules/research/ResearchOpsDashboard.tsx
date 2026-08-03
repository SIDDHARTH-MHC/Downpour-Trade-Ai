"use client";

import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { api, formatBytes, type ResearchDashboardResponse } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">{children}</CardContent>
    </Card>
  );
}

function PromotionQueue({
  items,
  onDecided,
}: {
  items: ResearchDashboardResponse["promotion_queue"];
  onDecided: () => void;
}) {
  const [reviewer, setReviewer] = useState("");
  const [busyId, setBusyId] = useState<string | null>(null);

  async function decide(runId: string, decision: "PROMOTED" | "REJECTED" | "DEFERRED") {
    const reason = window.prompt(`${decision} — reason (required):`);
    if (!reason?.trim()) {
      toast.error("Reason is required");
      return;
    }
    if (!reviewer.trim()) {
      toast.error("Enter your name in “Reviewer” first");
      return;
    }
    setBusyId(runId);
    try {
      const res = await api.researchPromotionDecide(runId, {
        decision,
        reason: reason.trim(),
        approved_by: reviewer.trim(),
      });
      toast.success(res.note || `Recorded ${decision}`);
      onDecided();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  if (items.length === 0) {
    return <p className="text-muted-foreground">No runs awaiting promotion review.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-2">
        <label className="text-xs text-muted-foreground">
          Reviewer
          <Input className="mt-1 w-48" value={reviewer} onChange={(e) => setReviewer(e.target.value)} />
        </label>
      </div>
      {items.map((row) => {
        const id = String(row.id);
        return (
          <div key={id} className="rounded-md border border-border/80 p-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs">{id.slice(0, 8)}…</span>
              <Badge variant="outline">{String(row.variant)}</Badge>
              <span className="text-muted-foreground">{String(row.run_kind)}</span>
            </div>
            <pre className="mt-2 max-h-32 overflow-auto rounded bg-muted/40 p-2 font-mono text-[10px]">
              {JSON.stringify(row.metrics, null, 2)}
            </pre>
            <div className="mt-2 flex flex-wrap gap-2">
              <Button size="sm" disabled={busyId === id} onClick={() => decide(id, "PROMOTED")}>
                Approve
              </Button>
              <Button size="sm" variant="secondary" disabled={busyId === id} onClick={() => decide(id, "DEFERRED")}>
                Defer
              </Button>
              <Button size="sm" variant="destructive" disabled={busyId === id} onClick={() => decide(id, "REJECTED")}>
                Reject
              </Button>
            </div>
          </div>
        );
      })}
      <p className="text-xs text-muted-foreground">
        Decisions are recorded only; engine config is never auto-deployed.
      </p>
    </div>
  );
}

export function ResearchOpsDashboard() {
  const { data, error, isLoading, mutate } = useSWR("research-dashboard", () => api.researchDashboard(), {
    refreshInterval: 30_000,
  });

  if (isLoading) return <LoadingCard />;
  if (error) return <ErrorState message={(error as Error).message} />;
  if (data === null) {
    return (
      <Card>
        <CardContent className="space-y-2 p-6 text-sm">
          <p className="font-medium">Internal research API is off</p>
          <p className="text-muted-foreground">
            On the API host, set{" "}
            <code className="rounded bg-muted px-1">RESEARCH_INTERNAL_API_ENABLED=true</code> and redeploy. For MDS
            data, also enable <code className="rounded bg-muted px-1">RESEARCH_DB_ENABLED=true</code>.
          </p>
        </CardContent>
      </Card>
    );
  }

  const sched = data.scheduler.jobs.filter((j) => j.id.startsWith("research_") || j.id.includes("calibration"));
  const fs = data.storage.filesystem;
  const ts = data.storage.timescale as { database_bytes?: number; hypertables?: Array<{ name: string; bytes: number }> };

  return (
    <div className="space-y-4">
      <DataStamp label={data.data_as_of_utc} />
      <div className="flex flex-wrap gap-2">
        <Badge variant={data.research_db_enabled ? "success" : "warning"}>
          MDS {data.research_db_enabled ? "on" : "off"}
        </Badge>
        <Badge variant={data.research_scheduler_enabled ? "success" : "outline"}>
          Scheduler {data.research_scheduler_enabled ? "on" : "off"}
        </Badge>
        <Badge variant="outline">{data.promotion_policy}</Badge>
      </div>

      <Section title="Scheduler">
        <p className="text-muted-foreground">
          APScheduler {data.scheduler.running ? "running" : "not started (start uvicorn API)"}.
        </p>
        <ul className="space-y-1 font-mono text-xs">
          {sched.length === 0 && <li>No research/calibration jobs registered yet.</li>}
          {sched.map((j) => (
            <li key={j.id}>
              <span className="text-foreground">{j.id}</span>
              <span className="text-muted-foreground"> — next: {j.next_run_utc ?? "—"}</span>
            </li>
          ))}
        </ul>
        <p className="text-xs text-muted-foreground">
          Last collector: {String((data.automation as Record<string, string>).collector_last || "—").slice(0, 120)}
        </p>
      </Section>

      <Section title="Collector">
        {data.collector.last_run ? (
          <pre className="max-h-40 overflow-auto rounded bg-muted/40 p-2 font-mono text-[10px]">
            {JSON.stringify(data.collector.last_run, null, 2)}
          </pre>
        ) : (
          <p className="text-muted-foreground">No collector run recorded.</p>
        )}
        {data.collector.watermarks.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-muted-foreground">
                  <th className="p-1">Symbol</th>
                  <th className="p-1">Series</th>
                  <th className="p-1">Last bar</th>
                </tr>
              </thead>
              <tbody>
                {data.collector.watermarks.slice(0, 12).map((w, i) => (
                  <tr key={i} className="border-t border-border/50">
                    <td className="p-1">{String(w.symbol)}</td>
                    <td className="p-1">{String(w.series)}</td>
                    <td className="p-1 font-mono">{String(w.last_ts ?? "—")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Section>

      <Section title="Data quality">
        <div className="flex gap-4">
          {Object.entries(data.data_quality.summary || {}).map(([k, v]) => (
            <div key={k}>
              <span className="text-muted-foreground capitalize">{k}</span>{" "}
              <span className="font-semibold">{v}</span>
            </div>
          ))}
        </div>
        <ul className="max-h-48 space-y-1 overflow-auto font-mono text-xs">
          {data.data_quality.reports.map((r) => (
            <li key={String(r.id)}>
              {String(r.symbol)} {String(r.severity)} — missing {String(r.missing_bars)} @ {String(r.run_at)}
            </li>
          ))}
        </ul>
      </Section>

      <div className="grid gap-4 lg:grid-cols-2">
        <Section title="Storage (filesystem)">
          <p>Total: {formatBytes(fs.total_bytes)}</p>
          <ul className="font-mono text-xs">
            {Object.entries(fs.bytes_by_path).map(([p, b]) => (
              <li key={p}>
                {p}: {formatBytes(b)}
              </li>
            ))}
          </ul>
        </Section>
        <Section title="Timescale / Postgres">
          {!data.research_db_enabled ? (
            <p className="text-muted-foreground">Research DB disabled.</p>
          ) : (
            <>
              <p>Database: {ts.database_bytes != null ? formatBytes(ts.database_bytes) : "—"}</p>
              <ul className="font-mono text-xs">
                {(ts.hypertables || []).map((h) => (
                  <li key={h.name}>
                    {h.name}: {formatBytes(h.bytes)}
                  </li>
                ))}
              </ul>
            </>
          )}
        </Section>
      </div>

      <Section title="Dataset versions">
        {data.datasets.length === 0 ? (
          <p className="text-muted-foreground">No dataset versions yet.</p>
        ) : (
          <ul className="space-y-1 text-xs">
            {data.datasets.map((d) => (
              <li key={String(d.id)}>
                <strong>{String(d.version_code)}</strong> — {String(d.status)} ({String(d.dataset_hash)?.slice(0, 12)}
                …)
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Walk-forward (latest)">
        {data.walk_forward.last && (
          <pre className="mb-2 max-h-32 overflow-auto rounded bg-muted/40 p-2 font-mono text-[10px]">
            {JSON.stringify(data.walk_forward.last, null, 2)}
          </pre>
        )}
        <ul className="space-y-1 font-mono text-xs">
          {data.walk_forward.recent_runs.map((r) => (
            <li key={String(r.id)}>
              {String(r.variant)} / {String(r.run_kind)} — {String(r.status)}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Calibration">
        <p>
          Last: {String(data.calibration.last_calibrated_utc ?? "never")}
          {data.calibration.running ? " (running…)" : ""}
        </p>
        <p className="text-muted-foreground">Buckets: {String(data.calibration.bucket_count ?? 0)}</p>
      </Section>

      <Section title="Promotion queue">
        <PromotionQueue items={data.promotion_queue} onDecided={() => mutate()} />
      </Section>

      <Section title="Promotion history">
        <ul className="max-h-40 space-y-1 overflow-auto text-xs">
          {data.promotion_history.map((p) => (
            <li key={String(p.id)}>
              {String(p.decision)} — {String(p.feature_name)} by {String(p.approved_by)} @ {String(p.approved_at)}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Experiment history">
        <ul className="max-h-48 space-y-1 overflow-auto font-mono text-xs">
          {data.experiments.map((e) => (
            <li key={String(e.id)}>
              {String(e.variant)} {String(e.run_kind)} {String(e.promotion_decision ?? "pending")}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Research log">
        <ul className="max-h-64 space-y-2 overflow-auto font-mono text-[10px]">
          {data.logs.map((e, i) => (
            <li key={i} className="border-b border-border/40 pb-1">
              <span className="text-muted-foreground">{e.at}</span> [{e.kind}] {e.status}
            </li>
          ))}
        </ul>
      </Section>
    </div>
  );
}
