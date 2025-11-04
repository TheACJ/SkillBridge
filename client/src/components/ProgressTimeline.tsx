import { Card } from "@/components/ui/card";
import { CheckCircle, Circle, Clock } from "lucide-react";

interface TimelineItem {
  id: string;
  title: string;
  description: string;
  status: "completed" | "in-progress" | "pending";
  date?: string;
}

interface ProgressTimelineProps {
  items: TimelineItem[];
}

export function ProgressTimeline({ items }: ProgressTimelineProps) {
  const getIcon = (status: TimelineItem["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />;
      case "in-progress":
        return <Clock className="h-5 w-5 text-primary" />;
      default:
        return <Circle className="h-5 w-5 text-muted-foreground" />;
    }
  };

  return (
    <Card className="p-6 border-card-border">
      <h3 className="text-lg font-medium mb-6">Learning Timeline</h3>
      <div className="space-y-6">
        {items.map((item, index) => (
          <div key={item.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              {getIcon(item.status)}
              {index < items.length - 1 && (
                <div className="w-0.5 h-full min-h-[40px] bg-border mt-2" />
              )}
            </div>
            <div className="flex-1 pb-2">
              <h4 className="font-medium mb-1">{item.title}</h4>
              <p className="text-sm text-muted-foreground mb-1">{item.description}</p>
              {item.date && (
                <span className="text-xs text-muted-foreground font-mono">{item.date}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
