from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from ..models import Team, TeamInvitation
from ..services.invitation_service import InvitationService
from ..permissions import can_manage_team

User = get_user_model()

@login_required
def invitation_list(request):
    pending_invitations = InvitationService.get_user_invitations(request.user)
    return render(request, 'teams/invitation_list.html', {
        'invitations': pending_invitations
    })

@login_required
def send_invitation(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to send invitations.")
        return redirect('teams:team_members', team_id=team.id)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user == request.user:
                messages.error(request, "You can't invite yourself.")
            elif team.members.filter(id=user.id).exists():
                messages.error(request, "User is already a member of this team.")
            elif TeamInvitation.objects.filter(team=team, invitee=user, status='pending').exists():
                messages.error(request, "User already has a pending invitation.")
            else:
                InvitationService.send_invitation(team, request.user, user)
                messages.success(request, f'Invitation sent to {user.email}.')
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")
    
    return redirect('teams:team_members', team_id=team.id)

@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, invitee=request.user, status='pending')
    
    InvitationService.accept_invitation(invitation)
    messages.success(request, f'You have joined team {invitation.team.name}.')
    
    return redirect('teams:team_detail', team_id=invitation.team.id)

@login_required
def reject_invitation(request, invitation_id):
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, invitee=request.user, status='pending')
    
    InvitationService.reject_invitation(invitation)
    messages.success(request, f'You have declined the invitation to join team {invitation.team.name}.')
    
    return redirect('teams:invitation_list')

@login_required
def cancel_invitation(request, invitation_id):
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, status='pending')
    team = invitation.team
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to cancel invitations.")
        return redirect('teams:team_members', team_id=team.id)
    
    InvitationService.cancel_invitation(invitation)
    messages.success(request, f'Invitation to {invitation.invitee.email} has been cancelled.')
    
    return redirect('teams:team_members', team_id=team.id)
