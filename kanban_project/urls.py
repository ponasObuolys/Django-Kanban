"""
URL configuration for kanban_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.views.generic import TemplateView, RedirectView
from accounts.views import CustomSignupView
from app_notifications.views import test_page, test_notification

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('notifications/test-page/', test_page, name='test_page'),
    path('notifications/test/', test_notification, name='test_notification'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),  # django-allauth URLs
    path('accounts/', include('accounts.urls')),  # Your custom profile views
    path('boards/', include('boards.urls')),
    path('teams/', include('teams.urls')),
    path('notifications/', include('app_notifications.urls', namespace='notifications')),
    path('docs/', include('docs.urls')),  # Documentation URLs
    prefix_default_language=True
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
