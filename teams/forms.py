from django import forms
from django.contrib.auth import get_user_model
from .models import Team, TeamInvitation

User = get_user_model()

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TeamInvitationForm(forms.ModelForm):
    class Meta:
        model = TeamInvitation
        fields = ['invited_user']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invited_user'].queryset = User.objects.filter(is_active=True)
        self.fields['invited_user'].widget.attrs.update({
            'class': 'form-control select2',
            'data-placeholder': 'Select a user to invite'
        }) 