import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Clock, BookOpen, CheckCircle } from "lucide-react";

interface RoadmapCardProps {
  title: string;
  description: string;
  progress: number;
  modules: number;
  completedModules: number;
  estimatedTime: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  onProgress?: () => void;
}

export function RoadmapCard({
  title,
  description,
  progress,
  modules,
  completedModules,
  estimatedTime,
  difficulty,
}: RoadmapCardProps) {
  const difficultyColors = {
    Beginner: "bg-green-500/10 text-green-700 dark:text-green-400",
    Intermediate: "bg-amber-500/10 text-amber-700 dark:text-amber-400",
    Advanced: "bg-red-500/10 text-red-700 dark:text-red-400",
  };

  return (
    <Card className="p-6 hover-elevate active-elevate-2 transition-all duration-200 border-card-border" data-testid="card-roadmap">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium mb-2">{title}</h3>
          <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-md font-medium ${difficultyColors[difficulty]}`}>
          {difficulty}
        </span>
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{progress}%</span>
          </div>
          {onProgress ? (
            <div className="flex items-center gap-2 cursor-pointer" onClick={onProgress}>
              <Progress value={progress} className="h-2 flex-1" />
              <Button variant="outline" size="icon" className="h-6 w-6">
                <CheckCircle className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <Progress value={progress} className="h-2" />
          )}
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <BookOpen className="h-4 w-4" />
            <span>{completedModules}/{modules} modules</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{estimatedTime}</span>
          </div>
        </div>

        <Button className="w-full hover-elevate active-elevate-2" data-testid="button-continue-learning">
          Continue Learning
        </Button>
      </div>
    </Card>
  );
}
