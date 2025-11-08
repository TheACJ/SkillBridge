from django.urls import path
from . import views

urlpatterns = [
    path('', views.RoadmapListCreateView.as_view(), name='roadmap-list-create'),
    path('<uuid:pk>/', views.RoadmapDetailView.as_view(), name='roadmap-detail'),
    path('generate/', views.generate_roadmap, name='generate-roadmap'),
    path('<uuid:pk>/progress/', views.update_roadmap_progress, name='update-roadmap-progress'),
    path('<uuid:pk>/share/', views.share_roadmap, name='share-roadmap'),
    path('<uuid:pk>/duplicate/', views.duplicate_roadmap, name='duplicate-roadmap'),
    path('<uuid:pk>/analytics/', views.get_roadmap_analytics, name='roadmap-analytics'),
    path('shared/<uuid:token>/', views.get_shared_roadmap, name='shared-roadmap'),
]