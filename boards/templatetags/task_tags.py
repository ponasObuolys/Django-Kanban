from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.simple_tag
def get_due_date_class(task):
    if not task.due_date or task.column.title in ['DONE', 'REJECTED']:
        return ''
    
    now = timezone.now().date()
    due_date = task.due_date.date()
    days_until_due = (due_date - now).days
    
    if days_until_due < 0:
        return 'overdue'
    elif days_until_due == 0:
        return 'due-today'
    elif days_until_due == 1:
        return 'due-tomorrow'
    return '' 