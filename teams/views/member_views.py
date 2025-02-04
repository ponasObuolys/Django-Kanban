from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from ..models import Team, TeamMembership
from ..services.team_service import TeamService
from ..permissions import can_manage_team

User = get_user_model()

@login_required
def team_members(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this team.")
        return redirect('teams:team_list')
    
    members = TeamService.get_member_info(team)
    return render(request, 'teams/team_members.html', {
        'team': team,
        'members': members,
        'is_admin': can_manage_team(request.user, team)
    })

@login_required
def add_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to add members.")
        return redirect('teams:team_members', team_id=team.id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user == request.user:
                messages.error(request, "You can't add yourself as a member.")
            elif team.members.filter(id=user.id).exists():
                messages.error(request, "User is already a member of this team.")
            else:
                TeamService.add_member(team, user)
                messages.success(request, f'{user.username} added to the team.')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
    
    return redirect('teams:team_members', team_id=team.id)

@login_required
def remove_member(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(User, id=user_id)
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to remove members.")
        return redirect('teams:team_members', team_id=team.id)
    
    if user == team.owner:
        messages.error(request, "You can't remove the team owner.")
    else:
        TeamService.remove_member(team, user)
        messages.success(request, f'{user.username} removed from the team.')
    
    return redirect('teams:team_members', team_id=team.id)

@login_required
def change_member_role(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(User, id=user_id)
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to change member roles.")
        return redirect('teams:team_members', team_id=team.id)
    
    if user == team.owner:
        messages.error(request, "You can't change the team owner's role.")
    else:
        new_role = request.POST.get('role')
        if new_role in [role[0] for role in TeamMembership.ROLE_CHOICES]:
            TeamService.change_member_role(team, user, new_role)
            messages.success(request, f"{user.username}'s role updated to {new_role}.")
        else:
            messages.error(request, "Invalid role specified.")
    
    return redirect('teams:team_members', team_id=team.id)
