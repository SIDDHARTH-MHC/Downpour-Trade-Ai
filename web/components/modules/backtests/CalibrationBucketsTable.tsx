"use client";

import { useMemo } from "react";
import type { ColumnDef } from "@tanstack/react-table";
import { DataTableFrame } from "@/components/data/DataTableFrame";

type BucketRow = {
  bucket: string;
  trade_count: number;
  win_rate: number;
  avg_r: number;
  profit_factor: number;
};

export function CalibrationBucketsTable({ buckets }: { buckets: Record<string, Omit<BucketRow, "bucket">> }) {
  const data = useMemo<BucketRow[]>(
    () =>
      Object.entries(buckets).map(([bucket, stats]) => ({
        bucket,
        trade_count: stats.trade_count,
        win_rate: stats.win_rate,
        avg_r: stats.avg_r,
        profit_factor: stats.profit_factor,
      })),
    [buckets]
  );

  const columns = useMemo<ColumnDef<BucketRow>[]>(
    () => [
      { accessorKey: "bucket", header: "Bucket" },
      { accessorKey: "trade_count", header: "Trades" },
      {
        accessorKey: "win_rate",
        header: "Win rate",
        cell: ({ row }) => `${(row.original.win_rate * 100).toFixed(1)}%`,
      },
      {
        accessorKey: "avg_r",
        header: "Avg R",
        cell: ({ row }) => row.original.avg_r.toFixed(2),
      },
      {
        accessorKey: "profit_factor",
        header: "Profit factor",
        cell: ({ row }) => Number(row.original.profit_factor).toFixed(2),
      },
    ],
    []
  );

  return (
    <DataTableFrame
      data={data}
      columns={columns}
      emptyMessage="No calibration buckets yet."
      getRowId={(row) => row.bucket}
    />
  );
}
