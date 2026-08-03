"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import type { Verdict } from "@/lib/api";
import { RegimeBadge } from "@/components/RegimeBadge";
import { VerdictChip } from "@/components/shared/VerdictChip";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type ScanTableProps = {
  results: Verdict[];
  className?: string;
};

export function ScanTable({ results, className }: ScanTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: "weighted_score", desc: true }]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const verdictFilter = (columnFilters.find((f) => f.id === "action")?.value as string | undefined) ?? "all";

  const columns = useMemo<ColumnDef<Verdict>[]>(
    () => [
      {
        accessorKey: "symbol",
        header: "Pair",
        cell: ({ row }) => (
          <Link
            className="font-medium text-primary hover:underline"
            href={`/pair/${encodeURIComponent(row.original.symbol)}`}
          >
            {row.original.symbol}
          </Link>
        ),
      },
      {
        id: "regime",
        accessorFn: (r) => r.regime.name,
        header: "Regime",
        cell: ({ row }) => (
          <RegimeBadge regime={row.original.regime.name} tradeable={row.original.regime.tradeable} />
        ),
      },
      {
        accessorKey: "weighted_score",
        header: "Score",
        cell: ({ row }) => (
          <span className="font-mono tabular-nums">{row.original.weighted_score.toFixed(1)}</span>
        ),
      },
      {
        accessorKey: "action",
        header: "Verdict",
        cell: ({ row }) => <VerdictChip action={row.original.action} />,
        filterFn: (row, _id, filter: string) => row.original.action === filter,
      },
      {
        accessorKey: "confidence",
        header: "Confidence",
        cell: ({ row }) => <span className="text-xs text-muted-foreground">{row.original.confidence}</span>,
      },
    ],
    []
  );

  const table = useReactTable({
    data: results,
    columns,
    state: { sorting, globalFilter, columnFilters },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnFiltersChange: setColumnFilters,
    globalFilterFn: (row, _columnId, filterValue) => {
      const q = String(filterValue).toLowerCase();
      if (!q) return true;
      return row.original.symbol.toLowerCase().includes(q);
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Filter pairs…"
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="h-8 max-w-xs"
          aria-label="Filter scan results by symbol"
        />
        <div className="flex gap-1 text-xs">
          {(["all", "LONG", "SHORT", "NO_TRADE"] as const).map((v) => (
            <button
              key={v}
              type="button"
              className={cn(
                "rounded-md border border-border px-2 py-1 text-muted-foreground transition-colors hover:bg-accent",
                verdictFilter === v && "border-primary/50 bg-accent text-foreground"
              )}
              onClick={() =>
                setColumnFilters(v === "all" ? [] : [{ id: "action", value: v }])
              }
            >
              {v === "all" ? "All" : v}
            </button>
          ))}
        </div>
        <span className="ml-auto text-xs text-muted-foreground">
          {table.getFilteredRowModel().rows.length} rows
        </span>
      </div>
      <div className="overflow-hidden rounded-xl border border-border bg-card">
        <div className="max-h-[min(60vh,28rem)] overflow-auto">
          <table className="min-w-full text-sm">
            <thead className="sticky top-0 z-10 bg-card/95 backdrop-blur">
              {table.getHeaderGroups().map((hg) => (
                <tr key={hg.id} className="border-b border-border text-left text-muted-foreground">
                  {hg.headers.map((header) => {
                    const sorted = header.column.getIsSorted();
                    return (
                      <th key={header.id} className="px-3 py-2 font-medium">
                        {header.isPlaceholder ? null : (
                          <button
                            type="button"
                            className="inline-flex items-center gap-1 hover:text-foreground"
                            onClick={header.column.getToggleSortingHandler()}
                          >
                            {flexRender(header.column.columnDef.header, header.getContext())}
                            {header.column.getCanSort() ? (
                              sorted === "asc" ? (
                                <ArrowUp className="h-3.5 w-3.5" />
                              ) : sorted === "desc" ? (
                                <ArrowDown className="h-3.5 w-3.5" />
                              ) : (
                                <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />
                              )
                            ) : null}
                          </button>
                        )}
                      </th>
                    );
                  })}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-t border-border/60 hover:bg-accent/30">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-3 py-2">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
