from django.contrib import admin
from .models import Board, Column, Task, Label, TaskComment, TaskAttachment

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'team', 'created_at', 'updated_at')
    list_filter = ('created_at', 'team')
    search_fields = ('title', 'description', 'owner__username', 'team__name')
    date_hierarchy = 'created_at'

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'type', 'position')
    list_filter = ('type', 'board')
    search_fields = ('title', 'board__title')
    ordering = ('board', 'position')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'column', 'created_by', 'priority', 'due_date')
    list_filter = ('priority', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'created_by__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('labels', 'assigned_to')

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'color')
    list_filter = ('board',)
    search_fields = ('name', 'board__title')

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'task__title')
    date_hierarchy = 'created_at'

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('task__title', 'uploaded_by__username')
