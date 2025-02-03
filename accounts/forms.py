from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser

class CustomUserChangeForm(UserChangeForm):
    password = None  # Remove password field from the form
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'avatar', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class NotificationPreferencesForm(forms.ModelForm):
    email_notifications = forms.BooleanField(required=False)
    task_assignments = forms.BooleanField(required=False)
    task_updates = forms.BooleanField(required=False)
    team_invitations = forms.BooleanField(required=False)
    board_updates = forms.BooleanField(required=False)
    
    class Meta:
        model = CustomUser
        fields = []  # No direct model fields
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values from the JSON field
        if self.instance.notification_preferences:
            for key, value in self.instance.notification_preferences.items():
                if key in self.fields:
                    self.fields[key].initial = value
        else:
            # Set default values if no preferences exist
            default_preferences = {
                'email_notifications': True,
                'task_assignments': True,
                'task_updates': True,
                'team_invitations': True,
                'board_updates': True
            }
            for key, value in default_preferences.items():
                self.fields[key].initial = value
    
    def save(self, commit=True):
        # Save preferences to the JSON field
        self.instance.notification_preferences = {
            'email_notifications': self.cleaned_data.get('email_notifications', True),
            'task_assignments': self.cleaned_data.get('task_assignments', True),
            'task_updates': self.cleaned_data.get('task_updates', True),
            'team_invitations': self.cleaned_data.get('team_invitations', True),
            'board_updates': self.cleaned_data.get('board_updates', True)
        }
        return super().save(commit=commit)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(
        help_text='Required. 150 characters or fewer. Letters, numbers and @/./+/-/_ only - no spaces allowed.'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user 