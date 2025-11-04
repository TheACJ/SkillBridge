# SkillBridge Design Guidelines (Compacted)

## Design Principles
**Framework:** Modern Web App with Design System Approach (Linear + GitHub + Notion inspired)
- Mobile-first, progressively enhanced
- Low-bandwidth optimized (minimal assets, efficient layouts)
- Developer-friendly aesthetics
- Natural gamification integration
- Balanced information density

---

## Typography

**Fonts:**
- Primary: Inter (UI/content)
- Accent: JetBrains Mono (code, badges, technical)

**Scale & Weights:**
```
Hero: text-4xl md:text-5xl font-bold leading-tight
Page titles: text-3xl font-semibold
Section headers: text-2xl md:text-3xl font-semibold  
Card titles: text-lg font-medium
Body: text-base font-normal leading-relaxed
Metadata: text-sm font-normal
Badges/micro: text-xs JetBrains Mono
```

---

## Layout & Spacing

**Spacing Units:** 2, 4, 6, 8, 12, 16, 20

```
Component padding: p-4 (mobile), p-6/p-8 (desktop)
Section spacing: py-12 md:py-16 lg:py-20
Gaps: gap-4 (mobile), gap-6 (tablet), gap-8 (desktop)
Related elements: space-y-2, grouped: space-y-4
```

**Grids:**
```
Dashboard: grid-cols-1 md:grid-cols-2 lg:grid-cols-3
Roadmap modules: grid-cols-1 lg:grid-cols-2
Mentor cards: grid-cols-1 sm:grid-cols-2 lg:grid-cols-3
Stats: grid-cols-1 sm:grid-cols-2 lg:grid-cols-4
```

**Containers:**
```
Full-width sections: w-full max-w-7xl mx-auto px-4
Dashboards: max-w-6xl
Reading content: max-w-prose
Sidebar: Fixed w-64 + flex-1 main
```

---

## Components

### Navigation
**Top Nav:**
- `sticky top-0 h-16` with backdrop-blur
- Flex layout: logo left, nav center, user menu right
- Mobile: hamburger → slide-out drawer
- Elements: logo, Dashboard/Roadmaps/Mentors/Community links, notifications, avatar dropdown

**Sidebar (Dashboard):**
- Desktop: fixed w-64 left, mobile: hidden (hamburger access)
- Icon-left items with active state indicator
- Sections: Learning, Mentorship, Community, Settings

### Cards

**Roadmap Module:**
```
rounded-lg p-6 border shadow
Header: icon + text-lg font-medium title
Content: progress bar, time estimate, resource count
Footer: CTA button
State: draggable on hover
```

**Mentor Profile:**
```
p-4 compact layout
Avatar + name + skills tags + badges
Stats: sessions, rating, availability
CTA: "Request Mentor" button
Hover: subtle lift + shadow
```

**Resource Card:**
```
16:9 thumbnail + platform badge (top-right)
text-base font-medium title (line-clamp-2)
Duration + difficulty indicator
Hover: "Watch Now" overlay
```

**Badges (Gamification):**
```
Sizes: w-8 h-8 (sm), w-12 h-12 (md), w-16 h-16 (lg)
Circular/shield with gradient treatment
Tooltip on hover (name + criteria)
Locked: semi-transparent
```

### Forms & Inputs

**Standard Input:**
```
h-12 px-4 rounded-md
Focus: ring-2
Label: text-sm font-medium mb-2
Helper: text-xs mt-1
```

**Onboarding Assessment:**
```
Multi-step wizard + progress indicator
Radio buttons: h-12 touch targets
Checkboxes: grid-cols-2 md:grid-cols-3
Navigation: secondary Back + primary Next buttons
```

**Search/Filters:**
```
Search: h-12 with icon-left
Filters: multi-select dropdowns
Active filters: dismissible chips below search
```

### Data Visualization

**Progress:**
```
Linear bars: h-2 rounded-full
Circular: SVG-based (dashboard summary)
Milestones: connected dots timeline
Streak: calendar heatmap grid
```

**Stats Cards:**
```
text-3xl font-bold number
text-sm label below
Icon/trend indicator
```

### Interactive Elements

**Buttons:**
```
Primary: rounded-md px-6 py-3 font-medium
Secondary: same size + border
Icon buttons: w-10 h-10 centered
Hero CTAs: backdrop-blur-sm semi-transparent bg
All: smooth transition
```

**Tabs:**
```
Horizontal bar + underline indicator
Mobile: scrollable overflow
Active: underline + font-medium
```

**Modals:**
```
max-w-2xl centered + backdrop-blur-sm
p-6 content
Close button: top-right absolute
Footer: flex justify-end gap-4 actions
```

### Community

**Forum:**
```
Thread rows: avatar + title + metadata
Category pills: inline badges
Upvote/reply: left indicators
```

**Chat:**
```
Bubbles: rounded-2xl max-w-md px-4 py-2
Own messages: justify-end
Others: justify-start
Timestamp: text-xs outside bubble
```

---

## Page Layouts

### Landing Page
**Hero:** `min-h-screen` centered, text-5xl font-bold headline, dual CTAs, floating stats overlay (10K+ Learners, 500+ Mentors)

**Features:** 3-col grid, icon-top cards (Heroicons), text-xl headings

**How It Works:** 3-step numbered flow, dotted connectors, alternating image/text (desktop), stacked (mobile)

**Social Proof:** 2-col testimonial grid with quotes + avatars + location tags

**Footer:** 4-col (About/Resources/Community/Legal) + newsletter + social icons

### Dashboard
**Layout:** w-64 sidebar + main area
- Sidebar: nav + user profile + streak
- Main: greeting header, 4-stat grid, current roadmap card, upcoming sessions, recommended resources carousel

### Roadmap
```
Timeline: vertical (mobile), horizontal Gantt (desktop)
Module cards: drag handles + checkbox + resources
Right sidebar: detail panel (slides in)
Sticky header: progress bar + "Request Mentor"
```

### Mentor Marketplace
```
Filter sidebar (desktop) / top bar (mobile)
3-col responsive grid
Sort: Top Rated/Most Available/Newest
```

### Profile
**Tabs:** Overview, Progress, Badges, Settings
- Overview: bio + skills + goals + GitHub widget
- Progress: timeline + certificates
- Badges: earned/locked grid
- Settings: preferences + notifications

---

## Images

**Hero:** Full-width African learners collaborating/coding, warm tones, authentic photography

**Features:** UI screenshots (roadmap/dashboard/progress) with device frames in How It Works section

**Avatars:** Profile photos, fallback: initials-based generated patterns

**Resources:** 16:9 video thumbnails + platform logos

**Badges:** Custom vector illustrations (Bronze/Silver/Gold tiers)

---

## Accessibility & Performance

**Touch Targets:** All interactive = min `h-11` (44px)

**Focus:** Visible ring on all focusable elements

**Semantic:** Proper heading hierarchy, nav/main/aside landmarks, alt text, aria-labels for icon buttons

**Keyboard:** Full support with logical tab order, skip-to-content link

**Loading:** Skeleton screens (no spinners), lazy load below-fold images (intersection observer)

**PWA:** Service worker for offline roadmaps, app shell caching

---

## Animation

**Principles:** Minimal, purposeful motion only

```
Page transitions: fade duration-200
Card hover: translate-y + shadow (transition-transform duration-200)
Button active: scale-95
Modal entry: slide-up + backdrop fade
Progress bars: smooth width transitions
```

**Avoid:** Auto-play, complex scroll effects, parallax (bandwidth considerations)

---

**Token Count:** ~1,950 tokens | All critical specs preserved for production implementation