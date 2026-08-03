"use client";

import { useEffect } from "react";

const STORAGE_KEY = "downpour.recent-symbols";
const MAX = 8;

export function recordRecentSymbol(symbol: string) {
  if (!symbol) return;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const prev: string[] = raw ? (JSON.parse(raw) as string[]) : [];
    const next = [symbol, ...prev.filter((s) => s !== symbol)].slice(0, MAX);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    /* ignore */
  }
}

export function useRecentSymbol(symbol: string) {
  useEffect(() => {
    recordRecentSymbol(symbol);
  }, [symbol]);
}

export function readRecentSymbols(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}
