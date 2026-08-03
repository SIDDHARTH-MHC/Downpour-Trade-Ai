"use client";

import { useState, type ReactNode } from "react";
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
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type DataTableFrameProps<T> = {
  data: T[];
  columns: ColumnDef<T, unknown>[];
  globalFilterPlaceholder?: string;
  globalFilterFn?: (row: T, filter: string) => boolean;
  toolbar?: ReactNode;
  emptyMessage?: string;
  maxHeightClass?: string;
  className?: string;
  getRowId?: (row: T, index: number) => string;
};

export function DataTableFrame<T>({
  data,
  columns,
  globalFilterPlaceholder,
  globalFilterFn,
  toolbar,
  emptyMessage = "No rows.",
  maxHeightClass = "max-h-[min(60vh,28rem)]",
  className,
  getRowId,
}: DataTableFrameProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter, columnFilters },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: (row, _columnId, filterValue) => {
      if (!globalFilterFn) return true;
      return globalFilterFn(row.original, String(filterValue));
    },
    getRowId,
  });

  const rowCount = table.getFilteredRowModel().rows.length;

  return (
    <div className={cn("space-y-3", className)}>
      {(globalFilterPlaceholder || toolbar) && (
        <div className="flex flex-wrap items-center gap-2">
          {globalFilterPlaceholder ? (
            <Input
              placeholder={globalFilterPlaceholder}
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              className="h-8 max-w-xs"
            />
          ) : null}
          {toolbar}
          <span className="ml-auto text-xs text-muted-foreground">{rowCount} rows</span>
        </div>
      )}
      <div className="overflow-hidden rounded-xl border border-border bg-card">
        <div className={cn("overflow-auto", maxHeightClass)}>
          <table className="min-w-full text-sm">
            <thead className="sticky top-0 z-10 bg-card/95 backdrop-blur">
              {table.getHeaderGroups().map((hg) => (
                <tr key={hg.id} className="border-b border-border text-left text-muted-foreground">
                  {hg.headers.map((header) => {
                    const sorted = header.column.getIsSorted();
                    return (
                      <th key={header.id} className="px-3 py-2 font-medium">
                        {header.isPlaceholder ? null : header.column.getCanSort() ? (
                          <button
                            type="button"
                            className="inline-flex items-center gap-1 hover:text-foreground"
                            onClick={header.column.getToggleSortingHandler()}
                          >
                            {flexRender(header.column.columnDef.header, header.getContext())}
                            {sorted === "asc" ? (
                              <ArrowUp className="h-3.5 w-3.5" />
                            ) : sorted === "desc" ? (
                              <ArrowDown className="h-3.5 w-3.5" />
                            ) : (
                              <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />
                            )}
                          </button>
                        ) : (
                          flexRender(header.column.columnDef.header, header.getContext())
                        )}
                      </th>
                    );
                  })}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="px-3 py-8 text-center text-muted-foreground">
                    {emptyMessage}
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-t border-border/60 hover:bg-accent/30">
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3 py-2">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
