import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ForumThread } from "@/components/ForumThread";
import { Search, Plus, MessageSquare, RefreshCw } from "lucide-react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import type { ForumPost } from "@shared/schema";

export default function Community() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newPost, setNewPost] = useState({
    title: "",
    content: "",
    category: "",
    tags: [] as string[]
  });

  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch forum posts with real-time refresh
  const { data: posts, isLoading, refetch } = useQuery({
    queryKey: ['forum-posts', selectedCategory, searchQuery],
    queryFn: () => apiClient.getForumPosts({
      category: selectedCategory !== 'all' ? selectedCategory : undefined,
      search: searchQuery || undefined
    }),
    refetchInterval: 30000, // Refresh every 30 seconds for real-time updates
  });

  // Create new post mutation
  const createPostMutation = useMutation({
    mutationFn: (data: typeof newPost) => apiClient.createForumPost(data),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Your discussion has been posted!",
      });
      setIsCreateDialogOpen(false);
      setNewPost({ title: "", content: "", category: "", tags: [] });
      queryClient.invalidateQueries({ queryKey: ['forum-posts'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create post",
        variant: "destructive",
      });
    },
  });

  // Manual refresh function
  const handleRefresh = () => {
    refetch();
    toast({
      title: "Refreshed",
      description: "Forum posts have been updated",
    });
  };

  // Filter posts based on search and category
  const filteredPosts = posts?.results || [];

  const categories = [
    { value: "all", label: "All" },
    { value: "python", label: "Python" },
    { value: "web", label: "Web Development" },
    { value: "blockchain", label: "Blockchain" },
    { value: "career", label: "Career" },
    { value: "general", label: "General" },
  ];

  return (
    <DashboardLayout activeSection="community">
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Community Forum</h1>
              <p className="text-muted-foreground">Ask questions, share knowledge, and learn together</p>
            </div>
            <Button
              onClick={handleRefresh}
              variant="outline"
              size="sm"
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
          </div>

          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="Search discussions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
                data-testid="input-search-forum"
              />
            </div>

            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2 hover-elevate active-elevate-2" data-testid="button-new-thread">
                  <Plus className="h-5 w-5" />
                  New Discussion
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>Create New Discussion</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      placeholder="What's your question or topic?"
                      value={newPost.title}
                      onChange={(e) => setNewPost(prev => ({ ...prev, title: e.target.value }))}
                    />
                  </div>

                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Select value={newPost.category} onValueChange={(value) => setNewPost(prev => ({ ...prev, category: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.slice(1).map((cat) => (
                          <SelectItem key={cat.value} value={cat.value}>
                            {cat.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="content">Content</Label>
                    <Textarea
                      id="content"
                      placeholder="Describe your question or share your knowledge..."
                      value={newPost.content}
                      onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                      rows={6}
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => setIsCreateDialogOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={() => createPostMutation.mutate(newPost)}
                      disabled={createPostMutation.isLoading || !newPost.title || !newPost.content || !newPost.category}
                    >
                      {createPostMutation.isLoading ? "Posting..." : "Post Discussion"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-6">
            <TabsList>
              {categories.map((cat) => (
                <TabsTrigger key={cat.value} value={cat.value} data-testid={`tab-${cat.value}`}>
                  {cat.label}
                </TabsTrigger>
              ))}
            </TabsList>

            {categories.map((cat) => (
              <TabsContent key={cat.value} value={cat.value} className="space-y-4 mt-6">
                {isLoading ? (
                  <div className="text-center py-8">
                    <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading discussions...</p>
                  </div>
                ) : filteredPosts.length === 0 ? (
                  <div className="text-center py-8">
                    <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No discussions found. Be the first to start one!</p>
                  </div>
                ) : (
                  filteredPosts.map((post: ForumPost) => (
                    <ForumThread
                      key={post.id}
                      id={post.id.toString()}
                      title={post.title}
                      author={post.author?.username || 'Anonymous'}
                      category={post.category}
                      replies={post.replies_count || 0}
                      upvotes={post.upvotes_count || 0}
                      timeAgo={new Date(post.created_at).toLocaleDateString()}
                      excerpt={post.content.substring(0, 150) + '...'}
                    />
                  ))
                )}
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </div>
    </DashboardLayout>
  );
}
