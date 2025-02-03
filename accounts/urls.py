from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings_view'),
    path('settings/profile/update/', views.update_profile, name='update_profile'),
    path('settings/password/update/', views.update_password, name='update_password'),
    path('settings/notifications/update/', views.update_notifications, name='update_notifications'),
    path('settings/theme/update/', views.update_theme, name='update_theme'),
] 