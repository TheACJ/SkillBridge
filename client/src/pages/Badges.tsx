import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import {
  Trophy,
  Star,
  Target,
  Flame,
  Award,
  Lock,
  CheckCircle,
  Calendar,
  TrendingUp
} from "lucide-react";

export default function Badges() {
  const [activeTab, setActiveTab] = useState("earned");

  // Fetch user's badges
  const { data: badgesData, isLoading } = useQuery({
    queryKey: ['user-badges'],
    queryFn: () => apiClient.getUserBadges(),
  });

  // Fetch all available badges
  const { data: allBadgesData } = useQuery({
    queryKey: ['all-badges'],
    queryFn: () => apiClient.getAllBadges(),
  });

  const earnedBadges = badgesData?.earned || [];
  const availableBadges = allBadgesData?.results || [];

  // Calculate progress for unearned badges
  const badgesWithProgress = availableBadges.map(badge => {
    const earned = earnedBadges.find(eb => eb.badge.id === badge.id);
    return {
      ...badge,
      earned: !!earned,
      earned_at: earned?.earned_at,
      progress: earned ? 100 : Math.min((badge.current_progress / badge.target_progress) * 100, 100)
    };
  });

  const unearnedBadges = badgesWithProgress.filter(badge => !badge.earned);
  const recentBadges = earnedBadges
    .sort((a, b) => new Date(b.earned_at).getTime() - new Date(a.earned_at).getTime())
    .slice(0, 5);

  const getBadgeIcon = (type: string) => {
    switch (type) {
      case 'achievement':
        return <Trophy className="h-6 w-6" />;
      case 'streak':
        return <Flame className="h-6 w-6" />;
      case 'skill':
        return <Target className="h-6 w-6" />;
      case 'milestone':
        return <Award className="h-6 w-6" />;
      case 'special':
        return <Star className="h-6 w-6" />;
      default:
        return <Award className="h-6 w-6" />;
    }
  };

  const getBadgeColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'from-purple-500 to-pink-500';
      case 'epic':
        return 'from-blue-500 to-purple-500';
      case 'rare':
        return 'from-green-500 to-blue-500';
      case 'uncommon':
        return 'from-yellow-500 to-orange-500';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const BadgeCard = ({ badge, earned = false, progress = 0, earned_at }: any) => (
    <Card className={`relative overflow-hidden transition-all hover:shadow-lg ${
      earned ? 'ring-2 ring-yellow-400' : ''
    }`}>
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-full bg-gradient-to-br ${getBadgeColor(badge.rarity)} text-white`}>
            {earned ? (
              <CheckCircle className="h-6 w-6" />
            ) : (
              getBadgeIcon(badge.type)
            )}
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-semibold text-lg">{badge.name}</h3>
              <Badge variant="secondary" className="text-xs">
                {badge.rarity}
              </Badge>
              {earned && (
                <Badge variant="default" className="text-xs bg-yellow-500">
                  Earned
                </Badge>
              )}
            </div>

            <p className="text-muted-foreground text-sm mb-3">
              {badge.description}
            </p>

            {earned ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>Earned {new Date(earned_at).toLocaleDateString()}</span>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{badge.current_progress || 0} / {badge.target_progress}</span>
                </div>
                <Progress value={progress} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  {badge.target_progress - (badge.current_progress || 0)} more to go!
                </p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <DashboardLayout activeSection="badges">
        <div className="p-8">
          <div className="max-w-6xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
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
    <DashboardLayout activeSection="badges">
      <div className="p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">My Badges</h1>
            <p className="text-muted-foreground">
              Track your achievements and unlock new badges as you progress
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-yellow-600">{earnedBadges.length}</div>
                <div className="text-sm text-muted-foreground">Earned</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-blue-600">{unearnedBadges.length}</div>
                <div className="text-sm text-muted-foreground">Available</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-purple-600">
                  {earnedBadges.filter(b => b.badge.rarity === 'legendary').length}
                </div>
                <div className="text-sm text-muted-foreground">Legendary</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-green-600">
                  {Math.round((earnedBadges.length / (earnedBadges.length + unearnedBadges.length)) * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">Completion</div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Badges */}
          {recentBadges.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Recently Earned
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recentBadges.map((earnedBadge) => (
                    <BadgeCard
                      key={earnedBadge.id}
                      badge={earnedBadge.badge}
                      earned={true}
                      earned_at={earnedBadge.earned_at}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Badges Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="earned">
                Earned ({earnedBadges.length})
              </TabsTrigger>
              <TabsTrigger value="available">
                Available ({unearnedBadges.length})
              </TabsTrigger>
              <TabsTrigger value="all">
                All Badges ({earnedBadges.length + unearnedBadges.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="earned" className="space-y-6">
              {earnedBadges.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Trophy className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No badges earned yet</h3>
                    <p className="text-muted-foreground mb-4">
                      Start learning and completing challenges to earn your first badge!
                    </p>
                    <Button>Explore Roadmaps</Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {earnedBadges.map((earnedBadge) => (
                    <BadgeCard
                      key={earnedBadge.id}
                      badge={earnedBadge.badge}
                      earned={true}
                      earned_at={earnedBadge.earned_at}
                    />
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="available" className="space-y-6">
              {unearnedBadges.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Award className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">All badges earned!</h3>
                    <p className="text-muted-foreground">
                      Congratulations! You've earned all available badges.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {unearnedBadges.map((badge) => (
                    <BadgeCard
                      key={badge.id}
                      badge={badge}
                      progress={badge.progress}
                    />
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="all" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {badgesWithProgress.map((badge) => (
                  <BadgeCard
                    key={badge.id}
                    badge={badge}
                    earned={badge.earned}
                    progress={badge.progress}
                    earned_at={badge.earned_at}
                  />
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </DashboardLayout>
  );
}