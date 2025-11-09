import { Card } from "@/components/ui/card";
import type { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: ReactNode;
}

export function StatCard({ title, value, change, icon }: StatCardProps) {
  return (
    <Card className="p-6 border-card-border">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-2">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
          {change && (
            <p className="text-xs text-green-600 dark:text-green-400 mt-2 flex items-center gap-1">
              {change}
            </p>
          )}
        </div>
        <div className="p-2 rounded-lg bg-primary/10">
          {icon}
        </div>
      </div>
    </Card>
  );
}