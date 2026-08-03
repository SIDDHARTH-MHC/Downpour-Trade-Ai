import type { LucideIcon } from "lucide-react";

export type ShortcutEntry = {
  keys: string;
  label: string;
  group: "Global" | "Navigation" | "Modules";
};

export const KEYBOARD_SHORTCUTS: ShortcutEntry[] = [
  { group: "Global", keys: "⌘ K", label: "Open command palette" },
  { group: "Global", keys: "/", label: "Focus command palette" },
  { group: "Global", keys: "?", label: "Keyboard shortcuts" },
  { group: "Global", keys: "⌘ B", label: "Toggle sidebar" },
  { group: "Navigation", keys: "G then D", label: "Dashboard" },
  { group: "Navigation", keys: "G then P", label: "Portfolio" },
  { group: "Navigation", keys: "G then H", label: "History" },
  { group: "Navigation", keys: "G then B", label: "Backtests" },
  { group: "Navigation", keys: "G then N", label: "Context (news)" },
  { group: "Navigation", keys: "G then C", label: "Compare" },
  { group: "Navigation", keys: "G then M", label: "Heatmap" },
  { group: "Navigation", keys: "G then S", label: "Status" },
  { group: "Navigation", keys: "G then A", label: "Alerts" },
  { group: "Modules", keys: "Esc", label: "Close palette / dialogs" },
];

export const GOTO_ROUTES: Record<string, string> = {
  d: "/",
  p: "/portfolio",
  h: "/history",
  b: "/backtests",
  n: "/news",
  c: "/compare",
  m: "/heatmap",
  s: "/status",
  a: "/alerts",
  i: "/integrations",
  g: "/glossary",
};
