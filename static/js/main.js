document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggling
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const themeIcon = themeToggle.querySelector('i');
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
    
    function updateThemeIcon(theme) {
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
    
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Handle Kanban Board Drag and Drop
    if (document.querySelector('.kanban-board')) {
        initializeKanbanBoard();
    }
});

function initializeKanbanBoard() {
    const tasks = document.querySelectorAll('.kanban-task');
    const columns = document.querySelectorAll('.kanban-column');
    
    tasks.forEach(task => {
        task.addEventListener('dragstart', handleDragStart);
        task.addEventListener('dragend', handleDragEnd);
    });
    
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
    });
}

function handleDragStart(e) {
    e.target.classList.add('dragging');
    e.dataTransfer.setData('text/plain', e.target.id);
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
}

async function handleDrop(e) {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('text/plain');
    const task = document.getElementById(taskId);
    const column = e.target.closest('.kanban-column');
    
    if (task && column) {
        const columnId = column.dataset.columnId;
        const taskList = column.querySelector('.kanban-tasks');
        
        // Get the position in the column
        const afterElement = getDragAfterElement(taskList, e.clientY);
        const position = afterElement ? Array.from(taskList.children).indexOf(afterElement) : taskList.children.length;
        
        try {
            // Send update to server
            const response = await fetch('/api/tasks/update-position/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    taskId: taskId,
                    columnId: columnId,
                    position: position
                })
            });
            
            if (response.ok) {
                // Update UI
                if (afterElement) {
                    taskList.insertBefore(task, afterElement);
                } else {
                    taskList.appendChild(task);
                }
            } else {
                console.error('Failed to update task position');
            }
        } catch (error) {
            console.error('Error updating task position:', error);
        }
    }
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.kanban-task:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Notification Functions
function markNotificationAsRead(notificationId) {
    fetch(`/notifications/mark-as-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notification) {
                notification.classList.add('read');
            }
            updateUnreadCount();
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

function updateUnreadCount() {
    const badge = document.querySelector('#notifications-badge');
    if (badge) {
        const currentCount = parseInt(badge.textContent) - 1;
        badge.textContent = currentCount > 0 ? currentCount : '';
        if (currentCount <= 0) {
            badge.style.display = 'none';
        }
    }
} 