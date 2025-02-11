from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

def get_lt_month_abbr(month):
    lt_months = {
        1: 'Sau',
        2: 'Vas',
        3: 'Kov',
        4: 'Bal',
        5: 'Geg',
        6: 'Bir',
        7: 'Lie',
        8: 'Rgp',
        9: 'Rgs',
        10: 'Spa',
        11: 'Lap',
        12: 'Grd'
    }
    return lt_months.get(month, '')

@register.filter
def lt_date(date):
    if not date:
        return ''
    return f"{get_lt_month_abbr(date.month)} {date.day}"

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