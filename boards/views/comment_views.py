from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import TaskComment
from ..permissions import can_manage_comment

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(TaskComment, id=comment_id)
    task = comment.task
    
    if not can_manage_comment(request.user, task):
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('boards:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    
    return redirect('boards:task_detail', task_id=task.id)
