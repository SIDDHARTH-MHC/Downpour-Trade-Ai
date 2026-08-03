"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  GitCompare,
  Grid3x3,
  History,
  LayoutDashboard,
  Newspaper,
  PieChart,
} from "lucide-react";
import { cn } from "@/lib/utils";

const MOBILE_TABS = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/heatmap", label: "Heatmap", icon: Grid3x3 },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/news", label: "Context", icon: Newspaper },
  { href: "/portfolio", label: "Portfolio", icon: PieChart },
  { href: "/history", label: "History", icon: History },
  { href: "/status", label: "Status", icon: Activity },
] as const;

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 flex border-t border-border bg-card/95 backdrop-blur lg:hidden"
      aria-label="Primary mobile"
    >
      {MOBILE_TABS.map(({ href, label, icon: Icon }) => {
        const active = href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px]",
              active ? "text-primary" : "text-muted-foreground"
            )}
          >
            <Icon className="h-5 w-5" strokeWidth={1.5} />
            <span>{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
