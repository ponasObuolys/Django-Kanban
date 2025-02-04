from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Team
from ..forms import TeamForm
from ..services.team_service import TeamService
from ..permissions import can_manage_team

@login_required
def team_list(request):
    owned_teams, member_teams, join_dates = TeamService.get_user_teams(request.user)
    return render(request, 'teams/team_list.html', {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
        'join_dates': join_dates
    })

@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = TeamService.create_team(request.user, form.cleaned_data)
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
    
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this team.")
        return redirect('teams:team_list')
    
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'is_admin': team.is_admin(request.user)
    })

@login_required
def team_edit(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to edit this team.")
        return redirect('teams:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            TeamService.update_team(team, form.cleaned_data)
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
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to delete this team.")
        return redirect('teams:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        TeamService.delete_team(team)
        messages.success(request, 'Team deleted successfully.')
        return redirect('teams:team_list')
    
    return render(request, 'teams/team_confirm_delete.html', {
        'team': team
    })
