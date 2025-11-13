import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
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
  ArrowLeft,
  Users,
  Calendar,
  TrendingUp
} from "lucide-react";

interface BadgeDetailsProps {
  params: { badgeId: string };
}

export default function BadgeDetails({ params }: BadgeDetailsProps) {
  const [, navigate] = useLocation();
  const badgeId = params.badgeId;

  // Fetch badge details
  const { data: badge, isLoading: badgeLoading } = useQuery({
    queryKey: ['badge', badgeId],
    queryFn: () => apiClient.getBadgeDetails(badgeId),
    enabled: !!badgeId,
  });

  // Fetch badge earners
  const { data: earnersData, isLoading: earnersLoading } = useQuery({
    queryKey: ['badge-earners', badgeId],
    queryFn: () => apiClient.getBadgeEarners(badgeId),
    enabled: !!badgeId,
  });

  const earners = earnersData?.results || [];

  const getBadgeIcon = (type: string) => {
    switch (type) {
      case 'achievement':
        return <Trophy className="h-8 w-8" />;
      case 'streak':
        return <Flame className="h-8 w-8" />;
      case 'skill':
        return <Target className="h-8 w-8" />;
      case 'milestone':
        return <Award className="h-8 w-8" />;
      case 'special':
        return <Star className="h-8 w-8" />;
      default:
        return <Award className="h-8 w-8" />;
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

  const getRarityInfo = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return { label: 'Legendary', description: 'Extremely rare and prestigious', color: 'text-purple-600' };
      case 'epic':
        return { label: 'Epic', description: 'Very rare and valuable', color: 'text-blue-600' };
      case 'rare':
        return { label: 'Rare', description: 'Uncommon achievement', color: 'text-green-600' };
      case 'uncommon':
        return { label: 'Uncommon', description: 'Moderately difficult', color: 'text-yellow-600' };
      default:
        return { label: 'Common', description: 'Standard achievement', color: 'text-gray-600' };
    }
  };

  if (badgeLoading) {
    return (
      <DashboardLayout activeSection="badges">
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-64 bg-muted rounded"></div>
                <div className="h-64 bg-muted rounded"></div>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!badge) {
    return (
      <DashboardLayout activeSection="badges">
        <div className="p-8">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-2xl font-bold mb-4">Badge Not Found</h1>
            <Button onClick={() => navigate("/badges")}>Back to Badges</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const rarityInfo = getRarityInfo(badge.rarity);
  const progressPercentage = badge.is_earned ? 100 : Math.min((badge.current_progress / badge.target_progress) * 100, 100);

  return (
    <DashboardLayout activeSection="badges">
      <div className="p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/badges")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Badges
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Badge Details</h1>
              <p className="text-muted-foreground">
                {badge.name}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Badge Info */}
            <div className="space-y-6">
              <Card>
                <CardContent className="p-8">
                  <div className="text-center space-y-6">
                    {/* Badge Icon */}
                    <div className={`inline-flex p-6 rounded-full bg-gradient-to-br ${getBadgeColor(badge.rarity)} text-white shadow-lg`}>
                      {badge.is_earned ? (
                        <CheckCircle className="h-12 w-12" />
                      ) : (
                        getBadgeIcon(badge.type)
                      )}
                    </div>

                    {/* Badge Name & Status */}
                    <div>
                      <h2 className="text-2xl font-bold mb-2">{badge.name}</h2>
                      <div className="flex items-center justify-center gap-2 mb-4">
                        <Badge variant="secondary" className={rarityInfo.color}>
                          {rarityInfo.label}
                        </Badge>
                        {badge.is_earned && (
                          <Badge variant="default" className="bg-yellow-500">
                            Earned
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-muted-foreground text-lg">
                      {badge.description}
                    </p>

                    {/* Progress */}
                    {!badge.is_earned && (
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span>Progress</span>
                          <span>{badge.current_progress || 0} / {badge.target_progress}</span>
                        </div>
                        <Progress value={progressPercentage} className="h-3" />
                        <p className="text-sm text-muted-foreground">
                          {badge.target_progress - (badge.current_progress || 0)} more to go!
                        </p>
                      </div>
                    )}

                    {/* Earned Date */}
                    {badge.is_earned && badge.earned_at && (
                      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>Earned on {new Date(badge.earned_at).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Requirements */}
              <Card>
                <CardHeader>
                  <CardTitle>How to Earn</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {badge.requirements?.map((requirement: any, index: number) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className={`p-1 rounded-full ${
                          requirement.completed ? 'bg-green-100 text-green-600' : 'bg-muted text-muted-foreground'
                        }`}>
                          {requirement.completed ? (
                            <CheckCircle className="h-4 w-4" />
                          ) : (
                            <Lock className="h-4 w-4" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className={`text-sm ${requirement.completed ? 'text-foreground' : 'text-muted-foreground'}`}>
                            {requirement.description}
                          </p>
                          {requirement.progress && (
                            <div className="mt-2">
                              <Progress value={requirement.progress} className="h-1" />
                            </div>
                          )}
                        </div>
                      </div>
                    )) || (
                      <p className="text-muted-foreground">
                        Complete the requirements listed above to earn this badge.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Statistics & Earners */}
            <div className="space-y-6">
              {/* Statistics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Statistics
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{badge.total_earned || 0}</div>
                      <div className="text-sm text-muted-foreground">Total Earned</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {badge.total_earned ? Math.round((badge.total_earned / badge.total_users) * 100) : 0}%
                      </div>
                      <div className="text-sm text-muted-foreground">Earn Rate</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Rarity</span>
                      <span className={rarityInfo.color}>{rarityInfo.label}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Type</span>
                      <span className="capitalize">{badge.type}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Points</span>
                      <span>{badge.points || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Earners */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Recent Earners
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {earnersLoading ? (
                    <div className="space-y-3">
                      {[...Array(3)].map((_, i) => (
                        <div key={i} className="animate-pulse flex items-center gap-3">
                          <div className="h-8 w-8 bg-muted rounded-full"></div>
                          <div className="flex-1 space-y-1">
                            <div className="h-4 bg-muted rounded w-32"></div>
                            <div className="h-3 bg-muted rounded w-24"></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : earners.length === 0 ? (
                    <div className="text-center py-4">
                      <Users className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">No one has earned this badge yet</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {earners.slice(0, 10).map((earner: any) => (
                        <div key={earner.id} className="flex items-center gap-3">
                          <Avatar className="h-8 w-8">
                            <AvatarImage src={earner.avatar} />
                            <AvatarFallback>
                              {earner.first_name?.[0]}{earner.last_name?.[0]}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <p className="text-sm font-medium">
                              {earner.first_name} {earner.last_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Earned {new Date(earner.earned_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      ))}
                      {earners.length > 10 && (
                        <p className="text-sm text-muted-foreground text-center">
                          And {earners.length - 10} more...
                        </p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}