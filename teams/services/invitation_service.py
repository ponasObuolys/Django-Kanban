from django.utils import timezone
from ..models import TeamInvitation, TeamMembership
from notifications.signals import notify

class InvitationService:
    @staticmethod
    def create_invitation(team, invited_user, invited_by):
        """Create a new team invitation"""
        # Check if user is already a member
        if team.members.filter(id=invited_user.id).exists():
            raise ValueError('User is already a member of this team.')
        
        # Check for existing pending invitation
        if TeamInvitation.objects.filter(
            team=team,
            invited_user=invited_user,
            status='pending'
        ).exists():
            raise ValueError('User already has a pending invitation.')
        
        invitation = TeamInvitation.objects.create(
            team=team,
            invited_user=invited_user,
            invited_by=invited_by
        )
        
        # Send notification to invited user
        notify.send(
            invited_by,
            recipient=invited_user,
            verb='invited you to join',
            target=team,
            description=f'You have been invited to join team "{team.name}"'
        )
        
        return invitation

    @staticmethod
    def accept_invitation(invitation, user):
        """Accept a team invitation"""
        if invitation.invited_user != user:
            raise ValueError('You cannot accept this invitation.')
        
        if invitation.status != 'pending':
            raise ValueError('This invitation is no longer pending.')
        
        invitation.status = 'accepted'
        invitation.response_date = timezone.now()
        invitation.save()
        
        # Add user to team
        TeamMembership.objects.create(
            team=invitation.team,
            user=user,
            role='member'
        )
        
        # Notify team owner
        notify.send(
            user,
            recipient=invitation.team.owner,
            verb='accepted invitation to',
            target=invitation.team,
            description=f'{user.username} has joined team "{invitation.team.name}"'
        )

    @staticmethod
    def reject_invitation(invitation, user):
        """Reject a team invitation"""
        if invitation.invited_user != user:
            raise ValueError('You cannot reject this invitation.')
        
        if invitation.status != 'pending':
            raise ValueError('This invitation is no longer pending.')
        
        invitation.status = 'rejected'
        invitation.response_date = timezone.now()
        invitation.save()
        
        # Notify team owner
        notify.send(
            user,
            recipient=invitation.team.owner,
            verb='rejected invitation to',
            target=invitation.team,
            description=f'{user.username} has declined to join team "{invitation.team.name}"'
        )

    @staticmethod
    def cancel_invitation(invitation):
        """Cancel a pending invitation"""
        if invitation.status != 'pending':
            raise ValueError('This invitation is no longer pending.')
        
        invitation.status = 'cancelled'
        invitation.response_date = timezone.now()
        invitation.save()
        
        # Notify invited user
        notify.send(
            invitation.invited_by,
            recipient=invitation.invited_user,
            verb='cancelled invitation to',
            target=invitation.team,
            description=f'Your invitation to join team "{invitation.team.name}" has been cancelled'
        )

    @staticmethod
    def get_user_invitations(user):
        """Get all invitations related to user"""
        sent_invitations = TeamInvitation.objects.filter(
            invited_by=user
        ).select_related('team', 'invited_user')
        
        received_invitations = TeamInvitation.objects.filter(
            invited_user=user
        ).select_related('team', 'invited_by')
        
        return sent_invitations, received_invitations
