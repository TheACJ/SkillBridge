from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.ForumPostListView.as_view(), name='forum-post-list'),
    path('posts/<uuid:post_id>/', views.ForumPostDetailView.as_view(), name='forum-post-detail'),
    path('posts/<uuid:post_id>/replies/', views.get_forum_replies, name='forum-replies'),
    path('categories/', views.get_categories, name='forum-categories'),
]