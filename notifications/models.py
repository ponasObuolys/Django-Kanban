from django.db import models
from notifications.base.models import AbstractNotification
from django.db.models import Index

class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        indexes = [
            Index(fields=['recipient', 'unread']),
            Index(fields=['recipient', 'timestamp']),
        ]
        # Remove deprecated index_together 