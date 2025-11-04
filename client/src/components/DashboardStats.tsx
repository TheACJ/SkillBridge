import { Card } from "@/components/ui/card";
import { TrendingUp, Award, Users, Zap } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ReactNode;
}

function StatCard({ title, value, change, icon }: StatCardProps) {
  return (
    <Card className="p-6 border-card-border">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-2">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
          {change && (
            <p className="text-xs text-green-600 dark:text-green-400 mt-2 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
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

export function DashboardStats() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Current Streak"
        value="12 days"
        change="+3 from last week"
        icon={<Zap className="h-5 w-5 text-primary" />}
      />
      <StatCard
        title="Modules Completed"
        value="24"
        change="+6 this month"
        icon={<Award className="h-5 w-5 text-primary" />}
      />
      <StatCard
        title="Mentor Sessions"
        value="8"
        change="+2 scheduled"
        icon={<Users className="h-5 w-5 text-primary" />}
      />
      <StatCard
        title="Learning Progress"
        value="68%"
        change="+12% this month"
        icon={<TrendingUp className="h-5 w-5 text-primary" />}
      />
    </div>
  );
}
