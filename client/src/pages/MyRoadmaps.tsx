import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { DashboardLayout } from "@/components/DashboardLayout";
import { RoadmapCard } from "@/components/RoadmapCard";
import { apiClient } from "@/lib/api";
import { Search, Plus, Filter, Grid, List, SortAsc } from "lucide-react";

export default function MyRoadmaps() {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("recent");
  const [filterBy, setFilterBy] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [, navigate] = useLocation();

  // Fetch user's roadmaps
  const { data: roadmapsData, isLoading } = useQuery({
    queryKey: ['user-roadmaps', sortBy, filterBy],
    queryFn: () => apiClient.getUserRoadmaps(),
  });

  const roadmaps = roadmapsData?.results || [];

  // Filter roadmaps based on search
  const filteredRoadmaps = roadmaps.filter(roadmap =>
    roadmap.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    roadmap.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sortOptions = [
    { value: "recent", label: "Recently Created" },
    { value: "progress", label: "Progress" },
    { value: "name", label: "Name (A-Z)" },
    { value: "time", label: "Time Commitment" },
  ];

  const filterOptions = [
    { value: "all", label: "All Roadmaps" },
    { value: "active", label: "Active" },
    { value: "completed", label: "Completed" },
    { value: "paused", label: "Paused" },
  ];

  const stats = {
    total: roadmaps.length,
    active: roadmaps.filter(r => r.progress_percentage < 100).length,
    completed: roadmaps.filter(r => r.progress_percentage === 100).length,
    totalHours: roadmaps.reduce((sum, r) => sum + (r.estimated_total_hours || 0), 0),
  };

  return (
    <DashboardLayout activeSection="roadmaps">
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">My Roadmaps</h1>
              <p className="text-muted-foreground">Track your learning journey and progress</p>
            </div>
            <Button onClick={() => navigate("/roadmaps/create")} className="gap-2">
              <Plus className="h-5 w-5" />
              Create Roadmap
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-sm text-muted-foreground">Total Roadmaps</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-600">{stats.active}</div>
                <div className="text-sm text-muted-foreground">Active</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
                <div className="text-sm text-muted-foreground">Completed</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-600">{stats.totalHours}</div>
                <div className="text-sm text-muted-foreground">Total Hours</div>
              </CardContent>
            </Card>
          </div>

          {/* Filters and Search */}
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search */}
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    placeholder="Search roadmaps..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {/* Filters */}
                <div className="flex gap-4">
                  <Select value={filterBy} onValueChange={setFilterBy}>
                    <SelectTrigger className="w-[140px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {filterOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger className="w-[160px]">
                      <SortAsc className="h-4 w-4 mr-2" />
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {sortOptions.map((option) => (
                        <SelectItem key={option.value} value={option.label}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* View Mode Toggle */}
                  <div className="flex border rounded-md">
                    <Button
                      variant={viewMode === "grid" ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setViewMode("grid")}
                      className="rounded-r-none"
                    >
                      <Grid className="h-4 w-4" />
                    </Button>
                    <Button
                      variant={viewMode === "list" ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setViewMode("list")}
                      className="rounded-l-none"
                    >
                      <List className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Roadmaps Grid/List */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-4 bg-muted rounded w-3/4"></div>
                    <div className="h-3 bg-muted rounded w-1/2"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-20 bg-muted rounded"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : filteredRoadmaps.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="space-y-4">
                  <div className="text-6xl">📚</div>
                  <h3 className="text-xl font-semibold">No roadmaps found</h3>
                  <p className="text-muted-foreground">
                    {searchQuery
                      ? "Try adjusting your search terms"
                      : "Create your first learning roadmap to get started"
                    }
                  </p>
                  {!searchQuery && (
                    <Button onClick={() => navigate("/roadmaps/create")} className="mt-4">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Your First Roadmap
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className={
              viewMode === "grid"
                ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                : "space-y-4"
            }>
              {filteredRoadmaps.map((roadmap) => (
                <div
                  key={roadmap.id}
                  onClick={() => navigate(`/roadmaps/${roadmap.id}`)}
                  className="cursor-pointer"
                >
                  {viewMode === "grid" ? (
                    <RoadmapCard
                      title={roadmap.title}
                      description={roadmap.description}
                      progress={roadmap.progress_percentage}
                      modules={roadmap.total_modules}
                      completedModules={Math.floor((roadmap.progress_percentage / 100) * roadmap.total_modules)}
                      estimatedTime={`${roadmap.estimated_total_hours}h`}
                      difficulty="Intermediate" // This would come from backend
                    />
                  ) : (
                    <Card className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg mb-2">{roadmap.title}</h3>
                            <p className="text-muted-foreground text-sm mb-3 line-clamp-2">
                              {roadmap.description}
                            </p>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span>{roadmap.total_modules} modules</span>
                              <span>{roadmap.estimated_total_hours}h total</span>
                              <Badge variant={roadmap.progress_percentage === 100 ? "default" : "secondary"}>
                                {roadmap.progress_percentage === 100 ? "Completed" : "In Progress"}
                              </Badge>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <div className="text-2xl font-bold text-primary mb-1">
                              {roadmap.progress_percentage}%
                            </div>
                            <Progress value={roadmap.progress_percentage} className="w-20 h-2" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Load More or Pagination could go here */}
          {filteredRoadmaps.length > 0 && (
            <div className="text-center">
              <p className="text-muted-foreground">
                Showing {filteredRoadmaps.length} of {roadmaps.length} roadmaps
              </p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}