import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DashboardLayout } from "@/components/DashboardLayout";
import { MentorCard } from "@/components/MentorCard";
import { apiClient } from "@/lib/api";
import { Search, Filter, MapPin, Star, Users, MessageSquare } from "lucide-react";

export default function MentorSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [experienceLevel, setExperienceLevel] = useState("all");
  const [availability, setAvailability] = useState("all");
  const [, navigate] = useLocation();

  // Fetch mentors with filters
  const { data: mentorsData, isLoading } = useQuery({
    queryKey: ['mentors', searchQuery, selectedSkills, experienceLevel, availability],
    queryFn: () => apiClient.getMentors({
      skills: selectedSkills.length > 0 ? selectedSkills.join(',') : undefined,
      experience_level: experienceLevel !== 'all' ? experienceLevel : undefined,
    }),
  });

  const mentors = mentorsData?.results || [];

  const popularSkills = [
    "Python", "JavaScript", "React", "Django", "Node.js",
    "SQL", "Git", "Docker", "AWS", "Machine Learning"
  ];

  const experienceLevels = [
    { value: "all", label: "All Levels" },
    { value: "beginner", label: "Beginner Friendly" },
    { value: "intermediate", label: "Intermediate" },
    { value: "advanced", label: "Advanced" },
  ];

  const availabilityOptions = [
    { value: "all", label: "Any Availability" },
    { value: "available", label: "Available Now" },
    { value: "busy", label: "Busy" },
    { value: "weekends", label: "Weekends Only" },
  ];

  const handleSkillToggle = (skill: string) => {
    setSelectedSkills(prev =>
      prev.includes(skill)
        ? prev.filter(s => s !== skill)
        : [...prev, skill]
    );
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedSkills([]);
    setExperienceLevel("all");
    setAvailability("all");
  };

  return (
    <DashboardLayout activeSection="mentors">
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold">Find Your Perfect Mentor</h1>
            <p className="text-muted-foreground text-lg">
              Connect with experienced developers who can guide your learning journey
            </p>
          </div>

          {/* Search and Filters */}
          <Card>
            <CardContent className="p-6">
              <div className="space-y-6">
                {/* Search Bar */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    placeholder="Search mentors by name, skills, or expertise..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 h-12 text-lg"
                  />
                </div>

                {/* Skill Tags */}
                <div className="space-y-3">
                  <h3 className="text-sm font-medium">Filter by Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {popularSkills.map((skill) => (
                      <Badge
                        key={skill}
                        variant={selectedSkills.includes(skill) ? "default" : "outline"}
                        className="cursor-pointer hover:bg-primary/80"
                        onClick={() => handleSkillToggle(skill)}
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Additional Filters */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Experience Level</label>
                    <Select value={experienceLevel} onValueChange={setExperienceLevel}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {experienceLevels.map((level) => (
                          <SelectItem key={level.value} value={level.value}>
                            {level.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Availability</label>
                    <Select value={availability} onValueChange={setAvailability}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {availabilityOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-end">
                    <Button variant="outline" onClick={clearFilters} className="w-full">
                      Clear Filters
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-muted rounded-full"></div>
                      <div className="space-y-2">
                        <div className="h-4 bg-muted rounded w-32"></div>
                        <div className="h-3 bg-muted rounded w-24"></div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="h-3 bg-muted rounded"></div>
                      <div className="h-3 bg-muted rounded w-3/4"></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : mentors.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="space-y-4">
                  <Users className="h-12 w-12 text-muted-foreground mx-auto" />
                  <h3 className="text-xl font-semibold">No mentors found</h3>
                  <p className="text-muted-foreground">
                    Try adjusting your search criteria or browse all available mentors.
                  </p>
                  <Button onClick={clearFilters} variant="outline">
                    Clear Filters
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mentors.map((mentor) => (
                <MentorCard
                  key={mentor.id}
                  name={`${mentor.first_name} ${mentor.last_name}`}
                  avatar={undefined}
                  location="Remote"
                  skills={mentor.skills || []}
                  rating={4.5}
                  sessions={15}
                  badges={["Top Mentor", "Quick Responder"]}
                  available={mentor.availability === 'available'}
                />
              ))}
            </div>
          )}

          {/* Stats Footer */}
          {mentors.length > 0 && (
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Showing {mentors.length} mentors</span>
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4" />
                      Average rating: 4.6
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-4 w-4" />
                      95% response rate
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}