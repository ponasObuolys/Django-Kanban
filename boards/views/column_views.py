from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import Column, Board
from ..forms import ColumnForm
from ..services.column_service import ColumnService
from ..permissions import can_manage_column

@login_required
def column_create(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if not can_manage_column(request.user, board):
        messages.error(request, "You don't have permission to create columns.")
        return redirect('boards:board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            ColumnService.create_column(board, form.cleaned_data)
            messages.success(request, 'Column created successfully.')
            return redirect('boards:board_detail', board_id=board.id)
    else:
        form = ColumnForm()
    
    return render(request, 'boards/column_form.html', {
        'form': form,
        'board': board,
        'title': 'Create Column'
    })

@login_required
def column_edit(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    
    if not can_manage_column(request.user, column):
        messages.error(request, "You don't have permission to edit this column.")
        return redirect('boards:board_detail', board_id=column.board.id)
    
    if request.method == 'POST':
        form = ColumnForm(request.POST, instance=column)
        if form.is_valid():
            ColumnService.update_column(column, form.cleaned_data)
            messages.success(request, 'Column updated successfully.')
            return redirect('boards:board_detail', board_id=column.board.id)
    else:
        form = ColumnForm(instance=column)
    
    return render(request, 'boards/column_form.html', {
        'form': form,
        'column': column,
        'board': column.board,
        'title': 'Edit Column'
    })

@login_required
def column_delete(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    
    if not can_manage_column(request.user, column):
        messages.error(request, "You don't have permission to delete this column.")
        return redirect('boards:board_detail', board_id=column.board.id)
    
    if request.method == 'POST':
        board_id = column.board.id
        ColumnService.delete_column(column)
        messages.success(request, 'Column deleted successfully.')
        return redirect('boards:board_detail', board_id=board_id)
    
    return render(request, 'boards/column_confirm_delete.html', {
        'column': column,
        'board': column.board
    })

@login_required
def update_column_position(request):
    if request.method == 'POST':
        columns_data = request.POST.get('columns', {})
        
        # Verify user has permission for all columns
        column_ids = columns_data.keys()
        columns = Column.objects.filter(id__in=column_ids)
        
        for column in columns:
            if not can_manage_column(request.user, column):
                return JsonResponse({
                    'error': "You don't have permission to move columns."
                }, status=403)
        
        ColumnService.update_positions(columns_data)
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
