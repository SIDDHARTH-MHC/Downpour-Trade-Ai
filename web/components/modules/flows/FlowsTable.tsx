"use client";

import Link from "next/link";
import { useMemo } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { DataTableFrame } from "@/components/tables/DataTableFrame";

type FlowRow = {
  symbol: string;
  funding_rate_pct: number | null;
  open_interest_usd: number | null;
  oi_change_1bar: number | null;
};

export function FlowsTable({ rows }: { rows: FlowRow[] }) {
  const columns = useMemo<ColumnDef<FlowRow>[]>(
    () => [
      {
        accessorKey: "symbol",
        header: "Pair",
        cell: ({ row }) => (
          <Link className="text-primary hover:underline" href={`/pair/${encodeURIComponent(row.original.symbol)}`}>
            {row.original.symbol}
          </Link>
        ),
      },
      {
        accessorKey: "funding_rate_pct",
        header: "Funding %",
        cell: ({ row }) => {
          const v = row.original.funding_rate_pct;
          if (v == null) return "—";
          const tone = v > 0.01 ? "text-short" : v < -0.01 ? "text-long" : "";
          return <span className={tone}>{v.toFixed(4)}%</span>;
        },
      },
      {
        accessorKey: "open_interest_usd",
        header: "OI (USD)",
        cell: ({ row }) =>
          row.original.open_interest_usd != null
            ? `$${(row.original.open_interest_usd / 1e6).toFixed(1)}M`
            : "—",
      },
      {
        accessorKey: "oi_change_1bar",
        header: "OI Δ 1 bar",
        cell: ({ row }) =>
          row.original.oi_change_1bar != null ? `${(row.original.oi_change_1bar * 100).toFixed(2)}%` : "—",
      },
    ],
    []
  );

  return (
    <DataTableFrame
      data={rows}
      columns={columns}
      globalFilterPlaceholder="Filter pairs…"
      globalFilterFn={(row, q) => row.symbol.toLowerCase().includes(q.toLowerCase())}
      getRowId={(row) => row.symbol}
    />
  );
}
