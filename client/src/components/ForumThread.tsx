import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageCircle, ThumbsUp, Clock } from "lucide-react";

interface ForumThreadProps {
  id: string;
  title: string;
  author: string;
  authorAvatar?: string;
  category: string;
  replies: number;
  upvotes: number;
  timeAgo: string;
  excerpt: string;
}

export function ForumThread({
  id,
  title,
  author,
  authorAvatar,
  category,
  replies,
  upvotes,
  timeAgo,
  excerpt,
}: ForumThreadProps) {
  const initials = author
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  return (
    <Card 
      className="p-4 hover-elevate active-elevate-2 transition-all duration-200 border-card-border cursor-pointer" 
      data-testid={`thread-${id}`}
      onClick={() => console.log(`Open thread ${id}`)}
    >
      <div className="flex gap-4">
        <div className="flex flex-col items-center gap-2">
          <button 
            className="flex flex-col items-center gap-1 hover-elevate active-elevate-2 p-2 rounded-md"
            onClick={(e) => {
              e.stopPropagation();
              console.log(`Upvote thread ${id}`);
            }}
            data-testid={`button-upvote-${id}`}
          >
            <ThumbsUp className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">{upvotes}</span>
          </button>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-3 mb-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src={authorAvatar} alt={author} />
              <AvatarFallback className="text-xs">{initials}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <h3 className="font-medium mb-1 line-clamp-1">{title}</h3>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                <span>{author}</span>
                <span>•</span>
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {timeAgo}
                </div>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2 mb-2">{excerpt}</p>
              <div className="flex items-center gap-3">
                <Badge variant="secondary" className="text-xs">
                  {category}
                </Badge>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <MessageCircle className="h-4 w-4" />
                  <span>{replies} replies</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
