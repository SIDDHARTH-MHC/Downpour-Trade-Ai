import type { LucideIcon } from "lucide-react";
import {
  Activity,
  Bell,
  BookOpen,
  Cpu,
  GitCompare,
  Grid3x3,
  History,
  LayoutDashboard,
  LineChart,
  Newspaper,
  PieChart,
  Plug,
  Scale,
  ScrollText,
  Settings2,
  Sparkles,
  TrendingUp,
  Waves,
} from "lucide-react";

export type NavSection = "quick" | "markets" | "research" | "workspace" | "system";

export type NavItem = {
  id: string;
  label: string;
  href: string;
  icon: LucideIcon;
  section: NavSection;
  keywords?: string[];
};

export const NAV_SECTION_LABELS: Record<NavSection, string> = {
  quick: "Quick",
  markets: "Markets",
  research: "Research",
  workspace: "Workspace",
  system: "System",
};

export const NAV_ITEMS: NavItem[] = [
  { id: "dashboard", label: "Dashboard", href: "/", icon: LayoutDashboard, section: "quick", keywords: ["home", "scan"] },
  { id: "compare", label: "Compare", href: "/compare", icon: GitCompare, section: "markets" },
  { id: "heatmap", label: "Heatmap", href: "/heatmap", icon: Grid3x3, section: "markets" },
  { id: "correlation", label: "Correlation", href: "/correlation", icon: LineChart, section: "markets" },
  { id: "news", label: "Context", href: "/news", icon: Newspaper, section: "research", keywords: ["news"] },
  { id: "scenarios", label: "Scenarios", href: "/scenarios", icon: Scale, section: "research" },
  { id: "flows", label: "Funding", href: "/flows", icon: Waves, section: "research" },
  { id: "macro", label: "Macro", href: "/macro", icon: TrendingUp, section: "research" },
  { id: "engine", label: "Engine", href: "/engine", icon: Cpu, section: "research" },
  { id: "portfolio", label: "Portfolio", href: "/portfolio", icon: PieChart, section: "workspace" },
  { id: "history", label: "History", href: "/history", icon: History, section: "workspace" },
  { id: "notebook", label: "Notebook", href: "/notebook", icon: BookOpen, section: "workspace" },
  { id: "alerts", label: "Alerts", href: "/alerts", icon: Bell, section: "workspace" },
  { id: "coach", label: "Coach", href: "/coach", icon: Sparkles, section: "workspace" },
  { id: "backtests", label: "Backtests", href: "/backtests", icon: ScrollText, section: "system" },
  { id: "status", label: "Status", href: "/status", icon: Activity, section: "system", keywords: ["health"] },
  { id: "integrations", label: "Integrations", href: "/integrations", icon: Plug, section: "system" },
  { id: "glossary", label: "Glossary", href: "/glossary", icon: BookOpen, section: "system" },
];

export function getNavItemForPath(pathname: string): NavItem | undefined {
  if (pathname.startsWith("/pair/")) {
    return { id: "pair", label: "Pair", href: pathname, icon: LineChart, section: "markets" };
  }
  return NAV_ITEMS.find((item) =>
    item.href === "/" ? pathname === "/" : pathname === item.href || pathname.startsWith(`${item.href}/`)
  );
}

export function groupNavBySection(items: NavItem[]): { section: NavSection; items: NavItem[] }[] {
  const order: NavSection[] = ["quick", "markets", "research", "workspace", "system"];
  return order.map((section) => ({
    section,
    items: items.filter((i) => i.section === section),
  })).filter((g) => g.items.length > 0);
}
