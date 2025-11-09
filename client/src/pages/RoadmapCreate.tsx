import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Target, BookOpen, Clock, Users, Sparkles } from "lucide-react";

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  category: string;
}

const quizQuestions: QuizQuestion[] = [
  {
    id: "goal",
    question: "What's your primary learning goal?",
    options: [
      "Become a full-stack web developer",
      "Master backend development",
      "Learn frontend technologies",
      "Build mobile applications",
      "Get into data science",
      "Start a tech career"
    ],
    category: "goal"
  },
  {
    id: "experience",
    question: "What's your current experience level?",
    options: ["Complete beginner", "Some coding knowledge", "Intermediate", "Advanced"],
    category: "experience"
  },
  {
    id: "time",
    question: "How much time can you dedicate per week?",
    options: ["5-10 hours", "10-20 hours", "20-30 hours", "30+ hours"],
    category: "time"
  },
  {
    id: "style",
    question: "What's your preferred learning style?",
    options: ["Hands-on projects", "Video tutorials", "Reading documentation", "Interactive courses"],
    category: "style"
  }
];

export default function RoadmapCreate() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [customGoal, setCustomGoal] = useState("");
  const [, navigate] = useLocation();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const createRoadmapMutation = useMutation({
    mutationFn: (data: any) => apiClient.generateRoadmap(data),
    onSuccess: (roadmap) => {
      toast({
        title: "Roadmap Created!",
        description: "Your personalized learning path is ready.",
      });
      queryClient.invalidateQueries({ queryKey: ['roadmaps'] });
      navigate(`/roadmaps/${roadmap.id}`);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create roadmap",
        variant: "destructive",
      });
    },
  });

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleNext = () => {
    if (currentStep < quizQuestions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleCreateRoadmap();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleCreateRoadmap = () => {
    const goal = answers.goal === "Other" ? customGoal : answers.goal;
    const experienceLevel = answers.experience?.toLowerCase() || "beginner";
    const timeCommitment = answers.time?.split("-")[0]?.split("+")[0] || "10";
    const learningStyle = answers.style?.toLowerCase().replace(" ", "_") || "hands_on";

    createRoadmapMutation.mutate({
      goal,
      current_skills: [],
      target_skills: [],
      time_commitment: `${timeCommitment}_hours_week`,
      timeline_months: 6,
      learning_style: learningStyle,
      experience_level: experienceLevel
    });
  };

  const currentQuestion = quizQuestions[currentStep];
  const progress = ((currentStep + 1) / quizQuestions.length) * 100;
  const isLastStep = currentStep === quizQuestions.length - 1;

  return (
    <DashboardLayout activeSection="roadmaps">
      <div className="p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <Sparkles className="h-8 w-8 text-primary" />
              <h1 className="text-3xl font-bold">Create Your Learning Roadmap</h1>
            </div>
            <p className="text-muted-foreground text-lg">
              Answer a few questions and we'll create a personalized learning path just for you
            </p>
          </div>

          {/* Progress Bar */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>Question {currentStep + 1} of {quizQuestions.length}</span>
                  <span>{Math.round(progress)}% Complete</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
            </CardContent>
          </Card>

          {/* Quiz Card */}
          <Card className="min-h-[400px]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {currentQuestion.category === "goal" && <Target className="h-5 w-5" />}
                {currentQuestion.category === "experience" && <BookOpen className="h-5 w-5" />}
                {currentQuestion.category === "time" && <Clock className="h-5 w-5" />}
                {currentQuestion.category === "style" && <Users className="h-5 w-5" />}
                {currentQuestion.question}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Answer Options */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentQuestion.options.map((option) => (
                  <button
                    key={option}
                    onClick={() => handleAnswer(currentQuestion.id, option)}
                    className={`p-4 text-left border rounded-lg transition-all hover:border-primary ${
                      answers[currentQuestion.id] === option
                        ? "border-primary bg-primary/5"
                        : "border-border hover:bg-muted/50"
                    }`}
                  >
                    <div className="font-medium">{option}</div>
                  </button>
                ))}
              </div>

              {/* Custom Goal Input */}
              {currentQuestion.id === "goal" && answers.goal === "Other" && (
                <div className="space-y-2">
                  <Label htmlFor="custom-goal">Tell us about your specific goal</Label>
                  <Textarea
                    id="custom-goal"
                    placeholder="Describe what you want to learn..."
                    value={customGoal}
                    onChange={(e) => setCustomGoal(e.target.value)}
                    rows={3}
                  />
                </div>
              )}

              {/* Navigation */}
              <div className="flex justify-between pt-6">
                <Button
                  variant="outline"
                  onClick={handleBack}
                  disabled={currentStep === 0}
                >
                  Back
                </Button>
                <Button
                  onClick={handleNext}
                  disabled={!answers[currentQuestion.id] || (currentQuestion.id === "goal" && answers.goal === "Other" && !customGoal.trim())}
                  className="min-w-[120px]"
                >
                  {createRoadmapMutation.isPending ? (
                    "Creating..."
                  ) : isLastStep ? (
                    "Create Roadmap"
                  ) : (
                    "Next"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Preview Section */}
          {Object.keys(answers).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Your Answers So Far</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(answers).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                      <span className="text-sm font-medium capitalize">{key}:</span>
                      <Badge variant="secondary">{value}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
