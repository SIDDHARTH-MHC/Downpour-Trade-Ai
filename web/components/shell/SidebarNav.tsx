"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { groupNavBySection, NAV_ITEMS, NAV_SECTION_LABELS } from "@/lib/navigation";
import { readRecentSymbols } from "@/hooks/use-recent-symbols";
import { readWatchlistSymbols } from "@/lib/watchlist-prefs";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useSidebar } from "@/components/shell/SidebarProvider";

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

type SidebarNavProps = {
  onNavigate?: () => void;
  className?: string;
};

export function SidebarNav({ onNavigate, className }: SidebarNavProps) {
  const pathname = usePathname();
  const { collapsed, toggle, hydrated } = useSidebar();
  const groups = groupNavBySection(NAV_ITEMS);
  const [recent, setRecent] = useState<string[]>([]);
  const [pinned, setPinned] = useState<string[]>([]);

  useEffect(() => {
    setRecent(readRecentSymbols());
    setPinned(readWatchlistSymbols());
  }, [pathname]);

  return (
    <aside
      className={cn(
        "hidden lg:flex lg:flex-col lg:border-r lg:border-border lg:bg-card/40",
        hydrated && collapsed ? "lg:w-[var(--sidebar-width-collapsed)]" : "lg:w-[var(--sidebar-width)]",
        className
      )}
    >
      <div className="flex h-[var(--topbar-height)] shrink-0 items-center border-b border-border px-3">
        <Link
          href="/"
          className={cn(
            "flex min-w-0 items-center gap-2 font-semibold tracking-tight text-primary",
            collapsed && "justify-center"
          )}
          onClick={onNavigate}
        >
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary/15 text-xs font-bold text-primary">
            D
          </span>
          {!collapsed && <span className="truncate text-sm text-foreground">Downpour</span>}
        </Link>
      </div>
      <ScrollArea className="flex-1 px-2 py-3">
        <nav className="space-y-4">
          {groups.map(({ section, items }) => (
            <div key={section}>
              {!collapsed && (
                <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {NAV_SECTION_LABELS[section]}
                </p>
              )}
              <ul className="space-y-0.5">
                {items.map((item) => {
                  const active = isActive(pathname, item.href);
                  const Icon = item.icon;
                  return (
                    <li key={item.id}>
                      <Link
                        href={item.href}
                        onClick={onNavigate}
                        title={collapsed ? item.label : undefined}
                        className={cn(
                          "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
                          collapsed && "justify-center px-0",
                          active
                            ? "bg-accent text-accent-foreground font-medium"
                            : "text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                        )}
                      >
                        <Icon className="h-4 w-4 shrink-0" strokeWidth={1.5} />
                        {!collapsed && <span className="truncate">{item.label}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
        {!collapsed && pinned.length > 0 ? (
          <div className="mt-4 border-t border-border pt-3">
            <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Pinned
            </p>
            <ul className="space-y-0.5">
              {pinned.map((sym) => (
                <li key={`pin-${sym}`}>
                  <Link
                    href={`/pair/${encodeURIComponent(sym)}`}
                    onClick={onNavigate}
                    className="block truncate rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                  >
                    {sym}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        {!collapsed && recent.length > 0 ? (
          <div className="mt-4 border-t border-border pt-3">
            <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Recent
            </p>
            <ul className="space-y-0.5">
              {recent.map((sym) => (
                <li key={sym}>
                  <Link
                    href={`/pair/${encodeURIComponent(sym)}`}
                    onClick={onNavigate}
                    className="block truncate rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                  >
                    {sym}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </ScrollArea>
      <div className="border-t border-border p-2">
        <Button
          type="button"
          variant="ghost"
          size={collapsed ? "icon" : "sm"}
          className={cn("w-full", !collapsed && "justify-start")}
          onClick={toggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed && <span className="text-muted-foreground">Collapse</span>}
        </Button>
      </div>
    </aside>
  );
}

export function SidebarNavMobile({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const groups = groupNavBySection(NAV_ITEMS);

  return (
    <nav className="space-y-4 p-4">
      {groups.map(({ section, items }) => (
        <div key={section}>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            {NAV_SECTION_LABELS[section]}
          </p>
          <ul className="space-y-1">
            {items.map((item) => {
              const active = isActive(pathname, item.href);
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <Link
                    href={item.href}
                    onClick={onNavigate}
                    className={cn(
                      "flex items-center gap-2 rounded-md px-2 py-2 text-sm",
                      active ? "bg-accent font-medium" : "text-muted-foreground hover:bg-accent/60"
                    )}
                  >
                    <Icon className="h-4 w-4" strokeWidth={1.5} />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
          <Separator className="mt-4" />
        </div>
      ))}
    </nav>
  );
}
