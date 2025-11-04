import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { DashboardStats } from "@/components/DashboardStats";
import { RoadmapCard } from "@/components/RoadmapCard";
import { ProgressTimeline } from "@/components/ProgressTimeline";
import { ResourceCard } from "@/components/ResourceCard";
import { BadgeDisplay } from "@/components/BadgeDisplay";
import { MentorCard } from "@/components/MentorCard";
import {
  Home,
  Map,
  Users,
  MessageSquare,
  Settings,
  Code2,
  LogOut,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const menuItems = [
  { icon: Home, label: "Overview", href: "#overview" },
  { icon: Map, label: "My Roadmaps", href: "#roadmaps" },
  { icon: Users, label: "Find Mentors", href: "#mentors" },
  { icon: MessageSquare, label: "Community", href: "#community" },
  { icon: Settings, label: "Settings", href: "#settings" },
];

export default function Dashboard() {
  const [activeSection, setActiveSection] = useState("overview");

  const timelineItems = [
    {
      id: "1",
      title: "Python Fundamentals",
      description: "Completed all basic syntax and data structures",
      status: "completed" as const,
      date: "Nov 1, 2025",
    },
    {
      id: "2",
      title: "Object-Oriented Programming",
      description: "Currently learning classes and inheritance",
      status: "in-progress" as const,
      date: "In Progress",
    },
    {
      id: "3",
      title: "Web Frameworks",
      description: "Django and Flask coming next",
      status: "pending" as const,
    },
  ];

  const badges = [
    {
      id: "1",
      name: "First Steps",
      description: "Complete your first module",
      tier: "Bronze" as const,
      earned: true,
    },
    {
      id: "2",
      name: "Committed Learner",
      description: "Maintain a 7-day streak",
      tier: "Silver" as const,
      earned: true,
    },
    {
      id: "3",
      name: "Python Master",
      description: "Complete Python roadmap",
      tier: "Gold" as const,
      earned: false,
    },
    {
      id: "4",
      name: "Mentor Helper",
      description: "Complete 5 mentor sessions",
      tier: "Bronze" as const,
      earned: true,
    },
    {
      id: "5",
      name: "Community Star",
      description: "Help 10 community members",
      tier: "Silver" as const,
      earned: false,
    },
    {
      id: "6",
      name: "Code Warrior",
      description: "50 GitHub commits tracked",
      tier: "Gold" as const,
      earned: false,
    },
  ];

  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  return (
    <SidebarProvider style={style as React.CSSProperties}>
      <div className="flex h-screen w-full">
        <Sidebar>
          <SidebarHeader className="p-4 border-b">
            <div className="flex items-center gap-2">
              <Code2 className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">SkillBridge</span>
            </div>
          </SidebarHeader>
          
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Navigation</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {menuItems.map((item) => (
                    <SidebarMenuItem key={item.label}>
                      <SidebarMenuButton
                        onClick={() => {
                          setActiveSection(item.label.toLowerCase().replace(/\s+/g, '-'));
                          console.log(`Navigate to ${item.label}`);
                        }}
                        data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                      >
                        <item.icon className="h-5 w-5" />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          
          <SidebarFooter className="p-4 border-t">
            <div className="flex items-center gap-3 mb-3">
              <Avatar>
                <AvatarFallback className="bg-primary text-primary-foreground">AO</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">Aisha Okafor</p>
                <p className="text-xs text-muted-foreground">12-day streak 🔥</p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              className="w-full justify-start gap-2 hover-elevate active-elevate-2"
              data-testid="button-logout"
              onClick={() => window.location.href = '/api/logout'}
            >
              <LogOut className="h-4 w-4" />
              Log Out
            </Button>
          </SidebarFooter>
        </Sidebar>

        <div className="flex flex-col flex-1">
          <header className="flex items-center justify-between p-4 border-b">
            <SidebarTrigger data-testid="button-sidebar-toggle" />
            <ThemeToggle />
          </header>

          <main className="flex-1 overflow-auto p-8">
            <div className="max-w-7xl mx-auto space-y-8">
              <div>
                <h1 className="text-3xl font-bold mb-2">Welcome back, Aisha!</h1>
                <p className="text-muted-foreground">Here's your learning progress</p>
              </div>

              <DashboardStats />

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-8">
                  <div>
                    <h2 className="text-2xl font-semibold mb-4">Active Roadmaps</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <RoadmapCard
                        title="Python for Web Development"
                        description="Learn Python fundamentals and build web applications with Django and Flask"
                        progress={65}
                        modules={12}
                        completedModules={8}
                        estimatedTime="8 weeks"
                        difficulty="Intermediate"
                      />
                      <RoadmapCard
                        title="Full Stack JavaScript"
                        description="Master React, Node.js, and MongoDB to build complete web applications"
                        progress={30}
                        modules={15}
                        completedModules={5}
                        estimatedTime="12 weeks"
                        difficulty="Advanced"
                      />
                    </div>
                  </div>

                  <div>
                    <h2 className="text-2xl font-semibold mb-4">Recommended Resources</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <ResourceCard
                        title="Django REST Framework Tutorial"
                        platform="YouTube"
                        duration="2h 15m"
                        difficulty="Intermediate"
                        url="#"
                      />
                      <ResourceCard
                        title="Python OOP Complete Guide"
                        platform="FreeCodeCamp"
                        duration="3h 45m"
                        difficulty="Beginner"
                        url="#"
                      />
                      <ResourceCard
                        title="Building APIs with Flask"
                        platform="Custom"
                        duration="1h 30m"
                        difficulty="Intermediate"
                        url="#"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-8">
                  <ProgressTimeline items={timelineItems} />
                  <BadgeDisplay badges={badges} />
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Your Mentors</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <MentorCard
                    name="Elena Nkosi"
                    location="Cape Town, South Africa"
                    skills={["Python", "Django", "PostgreSQL", "AWS"]}
                    rating={4.9}
                    sessions={12}
                    badges={["Gold Mentor", "Python Expert"]}
                    available={true}
                  />
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
