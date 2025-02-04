from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import TaskAttachment
from ..permissions import can_manage_attachment

@login_required
def delete_attachment(request, attachment_id):
    attachment = get_object_or_404(TaskAttachment, id=attachment_id)
    task = attachment.task
    
    if not can_manage_attachment(request.user, task):
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('boards:task_detail', task_id=task.id)
    
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully.')
    
    return redirect('boards:task_detail', task_id=task.id) 