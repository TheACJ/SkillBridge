import { Card } from "@/components/ui/card";
import { CheckCircle } from "lucide-react";

const steps = [
  {
    number: "01",
    title: "Take the Assessment",
    description: "Answer a few questions about your goals, current skill level, and learning preferences.",
  },
  {
    number: "02",
    title: "Get Your Roadmap",
    description: "Receive a personalized AI-generated learning path with modules, resources, and milestones.",
  },
  {
    number: "03",
    title: "Connect with Mentors",
    description: "Match with expert mentors based on your needs, schedule 1:1 sessions, and get guidance.",
  },
  {
    number: "04",
    title: "Learn & Grow",
    description: "Follow your roadmap, track progress through GitHub, and earn badges as you advance.",
  },
];

export function HowItWorks() {
  return (
    <section className="py-20 bg-muted/30">
      <div className="w-full max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-semibold mb-4">
            How SkillBridge Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Four simple steps to accelerate your learning journey
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <Card className="p-6 h-full border-card-border">
                <div className="flex flex-col h-full">
                  <div className="text-5xl font-bold text-primary/20 mb-4 font-mono">
                    {step.number}
                  </div>
                  <h3 className="text-xl font-medium mb-3">{step.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                    {step.description}
                  </p>
                  <CheckCircle className="h-5 w-5 text-primary mt-4" />
                </div>
              </Card>
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-0.5 bg-border" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
