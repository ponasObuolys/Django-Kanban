from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from notifications.models import Notification
import logging
from django.utils import timezone

# Sukuriame logerį
logger = logging.getLogger(__name__)

@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_notifications_as_read(request):
    """Pažymi visus vartotojo neperskaitytus pranešimus kaip perskaitytus."""
    try:
        # Gaukime neperskaitytų pranešimų skaičių prieš juos pažymint
        unread_count = request.user.notifications.unread().count()
        
        # Pažymime visus kaip perskaitytus 
        request.user.notifications.unread().mark_all_as_read()
        
        # Užregistruojame veiksmą žurnale
        logger.debug(f"Vartotojas {request.user.username} pažymėjo visus {unread_count} pranešimus kaip perskaitytus")
        
        return JsonResponse({
            'status': 'success',
            'marked_count': unread_count,
            'message': 'Visi pranešimai pažymėti kaip perskaityti'
        })
    except Exception as e:
        logger.error(f"Klaida žymint pranešimus kaip perskaitytus: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Įvyko klaida žymint pranešimus kaip perskaitytus'
        }, status=500)

@login_required
def get_count(request):
    """Grąžina neperskaitytų pranešimų skaičių JSON formatu."""
    # Derinimo informacija
    count = request.user.notifications.unread().count()
    logger.debug(f"Vartotojas: {request.user.username}, Neperskaitytų pranešimų: {count}")
    
    # Papildoma informacija derinimui
    if count > 0:
        notifications = request.user.notifications.unread()
        for i, notif in enumerate(notifications):
            logger.debug(f"Pranešimas {i+1}: ID={notif.id}, Aprašymas={notif.description}, Veiksmažodis={notif.verb}")
    
    return JsonResponse({'count': count})

@login_required
def get_list(request):
    """Grąžina neperšakitytų pranešimų sąrašą HTML formatu, įterptą į JSON atsakymą."""
    # Gauname neperskaitytus pranešimus
    notifications = request.user.notifications.unread()
    
    # Derinimo informacija
    logger.debug(f"get_list: Vartotojas: {request.user.username}, Neperskaitytų pranešimų: {notifications.count()}")
    
    # Sugeneruojame HTML
    html = render_to_string('app_notifications/notification_list.html', {
        'notifications': notifications
    }, request=request)
    
    return JsonResponse({'html': html})

# Papildome nauju testavimo endpointu
@login_required
def test_notification(request):
    """Sukuria testavimo pranešimą ir grąžina respone."""
    from notifications.signals import notify
    
    # Sukuriame testavimo pranešimą
    notify.send(
        sender=request.user,
        recipient=request.user,
        verb='assigned you',
        description=f'Testinis pranešimas (laikas: {timezone.now().strftime("%H:%M:%S")})'
    )
    
    # Gauname naują skaičių 
    count = request.user.notifications.unread().count()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Testinis pranešimas sukurtas sėkmingai',
        'count': count
    })

@login_required
def test_page(request):
    """Atvaizduoja testo puslapį, skirtą pranešimų funkcionalumo testavimui."""
    return render(request, 'app_notifications/test.html') 