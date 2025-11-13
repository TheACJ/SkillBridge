import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { MessageSquare, Calendar, Star, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function MyMatches() {
  const [activeTab, setActiveTab] = useState("active");
  const [, navigate] = useLocation();

  // Fetch user's matches
  const { data: matchesData, isLoading } = useQuery({
    queryKey: ['matches'],
    queryFn: () => apiClient.getMatches(),
  });

  const matches = matchesData?.results || [];

  // Filter matches by status
  const activeMatches = matches.filter(match => match.status === 'active');
  const pendingMatches = matches.filter(match => match.status === 'pending');
  const completedMatches = matches.filter(match => match.status === 'completed');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-50 border-green-200';
      case 'pending':
        return 'bg-yellow-50 border-yellow-200';
      case 'completed':
        return 'bg-blue-50 border-blue-200';
      case 'cancelled':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const MatchCard = ({ match }: { match: any }) => (
    <Card className={`hover:shadow-md transition-shadow cursor-pointer ${getStatusColor(match.status)}`}
          onClick={() => navigate(`/matches/${match.id}`)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <Avatar className="h-12 w-12">
              <AvatarImage src={match.mentor?.avatar} alt={match.mentor?.name} />
              <AvatarFallback>
                {match.mentor?.first_name?.[0]}{match.mentor?.last_name?.[0]}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-semibold text-lg">
                  {match.mentor?.first_name} {match.mentor?.last_name}
                </h3>
                <Badge variant="secondary" className="flex items-center gap-1">
                  {getStatusIcon(match.status)}
                  {match.status.charAt(0).toUpperCase() + match.status.slice(1)}
                </Badge>
              </div>

              <p className="text-muted-foreground mb-3">{match.mentor?.bio}</p>

              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4" />
                  <span>{match.mentor?.rating || 4.5} rating</span>
                </div>
                <div className="flex items-center gap-1">
                  <MessageSquare className="h-4 w-4" />
                  <span>{match.message_count || 0} messages</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>Started {new Date(match.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {match.last_message && (
                <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                  <p className="text-sm">
                    <span className="font-medium">Last message:</span> {match.last_message.content}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(match.last_message.created_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="text-right">
            <div className="text-sm text-muted-foreground mb-2">
              {match.session_count || 0} sessions
            </div>
            <Button size="sm" variant="outline">
              View Details
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-6xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-32 bg-muted rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="mentors">
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">My Mentorship Matches</h1>
            <p className="text-muted-foreground">
              Manage your mentorship relationships and track progress
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-600">{activeMatches.length}</div>
                <div className="text-sm text-muted-foreground">Active</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-yellow-600">{pendingMatches.length}</div>
                <div className="text-sm text-muted-foreground">Pending</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-600">{completedMatches.length}</div>
                <div className="text-sm text-muted-foreground">Completed</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-600">{matches.length}</div>
                <div className="text-sm text-muted-foreground">Total</div>
              </CardContent>
            </Card>
          </div>

          {/* Matches Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="active">
                Active ({activeMatches.length})
              </TabsTrigger>
              <TabsTrigger value="pending">
                Pending ({pendingMatches.length})
              </TabsTrigger>
              <TabsTrigger value="completed">
                Completed ({completedMatches.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="active" className="space-y-4">
              {activeMatches.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <div className="space-y-4">
                      <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto" />
                      <h3 className="text-xl font-semibold">No active matches</h3>
                      <p className="text-muted-foreground">
                        You don't have any active mentorship matches at the moment.
                      </p>
                      <Button onClick={() => navigate("/mentors")}>
                        Find a Mentor
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                activeMatches.map((match) => (
                  <MatchCard key={match.id} match={match} />
                ))
              )}
            </TabsContent>

            <TabsContent value="pending" className="space-y-4">
              {pendingMatches.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <div className="space-y-4">
                      <Clock className="h-12 w-12 text-muted-foreground mx-auto" />
                      <h3 className="text-xl font-semibold">No pending matches</h3>
                      <p className="text-muted-foreground">
                        You don't have any pending mentorship requests.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                pendingMatches.map((match) => (
                  <MatchCard key={match.id} match={match} />
                ))
              )}
            </TabsContent>

            <TabsContent value="completed" className="space-y-4">
              {completedMatches.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <div className="space-y-4">
                      <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto" />
                      <h3 className="text-xl font-semibold">No completed matches</h3>
                      <p className="text-muted-foreground">
                        You haven't completed any mentorship matches yet.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                completedMatches.map((match) => (
                  <MatchCard key={match.id} match={match} />
                ))
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </DashboardLayout>
  );
}