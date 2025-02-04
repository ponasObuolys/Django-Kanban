import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from teams.models import Team, TeamInvitation

User = get_user_model()

@pytest.mark.django_db
class TeamTests(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.third_user = User.objects.create_user(
            username='thirduser',
            email='third@example.com',
            password='testpass123'
        )

    def test_team_creation(self):
        """Test creating a new team"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        self.assertEqual(team.name, 'Test Team')
        self.assertEqual(team.owner, self.user)

    def test_team_member_addition(self):
        """Test adding members to a team"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        team.members.add(self.other_user)
        self.assertTrue(team.members.filter(id=self.other_user.id).exists())

    def test_team_invitation(self):
        """Test team invitation creation and acceptance"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        # Create invitation
        invitation = TeamInvitation.objects.create(
            team=team,
            invited_by=self.user,
            invited_user=self.other_user,
            status='pending'
        )
        self.assertEqual(invitation.status, 'pending')
        
        # Accept invitation
        invitation.status = 'accepted'
        invitation.save()
        team.members.add(self.other_user)
        self.assertTrue(team.members.filter(id=self.other_user.id).exists())

    def test_team_member_removal(self):
        """Test removing members from a team"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        team.members.add(self.other_user)
        self.assertTrue(team.members.filter(id=self.other_user.id).exists())
        
        team.members.remove(self.other_user)
        self.assertFalse(team.members.filter(id=self.other_user.id).exists())

    def test_team_multiple_members(self):
        """Test team with multiple members"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        team.members.add(self.other_user, self.third_user)
        self.assertEqual(team.members.count(), 2)  # not including owner

    def test_team_name_update(self):
        """Test updating team name"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        new_name = 'Updated Team Name'
        team.name = new_name
        team.save()
        self.assertEqual(team.name, new_name)

    def test_team_owner_permissions(self):
        """Test team owner special permissions"""
        team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        self.assertEqual(team.owner, self.user)
        # Add more specific permission tests based on your implementation
