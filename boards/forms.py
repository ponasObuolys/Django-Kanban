from django import forms
from .models import Board, Column, Task, Label, TaskComment, TaskAttachment

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
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'column', 'assigned_to',
                 'due_date', 'priority', 'labels']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'labels': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.column:
            self.fields['labels'].queryset = self.instance.column.board.labels.all()

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