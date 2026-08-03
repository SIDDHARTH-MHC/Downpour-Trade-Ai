"use client";

import { LayoutGrid, Monitor, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { usePreferences } from "@/components/providers/PreferencesProvider";
import { WORKSPACE_PRESETS, type Density, type ThemeMode, type WorkspaceId } from "@/lib/workspace-prefs";

export function WorkspaceMenu() {
  const { workspace, density, theme, setWorkspace, setDensity, setTheme, hydrated } = usePreferences();
  const current = WORKSPACE_PRESETS.find((w) => w.id === workspace);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button type="button" variant="outline" size="sm" className="hidden gap-1.5 md:inline-flex" disabled={!hydrated}>
          <LayoutGrid className="h-4 w-4" strokeWidth={1.5} />
          <span className="max-w-[7rem] truncate">{current?.label ?? "Workspace"}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Workspace</DropdownMenuLabel>
        <DropdownMenuRadioGroup value={workspace} onValueChange={(v) => setWorkspace(v as WorkspaceId)}>
          {WORKSPACE_PRESETS.map((w) => (
            <DropdownMenuRadioItem key={w.id} value={w.id}>
              <span className="flex flex-col gap-0.5">
                <span>{w.label}</span>
                <span className="text-[10px] font-normal text-muted-foreground">{w.description}</span>
              </span>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
        <DropdownMenuSeparator />
        <DropdownMenuLabel>Density</DropdownMenuLabel>
        <DropdownMenuRadioGroup value={density} onValueChange={(v) => setDensity(v as Density)}>
          <DropdownMenuRadioItem value="comfortable">Comfortable</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="compact">Compact</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
        <DropdownMenuSeparator />
        <DropdownMenuLabel>Theme</DropdownMenuLabel>
        <DropdownMenuRadioGroup value={theme} onValueChange={(v) => setTheme(v as ThemeMode)}>
          <DropdownMenuRadioItem value="dark">
            <Moon className="mr-2 h-3.5 w-3.5 inline" strokeWidth={1.5} />
            Dark
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="light">
            <Sun className="mr-2 h-3.5 w-3.5 inline" strokeWidth={1.5} />
            Light
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="system">
            <Monitor className="mr-2 h-3.5 w-3.5 inline" strokeWidth={1.5} />
            System
          </DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
