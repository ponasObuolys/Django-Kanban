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
    
    print(f"DEBUG: Užkraunamas komandos narių puslapis komandai {team_id}")
    print(f"DEBUG: Vartotojas: {request.user.username}")
    
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this team.")
        print("DEBUG: Vartotojas neturi prieigos prie komandos")
        return redirect('teams:team_list')
    
    members = TeamService.get_member_info(team)
    users = User.objects.exclude(id__in=team.members.values_list('id', flat=True))
    
    print("DEBUG: Vartotojai, kurie nėra komandos nariai:")
    for user in users:
        print(f"- {user.username} (ID: {user.id})")
    
    print(f"DEBUG: Iš viso ne narių: {users.count()}")
    print(f"DEBUG: Ar vartotojas yra administratorius: {can_manage_team(request.user, team)}")
    
    return render(request, 'teams/team_members.html', {
        'team': team,
        'members': members,
        'users': users,
        'available_users': users,  # Pridedame, kad atitiktų šablono kintamuosius
        'is_admin': can_manage_team(request.user, team)
    })

@login_required
def add_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    print(f"DEBUG: Bandoma pridėti narį į komandą {team_id}")
    print(f"DEBUG: Vartotojas: {request.user.username}")
    print(f"DEBUG: Ar vartotojas gali valdyti komandą: {can_manage_team(request.user, team)}")
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to add members.")
        print("DEBUG: Vartotojas neturi teisių pridėti narių")
        return redirect('teams:team_members', team_id=team.id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(f"DEBUG: POST duomenys: {request.POST}")
        print(f"DEBUG: Bandoma pridėti vartotoją ID: {user_id}")
        
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                messages.error(request, "You can't add yourself as a member.")
                print("DEBUG: Bandoma pridėti save")
            elif team.members.filter(id=user.id).exists():
                messages.error(request, "User is already a member of this team.")
                print("DEBUG: Vartotojas jau yra komandos narys")
            else:
                TeamService.add_member(team, user)
                messages.success(request, f'{user.username} added to the team.')
                print(f"DEBUG: Narys {user.username} sėkmingai pridėtas")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            print("DEBUG: Vartotojas nerastas")
        except Exception as e:
            print(f"DEBUG: Neapdorota klaida: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        print(f"DEBUG: Gautas {request.method} užklausos metodas, o ne POST")
    
    return redirect('teams:team_members', team_id=team.id)

@login_required
def remove_member(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(User, id=user_id)
    
    print(f"DEBUG: Bandoma pašalinti narį {user_id} iš komandos {team_id}")
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to remove members.")
        print("DEBUG: Vartotojas neturi teisių šalinti narių")
        return redirect('teams:team_members', team_id=team.id)
    
    if user == team.owner:
        messages.error(request, "You can't remove the team owner.")
        print("DEBUG: Bandoma pašalinti komandos savininką")
    else:
        try:
            membership = get_object_or_404(TeamMembership, team=team, user=user)
            TeamService.remove_member(membership, request.user)
            messages.success(request, f'{user.username} removed from the team.')
            print(f"DEBUG: Narys {user.username} sėkmingai pašalintas")
        except Exception as e:
            print(f"DEBUG: Klaida šalinant narį: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('teams:team_members', team_id=team.id)

@login_required
def change_member_role(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    user = get_object_or_404(User, id=user_id)
    
    print(f"DEBUG: Bandoma keisti nario {user_id} rolę komandoje {team_id}")
    
    if not can_manage_team(request.user, team):
        messages.error(request, "You don't have permission to change member roles.")
        print("DEBUG: Vartotojas neturi teisių keisti narių rolių")
        return redirect('teams:team_members', team_id=team.id)
    
    if user == team.owner:
        messages.error(request, "You can't change the team owner's role.")
        print("DEBUG: Bandoma keisti komandos savininko rolę")
    else:
        new_role = request.POST.get('role')
        print(f"DEBUG: Nauja rolė: {new_role}")
        
        if new_role in [role[0] for role in TeamMembership.ROLE_CHOICES]:
            try:
                membership = get_object_or_404(TeamMembership, team=team, user=user)
                TeamService.change_member_role(membership, new_role, request.user)
                messages.success(request, f"{user.username}'s role updated to {new_role}.")
                print(f"DEBUG: Nario {user.username} rolė sėkmingai pakeista į {new_role}")
            except Exception as e:
                print(f"DEBUG: Klaida keičiant rolę: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Invalid role specified.")
            print(f"DEBUG: Nurodyta neteisinga rolė: {new_role}")
    
    return redirect('teams:team_members', team_id=team.id)
