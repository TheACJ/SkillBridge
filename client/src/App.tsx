import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/lib/theme-provider";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import OfflineIndicator from "@/components/OfflineIndicator";
import { useAuth } from "@/hooks/useAuth";
import "./lib/i18n";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import Community from "@/pages/Community";
import NotFound from "@/pages/not-found";
import Signin from "@/pages/Signin";
import Signup from "@/pages/Signup";
import ForgotPassword from "@/pages/ForgotPassword";
import RoadmapCreate from "@/pages/RoadmapCreate";
import RoadmapViewer from "@/pages/RoadmapViewer";
import MyRoadmaps from "@/pages/MyRoadmaps";
import MentorSearch from "@/pages/MentorSearch";
import MentorRequest from "@/pages/MentorRequest";
import Notifications from "@/pages/Notifications";
import ProgressAnalytics from "@/pages/ProgressAnalytics";
import Settings from "@/pages/Settings";

function Router() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }
return (
  <Switch>
    {!isAuthenticated ? (
      <>
        <Route path="/" component={Landing} />
        <Route path="/signin" component={Signin} />
        <Route path="/signup" component={Signup} />
        <Route path="/forgot-password" component={ForgotPassword} />
      </>
    ) : (
      <>
        <Route path="/" component={Dashboard} />
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/community" component={Community} />
        <Route path="/roadmaps/create" component={RoadmapCreate} />
        <Route path="/roadmaps/:id" component={RoadmapViewer} />
        <Route path="/roadmaps" component={MyRoadmaps} />
        <Route path="/mentors" component={MentorSearch} />
        <Route path="/mentors/:id/request" component={MentorRequest} />
        <Route path="/notifications" component={Notifications} />
        <Route path="/progress" component={ProgressAnalytics} />
        <Route path="/settings" component={Settings} />
      </>
    )}
    <Route component={NotFound} />
  </Switch>
);
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider defaultTheme="light">
          <TooltipProvider>
            <OfflineIndicator />
            <Toaster />
            <Router />
          </TooltipProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
