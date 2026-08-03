"use client";

import { useCallback, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { NAV_ITEMS } from "@/lib/navigation";
import { COMMAND_ACTIONS } from "@/lib/command-registry";
import { readRecentSymbols } from "@/hooks/use-recent-symbols";
import { readWatchlistSymbols } from "@/lib/watchlist-prefs";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import { useCommandPalette } from "@/components/command/CommandPaletteProvider";
import { usePreferences } from "@/components/providers/PreferencesProvider";
import { WORKSPACE_PRESETS } from "@/lib/workspace-prefs";

const SYMBOL_QUICK = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"];

export function CommandPalette() {
  const router = useRouter();
  const { open, setOpen } = useCommandPalette();
  const { setWorkspace, setTheme, setDensity } = usePreferences();

  const recentSymbols = useMemo(() => (open ? readRecentSymbols() : []), [open]);
  const pinnedSymbols = useMemo(() => (open ? readWatchlistSymbols() : []), [open]);
  const pinnedOnly = pinnedSymbols.filter((s) => !recentSymbols.includes(s));

  const run = useCallback(
    (href: string) => {
      setOpen(false);
      router.push(href);
    },
    [router, setOpen]
  );

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(!open);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, setOpen]);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search modules, symbols, or actions…" />
      <CommandList>
        <CommandEmpty>No results.</CommandEmpty>
        {pinnedOnly.length > 0 ? (
          <>
            <CommandGroup heading="Pinned">
              {pinnedOnly.map((sym) => (
                <CommandItem
                  key={`pin-${sym}`}
                  value={`pinned ${sym}`}
                  onSelect={() => run(`/pair/${encodeURIComponent(sym)}`)}
                >
                  {sym}
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        ) : null}
        {recentSymbols.length > 0 ? (
          <>
            <CommandGroup heading="Recent">
              {recentSymbols.map((sym) => (
                <CommandItem
                  key={`recent-${sym}`}
                  value={`recent ${sym}`}
                  onSelect={() => run(`/pair/${encodeURIComponent(sym)}`)}
                >
                  {sym}
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        ) : null}
        <CommandGroup heading="Symbols">
          {SYMBOL_QUICK.map((sym) => (
            <CommandItem key={sym} value={`symbol ${sym}`} onSelect={() => run(`/pair/${encodeURIComponent(sym)}`)}>
              Open {sym}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Actions">
          {COMMAND_ACTIONS.map((action) => (
            <CommandItem
              key={action.id}
              value={[action.label, ...action.keywords].join(" ")}
              onSelect={() => action.href && run(action.href)}
            >
              {action.label}
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Workspace">
          {WORKSPACE_PRESETS.map((w) => (
            <CommandItem
              key={w.id}
              value={`workspace ${w.label} ${w.description}`}
              onSelect={() => {
                setOpen(false);
                setWorkspace(w.id);
              }}
            >
              Switch to {w.label}
            </CommandItem>
          ))}
          <CommandItem
            value="theme light appearance"
            onSelect={() => {
              setOpen(false);
              setTheme("light");
            }}
          >
            Theme: Light
          </CommandItem>
          <CommandItem
            value="theme dark appearance"
            onSelect={() => {
              setOpen(false);
              setTheme("dark");
            }}
          >
            Theme: Dark
          </CommandItem>
          <CommandItem
            value="density compact tables"
            onSelect={() => {
              setOpen(false);
              setDensity("compact");
            }}
          >
            Density: Compact
          </CommandItem>
          <CommandItem
            value="density comfortable spacing"
            onSelect={() => {
              setOpen(false);
              setDensity("comfortable");
            }}
          >
            Density: Comfortable
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <CommandItem
                key={item.id}
                value={[item.label, ...(item.keywords || [])].join(" ")}
                onSelect={() => run(item.href)}
              >
                <Icon className="h-4 w-4" strokeWidth={1.5} />
                {item.label}
              </CommandItem>
            );
          })}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
