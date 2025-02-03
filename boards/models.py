from django.db import models
from django.conf import settings
from colorfield.fields import ColorField
from teams.models import Team

class Board(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='boards',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.title

class Column(models.Model):
    COLUMN_TYPES = [
        ('todo', 'To Do'),
        ('doing', 'Doing'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
    ]
    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=COLUMN_TYPES)
    position = models.PositiveIntegerField()
    color = ColorField(default='#FF0000')
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.board.title} - {self.title}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    position = models.PositiveIntegerField()
    labels = models.ManyToManyField('Label', blank=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return self.title

class Label(models.Model):
    name = models.CharField(max_length=50)
    color = ColorField(default='#FF0000')
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='labels')
    
    def __str__(self):
        return self.name

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.task.title}"
