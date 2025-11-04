import { Card } from "@/components/ui/card";
import { Award, Lock } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface BadgeItem {
  id: string;
  name: string;
  description: string;
  tier: "Bronze" | "Silver" | "Gold";
  earned: boolean;
}

interface BadgeDisplayProps {
  badges: BadgeItem[];
}

export function BadgeDisplay({ badges }: BadgeDisplayProps) {
  const tierColors = {
    Bronze: "from-amber-700 to-amber-900",
    Silver: "from-gray-400 to-gray-600",
    Gold: "from-yellow-400 to-yellow-600",
  };

  return (
    <Card className="p-6 border-card-border">
      <h3 className="text-lg font-medium mb-6">Achievements</h3>
      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {badges.map((badge) => (
          <Tooltip key={badge.id}>
            <TooltipTrigger asChild>
              <div
                className={`relative aspect-square rounded-full flex items-center justify-center ${
                  badge.earned ? "cursor-pointer" : "cursor-not-allowed"
                }`}
                data-testid={`badge-${badge.id}`}
              >
                <div
                  className={`w-full h-full rounded-full bg-gradient-to-br ${
                    tierColors[badge.tier]
                  } flex items-center justify-center ${
                    !badge.earned && "opacity-30 grayscale"
                  }`}
                >
                  {badge.earned ? (
                    <Award className="h-8 w-8 text-white" />
                  ) : (
                    <Lock className="h-6 w-6 text-white" />
                  )}
                </div>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <div className="text-xs">
                <p className="font-medium">{badge.name}</p>
                <p className="text-muted-foreground">{badge.description}</p>
              </div>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </Card>
  );
}
