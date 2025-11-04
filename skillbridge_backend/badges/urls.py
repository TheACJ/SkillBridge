from django.urls import path
from . import views

urlpatterns = [
    path('', views.BadgeListView.as_view(), name='badge-list'),
    path('award/', views.award_badge, name='award-badge'),
]