import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Send, User, MessageSquare, Target } from "lucide-react";

interface MentorRequestProps {
  params: { id: string };
}

export default function MentorRequest({ params }: MentorRequestProps) {
  const [message, setMessage] = useState("");
  const [topics, setTopics] = useState<string[]>([]);
  const [goals, setGoals] = useState("");
  const [availability, setAvailability] = useState("");
  const [, navigate] = useLocation();
  const { toast } = useToast();

  const mentorId = parseInt(params.id);

  // Mock mentor data for now
  const mentor = {
    id: mentorId,
    first_name: "Jane",
    last_name: "Smith",
    skills: ["Python", "Django", "React"],
    experience_level: "advanced"
  };
  const mentorLoading = false;

  // Request mentorship mutation (mock for now)
  const requestMutation = useMutation({
    mutationFn: (data: any) => Promise.resolve({ success: true }),
    onSuccess: () => {
      toast({
        title: "Request Sent!",
        description: "Your mentorship request has been sent. You'll be notified when they respond.",
      });
      navigate("/dashboard");
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to send mentorship request",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || !goals.trim() || !availability) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    requestMutation.mutate({
      message,
      topics,
      goals,
      availability,
    });
  };

  const suggestedTopics = [
    "Python", "Django", "React", "JavaScript", "Web Development",
    "Data Science", "Machine Learning", "Career Advice", "Code Review"
  ];

  const toggleTopic = (topic: string) => {
    setTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  if (mentorLoading) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  <div className="h-32 bg-muted rounded"></div>
                  <div className="h-48 bg-muted rounded"></div>
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

  if (!mentor) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-2xl font-bold mb-4">Mentor Not Found</h1>
            <Button onClick={() => navigate("/mentors")}>Back to Mentors</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="mentors">
      <div className="p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/mentors")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Mentors
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Request Mentorship</h1>
              <p className="text-muted-foreground">Connect with an experienced developer</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Mentor Profile */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Mentor Profile
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-4">
                    <Avatar className="h-16 w-16">
                      <AvatarImage src={undefined} alt={mentor.first_name} />
                      <AvatarFallback className="text-lg">
                        {mentor.first_name[0]}{mentor.last_name[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-lg">
                        {mentor.first_name} {mentor.last_name}
                      </h3>
                      <p className="text-muted-foreground">Senior Developer</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium mb-2">Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {(mentor.skills || []).map((skill, index) => (
                          <Badge key={index} variant="secondary">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Experience</h4>
                      <p className="text-sm text-muted-foreground">
                        {mentor.experience_level || 'Intermediate'} level
                      </p>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Rating</h4>
                      <div className="flex items-center gap-2">
                        <div className="flex">
                          {[...Array(5)].map((_, i) => (
                            <span key={i} className="text-yellow-400">★</span>
                          ))}
                        </div>
                        <span className="text-sm text-muted-foreground">4.8 (24 reviews)</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Request Form */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    Send Mentorship Request
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Topics of Interest */}
                    <div className="space-y-3">
                      <Label className="text-base font-medium">Topics you're interested in</Label>
                      <div className="flex flex-wrap gap-2">
                        {suggestedTopics.map((topic) => (
                          <Badge
                            key={topic}
                            variant={topics.includes(topic) ? "default" : "outline"}
                            className="cursor-pointer hover:bg-primary/80"
                            onClick={() => toggleTopic(topic)}
                          >
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Learning Goals */}
                    <div className="space-y-2">
                      <Label htmlFor="goals" className="flex items-center gap-2">
                        <Target className="h-4 w-4" />
                        What are your learning goals?
                      </Label>
                      <Textarea
                        id="goals"
                        placeholder="Describe what you hope to achieve with this mentorship..."
                        value={goals}
                        onChange={(e) => setGoals(e.target.value)}
                        rows={3}
                        required
                      />
                    </div>

                    {/* Availability */}
                    <div className="space-y-2">
                      <Label htmlFor="availability">When are you available for sessions?</Label>
                      <select
                        id="availability"
                        value={availability}
                        onChange={(e) => setAvailability(e.target.value)}
                        className="w-full p-3 border rounded-md"
                        required
                      >
                        <option value="">Select availability</option>
                        <option value="weekdays_evening">Weekdays (Evening)</option>
                        <option value="weekends">Weekends</option>
                        <option value="flexible">Flexible</option>
                        <option value="weekdays_morning">Weekdays (Morning)</option>
                      </select>
                    </div>

                    {/* Personal Message */}
                    <div className="space-y-2">
                      <Label htmlFor="message">Personal Message</Label>
                      <Textarea
                        id="message"
                        placeholder="Introduce yourself and explain why you'd like to work with this mentor..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        rows={5}
                        required
                      />
                      <p className="text-sm text-muted-foreground">
                        A personalized message increases your chances of getting a response
                      </p>
                    </div>

                    {/* Submit Button */}
                    <div className="flex justify-end gap-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => navigate("/mentors")}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        disabled={requestMutation.isPending}
                        className="min-w-[140px]"
                      >
                        {requestMutation.isPending ? (
                          "Sending..."
                        ) : (
                          <>
                            <Send className="h-4 w-4 mr-2" />
                            Send Request
                          </>
                        )}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}