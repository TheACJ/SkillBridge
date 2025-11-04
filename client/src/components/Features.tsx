import { Card } from "@/components/ui/card";
import { Map, Users, BookOpen, TrendingUp, GitBranch, Award } from "lucide-react";
import featureImage1 from "@assets/generated_images/Feature_showcase_coding_b8b1d46a.png";
import featureImage2 from "@assets/generated_images/Mentorship_feature_image_a71495ee.png";
import featureImage3 from "@assets/generated_images/Community_learning_image_4f7fb64e.png";

const features = [
  {
    icon: Map,
    title: "Personalized Roadmaps",
    description: "AI-generated learning paths tailored to your goals, skill level, and available time. Track progress with GitHub integration.",
  },
  {
    icon: Users,
    title: "Expert Mentorship",
    description: "Connect with experienced developers who provide guidance, answer questions, and accelerate your learning journey.",
  },
  {
    icon: BookOpen,
    title: "Curated Resources",
    description: "Access free learning materials from YouTube, FreeCodeCamp, and other platforms, all organized in your roadmap.",
  },
  {
    icon: TrendingUp,
    title: "Progress Tracking",
    description: "Visualize your learning journey with interactive dashboards, streaks, and milestone achievements.",
  },
  {
    icon: GitBranch,
    title: "GitHub Integration",
    description: "Automatically update your progress as you commit code, turning real projects into learning milestones.",
  },
  {
    icon: Award,
    title: "Gamified Badges",
    description: "Earn recognition as you learn and mentor others. Share achievements on LinkedIn and social media.",
  },
];

export function Features() {
  return (
    <section className="py-20 bg-background">
      <div className="w-full max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-semibold mb-4">
            Everything You Need to Succeed
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            SkillBridge combines AI technology, community support, and proven learning methods to help you achieve your development goals.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="p-6 hover-elevate active-elevate-2 transition-transform duration-200 border-card-border"
              data-testid={`card-feature-${index}`}
            >
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
