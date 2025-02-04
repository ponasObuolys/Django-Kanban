from django.utils import timezone
from ..models import Team, TeamMembership
from notifications.signals import notify

class TeamService:
    @staticmethod
    def create_team(owner, data):
        """Create a new team and add owner as admin"""
        team = Team.objects.create(owner=owner, **data)
        
        # Add owner as team member with admin role
        TeamMembership.objects.create(
            team=team,
            user=owner,
            role='admin'
        )
        
        return team

    @staticmethod
    def update_team(team, data):
        """Update team with provided data"""
        for key, value in data.items():
            setattr(team, key, value)
        team.save()
        return team

    @staticmethod
    def get_user_teams(user):
        """Get all teams user is part of"""
        owned_teams = Team.objects.filter(owner=user)
        member_teams = Team.objects.filter(members=user).exclude(owner=user)
        
        # Get formatted join dates for member teams
        join_dates = TeamService.get_member_join_dates(user, member_teams)
        
        return owned_teams, member_teams, join_dates

    @staticmethod
    def get_member_info(team):
        """Get detailed member information for team"""
        return team.teammembership_set.all().select_related('user')

    @staticmethod
    def add_member(team, user, role='member'):
        """Add a new member to the team"""
        membership = TeamMembership.objects.create(
            team=team,
            user=user,
            role=role
        )
        
        # Notify the user
        notify.send(
            team.owner,
            recipient=user,
            verb='added you to',
            target=team,
            description=f'You have been added to team "{team.name}"'
        )
        
        return membership

    @staticmethod
    def change_member_role(membership, new_role, changed_by):
        """Change team member's role"""
        old_role = membership.role
        membership.role = new_role
        membership.save()
        
        # Notify the member
        if membership.user != changed_by:
            notify.send(
                changed_by,
                recipient=membership.user,
                verb='changed your role in',
                target=membership.team,
                description=f'Your role in team "{membership.team.name}" was changed from {old_role} to {new_role}'
            )

    @staticmethod
    def remove_member(membership, removed_by):
        """Remove member from team"""
        team = membership.team
        user = membership.user
        
        membership.delete()
        
        # Notify the member if they didn't remove themselves
        if user != removed_by:
            notify.send(
                removed_by,
                recipient=user,
                verb='removed you from',
                target=team,
                description=f'You have been removed from team "{team.name}"'
            )

    @staticmethod
    def get_member_join_dates(user, teams):
        """Get formatted join dates for teams"""
        memberships = TeamMembership.objects.filter(
            user=user,
            team__in=teams
        ).select_related('team')
        
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
        
        return join_dates
