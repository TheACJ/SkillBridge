from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProgressLogListView.as_view(), name='progress-list'),
    path('log/', views.log_progress, name='log-progress'),
    path('roadmap/<uuid:roadmap_id>/', views.get_roadmap_progress, name='roadmap-progress'),
    path('github/webhook/', views.github_webhook, name='github-webhook'),
    path('github/repositories/', views.get_user_repositories, name='user-repositories'),
]