from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Max, Count
from .models import Board, Column, Task, Label, TaskComment, TaskAttachment
from accounts.models import CustomUser
from .forms import (
    BoardForm, ColumnForm, TaskForm, LabelForm,
    TaskCommentForm, TaskAttachmentForm
)
from notifications.signals import notify

@login_required
def board_list(request):
    personal_boards = Board.objects.filter(owner=request.user, team__isnull=True)
    team_boards = Board.objects.filter(team__members=request.user)
    
    return render(request, 'boards/board_list.html', {
        'personal_boards': personal_boards,
        'team_boards': team_boards
    })

@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            
            # Create default columns
            columns = ['To Do', 'Doing', 'Done', 'Rejected']
            for i, title in enumerate(columns):
                Column.objects.create(
                    board=board,
                    title=title,
                    type=title.lower().replace(' ', ''),
                    position=i
                )
            
            messages.success(request, 'Board created successfully.')
            return redirect('board_detail', board_id=board.id)
    else:
        form = BoardForm()
    
    return render(request, 'boards/board_form.html', {
        'form': form,
        'title': 'Create Board'
    })

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Check if user has access to the board
    if not (board.owner == request.user or
            (board.team and request.user in board.team.members.all())):
        messages.error(request, "You don't have access to this board.")
        return redirect('board_list')
    
    # Calculate progress
    total_tasks = board.columns.aggregate(
        total=Count('tasks')
    )['total']
    
    completed_tasks = board.columns.filter(
        type='done'
    ).aggregate(
        done=Count('tasks')
    )['done']
    
    progress = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    # Get all users for member selection
    users = CustomUser.objects.filter(is_active=True)
    
    return render(request, 'boards/board_detail.html', {
        'board': board,
        'progress': progress,
        'users': users
    })

@login_required
def board_edit(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to edit this board.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, 'Board updated successfully.')
            return redirect('board_detail', board_id=board.id)
    else:
        form = BoardForm(instance=board)
    
    return render(request, 'boards/board_form.html', {
        'form': form,
        'title': 'Edit Board'
    })

@login_required
def board_delete(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to delete this board.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        board.delete()
        messages.success(request, 'Board deleted successfully.')
        return redirect('board_list')
    
    return render(request, 'boards/board_confirm_delete.html', {
        'board': board
    })

@login_required
def column_create(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            column = form.save(commit=False)
            column.board = board
            column.position = board.columns.aggregate(Max('position'))['position__max'] + 1
            column.save()
            messages.success(request, 'Column created successfully.')
            return redirect('board_detail', board_id=board.id)
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
    board = column.board
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to edit this column.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = ColumnForm(request.POST, instance=column)
        if form.is_valid():
            form.save()
            messages.success(request, 'Column updated successfully.')
            return redirect('board_detail', board_id=board.id)
    else:
        form = ColumnForm(instance=column)
    
    return render(request, 'boards/column_form.html', {
        'form': form,
        'board': board,
        'title': 'Edit Column'
    })

@login_required
def column_delete(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    board = column.board
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to delete this column.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        column.delete()
        messages.success(request, 'Column deleted successfully.')
        return redirect('board_detail', board_id=board.id)
    
    return render(request, 'boards/column_confirm_delete.html', {
        'column': column,
        'board': board
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            column = task.column
            task.position = column.tasks.aggregate(Max('position'))['position__max'] or 0
            task.position += 1
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Send notification if task is assigned
            if task.assigned_to:
                notify.send(
                    request.user,
                    recipient=task.assigned_to,
                    verb='assigned you to',
                    target=task,
                    description=f'You have been assigned to task "{task.title}"'
                )
            
            messages.success(request, 'Task created successfully.')
            return redirect('board_detail', board_id=task.column.board.id)
    else:
        column_id = request.GET.get('column')
        initial = {'column': column_id} if column_id else None
        form = TaskForm(initial=initial)
    
    return render(request, 'boards/task_form.html', {
        'form': form,
        'title': 'Create Task'
    })

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    if not (board.owner == request.user or task.created_by == request.user):
        messages.error(request, "You don't have permission to edit this task.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            
            # Send notification if assigned user has changed
            if 'assigned_to' in form.changed_data and task.assigned_to:
                notify.send(
                    request.user,
                    recipient=task.assigned_to,
                    verb='assigned you to',
                    target=task,
                    description=f'You have been assigned to task "{task.title}"'
                )
            
            messages.success(request, 'Task updated successfully.')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'boards/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Edit Task'
    })

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    if not (board.owner == request.user or task.created_by == request.user):
        messages.error(request, "You don't have permission to delete this task.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('board_detail', board_id=board.id)
    
    return render(request, 'boards/task_confirm_delete.html', {
        'task': task,
        'board': board
    })

@login_required
def task_assign(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            task.assigned_to_id = user_id
            task.save()
            
            # Send notification to the assigned user
            if task.assigned_to:
                notify.send(
                    request.user,
                    recipient=task.assigned_to,
                    verb='assigned you to',
                    target=task,
                    description=f'You have been assigned to task "{task.title}"'
                )
            
            messages.success(request, 'Task assigned successfully.')
        else:
            task.assigned_to = None
            task.save()
            messages.success(request, 'Task unassigned successfully.')
    
    return redirect('task_detail', task_id=task.id)

@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            
            # Notify task assignee of new comment
            if task.assigned_to and task.assigned_to != request.user:
                notify.send(
                    request.user,
                    recipient=task.assigned_to,
                    verb='commented on',
                    target=task,
                    description=f'New comment on task "{task.title}"'
                )
            
            messages.success(request, 'Comment added successfully.')
    
    return redirect('task_detail', task_id=task.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(TaskComment, id=comment_id)
    task = comment.task
    
    if comment.author != request.user and task.column.board.owner != request.user:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    
    return redirect('task_detail', task_id=task.id)

@login_required
def add_attachment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully.')
    
    return redirect('task_detail', task_id=task.id)

@login_required
def delete_attachment(request, attachment_id):
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task
    
    if attachment.uploaded_by != request.user and task.column.board.owner != request.user:
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully.')
    
    return redirect('task_detail', task_id=task.id)

@login_required
def label_create(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to create labels.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.board = board
            label.save()
            messages.success(request, 'Label created successfully.')
            return redirect('board_detail', board_id=board.id)
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
    board = label.board
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to edit this label.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        form = LabelForm(request.POST, instance=label)
        if form.is_valid():
            form.save()
            messages.success(request, 'Label updated successfully.')
            return redirect('board_detail', board_id=board.id)
    else:
        form = LabelForm(instance=label)
    
    return render(request, 'boards/label_form.html', {
        'form': form,
        'board': board,
        'label': label,
        'title': 'Edit Label'
    })

@login_required
def label_delete(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    board = label.board
    
    if board.owner != request.user:
        messages.error(request, "You don't have permission to delete this label.")
        return redirect('board_detail', board_id=board.id)
    
    if request.method == 'POST':
        label.delete()
        messages.success(request, 'Label deleted successfully.')
    
    return redirect('board_detail', board_id=board.id)

@login_required
def update_task_position(request):
    if request.method == 'POST':
        task_id = request.POST.get('taskId')
        column_id = request.POST.get('columnId')
        position = request.POST.get('position')
        
        try:
            task = Task.objects.get(id=task_id)
            new_column = Column.objects.get(id=column_id)
            
            # Update task position and column
            task.column = new_column
            task.position = position
            task.save()
            
            return JsonResponse({'status': 'success'})
        except (Task.DoesNotExist, Column.DoesNotExist):
            return JsonResponse({'status': 'error'}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def update_column_position(request):
    if request.method == 'POST':
        column_id = request.POST.get('columnId')
        position = request.POST.get('position')
        
        try:
            column = Column.objects.get(id=column_id)
            column.position = position
            column.save()
            
            return JsonResponse({'status': 'success'})
        except Column.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    
    # Check if user has access to the board
    if not (board.owner == request.user or
            (board.team and request.user in board.team.members.all())):
        messages.error(request, "You don't have access to this task.")
        return redirect('board_list')
    
    comments = task.comments.all().select_related('author')
    attachments = task.attachments.all().select_related('uploaded_by')
    
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        attachment_form = TaskAttachmentForm(request.POST, request.FILES)
        
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            
            # Notify task assignee of new comment
            if task.assigned_to and task.assigned_to != request.user:
                notify.send(
                    request.user,
                    recipient=task.assigned_to,
                    verb='commented on',
                    target=task,
                    description=f'New comment on task "{task.title}"'
                )
            
            messages.success(request, 'Comment added successfully.')
            return redirect('task_detail', task_id=task.id)
        
        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.task = task
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully.')
            return redirect('task_detail', task_id=task.id)
    else:
        comment_form = TaskCommentForm()
        attachment_form = TaskAttachmentForm()
    
    return render(request, 'boards/task_detail.html', {
        'task': task,
        'board': board,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'can_edit': board.owner == request.user or task.created_by == request.user
    })
