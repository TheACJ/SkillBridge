import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { DashboardLayout } from "@/components/DashboardLayout";
import { ResourceCard } from "@/components/ResourceCard";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  CheckCircle,
  Circle,
  Clock,
  BookOpen,
  ExternalLink,
  Play,
  FileText,
  Github,
  Trophy,
  Target,
  Calendar,
  BarChart3
} from "lucide-react";

interface RoadmapViewerProps {
  params: { id: string };
}

export default function RoadmapViewer({ params }: RoadmapViewerProps) {
  const [selectedModule, setSelectedModule] = useState<number | null>(null);
  const [showProgressDialog, setShowProgressDialog] = useState(false);
  const [progressNotes, setProgressNotes] = useState("");
  const [, navigate] = useLocation();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const roadmapId = parseInt(params.id);

  // Fetch roadmap details
  const { data: roadmap, isLoading: roadmapLoading } = useQuery({
    queryKey: ['roadmap', roadmapId],
    queryFn: () => apiClient.getRoadmapDetails(roadmapId),
    enabled: !!roadmapId,
  });

  // Fetch progress analytics
  const { data: analytics } = useQuery({
    queryKey: ['roadmap-analytics', roadmapId],
    queryFn: () => apiClient.getProgressAnalytics(roadmapId),
    enabled: !!roadmapId,
  });

  // Update module progress mutation
  const updateProgressMutation = useMutation({
    mutationFn: (data: { moduleId: number; completed: boolean; notes: string }) =>
      apiClient.updateRoadmapProgress(roadmapId, data.moduleId, {
        completed: data.completed,
        notes: data.notes,
        time_spent_minutes: 60 // Default 1 hour
      }),
    onSuccess: () => {
      toast({
        title: "Progress Updated",
        description: "Your learning progress has been saved.",
      });
      queryClient.invalidateQueries({ queryKey: ['roadmap', roadmapId] });
      queryClient.invalidateQueries({ queryKey: ['roadmap-analytics', roadmapId] });
      setShowProgressDialog(false);
      setProgressNotes("");
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update progress",
        variant: "destructive",
      });
    },
  });

  const handleModuleComplete = (moduleId: number, completed: boolean) => {
    setSelectedModule(moduleId);
    if (completed) {
      setShowProgressDialog(true);
    } else {
      updateProgressMutation.mutate({
        moduleId,
        completed: false,
        notes: "Marked as incomplete"
      });
    }
  };

  const handleProgressSubmit = () => {
    if (selectedModule) {
      updateProgressMutation.mutate({
        moduleId: selectedModule,
        completed: true,
        notes: progressNotes
      });
    }
  };

  if (roadmapLoading) {
    return (
      <DashboardLayout activeSection="roadmaps">
        <div className="p-8">
          <div className="max-w-6xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="h-4 bg-muted rounded w-1/2"></div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-32 bg-muted rounded"></div>
                  ))}
                </div>
                <div className="space-y-4">
                  <div className="h-48 bg-muted rounded"></div>
                  <div className="h-32 bg-muted rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!roadmap) {
    return (
      <DashboardLayout activeSection="roadmaps">
        <div className="p-8">
          <div className="max-w-6xl mx-auto text-center">
            <h1 className="text-2xl font-bold mb-4">Roadmap Not Found</h1>
            <Button onClick={() => navigate("/roadmaps")}>Back to Roadmaps</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="roadmaps">
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">{roadmap.title}</h1>
                <p className="text-muted-foreground mt-2">{roadmap.description}</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-primary">
                  {roadmap.progress_percentage}%
                </div>
                <div className="text-sm text-muted-foreground">Complete</div>
              </div>
            </div>

            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4" />
                <span>{roadmap.total_modules} modules</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>{roadmap.estimated_total_hours} hours total</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span>Created {new Date(roadmap.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <Progress value={roadmap.progress_percentage} className="h-3" />
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Modules List */}
            <div className="lg:col-span-2 space-y-4">
              <h2 className="text-xl font-semibold mb-4">Learning Modules</h2>

              {roadmap.modules?.map((module: any) => (
                <Card key={module.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {module.completed ? (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          ) : (
                            <Circle className="h-5 w-5 text-muted-foreground" />
                          )}
                          <h3 className="font-semibold">{module.title}</h3>
                          <Badge variant={module.completed ? "default" : "secondary"}>
                            {module.completed ? "Completed" : "In Progress"}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          {module.description}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{module.estimated_hours} hours</span>
                          <span>Order: {module.order}</span>
                        </div>
                      </div>
                    </div>
                  </CardHeader>

                  {module.resources && module.resources.length > 0 && (
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium">Resources</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {module.resources.map((resource: any, index: number) => (
                            <div key={index} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                              {resource.type === 'video' && <Play className="h-4 w-4 text-red-500" />}
                              {resource.type === 'article' && <FileText className="h-4 w-4 text-blue-500" />}
                              {resource.type === 'book' && <BookOpen className="h-4 w-4 text-green-500" />}
                              {resource.type === 'github' && <Github className="h-4 w-4 text-gray-700" />}
                              <div className="flex-1 min-w-0">
                                <div className="font-medium text-sm truncate">{resource.title}</div>
                                <div className="text-xs text-muted-foreground">{resource.platform}</div>
                              </div>
                              <Button size="sm" variant="ghost" asChild>
                                <a href={resource.url} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-4 w-4" />
                                </a>
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="flex justify-end mt-4">
                        <Button
                          size="sm"
                          variant={module.completed ? "outline" : "default"}
                          onClick={() => handleModuleComplete(module.id, !module.completed)}
                          disabled={updateProgressMutation.isPending}
                        >
                          {module.completed ? "Mark Incomplete" : "Mark Complete"}
                        </Button>
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Progress Stats */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Progress Stats
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Modules Completed</span>
                      <span>{roadmap.completed_modules || 0}/{roadmap.total_modules}</span>
                    </div>
                    <Progress value={(roadmap.completed_modules || 0) / roadmap.total_modules * 100} className="h-2" />
                  </div>

                  {analytics && (
                    <>
                      <div className="pt-4 border-t space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Total Time</span>
                          <span>{Math.round((analytics.total_time_spent || 0) / 60)}h</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Current Streak</span>
                          <span>{analytics.current_streak_days || 0} days</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Avg. Session</span>
                          <span>{Math.round(analytics.average_session_length || 0)}min</span>
                        </div>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full" variant="outline">
                    <Github className="h-4 w-4 mr-2" />
                    Connect GitHub
                  </Button>
                  <Button className="w-full" variant="outline">
                    <Trophy className="h-4 w-4 mr-2" />
                    View Achievements
                  </Button>
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={() => navigate("/progress")}
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Detailed Analytics
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Update Dialog */}
      <Dialog open={showProgressDialog} onOpenChange={setShowProgressDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update Progress</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="progress-notes">Notes (Optional)</Label>
              <Textarea
                id="progress-notes"
                placeholder="What did you learn? Any challenges faced?"
                value={progressNotes}
                onChange={(e) => setProgressNotes(e.target.value)}
                rows={4}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setShowProgressDialog(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleProgressSubmit}
                disabled={updateProgressMutation.isPending}
              >
                {updateProgressMutation.isPending ? "Saving..." : "Mark Complete"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}