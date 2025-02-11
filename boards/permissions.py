from .models import Board, Column, Task, TaskComment, TaskAttachment

def is_team_admin(user, team):
    """Check if user is team admin"""
    return team.teammembership_set.filter(
        user=user,
        role='admin'
    ).exists()

def is_team_member(user, team):
    """Check if user is team member"""
    return user in team.members.all()

def can_view_board(user, board):
    """Check if user can view the board"""
    return (board.owner == user or
            (board.team and user in board.team.members.all()))

def can_edit_board(user, board):
    """Check if user can edit the board"""
    is_admin = board.team and is_team_admin(user, board.team)
    return board.owner == user or is_admin

def can_delete_board(user, board):
    """Check if user can delete the board"""
    return can_edit_board(user, board)

def can_manage_column(user, column):
    """Check if user can manage (create/edit/delete) column"""
    return can_edit_board(user, column.board)

def can_manage_task(user, task):
    """Check if user can manage (create/edit/delete) task"""
    return can_view_board(user, task.column.board)

def can_manage_comment(user, comment):
    """Check if user can manage (create/edit/delete) comment"""
    return user == comment.author or can_edit_board(user, comment.task.column.board)

def can_manage_attachment(user, attachment):
    """Check if user can manage (create/delete) attachment"""
    return user == attachment.uploaded_by or can_edit_board(user, attachment.task.column.board)

def can_manage_label(user, label):
    """Check if user can manage (create/edit/delete) label"""
    return can_edit_board(user, label.board)
