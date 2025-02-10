from django import forms
from .models import Board, Column, Task, Label, TaskComment, TaskAttachment
from django.db.models import Max, Q
from accounts.models import CustomUser
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description', 'team']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['title', 'type', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'column', 'assigned_to', 'due_date', 'priority', 'labels', 'position']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'labels': forms.CheckboxSelectMultiple(),
            'column': forms.HiddenInput(),
            'position': forms.HiddenInput(),
        }
    
    def __init__(self, *args, board=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.board = board
        self.user = user
        
        if board:
            # Filter columns to only those belonging to this board
            self.fields['column'].queryset = board.columns.all()
            # Filter labels to only those belonging to this board
            self.fields['labels'].queryset = board.labels.all()
            
            # Filter assigned_to based on board type
            if board.team:
                self.fields['assigned_to'].queryset = board.team.members.all()
            else:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                    id__in=[board.owner.id, self.user.id] if self.user else [board.owner.id]
                ).distinct()
        
        self.fields['title'].required = True
        self.fields['priority'].required = True
        self.fields['position'].required = True  # Make position required

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set position if this is a new task and position is not provided
        if not instance.pk and not instance.position and instance.column:
            # Get the highest position in the column and add 1
            max_position = instance.column.tasks.aggregate(models.Max('position'))['position__max']
            instance.position = (max_position or -1) + 1
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...'}),
        }

def validate_file_type(value):
    if value.content_type not in settings.ALLOWED_UPLOAD_TYPES:
        raise ValidationError('File type not supported. Allowed types are: ' + 
                            ', '.join(settings.ALLOWED_UPLOAD_TYPES))

def validate_file_size(value):
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f'Please keep filesize under {filesizeformat(settings.MAX_UPLOAD_SIZE)}. ' +
                            f'Current filesize {filesizeformat(value.size)}')

class TaskAttachmentForm(forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            validate_file_type(file)
            validate_file_size(file)
        return file 