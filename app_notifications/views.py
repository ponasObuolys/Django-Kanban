from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from notifications.models import Notification

@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def mark_all_notifications_as_read(request):
    request.user.notifications.unread().mark_all_as_read()
    return JsonResponse({'status': 'success'})

@login_required
def get_count(request):
    """Grąžina neperskaitytų pranešimų skaičių JSON formatu."""
    count = request.user.notifications.unread().count()
    return JsonResponse({'count': count})

@login_required
def get_list(request):
    """Grąžina neperšakitytų pranešimų sąrašą HTML formatu, įterptą į JSON atsakymą."""
    # Gauname neperskaitytus pranešimus
    notifications = request.user.notifications.unread()
    
    # Sugeneruojame HTML
    html = render_to_string('app_notifications/notification_list.html', {
        'notifications': notifications
    }, request=request)
    
    return JsonResponse({'html': html}) 