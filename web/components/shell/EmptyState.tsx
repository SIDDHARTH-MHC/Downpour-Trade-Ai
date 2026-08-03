import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";

type EmptyStateProps = {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
};

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <Card className={cn("border-dashed", className)}>
      <CardContent className="flex flex-col items-center px-6 py-10 text-center">
        {Icon ? (
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-muted/60 text-muted-foreground">
            <Icon className="h-5 w-5" strokeWidth={1.5} aria-hidden />
          </div>
        ) : null}
        <h2 className="text-base font-medium text-foreground">{title}</h2>
        {description ? <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p> : null}
        {action ? <div className="mt-4">{action}</div> : null}
      </CardContent>
    </Card>
  );
}
