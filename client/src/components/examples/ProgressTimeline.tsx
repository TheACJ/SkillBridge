import { ProgressTimeline } from '../ProgressTimeline';

export default function ProgressTimelineExample() {
  const mockItems = [
    {
      id: "1",
      title: "Python Fundamentals",
      description: "Completed all basic syntax and data structures",
      status: "completed" as const,
      date: "Nov 1, 2025",
    },
    {
      id: "2",
      title: "Object-Oriented Programming",
      description: "Currently learning classes and inheritance",
      status: "in-progress" as const,
      date: "In Progress",
    },
    {
      id: "3",
      title: "Web Frameworks",
      description: "Django and Flask coming next",
      status: "pending" as const,
    },
  ];

  return (
    <div className="p-8 max-w-2xl">
      <ProgressTimeline items={mockItems} />
    </div>
  );
}
