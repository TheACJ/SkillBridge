from django.urls import path
from . import views

urlpatterns = [
    path('', views.MentorMatchListView.as_view(), name='match-list'),
    path('<uuid:match_id>/', views.MentorMatchDetailView.as_view(), name='match-detail'),
    path('create/', views.create_mentor_match, name='create-match'),
    path('<uuid:match_id>/chat/', views.send_match_message, name='send-message'),
    path('<uuid:match_id>/rate/', views.rate_mentor, name='rate-mentor'),
    path('mentor/<uuid:mentor_id>/reviews/', views.get_mentor_reviews, name='mentor-reviews'),
    path('history/', views.get_match_history, name='match-history'),
]