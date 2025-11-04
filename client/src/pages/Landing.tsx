import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Features } from "@/components/Features";
import { HowItWorks } from "@/components/HowItWorks";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { MentorCard } from "@/components/MentorCard";
import { Quote } from "lucide-react";

export default function Landing() {
  const testimonials = [
    {
      name: "Aisha Okafor",
      role: "Full Stack Developer",
      location: "Lagos, Nigeria",
      quote: "SkillBridge transformed my career. The personalized roadmap and mentor support helped me land my first dev job in 6 months!",
    },
    {
      name: "Kwame Mensah",
      role: "Blockchain Developer",
      location: "Accra, Ghana",
      quote: "The AI-generated roadmap was exactly what I needed. It adapted as I progressed and kept me motivated throughout my journey.",
    },
  ];

  const featuredMentors = [
    {
      name: "Elena Nkosi",
      location: "Cape Town, South Africa",
      skills: ["React", "Node.js", "TypeScript", "AWS"],
      rating: 4.9,
      sessions: 243,
      badges: ["Gold Mentor", "React Expert"],
      available: true,
    },
    {
      name: "David Kamau",
      location: "Nairobi, Kenya",
      skills: ["Python", "Machine Learning", "Data Science"],
      rating: 4.7,
      sessions: 156,
      badges: ["Silver Mentor", "AI Specialist"],
      available: true,
    },
    {
      name: "Fatima Ahmed",
      location: "Cairo, Egypt",
      skills: ["Blockchain", "Solidity", "Web3", "DeFi"],
      rating: 4.8,
      sessions: 98,
      badges: ["Gold Mentor", "Blockchain Guru"],
      available: false,
    },
  ];

  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      
      <div id="features">
        <Features />
      </div>
      
      <div id="how-it-works">
        <HowItWorks />
      </div>

      <section id="mentors" className="py-20 bg-background">
        <div className="w-full max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4">
              Meet Our Expert Mentors
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Connect with experienced developers who are passionate about helping you succeed
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {featuredMentors.map((mentor, index) => (
              <MentorCard key={index} {...mentor} />
            ))}
          </div>

          <div className="text-center">
            <Button size="lg" variant="outline" className="hover-elevate active-elevate-2" data-testid="button-view-all-mentors">
              View All Mentors
            </Button>
          </div>
        </div>
      </section>

      <section className="py-20 bg-muted/30">
        <div className="w-full max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4">
              Success Stories
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Hear from learners who transformed their careers with SkillBridge
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="p-8 border-card-border">
                <Quote className="h-8 w-8 text-primary mb-4" />
                <p className="text-lg mb-6 leading-relaxed">{testimonial.quote}</p>
                <div>
                  <p className="font-medium">{testimonial.name}</p>
                  <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  <p className="text-sm text-muted-foreground">{testimonial.location}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="community" className="py-20 bg-background">
        <div className="w-full max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold mb-4">
              Join Our Growing Community
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              Connect with thousands of learners, share knowledge, and grow together
            </p>
            <Button size="lg" className="hover-elevate active-elevate-2" data-testid="button-join-community">
              Join SkillBridge Today
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
