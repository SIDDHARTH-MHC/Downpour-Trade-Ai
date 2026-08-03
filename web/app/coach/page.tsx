"use client";

import { CoachPanel } from "@/components/CoachPanel";

export default function CoachPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">AI Coach</h1>
        <p className="text-sm text-muted">Habits, engine literacy, and process — separate from explain-only Copilot</p>
      </div>
      <CoachPanel />
    </div>
  );
}
