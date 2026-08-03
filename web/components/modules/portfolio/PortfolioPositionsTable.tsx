"use client";

import Link from "next/link";
import { useMemo } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import type { PortfolioAnalyticsResponse } from "@/lib/api";
import { VerdictChip } from "@/components/shared/VerdictChip";
import { DataTableFrame } from "@/components/data/DataTableFrame";

type Position = PortfolioAnalyticsResponse["positions"][number];

export function PortfolioPositionsTable({ positions }: { positions: Position[] }) {
  const columns = useMemo<ColumnDef<Position>[]>(
    () => [
      {
        accessorKey: "symbol",
        header: "Symbol",
        cell: ({ row }) => (
          <Link className="text-primary hover:underline" href={`/pair/${encodeURIComponent(row.original.symbol)}`}>
            {row.original.symbol}
          </Link>
        ),
      },
      {
        accessorKey: "action",
        header: "Side",
        cell: ({ row }) => {
          const a = row.original.action;
          if (a === "LONG" || a === "SHORT") return <VerdictChip action={a} />;
          return <span className="text-muted-foreground">{a}</span>;
        },
      },
      {
        accessorKey: "risk_usd",
        header: "Risk $",
        cell: ({ row }) => <span className="font-mono tabular-nums">${row.original.risk_usd.toFixed(0)}</span>,
      },
      {
        accessorKey: "reward_risk",
        header: "R:R",
        cell: ({ row }) => (
          <span className="font-mono tabular-nums">{row.original.reward_risk?.toFixed(2) ?? "—"}</span>
        ),
      },
    ],
    []
  );

  return (
    <DataTableFrame
      data={positions}
      columns={columns}
      emptyMessage="No open signals with trade plans."
      getRowId={(row, i) => `${row.symbol}-${i}`}
    />
  );
}
