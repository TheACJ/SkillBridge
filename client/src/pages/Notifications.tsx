import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import {
  Bell,
  CheckCircle,
  MessageSquare,
  User,
  Trophy,
  BookOpen,
  Calendar,
  AlertCircle,
  CheckCheck
} from "lucide-react";

export default function Notifications() {
  const [activeTab, setActiveTab] = useState("all");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch notifications
  const { data: notificationsData, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => apiClient.getNotifications(),
    refetchInterval: 30000, // Poll every 30 seconds
  });

  const notifications = notificationsData?.results || [];

  // Mark notification as read mutation
  const markReadMutation = useMutation({
    mutationFn: (notificationId: number) => apiClient.markNotificationAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to mark notification as read",
        variant: "destructive",
      });
    },
  });

  // Mark all as read mutation (mock for now)
  const markAllReadMutation = useMutation({
    mutationFn: () => Promise.resolve({ success: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      toast({
        title: "Success",
        description: "All notifications marked as read",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to mark all notifications as read",
        variant: "destructive",
      });
    },
  });

  const handleMarkRead = (notificationId: number) => {
    markReadMutation.mutate(notificationId);
  };

  const handleMarkAllRead = () => {
    markAllReadMutation.mutate();
  };

  // Filter notifications based on active tab
  const filteredNotifications = notifications.filter(notification => {
    if (activeTab === "all") return true;
    if (activeTab === "unread") return !notification.is_read;
    return notification.type === activeTab;
  });

  // Group notifications by date
  const groupedNotifications = filteredNotifications.reduce((groups, notification) => {
    const date = new Date(notification.created_at).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(notification);
    return groups;
  }, {} as Record<string, typeof notifications>);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "match_request":
        return <User className="h-5 w-5 text-blue-500" />;
      case "message":
        return <MessageSquare className="h-5 w-5 text-green-500" />;
      case "badge_earned":
        return <Trophy className="h-5 w-5 text-yellow-500" />;
      case "roadmap_progress":
        return <BookOpen className="h-5 w-5 text-purple-500" />;
      case "session_reminder":
        return <Calendar className="h-5 w-5 text-orange-500" />;
      default:
        return <Bell className="h-5 w-5 text-gray-500" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "match_request":
        return "border-l-blue-500";
      case "message":
        return "border-l-green-500";
      case "badge_earned":
        return "border-l-yellow-500";
      case "roadmap_progress":
        return "border-l-purple-500";
      case "session_reminder":
        return "border-l-orange-500";
      default:
        return "border-l-gray-500";
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (isLoading) {
    return (
      <DashboardLayout activeSection="notifications">
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-20 bg-muted rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="notifications">
      <div className="p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Notifications</h1>
              <p className="text-muted-foreground">
                Stay updated with your learning journey and community interactions
              </p>
            </div>
            {unreadCount > 0 && (
              <Button
                onClick={handleMarkAllRead}
                disabled={markAllReadMutation.isPending}
                variant="outline"
                className="gap-2"
              >
                <CheckCheck className="h-4 w-4" />
                Mark All Read ({unreadCount})
              </Button>
            )}
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="all" className="relative">
                All
                {notifications.length > 0 && (
                  <Badge variant="secondary" className="ml-2 h-5 w-5 p-0 text-xs">
                    {notifications.length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="unread" className="relative">
                Unread
                {unreadCount > 0 && (
                  <Badge variant="destructive" className="ml-2 h-5 w-5 p-0 text-xs">
                    {unreadCount}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="match_request">Requests</TabsTrigger>
              <TabsTrigger value="message">Messages</TabsTrigger>
              <TabsTrigger value="badge_earned">Badges</TabsTrigger>
              <TabsTrigger value="session_reminder">Sessions</TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="space-y-6">
              {Object.keys(groupedNotifications).length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">
                      {activeTab === "unread" ? "No unread notifications" : "No notifications"}
                    </h3>
                    <p className="text-muted-foreground">
                      {activeTab === "unread"
                        ? "You've read all your notifications!"
                        : "You'll see your notifications here when you have activity."
                      }
                    </p>
                  </CardContent>
                </Card>
              ) : (
                Object.entries(groupedNotifications)
                  .sort(([a], [b]) => new Date(b).getTime() - new Date(a).getTime())
                  .map(([date, dateNotifications]) => (
                    <div key={date} className="space-y-4">
                      <h3 className="text-sm font-medium text-muted-foreground sticky top-0 bg-background py-2">
                        {new Date(date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </h3>

                      <div className="space-y-3">
                        {dateNotifications.map((notification) => (
                          <Card
                            key={notification.id}
                            className={`transition-all hover:shadow-md ${
                              !notification.is_read ? 'bg-muted/30 border-l-4' : ''
                            } ${getNotificationColor(notification.type)}`}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-start gap-4">
                                <div className="flex-shrink-0 mt-1">
                                  {getNotificationIcon(notification.type)}
                                </div>

                                <div className="flex-1 min-w-0">
                                  <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                      <h4 className="font-medium text-sm mb-1">
                                        {notification.title}
                                      </h4>
                                      <p className="text-sm text-muted-foreground mb-2">
                                        {notification.message}
                                      </p>

                                      {notification.data && (
                                        <div className="text-xs text-muted-foreground mb-2">
                                          {notification.type === "match_request" && notification.data.requester_name && (
                                            <span>From: {notification.data.requester_name}</span>
                                          )}
                                          {notification.type === "badge_earned" && notification.data.badge_name && (
                                            <span>Badge: {notification.data.badge_name}</span>
                                          )}
                                          {notification.type === "system" && notification.data.session_time && (
                                            <span>Time: {new Date(notification.data.session_time).toLocaleString()}</span>
                                          )}
                                        </div>
                                      )}

                                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                        <span>
                                          {new Date(notification.created_at).toLocaleTimeString('en-US', {
                                            hour: '2-digit',
                                            minute: '2-digit'
                                          })}
                                        </span>
                                        {!notification.is_read && (
                                          <Badge variant="secondary" className="text-xs">
                                            New
                                          </Badge>
                                        )}
                                      </div>
                                    </div>

                                    {!notification.is_read && (
                                      <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => handleMarkRead(notification.id)}
                                        disabled={markReadMutation.isPending}
                                        className="flex-shrink-0"
                                      >
                                        <CheckCircle className="h-4 w-4" />
                                      </Button>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  ))
              )}
            </TabsContent>
          </Tabs>

          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Email Notifications</h4>
                    <p className="text-sm text-muted-foreground">
                      Receive email updates for important activities
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Configure
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Push Notifications</h4>
                    <p className="text-sm text-muted-foreground">
                      Get notified in your browser for real-time updates
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Configure
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}