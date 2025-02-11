import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from boards.models import Board, Column, Task
from boards.services.task_service import TaskService

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def board(user):
    return Board.objects.create(title='Test Board', owner=user)

@pytest.fixture
def column(board):
    return Column.objects.create(board=board, title='Test Column', type='todo', position=1)

@pytest.mark.django_db
class TestTaskCreation:
    def test_create_task_basic(self, user, column):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': timezone.now().date(),
            'priority': 'medium'
        }
        
        task = TaskService.create_task(column, data, user)
        
        assert task.title == data['title']
        assert task.description == data['description']
        assert task.due_date == data['due_date']
        assert task.priority == data['priority']
        assert task.created_by == user
        assert task.column == column
        assert task.position == 1

    def test_create_multiple_tasks_position(self, user, column):
        # Sukuriame pirmą užduotį
        task1 = TaskService.create_task(column, {'title': 'Task 1'}, user)
        # Sukuriame antrą užduotį
        task2 = TaskService.create_task(column, {'title': 'Task 2'}, user)
        
        assert task1.position == 1
        assert task2.position == 2

    def test_create_task_without_optional_fields(self, user, column):
        data = {
            'title': 'Minimal Task'
        }
        
        task = TaskService.create_task(column, data, user)
        
        assert task.title == data['title']
        assert task.description == ''
        assert task.due_date is None
        assert task.priority == 'medium'  # default priority

    def test_create_task_with_labels(self, user, column):
        from boards.models import Label
        
        # Sukuriame žymę
        label = Label.objects.create(board=column.board, name='Test Label', color='#FF0000')
        
        data = {
            'title': 'Task with Label'
        }
        
        task = TaskService.create_task(column, data, user)
        task.labels.add(label)
        
        assert task.title == data['title']
        assert list(task.labels.all()) == [label] 