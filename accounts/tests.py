import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError

User = get_user_model()

@pytest.mark.django_db
class AccountTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test creating a new user"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertTrue(isinstance(new_user, User))
        self.assertEqual(new_user.email, 'new@example.com')

    def test_user_authentication(self):
        """Test user authentication"""
        self.assertTrue(
            self.client.login(
                username=self.user_data['username'],
                password=self.user_data['password']
            )
        )

    def test_user_profile_update(self):
        """Test updating user profile"""
        self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        update_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'updated@example.com'
        }
        
        self.user.first_name = update_data['first_name']
        self.user.last_name = update_data['last_name']
        self.user.email = update_data['email']
        self.user.save()
        
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, update_data['first_name'])
        self.assertEqual(updated_user.last_name, update_data['last_name'])
        self.assertEqual(updated_user.email, update_data['email'])

    def test_password_change(self):
        """Test password change functionality"""
        self.client.login(
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        new_password = 'newpassword123'
        self.user.set_password(new_password)
        self.user.save()
        
        # Verify old password doesn't work
        self.assertFalse(
            self.client.login(
                username=self.user_data['username'],
                password=self.user_data['password']
            )
        )
        
        # Verify new password works
        self.assertTrue(
            self.client.login(
                username=self.user_data['username'],
                password=new_password
            )
        )

    def test_user_deletion(self):
        """Test user account deletion"""
        user_id = self.user.id
        self.user.delete()
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)

    def test_user_email_unique(self):
        """Test that email addresses must be unique"""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='another',
                email=self.user_data['email'],  # Same email as existing user
                password='anotherpass123'
            )

    def test_superuser_creation(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
