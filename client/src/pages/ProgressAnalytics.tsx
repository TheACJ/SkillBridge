import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import {
  BarChart3,
  TrendingUp,
  Calendar,
  Clock,
  Target,
  Trophy,
  BookOpen,
  Flame,
  Award,
  Activity
} from "lucide-react";

export default function ProgressAnalytics() {
  const [selectedRoadmap, setSelectedRoadmap] = useState("all");
  const [timeRange, setTimeRange] = useState("30");

  // Fetch user's roadmaps for filtering
  const { data: roadmaps } = useQuery({
    queryKey: ['user-roadmaps'],
    queryFn: () => apiClient.getUserRoadmaps(),
  });

  // Fetch progress analytics
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['progress-analytics', selectedRoadmap, timeRange],
    queryFn: () => apiClient.getProgressAnalytics({
      roadmap_id: selectedRoadmap !== 'all' ? selectedRoadmap : undefined,
      days: parseInt(timeRange)
    }),
  });

  // Mock analytics data
  const mockAnalytics = {
    total_time_spent: 1240, // minutes
    current_streak_days: 12,
    longest_streak_days: 28,
    completion_rate: 78.5,
    average_session_length: 45, // minutes
    total_modules_completed: 24,
    total_badges_earned: 8,
    skill_progress: {
      "Python": 85,
      "Django": 72,
      "React": 45,
      "JavaScript": 68,
      "SQL": 55
    },
    weekly_stats: [
      { week: "Week 1", time_spent: 180, modules_completed: 3 },
      { week: "Week 2", time_spent: 240, modules_completed: 5 },
      { week: "Week 3", time_spent: 320, modules_completed: 7 },
      { week: "Week 4", time_spent: 280, modules_completed: 6 },
      { week: "Week 5", time_spent: 220, modules_completed: 3 }
    ],
    recent_achievements: [
      { name: "Consistent Learner", description: "7-day streak", date: "2024-01-15" },
      { name: "Python Master", description: "Completed Python fundamentals", date: "2024-01-12" },
      { name: "Quick Study", description: "5 modules in one week", date: "2024-01-10" }
    ]
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getStreakColor = (streak: number) => {
    if (streak >= 30) return "text-purple-600";
    if (streak >= 14) return "text-blue-600";
    if (streak >= 7) return "text-green-600";
    return "text-orange-600";
  };

  if (isLoading) {
    return (
      <DashboardLayout activeSection="progress">
        <div className="p-8">
          <div className="max-w-7xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-32 bg-muted rounded"></div>
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-96 bg-muted rounded"></div>
                <div className="h-96 bg-muted rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="progress">
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Progress Analytics</h1>
              <p className="text-muted-foreground">
                Track your learning journey with detailed insights and achievements
              </p>
            </div>

            <div className="flex gap-4">
              <Select value={selectedRoadmap} onValueChange={setSelectedRoadmap}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select roadmap" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roadmaps</SelectItem>
                  {roadmaps?.results?.map((roadmap) => (
                    <SelectItem key={roadmap.id} value={roadmap.id.toString()}>
                      {roadmap.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                  <SelectItem value="90">Last 3 months</SelectItem>
                  <SelectItem value="365">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Clock className="h-8 w-8 text-blue-500" />
                  <div>
                    <div className="text-2xl font-bold">{formatTime(mockAnalytics.total_time_spent)}</div>
                    <div className="text-sm text-muted-foreground">Total Time</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Flame className={`h-8 w-8 ${getStreakColor(mockAnalytics.current_streak_days)}`} />
                  <div>
                    <div className="text-2xl font-bold">{mockAnalytics.current_streak_days}</div>
                    <div className="text-sm text-muted-foreground">Day Streak</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-8 w-8 text-green-500" />
                  <div>
                    <div className="text-2xl font-bold">{mockAnalytics.total_modules_completed}</div>
                    <div className="text-sm text-muted-foreground">Modules Done</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Trophy className="h-8 w-8 text-purple-500" />
                  <div>
                    <div className="text-2xl font-bold">{mockAnalytics.total_badges_earned}</div>
                    <div className="text-sm text-muted-foreground">Badges Earned</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Weekly Progress Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Weekly Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockAnalytics.weekly_stats.map((week, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{week.week}</span>
                        <span className="text-muted-foreground">
                          {formatTime(week.time_spent)} • {week.modules_completed} modules
                        </span>
                      </div>
                      <Progress value={(week.time_spent / 400) * 100} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Skill Progress */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Skill Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(mockAnalytics.skill_progress).map(([skill, progress]) => (
                    <div key={skill} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{skill}</span>
                        <span className="text-muted-foreground">{progress}%</span>
                      </div>
                      <Progress value={progress} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Analytics Tabs */}
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="achievements">Achievements</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Completion Rate</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-green-600 mb-2">
                      {mockAnalytics.completion_rate}%
                    </div>
                    <Progress value={mockAnalytics.completion_rate} className="h-2 mb-2" />
                    <p className="text-sm text-muted-foreground">
                      Average completion rate across all modules
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Average Session</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {mockAnalytics.average_session_length}m
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Typical study session length
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Longest Streak</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-3xl font-bold mb-2 ${getStreakColor(mockAnalytics.longest_streak_days)}`}>
                      {mockAnalytics.longest_streak_days}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Days of consecutive learning
                    </p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="achievements" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Recent Achievements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockAnalytics.recent_achievements.map((achievement, index) => (
                      <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
                        <div className="flex-shrink-0">
                          <Trophy className="h-8 w-8 text-yellow-500" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold">{achievement.name}</h4>
                          <p className="text-sm text-muted-foreground">{achievement.description}</p>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(achievement.date).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      Learning Patterns
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                      <h4 className="font-semibold text-blue-900 dark:text-blue-100">Peak Learning Time</h4>
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        You study most effectively between 7-9 PM on weekdays
                      </p>
                    </div>

                    <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                      <h4 className="font-semibold text-green-900 dark:text-green-100">Strength Areas</h4>
                      <p className="text-sm text-green-700 dark:text-green-300">
                        Python and JavaScript are your strongest skills
                      </p>
                    </div>

                    <div className="p-4 bg-orange-50 dark:bg-orange-950/20 rounded-lg">
                      <h4 className="font-semibold text-orange-900 dark:text-orange-100">Improvement Areas</h4>
                      <p className="text-sm text-orange-700 dark:text-orange-300">
                        Consider spending more time on React and SQL
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                        <div>
                          <h4 className="font-medium">Increase Study Frequency</h4>
                          <p className="text-sm text-muted-foreground">
                            Adding 2 more study sessions per week could accelerate your progress
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                        <div>
                          <h4 className="font-medium">Focus on Weak Areas</h4>
                          <p className="text-sm text-muted-foreground">
                            Dedicate more time to SQL and React fundamentals
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                        <div>
                          <h4 className="font-medium">Maintain Consistency</h4>
                          <p className="text-sm text-muted-foreground">
                            Your current streak is impressive - keep it up!
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </DashboardLayout>
  );
}