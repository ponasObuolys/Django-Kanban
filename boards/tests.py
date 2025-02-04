import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from boards.models import Board, Task, Column
from teams.models import Team

User = get_user_model()

@pytest.mark.django_db
class BoardTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create another user for task assignment tests
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        # Create test team
        self.team = Team.objects.create(
            name='Test Team',
            owner=self.user
        )
        self.team.members.add(self.user, self.other_user)
        
        # Create test board
        self.board = Board.objects.create(
            title='Test Board',
            team=self.team,
            owner=self.user
        )
        
        # Create default columns
        self.todo_column = Column.objects.create(
            title='To Do',
            board=self.board,
            position=0,
            type='todo'
        )
        self.in_progress_column = Column.objects.create(
            title='In Progress',
            board=self.board,
            position=1,
            type='doing'
        )
        self.done_column = Column.objects.create(
            title='Done',
            board=self.board,
            position=2,
            type='done'
        )

    def test_board_creation(self):
        """Test if board is created correctly"""
        self.assertEqual(self.board.title, 'Test Board')
        self.assertEqual(self.board.team, self.team)
        self.assertEqual(self.board.owner, self.user)

    def test_column_creation(self):
        """Test if columns are created correctly"""
        columns = self.board.columns.all()
        self.assertEqual(columns.count(), 3)
        self.assertEqual(columns[0].title, 'To Do')
        self.assertEqual(columns[1].title, 'In Progress')
        self.assertEqual(columns[2].title, 'Done')

    def test_task_creation(self):
        """Test creating a new task"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            column=self.todo_column,
            created_by=self.user,
            position=0
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.column, self.todo_column)
        self.assertEqual(task.created_by, self.user)

    def test_task_assignment(self):
        """Test assigning a task to another user"""
        task = Task.objects.create(
            title='Assignment Test',
            description='Test Description',
            column=self.todo_column,
            created_by=self.user,
            position=0
        )
        task.assigned_to = self.other_user
        task.save()
        self.assertEqual(task.assigned_to, self.other_user)

    def test_task_movement(self):
        """Test moving a task between columns"""
        task = Task.objects.create(
            title='Movement Test',
            description='Test Description',
            column=self.todo_column,
            created_by=self.user,
            position=0
        )
        # Move task to in progress
        task.column = self.in_progress_column
        task.save()
        self.assertEqual(task.column, self.in_progress_column)

    def test_task_priority(self):
        """Test setting task priority"""
        task = Task.objects.create(
            title='Priority Test',
            description='Test Description',
            column=self.todo_column,
            created_by=self.user,
            priority='high',
            position=0
        )
        self.assertEqual(task.priority, 'high')

    def test_task_due_date(self):
        """Test setting and updating task due date"""
        from django.utils import timezone
        import datetime
        
        due_date = timezone.now() + datetime.timedelta(days=7)
        task = Task.objects.create(
            title='Due Date Test',
            description='Test Description',
            column=self.todo_column,
            created_by=self.user,
            due_date=due_date,
            position=0
        )
        self.assertIsNotNone(task.due_date)
