import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";
import { DisclaimerFooter } from "@/components/DisclaimerFooter";

export const metadata: Metadata = {
  title: "Downpour Trade AI",
  description: "Deterministic crypto signal engine — no LLM, every number traceable",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-border bg-panel/80 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-lg font-bold text-sky-400">
              Downpour Trade AI
            </Link>
            <nav className="flex gap-4 text-sm text-muted">
              <Link href="/compare" className="hover:text-white">Compare</Link>
              <Link href="/correlation" className="hover:text-white">Correlation</Link>
              <Link href="/scenarios" className="hover:text-white">Scenarios</Link>
              <Link href="/coach" className="hover:text-white">Coach</Link>
              <Link href="/notebook" className="hover:text-white">Notebook</Link>
              <Link href="/portfolio" className="hover:text-white">Portfolio</Link>
              <Link href="/integrations" className="hover:text-white">Integrations</Link>
              <Link href="/" className="hover:text-white">Dashboard</Link>
              <Link href="/heatmap" className="hover:text-white">Heatmap</Link>
              <Link href="/status" className="hover:text-white">Status</Link>
              <Link href="/alerts" className="hover:text-white">Alerts</Link>
              <Link href="/history" className="hover:text-white">History</Link>
              <Link href="/flows" className="hover:text-white">Funding</Link>
              <Link href="/macro" className="hover:text-white">Macro</Link>
              <Link href="/engine" className="hover:text-white">Engine</Link>
              <Link href="/backtests" className="hover:text-white">Backtests</Link>
              <Link href="/glossary" className="hover:text-white">Glossary</Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
        <div className="mx-auto max-w-6xl px-4 pb-8">
          <DisclaimerFooter />
        </div>
      </body>
    </html>
  );
}
