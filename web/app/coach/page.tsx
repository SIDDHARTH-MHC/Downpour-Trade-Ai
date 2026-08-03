"use client";

import { CoachPanel } from "@/components/CoachPanel";
import { ModuleHeader } from "@/components/shell/ModuleHeader";

export default function CoachPage() {
  return (
    <div className="space-y-4">
      <ModuleHeader
        title="AI Coach"
        description="Habits, engine literacy, and process — separate from explain-only Copilot"
      />
      <CoachPanel />
    </div>
  );
}
