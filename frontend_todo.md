# SkillBridge Frontend Pages and Backend Integration ToDo List (Updated)

This updated ToDo list is tailored to your existing frontend architecture (React 18 with TypeScript, Vite, Wouter routing, Tailwind CSS, shadcn/ui components, TanStack Query for state, custom hooks like useAuth/use-toast, api.ts for backend calls with JWT handling, and extensive components/hooks/lib). It focuses on:

- **Creating Missing Pages**: Based on the PRD and previous responses, adding Signin (Login), Signup (Register), Forgot Password, and other essential pages like Roadmap Creation/Viewer/List, Mentor Search/Request/Details/List, Notifications, Progress Analytics, Settings, and Admin Moderation (if applicable for roles).
- **Enhancing Existing Pages**: Improve Landing.tsx (add dynamic content/CTA integrations), Dashboard.tsx (deeper backend sync, real-time updates), Community.tsx (full forum integration with posting/replies), and not-found.tsx (better UX with suggestions). Leverage your api.ts methods (e.g., `api.register()`, `api.getUserRoadmaps()`) for integrations.
- **Overall Focus**: Ensure all pages integrate with backend APIs using TanStack Query for fetching/mutations, handle auth via useAuth hook, show toasts via use-toast, respect theme via theme-provider, and maintain mobile responsiveness with use-mobile. Use Wouter for routing (e.g., `<Router><Route path="/login" component={LoginPage} /></Router>`). Add PWA/offline support if not present. Enhance with accessibility (ARIA via shadcn/ui), error boundaries, and optimistic updates.

Phases are sequential for dependencies. Each item includes:
- **Description**: Page/enhancement purpose, UI elements (aligning with your design system), integration points using api.ts.
- **Dependencies**: Existing elements or prior tasks.
- **Implementation Details**: Steps, code snippets for integration (using TanStack Query, api.ts).
- **Testing/Verification**: Manual/API tests.
- **Estimated Effort**: For integration-focused work.
- **Potential Risks**: Mitigations.

Total phases: 7. Integrate with your existing structure (e.g., add to /pages, use /components/ui for shadcn elements).

## Phase 1: Authentication Pages (Create Missing)
Focus: Add core auth pages using your useAuth hook and api.ts (login/register methods).

- **ToDo 1.1: Implement Signin (Login) Page**
  - **Description**: Dedicated login form with email/password fields, remember me checkbox, forgot password link. Integrate api.login() for auth, show toast on success/error, redirect to Dashboard on login. Use shadcn/ui Form/Input/Button for styling.
  - **Dependencies**: useAuth hook, api.ts (login method), use-toast.
  - **Implementation Details**: Create /pages/Signin.tsx. Use TanStack Query mutation:
    ```tsx
    import { useMutation } from '@tanstack/react-query';
    import { useAuth } from '../hooks/useAuth';
    import { Input, Button, Form } from '../components/ui'; // shadcn/ui

    const SigninPage = () => {
      const { login } = useAuth(); // Your hook's login
      const mutation = useMutation({
        mutationFn: (data: { email: string; password: string }) => api.login(data),
        onSuccess: (res) => { login(res.token); window.location.href = '/dashboard'; }, // Or Wouter navigate
        onError: (err) => toast({ title: 'Error', description: err.message }),
      });

      return (
        <Form onSubmit={(e) => { e.preventDefault(); mutation.mutate(formData); }}>
          <Input type="email" placeholder="Email" />
          <Input type="password" placeholder="Password" />
          <Button type="submit" disabled={mutation.isLoading}>Login</Button>
          <a href="/forgot-password">Forgot Password?</a>
        </Form>
      );
    };
    ```
    Add to Wouter routes in main app.
  - **Testing/Verification**: Submit valid/invalid creds, check token storage, redirect, toast.
  - **Estimated Effort**: 3-4 hours.
  - **Potential Risks**: Form validation gaps; integrate Zod for schema.

- **ToDo 1.2: Implement Signup (Register) Page**
  - **Description**: Multi-step form: Basic info (email/password/role), profile details (skills/location/GitHub), initial quiz for roadmap prefs. Integrate api.register(), then chain to api.generateRoadmap() if learner role. Redirect to Dashboard post-signup.
  - **Dependencies**: Signin page, api.ts (register/generateRoadmap), useAuth (register mutation).
  - **Implementation Details**: /pages/Signup.tsx. Use shadcn/ui Tabs for steps, TanStack mutation chain:
    ```tsx
    const mutation = useMutation({
      mutationFn: async (data) => {
        const regRes = await api.register(data);
        if (data.role === 'learner') await api.generateRoadmap({ domain: quizData.domain, ... });
        return regRes;
      },
      onSuccess: (res) => { login(res.token); navigate('/dashboard'); },
    });
    ```
  - **Testing/Verification**: Full signup flow, verify backend user/roadmap creation.
  - **Estimated Effort**: 5-6 hours.
  - **Potential Risks**: Step data loss; use local state or Zustand.

- **ToDo 1.3: Implement Forgot Password Page**
  - **Description**: Form for email input, send reset link via backend API (assume /auth/forgot-password POST). Show success toast, link back to Signin.
  - **Dependencies**: Signin page, api.ts (add forgotPassword method if missing).
  - **Implementation Details**: /pages/ForgotPassword.tsx. Mutation:
    ```tsx
    const mutation = useMutation({
      mutationFn: (email: string) => api.forgotPassword({ email }), // Add to api.ts if needed
      onSuccess: () => toast({ title: 'Success', description: 'Reset link sent!' }),
    });
    ```
  - **Testing/Verification**: Submit email, check backend email queue or mock.
  - **Estimated Effort**: 2-3 hours.
  - **Potential Risks**: Email delivery; test with console log fallback.

## Phase 2: Enhance Existing Pages
Focus: Improve Landing, Dashboard, Community with deeper integrations/real-time.

- **ToDo 2.1: Enhance Landing Page**
  - **Description**: Add dynamic CTAs (e.g., "Get Started" → Signup if unauth, Dashboard if auth). Integrate backend healthCheck() for status badge. Enhance Features/HowItWorks with lazy-loaded images/animations.
  - **Dependencies**: Auth pages, api.ts (healthCheck).
  - **Implementation Details**: In Landing.tsx, use useQuery for optional dynamic content:
    ```tsx
    const { data: status } = useQuery({ queryKey: ['health'], queryFn: api.healthCheck });
    // Conditional CTA: <Button onClick={() => auth ? navigate('/dashboard') : navigate('/signup')}>Get Started</Button>
    ```
    Add offline fallback message.
  - **Testing/Verification**: Auth/unauth views, API call success.
  - **Estimated Effort**: 3 hours.
  - **Potential Risks**: Perf on load; disable query if unauth.

- **ToDo 2.2: Enhance Dashboard Page**
  - **Description**: Deepen integrations: Real-time notifications via polling/api.getNotifications(), auto-fetch roadmaps/matches/badges on load. Enhance stats/timeline with charts (use your chart.tsx), add manual progress log button integrating api.logProgress().
  - **Dependencies**: Landing enhance, api.ts (getUserRoadmaps/getMatches/getEarnedBadges/getNotifications/logProgress).
  - **Implementation Details**: Use multiple useQuery in Dashboard.tsx:
    ```tsx
    const { data: roadmaps } = useQuery({ queryKey: ['roadmaps'], queryFn: api.getUserRoadmaps });
    const progressMutation = useMutation({ mutationFn: api.logProgress, onSuccess: () => queryClient.invalidateQueries(['roadmaps']) });
    // Poll notifications: enabled refetchInterval: 30000
    ```
    Enhance Sidebar with role-based items (e.g., hide mentor tools for learners).
  - **Testing/Verification**: Data sync, mutation updates UI optimistically.
  - **Estimated Effort**: 5-6 hours.
  - **Potential Risks**: Over-polling; use Supabase Realtime if setup.

- **ToDo 2.3: Enhance Community (Forum) Page**
  - **Description**: Add full CRUD: Post creation form integrating api.createForumPost(), replies via api.createForumPost(parentId), filtering/search. Enhance threads with real-time refresh on new posts.
  - **Dependencies**: Dashboard enhance, api.ts (getForumPosts/createForumPost).
  - **Implementation Details**: In Community.tsx, mutation for posts:
    ```tsx
    const { data: posts } = useQuery({ queryKey: ['forum', category], queryFn: () => api.getForumPosts({ category }) });
    const postMutation = useMutation({ mutationFn: api.createForumPost, onSuccess: () => queryClient.invalidateQueries(['forum']) });
    ```
    Add upvote PATCH if not present.
  - **Testing/Verification**: Create/post/reply flow, search results.
  - **Estimated Effort**: 4-5 hours.
  - **Potential Risks**: Nested replies depth; limit to 3 levels.

- **ToDo 2.4: Enhance Not-Found Page**
  - **Description**: Add search suggestions, recent pages history (localStorage), or backend-recommended links (e.g., popular roadmaps).
  - **Dependencies**: Community enhance.
  - **Implementation Details**: In not-found.tsx, optional query for suggestions.
  - **Testing/Verification**: Navigate to invalid URL, check UX.
  - **Estimated Effort**: 1-2 hours.
  - **Potential Risks**: Static feel; add animations.

## Phase 3: Roadmap Pages (Create Missing)
Focus: Add dedicated roadmap management pages.

- **ToDo 3.1: Implement Roadmap Creation Page**
  - **Description**: Quiz form for domain/level/time, integrate api.generateRoadmap(). Redirect to Viewer on success.
  - **Dependencies**: Phase 2, api.ts (generateRoadmap).
  - **Implementation Details**: /pages/RoadmapCreate.tsx. Mutation with form.
  - **Testing/Verification**: Quiz submit, AI-generated modules.
  - **Estimated Effort**: 4 hours.
  - **Potential Risks**: AI errors; fallback template.

- **ToDo 3.2: Implement Roadmap Viewer Page**
  - **Description**: Detailed module view with embeds (YouTube/FreeCodeCamp), mark complete (api.updateRoadmapProgress), GitHub progress sync (api.getProgressAnalytics).
  - **Dependencies**: Creation, api.ts (updateRoadmapProgress/getProgressAnalytics).
  - **Implementation Details**: /pages/RoadmapViewer.tsx (param for id). Use your ResourceCard for embeds.
  - **Testing/Verification**: Complete module, progress update.
  - **Estimated Effort**: 5 hours.
  - **Potential Risks**: Embed loading; lazy load.

- **ToDo 3.3: Implement My Roadmaps List Page**
  - **Description**: Grid of RoadmapCard components, filter by domain/progress. Integrate api.getUserRoadmaps().
  - **Dependencies**: Viewer, api.ts.
  - **Implementation Details**: /pages/MyRoadmaps.tsx. Query with filters.
  - **Testing/Verification**: List rendering, navigation to Viewer.
  - **Estimated Effort**: 3 hours.
  - **Potential Risks**: No roadmaps; add creation CTA.

## Phase 4: Mentor Matching Pages (Create Missing)
Focus: Add mentor discovery and interaction pages.

- **ToDo 4.1: Implement Mentor Search Page**
  - **Description**: Filters form (skills/location), grid of MentorCard. Integrate api.getMentors() with params.
  - **Dependencies**: Phase 3, api.ts (getMentors).
  - **Implementation Details**: /pages/MentorSearch.tsx. Debounced search query.
  - **Testing/Verification**: Filter results.
  - **Estimated Effort**: 4 hours.
  - **Potential Risks**: Large lists; pagination.

- **ToDo 4.2: Implement Match Request Page/Modal**
  - **Description**: From search, form for request message. Integrate api.requestMentorMatch().
  - **Dependencies**: Search, api.ts (requestMentorMatch).
  - **Implementation Details**: /pages/MatchRequest.tsx or modal in Search. Mutation.
  - **Testing/Verification**: Request sent, pending in backend.
  - **Estimated Effort**: 3 hours.
  - **Potential Risks**: Spam; add captcha if needed.

- **ToDo 4.3: Implement Match Details/Chat Page**
  - **Description**: Schedule view, chat input. Integrate api.getMatches(id), api.respondToMatch(), real-time polling.
  - **Dependencies**: Request, api.ts (getMatches/respondToMatch).
  - **Implementation Details**: /pages/MatchDetails.tsx. Chat with mutations.
  - **Testing/Verification**: Message send, status update.
  - **Estimated Effort**: 5 hours.
  - **Potential Risks**: Chat perf; limit history.

- **ToDo 4.4: Implement My Matches List Page**
  - **Description**: Tabbed list (pending/active/completed). Integrate api.getMatches().
  - **Dependencies**: Details, api.ts.
  - **Implementation Details**: /pages/MyMatches.tsx. Use your Tabs component.
  - **Testing/Verification**: Status changes reflect.
  - **Estimated Effort**: 3 hours.
  - **Potential Risks**: Learner-only; role guard.

## Phase 5: Additional Pages (Create Missing)
Focus: Notifications, Progress Analytics, Settings, Admin (role-based).

- **ToDo 5.1: Implement Notifications Page**
  - **Description**: List with mark read. Integrate api.getNotifications/markNotificationAsRead().
  - **Dependencies**: Phase 4, api.ts.
  - **Implementation Details**: /pages/Notifications.tsx. Mutation for read, polling.
  - **Testing/Verification**: Mark all read.
  - **Estimated Effort**: 3 hours.
  - **Potential Risks**: Unread count; add badge in Navbar.

- **ToDo 5.2: Implement Progress Analytics Page**
  - **Description**: Detailed charts/logs from api.getProgressAnalytics(). Link from Dashboard.
  - **Dependencies**: Notifications, api.ts (getProgressAnalytics/logProgress).
  - **Implementation Details**: /pages/ProgressAnalytics.tsx. Use chart.tsx.
  - **Testing/Verification**: Data visualization.
  - **Estimated Effort**: 4 hours.
  - **Potential Risks**: Large data; paginate logs.

- **ToDo 5.3: Implement Settings Page**
  - **Description**: Theme/language toggle (enhance your theme-provider), password change, notifications prefs. Integrate api.updateUserProfile().
  - **Dependencies**: Progress, api.ts.
  - **Implementation Details**: /pages/Settings.tsx. Forms with mutations.
  - **Testing/Verification**: Update prefs, persist.
  - **Estimated Effort**: 4 hours.
  - **Potential Risks**: Sensitive ops; confirm dialogs.

- **ToDo 5.4: Implement Admin Moderation Page (Role-Based)**
  - **Description**: For admins: Moderate forum/posts, approve mentors. Integrate custom api methods (e.g., moderatePost).
  - **Dependencies**: Settings, api.ts (add if missing).
  - **Implementation Details**: /pages/AdminModeration.tsx. Guard with role from useAuth.
  - **Testing/Verification**: Role access only.
  - **Estimated Effort**: 4 hours.
  - **Potential Risks**: Security; strict permissions.

## Phase 6: Global Enhancements and Polish
Focus: App-wide improvements leveraging existing.

- **ToDo 6.1: Enhance Global Routing and Guards**
  - **Description**: Update Wouter setup for all new pages, add auth guards to protected routes.
  - **Dependencies**: Phase 5.
  - **Implementation Details**: In main app: <Route path="/roadmaps/create" component={RoadmapCreatePage} /> etc. Use hook for guards.
  - **Testing/Verification**: Full navigation.
  - **Estimated Effort**: 2 hours.
  - **Potential Risks**: Route conflicts; unique paths.

- **ToDo 6.2: Add Global Error Handling and Offline Support**
  - **Description**: Error boundaries around app, offline detection with cached data (enhance TanStack offline).
  - **Dependencies**: Routing.
  - **Implementation Details**: Use React ErrorBoundary, navigator.onLine checks.
  - **Testing/Verification**: Simulate offline.
  - **Estimated Effort**: 3 hours.
  - **Potential Risks**: Cache staleness; expiration.

- **ToDo 6.3: Implement Multi-Language Support**
  - **Description**: Add i18next if not present, localize all pages (focus on new ones).
  - **Dependencies**: Error handling.
  - **Implementation Details**: Wrap app with I18nextProvider, use t() in components.
  - **Testing/Verification**: Lang switch.
  - **Estimated Effort**: 4 hours.
  - **Potential Risks**: Missing translations; defaults.

## Phase 7: Final Integration Testing and Deployment Enhancements
Focus: Ensure cohesion.

- **ToDo 7.1: Full E2E Flow Testing**
  - **Description**: Test flows: Signup → Roadmap Create → Mentor Search → Match → Community Post → Notifications.
  - **Dependencies**: All.
  - **Implementation Details**: Use Vitest or add Cypress for e2e.
  - **Testing/Verification**: Coverage reports.
  - **Estimated Effort**: 5 hours.
  - **Potential Risks**: Backend deps; mock api.ts.

- **ToDo 7.2: Enhance Deployment Config**
  - **Description**: Update Vite config for PWA/manifest, optimize builds for new pages.
  - **Dependencies**: Testing.
  - **Implementation Details**: Add service worker if missing.
  - **Testing/Verification**: npm run build/preview.
  - **Estimated Effort**: 2 hours.
  - **Potential Risks**: Bundle size; tree-shake.

- **ToDo 7.3: Documentation Updates**
  - **Description**: Update README with new pages/flows, add component stories if using Storybook.
  - **Dependencies**: Deployment.
  - **Implementation Details**: List all routes/integrations.
  - **Testing/Verification**: Review.
  - **Estimated Effort**: 2 hours.
  - **Potential Risks**: Outdated; git hook checks.