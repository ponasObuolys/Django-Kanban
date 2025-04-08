from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from ..models import Task, Column, Board
from ..forms import TaskForm, TaskCommentForm, TaskAttachmentForm
from ..services.task_service import TaskService
from ..permissions import can_manage_task, can_manage_comment, can_manage_attachment, can_edit_board
import json
from django.db.models import Max

@login_required
def task_create(request):
    # Gauname stulpelio ID iš URL parametrų
    column_id = request.GET.get('column')
    column = None
    board = None
    
    if column_id:
        column = get_object_or_404(Column, id=column_id)
        board = column.board
    else:
        # Jei nėra stulpelio ID, bandome gauti lentos ID
        board_id = request.GET.get('board')
        if board_id:
            board = get_object_or_404(Board, id=board_id)
    
    if not board or not can_edit_board(request.user, board):
        messages.error(request, "You don't have permission to create tasks.")
        return redirect('boards:board_list')
    
    if request.method == 'POST':
        # Jei nėra stulpelio POST duomenyse, naudojame stulpelį iš URL
        if not request.POST.get('column') and column:
            post_data = request.POST.copy()
            post_data['column'] = column.id
            form = TaskForm(post_data, board=board, user=request.user)
        else:
            form = TaskForm(request.POST, board=board, user=request.user)
        
        if form.is_valid():
            # Gauname stulpelį iš formos
            column = form.cleaned_data['column']
            # Pašaliname column iš cleaned_data, nes jis bus perduotas atskirai
            task_data = form.cleaned_data.copy()
            task_data.pop('column')
            
            task = TaskService.create_task(column, task_data, request.user)
            messages.success(request, 'Task created successfully.')
            return redirect('boards:board_detail', board_id=board.id)
    else:
        initial_data = {}
        if column:
            initial_data['column'] = column.id
        form = TaskForm(initial=initial_data, board=board, user=request.user)
    
    return render(request, 'boards/task_form.html', {
        'form': form,
        'title': 'Create Task',
        'board': board
    })

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    if not can_manage_task(request.user, task):
        messages.error(request, "You don't have permission to edit this task.")
        return redirect('boards:board_detail', board_id=task.column.board.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            TaskService.update_task(task, form.cleaned_data)
            messages.success(request, 'Task updated successfully.')
            return redirect('boards:board_detail', board_id=task.column.board.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'boards/task_form.html', {
        'form': form,
        'task': task,
        'board': board,
        'title': 'Edit Task'
    })

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not can_manage_task(request.user, task):
        messages.error(request, "You don't have permission to delete this task.")
        return redirect('boards:board_detail', board_id=task.column.board.id)
    
    if request.method == 'POST':
        board_id = task.column.board.id
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('boards:board_detail', board_id=board_id)
    
    return render(request, 'boards/task_confirm_delete.html', {
        'task': task
    })

@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not can_manage_comment(request.user, task):
        messages.error(request, "You don't have permission to comment on this task.")
        return redirect('boards:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            TaskService.add_comment(task, request.user, form.cleaned_data['content'])
            messages.success(request, 'Comment added successfully.')
            return redirect('boards:task_detail', task_id=task.id)
    else:
        form = TaskCommentForm()
    
    return render(request, 'boards/comment_form.html', {
        'form': form,
        'task': task
    })

@login_required
def add_attachment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not can_manage_attachment(request.user, task):
        messages.error(request, "You don't have permission to add attachments to this task.")
        return redirect('boards:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            TaskService.add_attachment(task, request.user, form.cleaned_data['file'])
            messages.success(request, 'Attachment added successfully.')
            return redirect('boards:task_detail', task_id=task.id)
    else:
        form = TaskAttachmentForm()
    
    return render(request, 'boards/attachment_form.html', {
        'form': form,
        'task': task
    })

@login_required
def update_task_position(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_column_id = data.get('column_id')
            new_position = int(data.get('position', 0))
            
            if not all([task_id, new_column_id]):
                return JsonResponse({
                    'error': 'Missing required fields'
                }, status=400)
            
            task = get_object_or_404(Task, id=task_id)
            new_column = get_object_or_404(Column, id=new_column_id)
            
            # Check if both columns belong to the same board
            if task.column.board_id != new_column.board_id:
                return JsonResponse({
                    'error': 'Cannot move task between different boards'
                }, status=400)
            
            # Patikrinti, ar vartotojas yra lentos savininkas
            if task.column.board.owner != request.user:
                return JsonResponse({
                    'error': "Tik lentos savininkas gali perkelti užduotis."
                }, status=403)
            
            TaskService.update_position(task, new_column, new_position)
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except ValueError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'error': 'Invalid request method'
    }, status=405)

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not can_manage_task(request.user, task):
        messages.error(request, "You don't have permission to view this task.")
        return redirect('boards:board_detail', board_id=task.column.board.id)
    
    if request.method == 'POST':
        if 'file' in request.FILES:  # Handle file upload
            form = TaskAttachmentForm(request.POST, request.FILES)
            try:
                if form.is_valid():
                    TaskService.add_attachment(task, request.user, form.cleaned_data['file'])
                    if request.is_ajax():
                        return JsonResponse({'status': 'success'})
                    messages.success(request, 'Attachment added successfully.')
                    return redirect('boards:task_detail', task_id=task.id)
                else:
                    if request.is_ajax():
                        return JsonResponse({
                            'status': 'error',
                            'errors': form.errors
                        }, status=400)
                    messages.error(request, 'Failed to upload attachment. ' + ' '.join([error for errors in form.errors.values() for error in errors]))
            except Exception as e:
                if request.is_ajax():
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=500)
                messages.error(request, f'An error occurred while uploading the attachment: {str(e)}')
        else:  # Handle comment
            form = TaskCommentForm(request.POST)
            try:
                if form.is_valid():
                    TaskService.add_comment(task, request.user, form.cleaned_data['content'])
                    messages.success(request, 'Comment added successfully.')
                    return redirect('boards:task_detail', task_id=task.id)
                else:
                    messages.error(request, 'Failed to add comment. ' + ' '.join([error for errors in form.errors.values() for error in errors]))
            except Exception as e:
                messages.error(request, f'An error occurred while adding the comment: {str(e)}')
    
    comment_form = TaskCommentForm()
    attachment_form = TaskAttachmentForm()
    
    return render(request, 'boards/task_detail.html', {
        'task': task,
        'board': task.column.board,
        'comments': task.comments.all().order_by('-created_at'),
        'attachments': task.attachments.all().order_by('-uploaded_at'),
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'can_edit': can_manage_task(request.user, task)
    })
