from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Board
from ..forms import BoardForm
from ..services.board_service import BoardService
from ..permissions import can_view_board, can_edit_board, can_delete_board

@login_required
def board_list(request):
    personal_boards, team_boards = BoardService.get_user_boards(request.user)
    return render(request, 'boards/board_list.html', {
        'personal_boards': personal_boards,
        'team_boards': team_boards
    })

@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST, user=request.user)
        if form.is_valid():
            board = BoardService.create_board(request.user, form.cleaned_data)
            messages.success(request, 'Board created successfully.')
            return redirect('boards:board_detail', board_id=board.id)
    else:
        form = BoardForm(user=request.user)
    
    return render(request, 'boards/board_form.html', {
        'form': form,
        'title': 'Create Board'
    })

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if not can_view_board(request.user, board):
        messages.error(request, "You don't have access to this board.")
        return redirect('boards:board_list')
    
    # Get board statistics
    stats = BoardService.get_board_stats(board)
    
    # Get users who can access the board
    users = BoardService.get_board_members(board)
    
    # Get team information if applicable
    is_team_admin = False
    pending_invitations = None
    
    if board.team:
        is_team_admin = board.team.teammembership_set.filter(
            user=request.user,
            role='admin'
        ).exists()
        
        if is_team_admin:
            pending_invitations = board.team.invitations.filter(status='pending')
    
    return render(request, 'boards/board_detail.html', {
        'board': board,
        'progress': stats['progress'],
        'users': users,
        'is_admin': is_team_admin,
        'pending_invitations': pending_invitations,
        'is_team_member': board.team and request.user in board.team.members.all()
    })

@login_required
def board_edit(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if not can_edit_board(request.user, board):
        messages.error(request, "You don't have permission to edit this board.")
        return redirect('boards:board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Board updated successfully.')
            return redirect('boards:board_detail', board_id=board.id)
    else:
        form = BoardForm(instance=board, user=request.user)
    
    return render(request, 'boards/board_form.html', {
        'form': form,
        'board': board,
        'title': 'Edit Board'
    })

@login_required
def board_delete(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if not can_delete_board(request.user, board):
        messages.error(request, "You don't have permission to delete this board.")
        return redirect('boards:board_detail', board_id=board.id)
    
    if request.method == 'POST':
        board.delete()
        messages.success(request, 'Board deleted successfully.')
        return redirect('boards:board_list')
    
    return render(request, 'boards/board_confirm_delete.html', {
        'board': board,
        'title': 'Delete Board'
    })
