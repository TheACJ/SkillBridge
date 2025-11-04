import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MapPin, Star, Award } from "lucide-react";
import { SiGithub } from "react-icons/si";

interface MentorCardProps {
  name: string;
  avatar?: string;
  location: string;
  skills: string[];
  rating: number;
  sessions: number;
  badges: string[];
  available: boolean;
}

export function MentorCard({
  name,
  avatar,
  location,
  skills,
  rating,
  sessions,
  badges,
  available,
}: MentorCardProps) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <Card className="p-6 hover-elevate active-elevate-2 transition-all duration-200 border-card-border" data-testid="card-mentor">
      <div className="flex items-start gap-4 mb-4">
        <Avatar className="h-16 w-16">
          <AvatarImage src={avatar} alt={name} />
          <AvatarFallback className="text-lg font-medium">{initials}</AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium mb-1">{name}</h3>
          <div className="flex items-center gap-1 text-sm text-muted-foreground mb-2">
            <MapPin className="h-3 w-3" />
            <span>{location}</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
              <span className="font-medium">{rating.toFixed(1)}</span>
            </div>
            <div className="text-muted-foreground">{sessions} sessions</div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {skills.slice(0, 4).map((skill, index) => (
          <Badge key={index} variant="secondary" className="text-xs">
            {skill}
          </Badge>
        ))}
      </div>

      {badges.length > 0 && (
        <div className="flex items-center gap-2 mb-4">
          <Award className="h-4 w-4 text-primary" />
          <span className="text-xs text-muted-foreground font-mono">
            {badges.join(", ")}
          </span>
        </div>
      )}

      <div className="flex gap-2">
        <Button 
          className="flex-1 hover-elevate active-elevate-2" 
          disabled={!available}
          data-testid="button-request-mentor"
        >
          {available ? "Request Mentor" : "Unavailable"}
        </Button>
        <Button 
          variant="outline" 
          size="icon"
          className="hover-elevate active-elevate-2"
          data-testid="button-view-github"
        >
          <SiGithub className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  );
}
