import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";
import { AppNav } from "@/components/AppNav";
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
          <div className="mx-auto flex max-w-6xl flex-wrap items-start justify-between gap-3 px-4 py-3">
            <Link href="/" className="shrink-0 text-lg font-bold text-sky-400">
              Downpour Trade AI
            </Link>
            <AppNav />
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
