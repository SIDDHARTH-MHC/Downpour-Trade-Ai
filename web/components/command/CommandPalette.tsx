"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { NAV_ITEMS } from "@/lib/navigation";
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

const SYMBOL_QUICK = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"];

export function CommandPalette() {
  const router = useRouter();
  const { open, setOpen } = useCommandPalette();

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
      <CommandInput placeholder="Search modules or type a symbol…" />
      <CommandList>
        <CommandEmpty>No results.</CommandEmpty>
        <CommandGroup heading="Symbols">
          {SYMBOL_QUICK.map((sym) => (
            <CommandItem key={sym} value={`symbol ${sym}`} onSelect={() => run(`/pair/${encodeURIComponent(sym)}`)}>
              Open {sym}
            </CommandItem>
          ))}
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
