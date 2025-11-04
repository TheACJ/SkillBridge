from django.urls import path
from . import views

urlpatterns = [
    path('', views.RoadmapListCreateView.as_view(), name='roadmap-list-create'),
    path('<uuid:roadmap_id>/', views.RoadmapDetailView.as_view(), name='roadmap-detail'),
    path('generate/', views.generate_roadmap, name='generate-roadmap'),
    path('<uuid:roadmap_id>/progress/', views.update_roadmap_progress, name='update-roadmap-progress'),
]