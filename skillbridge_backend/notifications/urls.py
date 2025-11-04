from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<uuid:notification_id>/read/', views.mark_notification_read, name='mark-read'),
    path('unread/count/', views.get_unread_count, name='unread-count'),
]