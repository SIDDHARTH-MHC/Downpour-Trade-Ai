"use client";

import { ResearchOpsDashboard } from "@/components/modules/research/ResearchOpsDashboard";
import { ModuleHeader } from "@/components/shell/ModuleHeader";

export default function ResearchOpsPage() {
  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Research ops"
        description="Internal MDS dashboard — scheduler, data quality, experiments, and manual promotion"
      />
      <ResearchOpsDashboard />
    </div>
  );
}
