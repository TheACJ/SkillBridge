import { Code2 } from "lucide-react";
import { SiGithub, SiLinkedin, SiX } from "react-icons/si";

export function Footer() {
  const footerSections = [
    {
      title: "About",
      links: [
        { label: "Our Mission", href: "#" },
        { label: "Team", href: "#" },
        { label: "Careers", href: "#" },
        { label: "Blog", href: "#" },
      ],
    },
    {
      title: "Resources",
      links: [
        { label: "Learning Paths", href: "#" },
        { label: "Mentor Network", href: "#" },
        { label: "Free Courses", href: "#" },
        { label: "Documentation", href: "#" },
      ],
    },
    {
      title: "Community",
      links: [
        { label: "Forums", href: "#" },
        { label: "Discord", href: "#" },
        { label: "Events", href: "#" },
        { label: "Success Stories", href: "#" },
      ],
    },
    {
      title: "Legal",
      links: [
        { label: "Privacy Policy", href: "#" },
        { label: "Terms of Service", href: "#" },
        { label: "Cookie Policy", href: "#" },
        { label: "NDPR Compliance", href: "#" },
      ],
    },
  ];

  return (
    <footer className="bg-muted/30 border-t mt-20">
      <div className="w-full max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <Code2 className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold">SkillBridge</span>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              Empowering African developers with AI-powered learning and community mentorship.
            </p>
            <div className="flex gap-3">
              <a href="#" className="hover-elevate active-elevate-2 p-2 rounded-md" data-testid="link-github">
                <SiGithub className="h-5 w-5" />
              </a>
              <a href="#" className="hover-elevate active-elevate-2 p-2 rounded-md" data-testid="link-linkedin">
                <SiLinkedin className="h-5 w-5" />
              </a>
              <a href="#" className="hover-elevate active-elevate-2 p-2 rounded-md" data-testid="link-x">
                <SiX className="h-5 w-5" />
              </a>
            </div>
          </div>

          {footerSections.map((section) => (
            <div key={section.title}>
              <h3 className="font-medium mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                      data-testid={`link-footer-${link.label.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} SkillBridge. All rights reserved.
            </p>
            <p className="text-sm text-muted-foreground">
              Made with ❤️ for developers in Africa and beyond
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
