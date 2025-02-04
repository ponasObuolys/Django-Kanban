from django.db import models
from notifications.models import AbstractNotification
from django.db.models import Index
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(AbstractNotification):
    # Override ForeignKey fields to add unique related_names
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='app_notifications',
        blank=False
    )
    actor_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_actor_app',
        blank=False
    )
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_target_app',
        blank=True,
        null=True
    )
    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notify_action_object_app',
        blank=True,
        null=True
    )

    class Meta(AbstractNotification.Meta):
        abstract = False
        indexes = [
            Index(fields=['recipient', 'unread']),
            Index(fields=['recipient', 'timestamp']),
        ]
        # Remove deprecated index_together 