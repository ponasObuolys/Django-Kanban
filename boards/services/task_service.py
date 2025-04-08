from django.db.models import Max
from django.utils import timezone
from ..models import Task, TaskComment, TaskAttachment
from notifications.signals import notify

class TaskService:
    @staticmethod
    def create_task(column, data, user):
        """Create a new task in the specified column"""
        # Get the next position
        max_position = column.tasks.aggregate(Max('position'))['position__max']
        position = (max_position or 0) + 1
        
        # Išsaugome žymes ir priskirtus vartotojus atskirai
        labels = data.pop('labels', None)
        assigned_users = data.pop('assigned_to', None)
        
        # Create the task
        task = Task.objects.create(
            column=column,
            position=position,
            created_by=user,
            **data
        )
        
        # Jei yra žymių, priskiriame jas
        if labels is not None:
            task.labels.set(labels)
        
        # Jei yra priskirtų vartotojų, priskiriame juos
        if assigned_users is not None:
            task.assigned_to.set(assigned_users)
        
        return task

    @staticmethod
    def update_task(task, data):
        """Update task with provided data"""
        # Išsaugome žymes ir priskirtus vartotojus atskirai
        labels = data.pop('labels', None)
        assigned_users = data.pop('assigned_to', None)
        
        # Atnaujiname kitus laukus
        for key, value in data.items():
            setattr(task, key, value)
        task.save()
        
        # Jei yra žymių, atnaujiname jas naudodami set() metodą
        if labels is not None:
            task.labels.set(labels)
        
        # Jei yra priskirtų vartotojų, atnaujiname juos
        if assigned_users is not None:
            task.assigned_to.set(assigned_users)
        
        return task

    @staticmethod
    def add_comment(task, user, content):
        """Add a comment to the task"""
        comment = TaskComment.objects.create(
            task=task,
            author=user,
            content=content
        )
        
        # Notify task assignees and creator
        recipients = set(task.assigned_to.all()) | {task.created_by} - {user, None}
        for recipient in recipients:
            notify.send(
                user,
                recipient=recipient,
                verb='commented on',
                target=task,
                description=f'New comment on task "{task.title}"'
            )
        
        return comment

    @staticmethod
    def add_attachment(task, user, file):
        """Add an attachment to the task"""
        attachment = TaskAttachment.objects.create(
            task=task,
            file=file,
            uploaded_by=user
        )
        
        # Notify task assignees and creator
        recipients = set(task.assigned_to.all()) | {task.created_by} - {user, None}
        for recipient in recipients:
            notify.send(
                user,
                recipient=recipient,
                verb='added attachment to',
                target=task,
                description=f'New attachment added to task "{task.title}"'
            )
        
        return attachment

    @staticmethod
    def update_position(task, new_column, new_position):
        """Update task position and/or column"""
        old_column = task.column
        task.column = new_column
        task.position = new_position
        task.save()
        
        # If moved to Done column, set completed date
        if new_column.type == 'done' and old_column.type != 'done':
            task.completed_at = timezone.now()
            task.save()
        # If moved from Done column, clear completed date
        elif new_column.type != 'done' and old_column.type == 'done':
            task.completed_at = None
            task.save()
