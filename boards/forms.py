from django import forms
from .models import Board, Column, Task, Label, TaskComment, TaskAttachment
from django.db.models import Max, Q
from accounts.models import CustomUser
from django.contrib.auth.models import User

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
        fields = ['title', 'description', 'column', 'assigned_to', 'due_date', 'priority', 'labels']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'labels': forms.CheckboxSelectMultiple(),
            'column': forms.HiddenInput(),
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
            
            # Set initial position based on column's tasks
            if self.instance and not self.instance.pk and 'column' in self.data:
                try:
                    column = board.columns.get(id=self.data['column'])
                    self.instance.position = column.tasks.count()
                except (Column.DoesNotExist, ValueError):
                    pass
        
        self.fields['title'].required = True
        self.fields['priority'].required = True

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

class TaskAttachmentForm(forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        } 