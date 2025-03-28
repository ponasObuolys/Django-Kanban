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
    
    // Language selection form handling
    const languageForms = document.querySelectorAll('.language-form');
    languageForms.forEach(form => {
        const buttons = form.querySelectorAll('button[name="language"]');
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                localStorage.setItem('preferredLanguage', this.value);
            });
        });
    });
    
    // Initialize all tooltips
    const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(popoverTriggerEl => {
        new bootstrap.Popover(popoverTriggerEl);
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

    // Add click handler for individual notifications
    document.querySelectorAll('[data-notification-id]').forEach(notification => {
        notification.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.dataset.notificationId;
            markNotificationAsRead(notificationId);
        });
    });

    // Add click handler for mark all as read button
    const markAllBtn = document.getElementById('markAllAsRead');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsAsRead();
        });
    }

    // Užduoties kūrimo mygtuko paspaudimo apdorojimas
    document.querySelectorAll('.add-task-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const columnId = this.dataset.columnId;
            const boardId = this.dataset.boardId;
            
            // Nukreipiame į užduoties kūrimo formą su stulpelio ID
            window.location.href = `/lt/boards/tasks/create/?column=${columnId}`;
        });
    });
});

function initializeKanbanBoard() {
    const tasks = document.querySelectorAll('.task-card');
    const columns = document.querySelectorAll('.task-list');
    
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
    e.dataTransfer.setData('text/plain', e.target.dataset.taskId);
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
    const task = document.querySelector(`[data-task-id="${taskId}"]`);
    const column = e.target.closest('.task-list');
    
    if (task && column) {
        const columnId = column.dataset.columnId;
        
        // Get the position in the column
        const afterElement = getDragAfterElement(column, e.clientY);
        const position = afterElement ? Array.from(column.children).indexOf(afterElement) : column.children.length;
        
        try {
            // Send update to server
            const response = await fetch('/lt/boards/tasks/update-position/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    task_id: parseInt(taskId),
                    column_id: parseInt(columnId),
                    position: position
                })
            });
            
            if (response.ok) {
                // Update UI
                if (afterElement) {
                    column.insertBefore(task, afterElement);
                } else {
                    column.appendChild(task);
                }
                
                // Update task count badges
                const oldColumn = task.closest('.task-list');
                if (oldColumn && oldColumn !== column) {
                    updateColumnTaskCount(oldColumn);
                }
                updateColumnTaskCount(column);
            } else {
                const errorData = await response.json();
                console.error('Failed to update task position:', errorData.error);
            }
        } catch (error) {
            console.error('Error updating task position:', error);
        }
    }
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];
    
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
                notification.style.display = 'none';
            }
            updateUnreadCount();
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

function markAllNotificationsAsRead() {
    fetch('/notifications/mark-all-as-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            const notifications = document.querySelectorAll('[data-notification-id]');
            notifications.forEach(notification => {
                notification.classList.add('read');
                notification.style.display = 'none';
            });
            const badge = document.getElementById('notifications-badge');
            if (badge) {
                badge.style.display = 'none';
                badge.textContent = '0';
            }
            // Hide the mark all as read button and show empty message
            const markAllBtn = document.getElementById('markAllAsRead');
            if (markAllBtn) {
                markAllBtn.closest('.dropdown-divider')?.remove();
                markAllBtn.remove();
            }
            const dropdownMenu = document.querySelector('.dropdown-menu');
            if (dropdownMenu && !dropdownMenu.querySelector('.dropdown-item:not(.read)')) {
                dropdownMenu.innerHTML = '<span class="dropdown-item">No new notifications</span>';
            }
        }
    })
    .catch(error => console.error('Error marking all notifications as read:', error));
}

function updateUnreadCount() {
    const badge = document.getElementById('notifications-badge');
    if (badge) {
        const currentCount = parseInt(badge.textContent) - 1;
        badge.textContent = currentCount > 0 ? currentCount : '';
        if (currentCount <= 0) {
            badge.style.display = 'none';
        }
    }
}

function updateColumnTaskCount(column) {
    const taskCount = column.children.length;
    const badge = column.closest('.kanban-column').querySelector('.badge');
    if (badge) {
        badge.textContent = taskCount;
    }
} 