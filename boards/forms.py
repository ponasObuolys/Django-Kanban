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
            'column': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['column'].required = True
        
        # Get the column from either the instance or initial data
        column = None
        if self.instance and self.instance.column:
            column = self.instance.column
        elif self.initial and 'column' in self.initial:
            try:
                column = Column.objects.get(id=self.initial['column'])
            except Column.DoesNotExist:
                pass
        
        # Set labels queryset based on the column's board
        if column:
            self.fields['labels'].queryset = column.board.labels.all()
        else:
            self.fields['labels'].queryset = Label.objects.none()
    
    def clean_column(self):
        column = self.cleaned_data.get('column')
        if not column:
            raise forms.ValidationError('Column is required.')
        return column
    
    def clean(self):
        cleaned_data = super().clean()
        column = cleaned_data.get('column')
        labels = cleaned_data.get('labels')
        
        # Validate that selected labels belong to the board
        if column and labels:
            valid_label_ids = set(column.board.labels.values_list('id', flat=True))
            selected_label_ids = set(label.id for label in labels)
            invalid_labels = selected_label_ids - valid_label_ids
            
            if invalid_labels:
                raise forms.ValidationError('Some selected labels do not belong to this board.')

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