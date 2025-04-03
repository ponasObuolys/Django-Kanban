from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark_all_as_read'),
    path('get-count/', views.get_count, name='get_count'),
    path('get-list/', views.get_list, name='get_list'),
    path('test/', views.test_notification, name='test_notification'),
    path('test-page/', views.test_page, name='test_page'),
] 