from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
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