from django.db.models import Max, Count, Q
from ..models import Board, Column
from ..permissions import can_view_board, can_edit_board

class BoardService:
    @staticmethod
    def get_user_boards(user):
        """Get all boards accessible to user"""
        personal_boards = Board.objects.filter(owner=user, team__isnull=True)
        team_boards = Board.objects.filter(team__members=user)
        return personal_boards, team_boards

    @staticmethod
    def create_board(user, data):
        """Create a new board with default columns"""
        board = Board.objects.create(owner=user, **data)
        
        # Create default columns
        columns = ['To Do', 'Doing', 'Done', 'Rejected']
        for i, title in enumerate(columns):
            Column.objects.create(
                board=board,
                title=title,
                type=title.lower().replace(' ', ''),
                position=i
            )
        
        return board

    @staticmethod
    def get_board_stats(board):
        """Get board statistics including progress"""
        total_tasks = board.columns.aggregate(
            total=Count('tasks')
        )['total']
        
        completed_tasks = board.columns.filter(
            type='done'
        ).aggregate(
            done=Count('tasks')
        )['done']
        
        progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress': progress
        }

    @staticmethod
    def get_board_members(board):
        """Get all members who can access the board"""
        if board.team:
            return board.team.members.filter(is_active=True)
        return board.owner._meta.model.objects.filter(
            id__in=[board.owner.id]
        )

    @staticmethod
    def get_team_info(board, user):
        """Get team-related information for board"""
        if not board.team:
            return None, None
        
        is_team_admin = board.team.teammembership_set.filter(
            user=user,
            role='admin'
        ).exists()
        
        pending_invitations = None
        if is_team_admin:
            pending_invitations = board.team.invitations.filter(status='pending')
        
        return is_team_admin, pending_invitations
