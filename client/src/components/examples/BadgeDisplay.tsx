import { BadgeDisplay } from '../BadgeDisplay';

export default function BadgeDisplayExample() {
  const mockBadges = [
    {
      id: "1",
      name: "First Steps",
      description: "Complete your first module",
      tier: "Bronze" as const,
      earned: true,
    },
    {
      id: "2",
      name: "Committed Learner",
      description: "Maintain a 7-day streak",
      tier: "Silver" as const,
      earned: true,
    },
    {
      id: "3",
      name: "Python Master",
      description: "Complete Python roadmap",
      tier: "Gold" as const,
      earned: false,
    },
    {
      id: "4",
      name: "Mentor Helper",
      description: "Complete 5 mentor sessions",
      tier: "Bronze" as const,
      earned: true,
    },
    {
      id: "5",
      name: "Community Star",
      description: "Help 10 community members",
      tier: "Silver" as const,
      earned: false,
    },
    {
      id: "6",
      name: "Code Warrior",
      description: "50 GitHub commits tracked",
      tier: "Gold" as const,
      earned: false,
    },
  ];

  return (
    <div className="p-8">
      <BadgeDisplay badges={mockBadges} />
    </div>
  );
}
