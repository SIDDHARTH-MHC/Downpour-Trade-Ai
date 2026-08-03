"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Menu, Search } from "lucide-react";
import { getNavItemForPath, NAV_SECTION_LABELS } from "@/lib/navigation";
import { Button } from "@/components/ui/button";
import { useCommandPalette } from "@/components/command/CommandPaletteProvider";
import { useShortcutsDialog } from "@/components/command/ShortcutsProvider";
import { WorkspaceMenu } from "@/components/shell/WorkspaceMenu";

type TopBarProps = {
  onOpenMobileNav?: () => void;
};

function decodePairSymbol(segment: string) {
  try {
    return decodeURIComponent(segment);
  } catch {
    return segment;
  }
}

export function TopBar({ onOpenMobileNav }: TopBarProps) {
  const pathname = usePathname();
  const { setOpen } = useCommandPalette();
  const { setOpen: setShortcutsOpen } = useShortcutsDialog();
  const navItem = getNavItemForPath(pathname);

  const crumbs: { label: string; href?: string }[] = [];
  if (pathname.startsWith("/pair/")) {
    const symbol = decodePairSymbol(pathname.replace(/^\/pair\//, ""));
    crumbs.push({ label: "Markets", href: "/heatmap" });
    crumbs.push({ label: symbol });
  } else if (navItem) {
    if (navItem.id !== "dashboard") {
      crumbs.push({ label: NAV_SECTION_LABELS[navItem.section] });
    }
    crumbs.push({ label: navItem.label });
  }

  return (
    <header className="flex h-[var(--topbar-height)] shrink-0 items-center gap-2 border-b border-border bg-background/80 px-3 backdrop-blur md:px-4">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onOpenMobileNav}
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </Button>
      <nav aria-label="Breadcrumb" className="hidden min-w-0 flex-1 items-center gap-1 text-sm md:flex">
        {crumbs.map((crumb, i) => (
          <span key={`${crumb.label}-${i}`} className="flex min-w-0 items-center gap-1">
            {i > 0 && <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />}
            {crumb.href ? (
              <Link href={crumb.href} className="truncate text-muted-foreground hover:text-foreground">
                {crumb.label}
              </Link>
            ) : (
              <span className="truncate font-medium text-foreground">{crumb.label}</span>
            )}
          </span>
        ))}
      </nav>
      <div className="flex flex-1 items-center justify-end gap-2 md:flex-none">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="hidden h-8 w-full max-w-xs justify-start gap-2 text-muted-foreground sm:flex md:w-56"
          onClick={() => setOpen(true)}
        >
          <Search className="h-4 w-4 shrink-0" />
          <span className="truncate">Search…</span>
          <kbd className="pointer-events-none ml-auto hidden rounded border border-border bg-muted px-1.5 font-mono text-[10px] text-muted-foreground lg:inline">
            ⌘K
          </kbd>
        </Button>
        <Button type="button" variant="ghost" size="icon" className="sm:hidden" onClick={() => setOpen(true)} aria-label="Search">
          <Search className="h-5 w-5" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="hidden sm:inline-flex"
          onClick={() => setShortcutsOpen(true)}
          aria-label="Keyboard shortcuts"
        >
          <span className="font-mono text-sm text-muted-foreground">?</span>
        </Button>
        <WorkspaceMenu />
        <Button type="button" variant="ghost" size="sm" className="hidden md:inline-flex" asChild>
          <Link href="/integrations">
            <span className="text-muted-foreground">Settings</span>
          </Link>
        </Button>
      </div>
    </header>
  );
}
