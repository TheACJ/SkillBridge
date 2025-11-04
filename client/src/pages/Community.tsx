import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ForumThread } from "@/components/ForumThread";
import { Search, Plus } from "lucide-react";

export default function Community() {
  const [searchQuery, setSearchQuery] = useState("");

  const threads = [
    {
      id: "1",
      title: "How do I handle async/await in Python?",
      author: "Kwame Mensah",
      category: "Python",
      replies: 12,
      upvotes: 24,
      timeAgo: "2 hours ago",
      excerpt: "I'm working on a web scraping project and I'm confused about when to use async/await vs regular functions. Can someone explain the best practices?",
    },
    {
      id: "2",
      title: "Best resources for learning React Hooks?",
      author: "Aisha Ibrahim",
      category: "Web Development",
      replies: 8,
      upvotes: 15,
      timeAgo: "5 hours ago",
      excerpt: "Looking for comprehensive tutorials on React Hooks. I've completed the basics and want to dive deeper into useEffect and custom hooks.",
    },
    {
      id: "3",
      title: "How to prepare for technical interviews?",
      author: "David Kamau",
      category: "Career",
      replies: 25,
      upvotes: 42,
      timeAgo: "1 day ago",
      excerpt: "I have my first technical interview coming up next week. What are the most important topics I should focus on? Any tips from those who've been through this?",
    },
    {
      id: "4",
      title: "Understanding blockchain consensus mechanisms",
      author: "Fatima Ahmed",
      category: "Blockchain",
      replies: 6,
      upvotes: 18,
      timeAgo: "2 days ago",
      excerpt: "Can someone break down the differences between Proof of Work and Proof of Stake in simple terms? I'm new to blockchain development.",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="w-full max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Community Forum</h1>
          <p className="text-muted-foreground">Ask questions, share knowledge, and learn together</p>
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
          <Button className="gap-2 hover-elevate active-elevate-2" data-testid="button-new-thread">
            <Plus className="h-5 w-5" />
            New Discussion
          </Button>
        </div>

        <Tabs defaultValue="all" className="mb-6">
          <TabsList>
            <TabsTrigger value="all" data-testid="tab-all">All</TabsTrigger>
            <TabsTrigger value="python" data-testid="tab-python">Python</TabsTrigger>
            <TabsTrigger value="web" data-testid="tab-web">Web Dev</TabsTrigger>
            <TabsTrigger value="blockchain" data-testid="tab-blockchain">Blockchain</TabsTrigger>
            <TabsTrigger value="career" data-testid="tab-career">Career</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4 mt-6">
            {threads.map((thread) => (
              <ForumThread key={thread.id} {...thread} />
            ))}
          </TabsContent>

          <TabsContent value="python" className="mt-6">
            <ForumThread {...threads[0]} />
          </TabsContent>

          <TabsContent value="web" className="mt-6">
            <ForumThread {...threads[1]} />
          </TabsContent>

          <TabsContent value="blockchain" className="mt-6">
            <ForumThread {...threads[3]} />
          </TabsContent>

          <TabsContent value="career" className="mt-6">
            <ForumThread {...threads[2]} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
