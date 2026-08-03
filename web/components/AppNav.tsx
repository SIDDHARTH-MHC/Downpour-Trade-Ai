"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const PRIMARY = [
  { href: "/", label: "Dashboard" },
  { href: "/compare", label: "Compare" },
  { href: "/heatmap", label: "Heatmap" },
  { href: "/correlation", label: "Correlation" },
  { href: "/news", label: "Context" },
] as const;

const GROUPS = [
  {
    title: "Analysis",
    links: [
      { href: "/scenarios", label: "Scenarios" },
      { href: "/flows", label: "Funding" },
      { href: "/macro", label: "Macro" },
      { href: "/engine", label: "Engine" },
      { href: "/backtests", label: "Backtests" },
    ],
  },
  {
    title: "Workspace",
    links: [
      { href: "/coach", label: "Coach" },
      { href: "/notebook", label: "Notebook" },
      { href: "/portfolio", label: "Portfolio" },
      { href: "/history", label: "History" },
      { href: "/alerts", label: "Alerts" },
    ],
  },
  {
    title: "System",
    links: [
      { href: "/integrations", label: "Integrations" },
      { href: "/status", label: "Status" },
      { href: "/glossary", label: "Glossary" },
    ],
  },
] as const;

function NavLink({ href, label }: { href: string; label: string }) {
  const pathname = usePathname();
  const active = href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
  return (
    <Link
      href={href}
      className={`whitespace-nowrap rounded px-2 py-1 transition-colors hover:text-white ${
        active ? "bg-slate-800 text-white" : "text-muted"
      }`}
    >
      {label}
    </Link>
  );
}

export function AppNav() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) {
        setMoreOpen(false);
      }
    }
    document.addEventListener("click", onDocClick);
    return () => document.removeEventListener("click", onDocClick);
  }, []);

  return (
    <div className="flex flex-1 flex-col items-end gap-2 md:items-end">
      <div className="flex w-full items-center justify-end gap-2 md:w-auto">
        <nav className="hidden items-center gap-1 text-sm md:flex">
          {PRIMARY.map((item) => (
            <NavLink key={item.href} href={item.href} label={item.label} />
          ))}
        </nav>
        <div className="relative hidden md:block" ref={moreRef}>
          <button
            type="button"
            onClick={() => setMoreOpen((v) => !v)}
            className="rounded px-2 py-1 text-sm text-muted hover:bg-slate-800 hover:text-white"
            aria-expanded={moreOpen}
          >
            More
          </button>
          {moreOpen && (
            <div className="absolute right-0 z-50 mt-1 grid w-[min(90vw,28rem)] grid-cols-3 gap-4 rounded-lg border border-border bg-panel p-4 shadow-xl">
              {GROUPS.map((group) => (
                <div key={group.title}>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-sky-400/90">{group.title}</p>
                  <ul className="space-y-1 text-sm">
                    {group.links.map((link) => (
                      <li key={link.href}>
                        <Link
                          href={link.href}
                          className="block rounded px-2 py-1 text-muted hover:bg-slate-800 hover:text-white"
                          onClick={() => setMoreOpen(false)}
                        >
                          {link.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
        <button
          type="button"
          className="rounded border border-border px-3 py-1 text-sm text-muted hover:text-white md:hidden"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((v) => !v)}
        >
          Menu
        </button>
      </div>
      {menuOpen && (
        <nav className="w-full rounded-lg border border-border bg-panel p-3 text-sm md:hidden">
          <p className="mb-2 text-xs font-semibold uppercase text-muted">Main</p>
          <div className="mb-3 flex flex-wrap gap-1">
            {PRIMARY.map((item) => (
              <NavLink key={item.href} href={item.href} label={item.label} />
            ))}
          </div>
          {GROUPS.map((group) => (
            <div key={group.title} className="mb-3 border-t border-border/40 pt-3">
              <p className="mb-2 text-xs font-semibold uppercase text-sky-400/90">{group.title}</p>
              <div className="flex flex-wrap gap-1">
                {group.links.map((link) => (
                  <NavLink key={link.href} href={link.href} label={link.label} />
                ))}
              </div>
            </div>
          ))}
        </nav>
      )}
    </div>
  );
}
