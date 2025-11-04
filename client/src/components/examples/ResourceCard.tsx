import { ResourceCard } from '../ResourceCard';

export default function ResourceCardExample() {
  return (
    <div className="p-8 max-w-sm">
      <ResourceCard
        title="Python Programming Complete Course - From Basics to Advanced"
        platform="YouTube"
        duration="4h 32m"
        difficulty="Beginner"
        url="https://youtube.com"
      />
    </div>
  );
}
