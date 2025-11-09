import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { MessageCircle, ThumbsUp, Clock, Reply, Send } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

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
  const [showReplies, setShowReplies] = useState(false);
  const [replyContent, setReplyContent] = useState("");
  const [isReplying, setIsReplying] = useState(false);

  const queryClient = useQueryClient();
  const { toast } = useToast();

  const initials = author
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase();

  // Reply mutation
  const replyMutation = useMutation({
    mutationFn: (content: string) => apiClient.createForumPost({
      title: `Re: ${title}`,
      content,
      category,
      tags: []
    }),
    onSuccess: () => {
      toast({
        title: "Reply posted",
        description: "Your reply has been added to the discussion",
      });
      setReplyContent("");
      setIsReplying(false);
      queryClient.invalidateQueries({ queryKey: ['forum-posts'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to post reply",
        variant: "destructive",
      });
    },
  });

  const isLoading = replyMutation.status === 'pending';

  const handleReply = () => {
    if (replyContent.trim()) {
      replyMutation.mutate(replyContent);
    }
  };

  return (
    <Card
      className="p-4 hover-elevate active-elevate-2 transition-all duration-200 border-card-border"
      data-testid={`thread-${id}`}
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
              <h3 className="font-medium mb-1 line-clamp-1 cursor-pointer hover:text-primary"
                  onClick={() => console.log(`Open thread ${id}`)}>
                {title}
              </h3>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                <span>{author}</span>
                <span>•</span>
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {timeAgo}
                </div>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2 mb-2">{excerpt}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Badge variant="secondary" className="text-xs">
                    {category}
                  </Badge>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <MessageCircle className="h-4 w-4" />
                    <span>{replies} replies</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsReplying(!isReplying)}
                  >
                    <Reply className="h-4 w-4 mr-1" />
                    Reply
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowReplies(!showReplies)}
                  >
                    {showReplies ? 'Hide' : 'Show'} Replies
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Reply Form */}
          {isReplying && (
            <div className="mt-4 p-4 border rounded-lg bg-muted/50">
              <Textarea
                placeholder="Write your reply..."
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                rows={3}
                className="mb-2"
              />
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsReplying(false)}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleReply}
                  disabled={isLoading || !replyContent.trim()}
                >
                  {isLoading ? (
                    "Posting..."
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-1" />
                      Post Reply
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Replies Section */}
          {showReplies && replies > 0 && (
            <div className="mt-4 border-t pt-4">
              <h4 className="text-sm font-medium mb-3">Recent Replies</h4>
              <div className="space-y-3">
                {/* Mock replies - in real app, fetch from API */}
                <div className="flex gap-3 p-3 bg-muted/30 rounded-lg">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="text-xs">JD</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-sm mb-1">
                      <span className="font-medium">John Doe</span>
                      <span className="text-muted-foreground">2 hours ago</span>
                    </div>
                    <p className="text-sm">This is a helpful reply to the discussion...</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
