# SkillBridge - Learning Platform

A comprehensive learning platform that connects learners with mentors to accelerate skill development through personalized roadmaps, community interaction, and progress tracking.

## 🚀 Features

### Core Functionality
- **Personalized Learning Roadmaps**: AI-generated learning paths based on user goals and experience
- **Mentor Matching**: Connect with experienced developers for guidance
- **Community Forum**: Share knowledge and learn from peers
- **Progress Analytics**: Detailed insights into learning journey
- **Multi-language Support**: Available in English, Spanish, French, and German

### User Experience
- **Progressive Web App (PWA)**: Installable, offline-capable application
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Real-time Notifications**: Stay updated with learning activities
- **Offline Support**: Continue learning without internet connection
- **Error Boundaries**: Graceful error handling and recovery

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter for client-side routing
- **State Management**: TanStack Query for server state, React Query for caching
- **UI Components**: Radix UI primitives with Tailwind CSS
- **Styling**: Tailwind CSS with custom design system
- **Internationalization**: i18next with language detection
- **PWA**: Vite PWA plugin with service worker

### Backend (Django REST Framework)
- **Framework**: Django 4.x with Django REST Framework
- **Database**: PostgreSQL with Django ORM
- **Authentication**: JWT tokens with refresh mechanism
- **API**: RESTful API with OpenAPI documentation
- **Background Tasks**: Celery with Redis
- **Monitoring**: Prometheus and Grafana

## 📁 Project Structure

```
SkillBridge/
├── client/                          # React frontend
│   ├── public/                      # Static assets
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Page components
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── lib/                     # Utilities and configurations
│   │   └── types/                   # TypeScript type definitions
│   ├── e2e/                         # End-to-end tests
│   ├── vite.config.ts              # Vite configuration
│   └── package.json
├── skillbridge_backend/             # Django backend
│   ├── skillbridge_backend/         # Main Django project
│   ├── users/                       # User management app
│   ├── roadmaps/                    # Learning roadmaps app
│   ├── notifications/               # Notification system
│   ├── progress/                    # Progress tracking
│   └── requirements.txt
├── shared/                          # Shared types/schemas
└── docs/                           # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 13+
- Redis (for background tasks)

### Frontend Setup

```bash
cd client
npm install
npm run dev
```

### Backend Setup

```bash
cd skillbridge_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Environment Variables

Create `.env` files in both `client/` and `skillbridge_backend/` directories:

**Frontend (.env):**
```env
VITE_DJANGO_API_URL=http://localhost:8000/api/v1
```

**Backend (.env):**
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/skillbridge
REDIS_URL=redis://localhost:6379
```

## 🧪 Testing

### Frontend Tests
```bash
cd client
npm run test          # Unit tests
npm run test:e2e      # End-to-end tests
npm run test:e2e:ui   # E2E tests with UI
```

### Backend Tests
```bash
cd skillbridge_backend
python manage.py test
```

## 📱 Progressive Web App

SkillBridge is a PWA that can be installed on devices:

1. **Install**: Click "Install" when prompted by the browser
2. **Offline Access**: Core functionality works without internet
3. **Background Sync**: Data syncs when connection is restored
4. **Push Notifications**: Receive updates even when app is closed

## 🌐 Internationalization

The app supports multiple languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)

Language is automatically detected from browser settings and can be changed in Settings.

## 🔧 Available Scripts

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run unit tests
- `npm run test:e2e` - Run E2E tests

### Backend
- `python manage.py runserver` - Start development server
- `python manage.py test` - Run tests
- `python manage.py migrate` - Apply database migrations
- `celery -A skillbridge_backend worker` - Start Celery worker

## 🚢 Deployment

### Frontend
```bash
npm run build
# Deploy dist/ folder to static hosting (Vercel, Netlify, etc.)
```

### Backend
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

- **Frontend**: Error tracking with error boundaries
- **Backend**: Prometheus metrics, Grafana dashboards
- **Database**: Query performance monitoring
- **Infrastructure**: Health checks and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- React and TypeScript communities
- Django and DRF communities
- All contributors and users

## 📞 Support

For support, email support@skillbridge.com or join our Discord community.

---

**SkillBridge** - Accelerate your learning journey with personalized mentorship and community support.