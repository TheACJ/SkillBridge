import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  ArrowLeft,
  Send,
  Star,
  Calendar,
  MessageSquare,
  Clock,
  CheckCircle,
  User,
  ThumbsUp,
  ThumbsDown
} from "lucide-react";

interface MatchDetailsProps {
  params: { id: string };
}

export default function MatchDetails({ params }: MatchDetailsProps) {
  const [message, setMessage] = useState("");
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState("");
  const [showRating, setShowRating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const matchId = params.id;

  // Fetch match details
  const { data: match, isLoading: matchLoading } = useQuery({
    queryKey: ['match', matchId],
    queryFn: () => apiClient.getMatchDetails(matchId),
    enabled: !!matchId,
  });

  // Fetch chat messages
  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['match-messages', matchId],
    queryFn: () => apiClient.getMatchMessages(matchId),
    enabled: !!matchId,
    refetchInterval: 5000, // Poll every 5 seconds
  });

  const messages = messagesData?.results || [];

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (content: string) => apiClient.sendMatchMessage(matchId, { content }),
    onSuccess: () => {
      setMessage("");
      queryClient.invalidateQueries({ queryKey: ['match-messages', matchId] });
      queryClient.invalidateQueries({ queryKey: ['match', matchId] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to send message",
        variant: "destructive",
      });
    },
  });

  // Rate mentor mutation
  const rateMentorMutation = useMutation({
    mutationFn: (data: { rating: number; review: string }) =>
      apiClient.rateMentor(matchId, data),
    onSuccess: () => {
      toast({
        title: "Review Submitted",
        description: "Thank you for your feedback!",
      });
      setShowRating(false);
      setRating(0);
      setReview("");
      queryClient.invalidateQueries({ queryKey: ['match', matchId] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to submit review",
        variant: "destructive",
      });
    },
  });

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      sendMessageMutation.mutate(message.trim());
    }
  };

  const handleSubmitRating = (e: React.FormEvent) => {
    e.preventDefault();
    if (rating > 0 && review.trim()) {
      rateMentorMutation.mutate({ rating, review: review.trim() });
    }
  };

  if (matchLoading) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-6xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  <div className="h-96 bg-muted rounded"></div>
                </div>
                <div className="space-y-4">
                  <div className="h-64 bg-muted rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!match) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-6xl mx-auto text-center">
            <h1 className="text-2xl font-bold mb-4">Match Not Found</h1>
            <Button onClick={() => navigate("/matches")}>Back to Matches</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="mentors">
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/matches")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Matches
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Mentorship Chat</h1>
              <p className="text-muted-foreground">
                Connected with {match.mentor?.first_name} {match.mentor?.last_name}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chat Section */}
            <div className="lg:col-span-2">
              <Card className="h-[600px] flex flex-col">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5" />
                      Messages
                    </CardTitle>
                    <Badge variant={match.status === 'active' ? 'default' : 'secondary'}>
                      {match.status}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col p-0">
                  {/* Messages */}
                  <ScrollArea className="flex-1 p-4">
                    <div className="space-y-4">
                      {messagesLoading ? (
                        <div className="space-y-3">
                          {[...Array(3)].map((_, i) => (
                            <div key={i} className="animate-pulse">
                              <div className="h-16 bg-muted rounded"></div>
                            </div>
                          ))}
                        </div>
                      ) : messages.length === 0 ? (
                        <div className="text-center py-8">
                          <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                          <p className="text-muted-foreground">No messages yet. Start the conversation!</p>
                        </div>
                      ) : (
                        messages.map((msg: any) => (
                          <div
                            key={msg.id}
                            className={`flex gap-3 ${msg.is_from_mentor ? 'justify-start' : 'justify-end'}`}
                          >
                            {msg.is_from_mentor && (
                              <Avatar className="h-8 w-8">
                                <AvatarImage src={match.mentor?.avatar} />
                                <AvatarFallback>
                                  {match.mentor?.first_name?.[0]}
                                </AvatarFallback>
                              </Avatar>
                            )}
                            <div className={`max-w-[70%] ${msg.is_from_mentor ? '' : 'order-first'}`}>
                              <div className={`p-3 rounded-lg ${
                                msg.is_from_mentor
                                  ? 'bg-muted'
                                  : 'bg-primary text-primary-foreground'
                              }`}>
                                <p className="text-sm">{msg.content}</p>
                              </div>
                              <p className="text-xs text-muted-foreground mt-1">
                                {new Date(msg.created_at).toLocaleString()}
                              </p>
                            </div>
                            {!msg.is_from_mentor && (
                              <Avatar className="h-8 w-8">
                                <AvatarFallback>U</AvatarFallback>
                              </Avatar>
                            )}
                          </div>
                        ))
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  </ScrollArea>

                  {/* Message Input */}
                  {match.status === 'active' && (
                    <div className="p-4 border-t">
                      <form onSubmit={handleSendMessage} className="flex gap-2">
                        <Input
                          value={message}
                          onChange={(e) => setMessage(e.target.value)}
                          placeholder="Type your message..."
                          disabled={sendMessageMutation.isPending}
                        />
                        <Button
                          type="submit"
                          disabled={!message.trim() || sendMessageMutation.isPending}
                        >
                          <Send className="h-4 w-4" />
                        </Button>
                      </form>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Mentor Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Mentor Info
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-4">
                    <Avatar className="h-16 w-16">
                      <AvatarImage src={match.mentor?.avatar} />
                      <AvatarFallback className="text-lg">
                        {match.mentor?.first_name?.[0]}{match.mentor?.last_name?.[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-lg">
                        {match.mentor?.first_name} {match.mentor?.last_name}
                      </h3>
                      <p className="text-muted-foreground">Senior Developer</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Rating</span>
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span>{match.mentor?.rating || 4.5}</span>
                      </div>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Sessions</span>
                      <span>{match.session_count || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Started</span>
                      <span>{new Date(match.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {match.status === 'active' && (
                    <Button
                      className="w-full"
                      variant="outline"
                      onClick={() => setShowRating(true)}
                    >
                      <Star className="h-4 w-4 mr-2" />
                      Rate & Review
                    </Button>
                  )}

                  <Button className="w-full" variant="outline">
                    <Calendar className="h-4 w-4 mr-2" />
                    Schedule Session
                  </Button>

                  <Button className="w-full" variant="outline">
                    <Clock className="h-4 w-4 mr-2" />
                    View History
                  </Button>
                </CardContent>
              </Card>

              {/* Match Stats */}
              <Card>
                <CardHeader>
                  <CardTitle>Match Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Total Messages</span>
                    <span className="font-medium">{messages.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Sessions Completed</span>
                    <span className="font-medium">{match.session_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Days Active</span>
                    <span className="font-medium">
                      {Math.ceil((Date.now() - new Date(match.created_at).getTime()) / (1000 * 60 * 60 * 24))}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Rating Modal */}
          {showRating && (
            <Card className="max-w-md mx-auto">
              <CardHeader>
                <CardTitle>Rate Your Mentor</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmitRating} className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Rating</label>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          type="button"
                          onClick={() => setRating(star)}
                          className="focus:outline-none"
                        >
                          <Star
                            className={`h-6 w-6 ${
                              star <= rating
                                ? 'fill-yellow-400 text-yellow-400'
                                : 'text-gray-300'
                            }`}
                          />
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Review</label>
                    <Textarea
                      value={review}
                      onChange={(e) => setReview(e.target.value)}
                      placeholder="Share your experience..."
                      rows={3}
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" disabled={rating === 0 || !review.trim()}>
                      Submit Review
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowRating(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}