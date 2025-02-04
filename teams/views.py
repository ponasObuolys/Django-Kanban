from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership, TeamInvitation
from .forms import TeamForm, TeamInvitationForm
from notifications.signals import notify

User = get_user_model()

@login_required
def team_list(request):
    owned_teams = Team.objects.filter(owner=request.user)
    member_teams = Team.objects.filter(members=request.user).exclude(owner=request.user)
    pending_invitations = TeamInvitation.objects.filter(
        invited_user=request.user,
        status='pending'
    )
    
    # Get membership info for each team
    memberships = TeamMembership.objects.filter(user=request.user).select_related('team')
    
    # Create a dictionary of team_id: formatted_date
    join_dates = {}
    for membership in memberships:
        time_diff = timezone.now() - membership.joined_at
        days = time_diff.days
        if days < 1:
            join_dates[membership.team_id] = 'today'
        elif days == 1:
            join_dates[membership.team_id] = 'yesterday'
        else:
            join_dates[membership.team_id] = f'{days} days ago'
    
    return render(request, 'teams/team_list.html', {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
        'pending_invitations': pending_invitations,
        'join_dates': join_dates
    })

@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            
            # Add owner as team member with admin role
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role='admin'
            )
            
            messages.success(request, 'Team created successfully.')
            return redirect('teams:team_detail', team_id=team.id)
    else:
        form = TeamForm()
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'title': 'Create Team'
    })

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is a member of the team
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this team.")
        return redirect('teams:team_list')
    
    members = team.teammembership_set.all()
    pending_invitations = team.invitations.filter(status='pending')
    
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'pending_invitations': pending_invitations,
        'is_admin': team.teammembership_set.get(user=request.user).role == 'admin'
    })

@login_required
def team_edit(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is team admin
    if not team.teammembership_set.filter(user=request.user, role='admin').exists():
        messages.error(request, "You don't have permission to edit this team.")
        return redirect('teams:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team updated successfully.')
            return redirect('teams:team_detail', team_id=team.id)
    else:
        form = TeamForm(instance=team)
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'team': team,
        'title': 'Edit Team'
    })

@login_required
def team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if team.owner != request.user:
        messages.error(request, "You don't have permission to delete this team.")
        return redirect('teams:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        team.delete()
        messages.success(request, 'Team deleted successfully.')
        return redirect('teams:team_list')
    
    return render(request, 'teams/team_confirm_delete.html', {
        'team': team
    })

@login_required
def invitation_list(request):
    # Get invitations sent by the user
    sent_invitations = TeamInvitation.objects.filter(
        invited_by=request.user
    ).select_related('team', 'invited_user')
    
    # Get invitations received by the user
    received_invitations = TeamInvitation.objects.filter(
        invited_user=request.user
    ).select_related('team', 'invited_by')
    
    return render(request, 'teams/invitation_list.html', {
        'sent_invitations': sent_invitations,
        'received_invitations': received_invitations
    })

@login_required
def send_invitation(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is team admin
    if not team.teammembership_set.filter(user=request.user, role='admin').exists():
        messages.error(request, "You don't have permission to send invitations.")
        return redirect('teams:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        form = TeamInvitationForm(request.POST, team=team)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.team = team
            invitation.invited_by = request.user
            
            # Check if user is already a member
            if team.members.filter(id=invitation.invited_user.id).exists():
                messages.error(request, 'User is already a member of this team.')
                return redirect('teams:team_detail', team_id=team.id)
            
            # Check for existing pending invitation
            if TeamInvitation.objects.filter(
                team=team,
                invited_user=invitation.invited_user,
                status='pending'
            ).exists():
                messages.error(request, 'User already has a pending invitation.')
                return redirect('teams:team_detail', team_id=team.id)
            
            invitation.save()
            
            # Send notification to invited user
            notify.send(
                request.user,
                recipient=invitation.invited_user,
                verb='invited you to join',
                target=team,
                description=f'You have been invited to join team "{team.name}"'
            )
            
            messages.success(request, 'Invitation sent successfully.')
            return redirect('teams:team_detail', team_id=team.id)
    else:
        form = TeamInvitationForm(team=team)
    
    return render(request, 'teams/invitation_form.html', {
        'form': form,
        'team': team
    })

@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        invited_user=request.user,
        status='pending'
    )
    
    invitation.status = 'accepted'
    invitation.response_date = timezone.now()
    invitation.save()
    
    # Add user to team
    TeamMembership.objects.create(
        team=invitation.team,
        user=request.user,
        role='member'
    )
    
    # Notify team owner
    notify.send(
        request.user,
        recipient=invitation.team.owner,
        verb='accepted invitation to',
        target=invitation.team,
        description=f'{request.user.username} has joined team "{invitation.team.name}"'
    )
    
    messages.success(request, f'You have joined team "{invitation.team.name}".')
    return redirect('teams:team_detail', team_id=invitation.team.id)

@login_required
def reject_invitation(request, invitation_id):
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        invited_user=request.user,
        status='pending'
    )
    
    invitation.status = 'rejected'
    invitation.response_date = timezone.now()
    invitation.save()
    
    # Notify team owner
    notify.send(
        request.user,
        recipient=invitation.team.owner,
        verb='rejected invitation to',
        target=invitation.team,
        description=f'{request.user.username} has declined to join team "{invitation.team.name}"'
    )
    
    messages.success(request, 'Invitation rejected.')
    return redirect('teams:invitation_list')

@login_required
def cancel_invitation(request, invitation_id):
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        invited_by=request.user,
        status='pending'
    )
    
    invitation.delete()
    
    # Notify invited user
    notify.send(
        request.user,
        recipient=invitation.invited_user,
        verb='cancelled invitation to',
        target=invitation.team,
        description=f'Invitation to join team "{invitation.team.name}" has been cancelled'
    )
    
    messages.success(request, 'Invitation cancelled successfully.')
    return redirect('teams:invitation_list')

@login_required
def team_members(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this team.")
        return redirect('teams:team_list')
    
    members = team.teammembership_set.all().select_related('user')
    
    return render(request, 'teams/team_members.html', {
        'team': team,
        'members': members,
        'is_admin': team.teammembership_set.get(user=request.user).role == 'admin'
    })

@login_required
def change_member_role(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is team admin
    if not team.teammembership_set.filter(user=request.user, role='admin').exists():
        messages.error(request, "You don't have permission to change member roles.")
        return redirect('teams:team_members', team_id=team.id)
    
    membership = get_object_or_404(TeamMembership, team=team, user_id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['member', 'admin']:
            # Prevent removing the last admin
            if new_role == 'member' and membership.role == 'admin':
                admin_count = team.teammembership_set.filter(role='admin').count()
                if admin_count <= 1:
                    messages.error(request, "Cannot remove the last admin.")
                    return redirect('teams:team_members', team_id=team.id)
            
            membership.role = new_role
            membership.save()
            messages.success(request, f"Member role updated to {new_role}.")
        
    return redirect('teams:team_members', team_id=team.id)

@login_required
def add_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user is team admin
    if not team.teammembership_set.filter(user=request.user, role='admin').exists():
        messages.error(request, "You don't have permission to add members.")
        return redirect('teams:team_members', team_id=team.id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(User, id=user_id)
            
            # Check if user is already a member
            if team.members.filter(id=user.id).exists():
                messages.error(request, 'User is already a member of this team.')
                return redirect('teams:team_members', team_id=team.id)
            
            # Add user to team
            TeamMembership.objects.create(
                team=team,
                user=user,
                role='member'
            )
            
            # Notify added user
            notify.send(
                request.user,
                recipient=user,
                verb='added you to',
                target=team,
                description=f'You have been added to team "{team.name}"'
            )
            
            messages.success(request, f'{user.username} has been added to the team.')
        
    return redirect('teams:team_members', team_id=team.id)

@login_required
def remove_member(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Check if user is team admin
    if not team.teammembership_set.filter(user=request.user, role='admin').exists():
        messages.error(request, "You don't have permission to remove members.")
        return redirect('teams:team_members', team_id=team.id)
    
    # Prevent removing the team owner
    if user_to_remove == team.owner:
        messages.error(request, "Cannot remove the team owner.")
        return redirect('teams:team_members', team_id=team.id)
    
    membership = get_object_or_404(TeamMembership, team=team, user=user_to_remove)
    
    # Prevent removing the last admin
    if membership.role == 'admin':
        admin_count = team.teammembership_set.filter(role='admin').count()
        if admin_count <= 1:
            messages.error(request, "Cannot remove the last admin.")
            return redirect('teams:team_members', team_id=team.id)
    
    membership.delete()
    
    # Notify removed user
    notify.send(
        request.user,
        recipient=user_to_remove,
        verb='removed you from',
        target=team,
        description=f'You have been removed from team "{team.name}"'
    )
    
    messages.success(request, f'{user_to_remove.username} has been removed from the team.')
    return redirect('teams:team_members', team_id=team.id)
