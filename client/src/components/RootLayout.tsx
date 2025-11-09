import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

interface RootLayoutProps {
  children: React.ReactNode;
  /**
   * Whether to add vertical padding to the main content.
   * Useful for pages that need the content to touch the navbar (like Landing)
   */
  withPadding?: boolean;
}

export function RootLayout({ children, withPadding = true }: RootLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className={`flex-1 ${withPadding ? 'py-20' : ''}`}>
        {children}
      </main>
      <Footer />
    </div>
  );
}