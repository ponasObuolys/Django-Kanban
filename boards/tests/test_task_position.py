import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from boards.models import Board, Column, Task
from teams.models import Team
import json

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
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
    for i, title in enumerate(['To Do', 'Doing', 'Done']):
        column = Column.objects.create(
            board=board,
            title=title,
            type=title.lower().replace(' ', ''),
            position=i,
            color='#FF0000'
        )
        columns.append(column)
    return columns

@pytest.fixture
def task(user, columns):
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        column=columns[0],  # To Do column
        created_by=user,
        priority='medium',
        position=0
    )

@pytest.mark.django_db
class TestTaskPositionUpdate:
    def test_update_task_position_success(self, client, user, board, columns, task):
        """Test successful task position update between columns"""
        client.login(username='testuser', password='testpass123')
        
        # Move task from To Do to Doing
        data = {
            'task_id': task.id,
            'column_id': columns[1].id,  # Doing column
            'position': 0
        }
        
        response = client.post(
            reverse('boards:update_task_position'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['status'] == 'success'
        
        # Verify task was moved
        task.refresh_from_db()
        assert task.column == columns[1]
        assert task.position == 0

    def test_update_task_position_missing_fields(self, client, user, board, columns, task):
        """Test task position update with missing required fields"""
        client.login(username='testuser', password='testpass123')
        
        # Missing position field
        data = {
            'task_id': task.id,
            'column_id': columns[1].id
        }
        
        response = client.post(
            reverse('boards:update_task_position'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.content)
        assert response_data['status'] == 'error'
        assert 'Missing required fields' in response_data['error']
        
        # Verify task hasn't moved
        task.refresh_from_db()
        assert task.column == columns[0]
        assert task.position == 0

    def test_update_task_position_invalid_column(self, client, user, board, columns, task):
        """Test task position update with invalid column ID"""
        client.login(username='testuser', password='testpass123')
        
        data = {
            'task_id': task.id,
            'column_id': 999,  # Non-existent column
            'position': 0
        }
        
        response = client.post(
            reverse('boards:update_task_position'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        response_data = json.loads(response.content)
        assert response_data['status'] == 'error'
        
        # Verify task hasn't moved
        task.refresh_from_db()
        assert task.column == columns[0]
        assert task.position == 0

    def test_update_task_position_unauthorized(self, client, user, board, columns, task):
        """Test task position update by unauthorized user"""
        # Create another user
        User = get_user_model()
        another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpass123'
        )
        client.login(username='anotheruser', password='testpass123')
        
        data = {
            'task_id': task.id,
            'column_id': columns[1].id,
            'position': 0
        }
        
        response = client.post(
            reverse('boards:update_task_position'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 403
        response_data = json.loads(response.content)
        assert response_data['status'] == 'error'
        assert "You don't have access to this board" in response_data['error']
        
        # Verify task hasn't moved
        task.refresh_from_db()
        assert task.column == columns[0]
        assert task.position == 0 