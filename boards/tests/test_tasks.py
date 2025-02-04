import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from boards.models import Board, Column, Task
from teams.models import Team

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )

@pytest.fixture
def another_user():
    User = get_user_model()
    return User.objects.create_user(
        username='anotheruser',
        email='anotheruser@example.com',
        password='testpass123'
    )

@pytest.fixture
def board(user):
    return Board.objects.create(
        title='Test Board',
        description='Test Description',
        owner=user
    )

@pytest.fixture
def columns(board):
    columns = []
    for i, title in enumerate(['To Do', 'Doing', 'Done', 'Rejected']):
        column = Column.objects.create(
            board=board,
            title=title,
            type=title.lower().replace(' ', ''),
            position=i,
            color='#FF0000'
        )
        columns.append(column)
    return columns

@pytest.mark.django_db
class TestTaskCreation:
    def test_create_task_valid_column(self, client, user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]  # To Do column
        
        response = client.post(reverse('boards:task_create'), {
            'title': 'Test Task',
            'description': 'Test Description',
            'column': todo_column.id,
            'priority': 'medium',
            'position': 1,  # Add position field
            'assigned_to': '',  # Optional field
            'due_date': '',  # Optional field
            'labels': []  # Optional field
        })
        
        assert response.status_code == 302  # Redirect after successful creation
        assert Task.objects.count() == 1
        task = Task.objects.first()
        assert task.title == 'Test Task'
        assert task.column == todo_column
        assert task.created_by == user
        assert task.position == 1

    def test_create_task_invalid_column(self, client, user, board):
        client.login(username='testuser', password='testpass123')
        
        response = client.post(reverse('boards:task_create'), {
            'title': 'Test Task',
            'description': 'Test Description',
            'column': 999,  # Non-existent column ID
            'priority': 'medium',
            'assigned_to': '',
            'due_date': '',
            'labels': []
        })
        
        assert response.status_code == 302  # Redirect with error message
        assert Task.objects.count() == 0

    def test_create_task_unauthorized_board(self, client, another_user, board, columns):
        client.login(username='anotheruser', password='testpass123')
        todo_column = columns[0]
        
        response = client.post(reverse('boards:task_create'), {
            'title': 'Test Task',
            'description': 'Test Description',
            'column': todo_column.id,
            'priority': 'medium',
            'assigned_to': '',
            'due_date': '',
            'labels': []
        })
        
        assert response.status_code == 302  # Redirect with error message
        assert Task.objects.count() == 0

    def test_create_task_missing_column(self, client, user, board, columns):
        client.login(username='testuser', password='testpass123')
        
        response = client.post(reverse('boards:task_create'), {
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 'medium',
            'assigned_to': '',
            'due_date': '',
            'labels': []
        })
        
        assert response.status_code == 302  # Redirect with error message
        assert Task.objects.count() == 0

    def test_create_task_empty_column(self, client, user, board, columns):
        client.login(username='testuser', password='testpass123')
        
        response = client.post(reverse('boards:task_create'), {
            'title': 'Test Task',
            'description': 'Test Description',
            'column': '',  # Empty column ID
            'priority': 'medium',
            'assigned_to': '',
            'due_date': '',
            'labels': []
        })
        
        assert response.status_code == 302  # Redirect with error message
        assert Task.objects.count() == 0

    def test_create_task_with_position(self, client, user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]
        
        # Create first task
        Task.objects.create(
            title='Existing Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            priority='medium',
            position=1
        )
        
        response = client.post(reverse('boards:task_create'), {
            'title': 'New Task',
            'description': 'Test Description',
            'column': todo_column.id,
            'priority': 'medium',
            'position': 2,  # Add position field
            'assigned_to': '',
            'due_date': '',
            'labels': []
        })
        
        assert response.status_code == 302
        assert Task.objects.count() == 2
        new_task = Task.objects.get(title='New Task')
        assert new_task.position == 2  # Should be positioned after existing task

@pytest.mark.django_db
class TestTaskAssignment:
    def test_assign_task_to_user(self, client, user, another_user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]
        
        # Create a task first
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            priority='medium',
            position=1
        )
        
        # Add another_user to board's team members
        team = Team.objects.create(name='Test Team', owner=user)
        team.members.add(user, another_user)
        board.team = team
        board.save()
        
        response = client.post(reverse('boards:task_assign', args=[task.id]), {
            'user_id': another_user.id
        })
        
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.assigned_to == another_user

    def test_assign_task_to_invalid_user(self, client, user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            priority='medium',
            position=1
        )
        
        response = client.post(reverse('boards:task_assign', args=[task.id]), {
            'user_id': 999  # Non-existent user ID
        })
        
        assert response.status_code == 302  # Should redirect with error
        task.refresh_from_db()
        assert task.assigned_to is None

    def test_assign_task_unauthorized_user(self, client, user, another_user, board, columns):
        client.login(username='anotheruser', password='testpass123')
        todo_column = columns[0]
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            priority='medium',
            position=1
        )
        
        response = client.post(reverse('boards:task_assign', args=[task.id]), {
            'user_id': another_user.id
        })
        
        assert response.status_code == 302  # Redirect with error message
        task.refresh_from_db()
        assert task.assigned_to is None

    def test_assign_task_to_non_team_member(self, client, user, another_user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            priority='medium',
            position=1
        )
        
        # Create team but don't add another_user to it
        team = Team.objects.create(name='Test Team', owner=user)
        team.members.add(user)
        board.team = team
        board.save()
        
        response = client.post(reverse('boards:task_assign', args=[task.id]), {
            'user_id': another_user.id
        })
        
        assert response.status_code == 302  # Should redirect with error
        task.refresh_from_db()
        assert task.assigned_to is None

    def test_assign_task_in_personal_board(self, client, user, another_user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            priority='medium',
            position=1
        )
        
        # Board is personal (no team)
        response = client.post(reverse('boards:task_assign', args=[task.id]), {
            'user_id': another_user.id
        })
        
        assert response.status_code == 302  # Should redirect with error
        task.refresh_from_db()
        assert task.assigned_to is None

    def test_reassign_task(self, client, user, another_user, board, columns):
        client.login(username='testuser', password='testpass123')
        todo_column = columns[0]
        
        # Create team and add both users
        team = Team.objects.create(name='Test Team', owner=user)
        team.members.add(user, another_user)
        board.team = team
        board.save()
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=todo_column,
            created_by=user,
            assigned_to=user,  # Initially assigned to owner
            priority='medium',
            position=1
        )
        
        # Reassign to another user
        response = client.post(reverse('boards:task_assign', args=[task.id]), {
            'user_id': another_user.id
        })
        
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.assigned_to == another_user 