import { RoadmapCard } from '../RoadmapCard';

export default function RoadmapCardExample() {
  return (
    <div className="p-8 max-w-md">
      <RoadmapCard
        title="Python for Web Development"
        description="Learn Python fundamentals and build web applications with Django and Flask"
        progress={65}
        modules={12}
        completedModules={8}
        estimatedTime="8 weeks"
        difficulty="Intermediate"
      />
    </div>
  );
}
