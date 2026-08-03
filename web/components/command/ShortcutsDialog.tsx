"use client";

import { KEYBOARD_SHORTCUTS } from "@/lib/shortcuts";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useShortcutsDialog } from "@/components/command/ShortcutsProvider";

const GROUP_ORDER = ["Global", "Navigation", "Modules"] as const;

export function ShortcutsDialog() {
  const { open, setOpen } = useShortcutsDialog();

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-h-[min(85vh,32rem)] overflow-y-auto sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Keyboard shortcuts</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          {GROUP_ORDER.map((group) => {
            const items = KEYBOARD_SHORTCUTS.filter((s) => s.group === group);
            if (!items.length) return null;
            return (
              <div key={group}>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{group}</p>
                <ul className="space-y-2">
                  {items.map((item) => (
                    <li key={item.keys + item.label} className="flex items-center justify-between gap-4 text-sm">
                      <span className="text-muted-foreground">{item.label}</span>
                      <kbd className="shrink-0 rounded border border-border bg-muted px-2 py-0.5 font-mono text-[11px] text-foreground">
                        {item.keys}
                      </kbd>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </DialogContent>
    </Dialog>
  );
}
