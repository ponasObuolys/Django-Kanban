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
        widgets = {
            'invited_user': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select a user to invite'
            })
        }
    
    def __init__(self, *args, team=None, **kwargs):
        super().__init__(*args, **kwargs)
        if team:
            # Exclude team owner, existing members, and users with empty usernames
            existing_members = team.members.all()
            self.fields['invited_user'].queryset = User.objects.filter(
                is_active=True
            ).exclude(
                id__in=existing_members.values_list('id', flat=True)
            ).exclude(
                id=team.owner.id
            ).exclude(
                username=''
            ).order_by('username')
        else:
            self.fields['invited_user'].queryset = User.objects.filter(
                is_active=True
            ).exclude(
                username=''
            ).order_by('username')
            
        self.fields['invited_user'].empty_label = None 