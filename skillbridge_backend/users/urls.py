from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('refresh-token/', views.refresh_token, name='refresh-token'),
    path('password/reset/', views.request_password_reset, name='request-password-reset'),
    path('password/reset/confirm/', views.reset_password, name='reset-password'),

    # User management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('mentors/', views.MentorListView.as_view(), name='mentor-list'),
    path('statistics/', views.get_user_statistics, name='user-statistics'),
]