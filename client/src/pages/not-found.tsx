import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, Search, Home, BookOpen, Users, MessageSquare, ArrowLeft } from "lucide-react";
import { useLocation } from "wouter";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function NotFound() {
  const [searchQuery, setSearchQuery] = useState("");
  const [, navigate] = useLocation();
  const { isAuthenticated } = useAuth();

  // Fetch popular roadmaps for suggestions
  const { data: popularRoadmaps } = useQuery({
    queryKey: ['popular-roadmaps'],
    queryFn: () => apiClient.getUserRoadmaps(),
    enabled: isAuthenticated,
  });

  // Get recent pages from localStorage
  const [recentPages, setRecentPages] = useState<string[]>([]);

  useEffect(() => {
    const recent = localStorage.getItem('recentPages');
    if (recent) {
      try {
        setRecentPages(JSON.parse(recent));
      } catch (e) {
        // Ignore invalid JSON
      }
    }
  }, []);

  const quickActions = [
    {
      icon: Home,
      label: "Go Home",
      description: "Return to the main dashboard",
      action: () => navigate(isAuthenticated ? "/dashboard" : "/"),
      primary: true,
    },
    {
      icon: BookOpen,
      label: "Browse Roadmaps",
      description: "Explore learning paths",
      action: () => navigate("/roadmaps"),
    },
    {
      icon: Users,
      label: "Find Mentors",
      description: "Connect with experienced developers",
      action: () => navigate("/mentors"),
    },
    {
      icon: MessageSquare,
      label: "Community Forum",
      description: "Ask questions and share knowledge",
      action: () => navigate("/community"),
    },
  ];

  const suggestedPages = [
    { path: "/", label: "Landing Page", description: "Welcome and overview" },
    { path: "/dashboard", label: "Dashboard", description: "Your learning hub" },
    { path: "/community", label: "Community", description: "Forum discussions" },
    { path: "/roadmaps", label: "My Roadmaps", description: "Your learning paths" },
    { path: "/mentors", label: "Find Mentors", description: "Mentor discovery" },
    { path: "/progress", label: "Progress Analytics", description: "Learning insights" },
    { path: "/settings", label: "Settings", description: "Account preferences" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8">
        {/* Main Error Card */}
        <Card className="text-center">
          <CardHeader className="pb-4">
            <div className="flex justify-center mb-4">
              <div className="rounded-full bg-destructive/10 p-6">
                <AlertCircle className="h-12 w-12 text-destructive" />
              </div>
            </div>
            <CardTitle className="text-3xl font-bold">Oops! Page Not Found</CardTitle>
            <p className="text-muted-foreground mt-2">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search Functionality */}
            <div className="max-w-md mx-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  placeholder="Search for pages or content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  onClick={action.action}
                  variant={action.primary ? "default" : "outline"}
                  className="h-auto p-4 justify-start"
                >
                  <action.icon className="h-5 w-5 mr-3 flex-shrink-0" />
                  <div className="text-left">
                    <div className="font-medium">{action.label}</div>
                    <div className="text-sm opacity-70">{action.description}</div>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Suggestions Section */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Popular Pages */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <ArrowLeft className="h-5 w-5" />
                Suggested Pages
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {suggestedPages.slice(0, 5).map((page) => (
                <button
                  key={page.path}
                  onClick={() => navigate(page.path)}
                  className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="font-medium">{page.label}</div>
                  <div className="text-sm text-muted-foreground">{page.description}</div>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Recent Pages or Popular Content */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {recentPages.length > 0 ? "Recent Pages" : "Popular Roadmaps"}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentPages.length > 0 ? (
                recentPages.slice(0, 3).map((page, index) => (
                  <button
                    key={index}
                    onClick={() => navigate(page)}
                    className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors"
                  >
                    <div className="font-medium">{page}</div>
                    <div className="text-sm text-muted-foreground">Recently visited</div>
                  </button>
                ))
              ) : popularRoadmaps?.results ? (
                popularRoadmaps.results.slice(0, 3).map((roadmap) => (
                  <button
                    key={roadmap.id}
                    onClick={() => navigate(`/roadmaps/${roadmap.id}`)}
                    className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors"
                  >
                    <div className="font-medium">{roadmap.title}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary" className="text-xs">
                        {roadmap.progress_percentage}% complete
                      </Badge>
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No recent activity</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Help Section */}
        <Card>
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <h3 className="text-lg font-semibold">Need Help?</h3>
              <p className="text-muted-foreground">
                If you believe this is an error, please contact our support team or try refreshing the page.
              </p>
              <div className="flex justify-center gap-4">
                <Button variant="outline" onClick={() => window.location.reload()}>
                  Refresh Page
                </Button>
                <Button variant="outline" onClick={() => navigate("/community")}>
                  Ask Community
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
