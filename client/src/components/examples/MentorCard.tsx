import { MentorCard } from '../MentorCard';

export default function MentorCardExample() {
  return (
    <div className="p-8 max-w-sm">
      <MentorCard
        name="Amara Okafor"
        location="Lagos, Nigeria"
        skills={["Python", "Django", "React", "PostgreSQL"]}
        rating={4.8}
        sessions={127}
        badges={["Gold Mentor", "Python Expert"]}
        available={true}
      />
    </div>
  );
}
