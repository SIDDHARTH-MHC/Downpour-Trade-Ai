import { NAV_ITEMS } from "@/lib/navigation";

export type CommandAction = {
  id: string;
  label: string;
  keywords: string[];
  href?: string;
  group: "Actions" | "Navigation" | "Settings";
};

export const COMMAND_ACTIONS: CommandAction[] = [
  {
    id: "scan-dashboard",
    label: "Open dashboard scan",
    keywords: ["scan", "refresh", "home"],
    href: "/",
    group: "Actions",
  },
  {
    id: "settings-integrations",
    label: "Settings — Integrations",
    keywords: ["settings", "webhook", "discord", "slack"],
    href: "/integrations",
    group: "Settings",
  },
  {
    id: "settings-alerts",
    label: "Settings — Alerts",
    keywords: ["alerts", "rules", "telegram"],
    href: "/alerts",
    group: "Settings",
  },
];

export const COMMAND_NAV = NAV_ITEMS.map((item) => ({
  id: item.id,
  label: item.label,
  href: item.href,
  keywords: item.keywords ?? [],
  group: "Navigation" as const,
}));
