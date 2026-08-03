import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";
import "./globals.css";
import type { Metadata } from "next";
import { AppShell } from "@/components/shell/AppShell";
import { AppProviders } from "@/components/providers/AppProviders";
import { themeBootstrapScript } from "@/lib/theme-bootstrap";

export const metadata: Metadata = {
  title: "Downpour Trade AI",
  description: "Deterministic crypto signal engine — no LLM, every number traceable",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeBootstrapScript() }} />
      </head>
      <body className="min-h-screen font-sans">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
        >
          Skip to content
        </a>
        <AppProviders>
          <AppShell>
            <div id="main-content">{children}</div>
          </AppShell>
        </AppProviders>
      </body>
    </html>
  );
}
