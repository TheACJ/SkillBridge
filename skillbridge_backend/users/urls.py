from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),

    # User management
    path('me/', views.UserProfileView.as_view(), name='user-profile'),
    path('mentors/', views.MentorListView.as_view(), name='mentor-list'),
]