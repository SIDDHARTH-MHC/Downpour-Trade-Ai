"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function StatusPage() {
  const { data, error, isLoading } = useSWR("engine-status", () => api.engineStatus(), {
    refreshInterval: 60_000,
  });

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Engine health"
        description="Live dependency checks for data feeds and calibration"
      />
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <>
          <p className="text-sm">
            Overall{" "}
            <Badge variant={data.status === "ok" ? "success" : "warning"} className="ml-1">
              {data.status}
            </Badge>
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            {Object.entries(data.checks).map(([name, check]) => (
              <Card key={name}>
                <CardContent className="p-4 text-sm">
                  <div className="font-medium capitalize">{name.replace(/_/g, " ")}</div>
                  <div className={check.status === "ok" ? "text-long" : "text-warning"}>{check.status}</div>
                  <div className="text-xs text-muted">{check.detail}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
