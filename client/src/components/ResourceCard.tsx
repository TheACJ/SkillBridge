import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, Play } from "lucide-react";
import { SiYoutube } from "react-icons/si";

interface ResourceCardProps {
  title: string;
  platform: "YouTube" | "FreeCodeCamp" | "Custom";
  thumbnail?: string;
  duration: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  url: string;
}

export function ResourceCard({
  title,
  platform,
  thumbnail,
  duration,
  difficulty,
  url,
}: ResourceCardProps) {
  const platformColors = {
    YouTube: "bg-red-500 text-white",
    FreeCodeCamp: "bg-green-600 text-white",
    Custom: "bg-primary text-primary-foreground",
  };

  const difficultyColors = {
    Beginner: "bg-green-500/10 text-green-700 dark:text-green-400",
    Intermediate: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
    Advanced: "bg-red-500/10 text-red-700 dark:text-red-400",
  };

  return (
    <Card className="overflow-hidden hover-elevate active-elevate-2 transition-all duration-200 border-card-border group" data-testid="card-resource">
      <div className="relative aspect-video bg-muted">
        {thumbnail ? (
          <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Play className="h-12 w-12 text-muted-foreground" />
          </div>
        )}
        <div className={`absolute top-2 right-2 px-2 py-1 rounded-md text-xs font-medium ${platformColors[platform]}`}>
          {platform}
        </div>
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <Button size="lg" className="gap-2 hover-elevate active-elevate-2" data-testid="button-watch-now">
            <Play className="h-5 w-5" />
            Watch Now
          </Button>
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-base font-medium mb-2 line-clamp-2">{title}</h3>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{duration}</span>
          </div>
          <Badge variant="secondary" className={`text-xs ${difficultyColors[difficulty]}`}>
            {difficulty}
          </Badge>
        </div>
      </div>
    </Card>
  );
}
