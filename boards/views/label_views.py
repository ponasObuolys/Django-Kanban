from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Label, Board
from ..forms import LabelForm
from ..services.label_service import LabelService
from ..permissions import can_manage_label

@login_required
def label_create(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if not can_manage_label(request.user, board):
        messages.error(request, "You don't have permission to create labels.")
        return redirect('boards:board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            LabelService.create_label(board, form.cleaned_data)
            messages.success(request, 'Label created successfully.')
            return redirect('boards:board_detail', board_id=board.id)
    else:
        form = LabelForm()
    
    return render(request, 'boards/label_form.html', {
        'form': form,
        'board': board,
        'title': 'Create Label'
    })

@login_required
def label_edit(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    
    if not can_manage_label(request.user, label.board):
        messages.error(request, "You don't have permission to edit this label.")
        return redirect('boards:board_detail', board_id=label.board.id)
    
    if request.method == 'POST':
        form = LabelForm(request.POST, instance=label)
        if form.is_valid():
            LabelService.update_label(label, form.cleaned_data)
            messages.success(request, 'Label updated successfully.')
            return redirect('boards:board_detail', board_id=label.board.id)
    else:
        form = LabelForm(instance=label)
    
    return render(request, 'boards/label_form.html', {
        'form': form,
        'label': label,
        'board': label.board,
        'title': 'Edit Label'
    })

@login_required
def label_delete(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    
    if not can_manage_label(request.user, label.board):
        messages.error(request, "You don't have permission to delete this label.")
        return redirect('boards:board_detail', board_id=label.board.id)
    
    if request.method == 'POST':
        board_id = label.board.id
        label.delete()
        messages.success(request, 'Label deleted successfully.')
        return redirect('boards:board_detail', board_id=board_id)
    
    return render(request, 'boards/label_confirm_delete.html', {
        'label': label,
        'board': label.board
    })
