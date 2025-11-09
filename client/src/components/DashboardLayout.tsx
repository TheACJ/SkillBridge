import React from "react";
import { Code2, Home, LogOut, Map, MessageSquare, Settings, Users } from "lucide-react";
import { RootLayout } from "@/components/RootLayout";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
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

const menuItems = [
  { icon: Home, label: "Overview", href: "#overview" },
  { icon: Map, label: "My Roadmaps", href: "#roadmaps" },
  { icon: Users, label: "Find Mentors", href: "#mentors" },
  { icon: MessageSquare, label: "Community", href: "#community" },
  { icon: Settings, label: "Settings", href: "#settings" },
];

interface DashboardLayoutProps {
  children: React.ReactNode;
  activeSection?: string;
  onSectionChange?: (section: string) => void;
}

export function DashboardLayout({ 
  children,
  activeSection = "overview",
  onSectionChange
}: DashboardLayoutProps) {
  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  return (
    <RootLayout withPadding={false}>
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
                            const section = item.label.toLowerCase().replace(/\s+/g, '-');
                            onSectionChange?.(section);
                          }}
                          data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                          isActive={activeSection === item.label.toLowerCase().replace(/\s+/g, '-')}
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

            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </div>
      </SidebarProvider>
    </RootLayout>
  );
}