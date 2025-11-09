import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { DashboardLayout } from "@/components/DashboardLayout";
import { RoadmapCard } from "@/components/RoadmapCard";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import {
  BookOpen,
  Users,
  Trophy,
  TrendingUp,
  Calendar,
  Target,
  MessageSquare,
  Plus,
  ArrowRight
} from "lucide-react";
import { useLocation } from "wouter";

export default function Dashboard() {
  const { user } = useAuth();
  const [, navigate] = useLocation();

  // Mock dashboard data for now
  const dashboardData = null;
  const isLoading = false;

  // Mock data for now
  const mockData = {
    activeRoadmaps: [
      {
        id: 1,
        title: "Full-Stack Python Developer",
        progress: 65,
        modules: 12,
        completedModules: 8,
        estimatedTime: "120h",
        difficulty: "Intermediate" as const,
        tags: ["Python", "Django", "React"],
        nextMilestone: "Complete API development module"
      },
      {
        id: 2,
        title: "Machine Learning Fundamentals",
        progress: 30,
        modules: 8,
        completedModules: 2,
        estimatedTime: "80h",
        difficulty: "Advanced" as const,
        tags: ["ML", "Python", "TensorFlow"],
        nextMilestone: "Learn neural networks basics"
      }
    ],
    recentActivity: [
      { type: "module_completed", title: "Django Models", time: "2 hours ago" },
      { type: "badge_earned", title: "First Steps Badge", time: "1 day ago" },
      { type: "mentor_request", title: "Request sent to Jane Smith", time: "2 days ago" },
      { type: "roadmap_created", title: "Started React learning path", time: "3 days ago" }
    ],
    stats: {
      totalTimeSpent: 45,
      currentStreak: 7,
      completedModules: 8,
      earnedBadges: 3
    },
    upcomingSessions: [
      { mentor: "Jane Smith", topic: "Django Best Practices", time: "Tomorrow 3 PM" },
      { mentor: "John Doe", topic: "React Hooks Deep Dive", time: "Friday 2 PM" }
    ]
  };

  const quickActions = [
    {
      icon: BookOpen,
      title: "Create Roadmap",
      description: "Generate a personalized learning path",
      action: () => navigate("/roadmaps/create"),
      color: "bg-blue-500"
    },
    {
      icon: Users,
      title: "Find Mentors",
      description: "Connect with experienced developers",
      action: () => navigate("/mentors"),
      color: "bg-green-500"
    },
    {
      icon: MessageSquare,
      title: "Join Community",
      description: "Ask questions and share knowledge",
      action: () => navigate("/community"),
      color: "bg-purple-500"
    },
    {
      icon: Trophy,
      title: "View Progress",
      description: "Track your learning achievements",
      action: () => navigate("/progress"),
      color: "bg-orange-500"
    }
  ];

  if (isLoading) {
    return (
      <DashboardLayout activeSection="dashboard">
        <div className="p-8">
          <div className="max-w-7xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-32 bg-muted rounded"></div>
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  <div className="h-64 bg-muted rounded"></div>
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

  return (
    <DashboardLayout activeSection="dashboard">
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Welcome Header */}
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">
              Welcome back, {user?.first_name || 'Developer'}! 👋
            </h1>
            <p className="text-muted-foreground">
              Continue your learning journey and achieve your goals
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-8 w-8 text-blue-500" />
                  <div>
                    <div className="text-2xl font-bold">{mockData.stats.totalTimeSpent}h</div>
                    <div className="text-sm text-muted-foreground">Time Spent</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Target className="h-8 w-8 text-green-500" />
                  <div>
                    <div className="text-2xl font-bold">{mockData.stats.currentStreak}</div>
                    <div className="text-sm text-muted-foreground">Day Streak</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-8 w-8 text-purple-500" />
                  <div>
                    <div className="text-2xl font-bold">{mockData.stats.completedModules}</div>
                    <div className="text-sm text-muted-foreground">Modules Done</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Trophy className="h-8 w-8 text-orange-500" />
                  <div>
                    <div className="text-2xl font-bold">{mockData.stats.earnedBadges}</div>
                    <div className="text-sm text-muted-foreground">Badges Earned</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer" onClick={action.action}>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-lg ${action.color}`}>
                      <action.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold">{action.title}</h3>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Active Roadmaps */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold">Active Roadmaps</h2>
                <Button variant="outline" onClick={() => navigate("/roadmaps")}>
                  View All
                </Button>
              </div>

              {mockData.activeRoadmaps.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No active roadmaps</h3>
                    <p className="text-muted-foreground mb-4">
                      Create your first learning roadmap to get started
                    </p>
                    <Button onClick={() => navigate("/roadmaps/create")}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Roadmap
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {mockData.activeRoadmaps.map((roadmap) => (
                    <RoadmapCard
                      key={roadmap.id}
                      title={roadmap.title}
                      description={`Next: ${roadmap.nextMilestone}`}
                      progress={roadmap.progress}
                      modules={roadmap.modules}
                      completedModules={roadmap.completedModules}
                      estimatedTime={roadmap.estimatedTime}
                      difficulty={roadmap.difficulty}
                    />
                  ))}
                </div>
              )}

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockData.recentActivity.map((activity, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted/50">
                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                        <div className="flex-1">
                          <p className="text-sm font-medium">{activity.title}</p>
                          <p className="text-xs text-muted-foreground">{activity.time}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {activity.type.replace('_', ' ')}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Upcoming Sessions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Upcoming Sessions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {mockData.upcomingSessions.length === 0 ? (
                    <div className="text-center py-4">
                      <Calendar className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">No upcoming sessions</p>
                      <Button variant="outline" size="sm" className="mt-2" onClick={() => navigate("/mentors")}>
                        Find a Mentor
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {mockData.upcomingSessions.map((session, index) => (
                        <div key={index} className="p-3 border rounded-lg">
                          <div className="flex items-center gap-3 mb-2">
                            <Users className="h-4 w-4 text-primary" />
                            <span className="font-medium text-sm">{session.mentor}</span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-1">{session.topic}</p>
                          <p className="text-xs text-muted-foreground">{session.time}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Progress Overview */}
              <Card>
                <CardHeader>
                  <CardTitle>Progress Overview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Weekly Goal</span>
                      <span>12/20 hours</span>
                    </div>
                    <Progress value={60} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Monthly Goal</span>
                      <span>45/80 hours</span>
                    </div>
                    <Progress value={56} className="h-2" />
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Next Milestone</span>
                      <Badge variant="secondary">2 days left</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Complete Django authentication module
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Tips */}
              <Card>
                <CardHeader>
                  <CardTitle>💡 Learning Tip</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    "Consistent practice is more important than long study sessions.
                    Try the Pomodoro technique: 25 minutes of focused work followed by a 5-minute break."
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
