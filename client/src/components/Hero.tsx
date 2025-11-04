import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import heroImage from "@assets/generated_images/Hero_section_collaboration_image_b6d8e5f4.png";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `linear-gradient(to bottom, rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      />
      
      <div className="relative z-10 w-full max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/20 backdrop-blur-sm border border-primary/30 mb-6">
          <Sparkles className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-white">AI-Powered Learning Platform</span>
        </div>
        
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
          Your Bridge to Digital Skills<br />
          <span className="text-primary">Powered by AI & Community</span>
        </h1>
        
        <p className="text-lg md:text-xl text-gray-200 max-w-3xl mx-auto mb-8 leading-relaxed">
          Connect with expert mentors, follow personalized learning roadmaps, and access curated free resources. Built for aspiring developers in Africa and beyond.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <Button 
            size="lg" 
            className="bg-primary text-primary-foreground hover-elevate active-elevate-2 border border-primary-border px-8"
            data-testid="button-get-started"
            onClick={() => window.location.href = '/api/login'}
          >
            Get Started Free
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button 
            size="lg" 
            variant="outline"
            className="backdrop-blur-sm bg-white/10 text-white border-white/20 hover-elevate active-elevate-2 px-8"
            data-testid="button-explore-roadmaps"
            onClick={() => window.location.href = '/api/login'}
          >
            Explore Roadmaps
          </Button>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl mx-auto">
          <div className="backdrop-blur-sm bg-white/10 rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold text-white mb-1">10K+</div>
            <div className="text-sm text-gray-200">Active Learners</div>
          </div>
          <div className="backdrop-blur-sm bg-white/10 rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold text-white mb-1">500+</div>
            <div className="text-sm text-gray-200">Expert Mentors</div>
          </div>
          <div className="backdrop-blur-sm bg-white/10 rounded-lg p-4 border border-white/20">
            <div className="text-3xl font-bold text-white mb-1">50+</div>
            <div className="text-sm text-gray-200">Learning Paths</div>
          </div>
        </div>
      </div>
    </section>
  );
}
