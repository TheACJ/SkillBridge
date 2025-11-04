import { ForumThread } from '../ForumThread';

export default function ForumThreadExample() {
  return (
    <div className="p-8 max-w-3xl space-y-4">
      <ForumThread
        id="1"
        title="How do I handle async/await in Python?"
        author="Kwame Mensah"
        category="Python"
        replies={12}
        upvotes={24}
        timeAgo="2 hours ago"
        excerpt="I'm working on a web scraping project and I'm confused about when to use async/await vs regular functions. Can someone explain the best practices?"
      />
      <ForumThread
        id="2"
        title="Best resources for learning React Hooks?"
        author="Aisha Ibrahim"
        category="Web Development"
        replies={8}
        upvotes={15}
        timeAgo="5 hours ago"
        excerpt="Looking for comprehensive tutorials on React Hooks. I've completed the basics and want to dive deeper into useEffect and custom hooks."
      />
    </div>
  );
}
