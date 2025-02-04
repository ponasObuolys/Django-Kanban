from .models import Team, TeamMembership, TeamInvitation

def is_team_admin(user, team):
    """Check if user is team admin"""
    return team.teammembership_set.filter(
        user=user,
        role='admin'
    ).exists()

def can_manage_team(user, team):
    """Check if user can manage (edit/delete) team"""
    return team.owner == user or is_team_admin(user, team)

def can_manage_members(user, team):
    """Check if user can manage team members"""
    return can_manage_team(user, team)

def can_send_invitations(user, team):
    """Check if user can send team invitations"""
    return can_manage_team(user, team)

def can_manage_invitation(user, invitation):
    """Check if user can manage (cancel) invitation"""
    return invitation.invited_by == user or can_manage_team(user, invitation.team)

def can_respond_to_invitation(user, invitation):
    """Check if user can respond to invitation"""
    return invitation.invited_user == user and invitation.status == 'pending'
