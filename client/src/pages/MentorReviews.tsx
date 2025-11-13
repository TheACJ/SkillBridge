import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { Star, MessageSquare, ThumbsUp, ThumbsDown, Filter, ArrowLeft } from "lucide-react";

interface MentorReviewsProps {
  params: { mentorId: string };
}

export default function MentorReviews({ params }: MentorReviewsProps) {
  const [sortBy, setSortBy] = useState("recent");
  const [filterBy, setFilterBy] = useState("all");
  const [, navigate] = useLocation();

  const mentorId = params.mentorId;

  // Fetch mentor details
  const { data: mentor, isLoading: mentorLoading } = useQuery({
    queryKey: ['mentor', mentorId],
    queryFn: () => apiClient.getMentorDetails(mentorId),
    enabled: !!mentorId,
  });

  // Fetch mentor reviews
  const { data: reviewsData, isLoading: reviewsLoading } = useQuery({
    queryKey: ['mentor-reviews', mentorId, sortBy, filterBy],
    queryFn: () => apiClient.getMentorReviews(mentorId, { sort: sortBy, filter: filterBy }),
    enabled: !!mentorId,
  });

  const reviews = reviewsData?.results || [];

  const averageRating = reviews.length > 0
    ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length
    : 0;

  const ratingDistribution = [5, 4, 3, 2, 1].map(rating => ({
    rating,
    count: reviews.filter(review => review.rating === rating).length,
    percentage: reviews.length > 0 ? (reviews.filter(review => review.rating === rating).length / reviews.length) * 100 : 0
  }));

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ));
  };

  if (mentorLoading || reviewsLoading) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-muted rounded w-1/3"></div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                  <div className="h-32 bg-muted rounded"></div>
                  <div className="h-48 bg-muted rounded"></div>
                </div>
                <div className="space-y-4">
                  <div className="h-64 bg-muted rounded"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!mentor) {
    return (
      <DashboardLayout activeSection="mentors">
        <div className="p-8">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-2xl font-bold mb-4">Mentor Not Found</h1>
            <Button onClick={() => navigate("/mentors")}>Back to Mentors</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout activeSection="mentors">
      <div className="p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/mentors")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Mentors
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Mentor Reviews</h1>
              <p className="text-muted-foreground">
                Reviews for {mentor.first_name} {mentor.last_name}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Mentor Info & Stats */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle>Mentor Profile</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-4">
                    <Avatar className="h-16 w-16">
                      <AvatarImage src={mentor.avatar} />
                      <AvatarFallback className="text-lg">
                        {mentor.first_name[0]}{mentor.last_name[0]}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-lg">
                        {mentor.first_name} {mentor.last_name}
                      </h3>
                      <p className="text-muted-foreground">Senior Developer</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-600 mb-1">
                        {averageRating.toFixed(1)}
                      </div>
                      <div className="flex justify-center mb-1">
                        {renderStars(Math.round(averageRating))}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {reviews.length} reviews
                      </p>
                    </div>

                    {/* Rating Distribution */}
                    <div className="space-y-2">
                      {ratingDistribution.map(({ rating, count, percentage }) => (
                        <div key={rating} className="flex items-center gap-2 text-sm">
                          <span className="w-3">{rating}</span>
                          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                          <div className="flex-1 bg-muted rounded-full h-2">
                            <div
                              className="bg-yellow-400 h-2 rounded-full"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="w-8 text-right">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Reviews List */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Reviews</CardTitle>
                    <div className="flex gap-2">
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="text-sm border rounded px-2 py-1"
                      >
                        <option value="recent">Most Recent</option>
                        <option value="rating_high">Highest Rating</option>
                        <option value="rating_low">Lowest Rating</option>
                        <option value="helpful">Most Helpful</option>
                      </select>
                      <select
                        value={filterBy}
                        onChange={(e) => setFilterBy(e.target.value)}
                        className="text-sm border rounded px-2 py-1"
                      >
                        <option value="all">All Reviews</option>
                        <option value="5">5 Stars</option>
                        <option value="4">4 Stars</option>
                        <option value="3">3 Stars</option>
                        <option value="2">2 Stars</option>
                        <option value="1">1 Star</option>
                      </select>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {reviews.length === 0 ? (
                    <div className="text-center py-8">
                      <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No reviews yet</h3>
                      <p className="text-muted-foreground">
                        This mentor hasn't received any reviews yet.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {reviews.map((review: any) => (
                        <div key={review.id} className="border-b pb-6 last:border-b-0 last:pb-0">
                          <div className="flex items-start gap-4">
                            <Avatar className="h-10 w-10">
                              <AvatarImage src={review.reviewer?.avatar} />
                              <AvatarFallback>
                                {review.reviewer?.first_name?.[0]}{review.reviewer?.last_name?.[0]}
                              </AvatarFallback>
                            </Avatar>

                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h4 className="font-semibold">
                                  {review.reviewer?.first_name} {review.reviewer?.last_name}
                                </h4>
                                <div className="flex items-center gap-1">
                                  {renderStars(review.rating)}
                                </div>
                                <span className="text-sm text-muted-foreground">
                                  {new Date(review.created_at).toLocaleDateString()}
                                </span>
                              </div>

                              <p className="text-muted-foreground mb-3">
                                {review.review}
                              </p>

                              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <button className="flex items-center gap-1 hover:text-foreground">
                                  <ThumbsUp className="h-4 w-4" />
                                  <span>Helpful ({review.helpful_count || 0})</span>
                                </button>
                                <span>•</span>
                                <span>Mentored for {review.mentorship_duration || '3 months'}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
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