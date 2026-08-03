"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Verdict } from "@/lib/api";
import { VerdictChip } from "@/components/shared/VerdictChip";
import { DataTableFrame } from "@/components/tables/DataTableFrame";
import { cn } from "@/lib/utils";
import { useMemo } from "react";

type HistoryTableProps = {
  verdicts: Verdict[];
  actionFilter?: "all" | "LONG" | "SHORT" | "NO_TRADE";
  onActionFilterChange?: (v: NonNullable<HistoryTableProps["actionFilter"]>) => void;
};

export function HistoryTable({ verdicts, actionFilter = "all", onActionFilterChange }: HistoryTableProps) {
  const filtered =
    actionFilter === "all" ? verdicts : verdicts.filter((v) => v.action === actionFilter);

  const columns = useMemo<ColumnDef<Verdict>[]>(
    () => [
      {
        accessorKey: "timestamp",
        header: "Time",
        cell: ({ row }) => (
          <span className="whitespace-nowrap text-xs text-muted-foreground">{row.original.timestamp}</span>
        ),
      },
      {
        accessorKey: "symbol",
        header: "Pair",
        cell: ({ row }) => (
          <Link className="font-medium text-primary hover:underline" href={`/pair/${encodeURIComponent(row.original.symbol)}`}>
            {row.original.symbol}
          </Link>
        ),
      },
      { accessorKey: "timeframe", header: "TF" },
      {
        accessorKey: "action",
        header: "Action",
        cell: ({ row }) => <VerdictChip action={row.original.action} />,
      },
      {
        accessorKey: "weighted_score",
        header: "Score",
        cell: ({ row }) => (
          <span className="font-mono tabular-nums">{row.original.weighted_score.toFixed(1)}</span>
        ),
      },
      { accessorKey: "confidence", header: "Confidence" },
    ],
    []
  );

  return (
    <DataTableFrame
      data={filtered}
      columns={columns}
      globalFilterPlaceholder="Filter by pair…"
      globalFilterFn={(row, q) => row.symbol.toLowerCase().includes(q.toLowerCase())}
      getRowId={(row) => `${row.symbol}-${row.timestamp}-${row.timeframe}`}
      toolbar={
        onActionFilterChange ? (
          <HistoryActionFilters value={actionFilter} onChange={onActionFilterChange} />
        ) : undefined
      }
    />
  );
}

export function HistoryActionFilters({
  value,
  onChange,
}: {
  value: NonNullable<HistoryTableProps["actionFilter"]>;
  onChange: (v: NonNullable<HistoryTableProps["actionFilter"]>) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1 text-xs">
      {(["all", "LONG", "SHORT", "NO_TRADE"] as const).map((v) => (
        <button
          key={v}
          type="button"
          className={cn(
            "rounded-md border border-border px-2 py-1 text-muted-foreground hover:bg-accent",
            value === v && "border-primary/50 bg-accent text-foreground"
          )}
          onClick={() => onChange(v)}
        >
          {v === "all" ? "All" : v}
        </button>
      ))}
    </div>
  );
}
