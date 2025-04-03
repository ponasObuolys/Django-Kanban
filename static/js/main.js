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
    
    // Pranešimų garso inicializavimas
    initializeNotificationSound();
    
    // Patikrinti, ar yra neskaityti pranešimai ir jei taip, groti garsą
    checkUnreadNotifications();
    
    // Pradėti reguliariai tikrinti naujus pranešimus
    startNotificationPolling();
    
    // Handle Kanban Board Drag and Drop
    if (document.querySelector('.kanban-board')) {
        initializeKanbanBoard();
        
        // Handle task sorting
        document.querySelectorAll('.sort-tasks').forEach(button => {
            button.addEventListener('click', function() {
                const columnId = this.dataset.columnId;
                const sortBy = this.dataset.sortBy;
                const sortOrder = this.dataset.sortOrder;
                
                sortTasks(columnId, sortBy, sortOrder);
                
                // Save sorting preference to localStorage
                localStorage.setItem(`column_${columnId}_sort_by`, sortBy);
                localStorage.setItem(`column_${columnId}_sort_order`, sortOrder);
                
                // Update UI to indicate current sort
                updateSortingIndicator(columnId, sortBy, sortOrder);
            });
        });
        
        // Apply saved sorting on page load
        document.querySelectorAll('.task-list').forEach(column => {
            const columnId = column.dataset.columnId;
            const savedSortBy = localStorage.getItem(`column_${columnId}_sort_by`);
            const savedSortOrder = localStorage.getItem(`column_${columnId}_sort_order`);
            
            if (savedSortBy && savedSortOrder) {
                sortTasks(columnId, savedSortBy, savedSortOrder);
                updateSortingIndicator(columnId, savedSortBy, savedSortOrder);
            }
        });
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
    console.log('Bandoma pažymėti visus pranešimus kaip perskaitytus...');
    
    // Pirmiausia bandome POST metodą
    fetch('/notifications/mark-all-as-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (!response.ok) {
            // Jei POST nepavyko, bandome GET
            console.log('POST metodas nepavyko, bandome GET...');
            return fetch('/notifications/mark-all-as-read/');
        }
        return response;
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Serverio klaida: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Visi pranešimai pažymėti kaip perskaityti:', data);
        
        // Atnaujiname pranešimų skaičių
        const badge = document.getElementById('notifications-badge');
        if (badge) {
            badge.style.display = 'none';
            badge.textContent = '0';
        }
        
        // Arba užkraukime visą pranešimų sąrašą iš naujo
        updateNotificationsList();
        
        // Atnaujiname paskutinį žinomą pranešimų skaičių
        lastNotificationCount = 0;
    })
    .catch(error => {
        console.error('Klaida žymint visus pranešimus kaip perskaitytus:', error);
        
        // Paskutinis bandymas tiesiogiai naudojant window.location
        console.log('Bandoma paskutinis variantas - nukreipimas į mark-all-as-read URL');
        window.location.href = '/notifications/mark-all-as-read/';
    });
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

// Garsinio pranešimo funkcijos
let notificationSound = null;
let lastNotificationCount = null;

function initializeNotificationSound() {
    // Sukuriame audio objektą
    notificationSound = new Audio('/static/audio/Notification.mp3');
    
    // Nustatome garsumą (nuo 0 iki 1)
    notificationSound.volume = 0.5;
    
    // Įkrauname garsą iš anksto
    notificationSound.load();
    
    // Išsaugome pradinį neperskaitytų pranešimų skaičių
    const badge = document.getElementById('notifications-badge');
    if (badge) {
        lastNotificationCount = parseInt(badge.textContent) || 0;
    }
}

function playNotificationSound() {
    if (notificationSound) {
        // Sustabdome garsą, jei jis jau groja
        notificationSound.pause();
        notificationSound.currentTime = 0;
        
        // Grojame garsą
        notificationSound.play().catch(err => {
            console.warn('Nepavyko paleisti pranešimo garso:', err);
        });
    }
}

function checkUnreadNotifications() {
    const badge = document.getElementById('notifications-badge');
    if (!badge) return;
    
    const currentCount = parseInt(badge.textContent) || 0;
    
    // Jei tai pirmas patikrinimas, tiesiog išsaugome skaičių
    if (lastNotificationCount === null) {
        lastNotificationCount = currentCount;
        return;
    }
    
    // Jei pranešimų padaugėjo, grojame garsą
    if (currentCount > lastNotificationCount) {
        playNotificationSound();
    }
    
    // Atnaujiname paskutinį žinomą pranešimų skaičių
    lastNotificationCount = currentCount;
}

function startNotificationPolling() {
    // Pirmiausia iškart patikriname, ar yra pranešimų
    checkForNewNotifications();
    
    // Reguliariai tikriname neperskaitytų pranešimų skaičių (kas 10 sekundžių)
    setInterval(function() {
        checkForNewNotifications();
    }, 10000); // 10 sekundžių intervalas
}

function checkForNewNotifications() {
    console.debug("Tikrinami pranešimai...");
    
    // Įtraukime naują pranešimų tikrinimo metodą
    const currentRoute = window.location.pathname;
    console.debug("Dabartinis kelias:", currentRoute);
    
    // Nukreipimas, jei tai testo puslapis
    if (currentRoute.includes('test-page')) {
        console.debug("Aptiktas testo puslapis, naudojama speciali logika");
    }
    
    // Siunčiame užklausą, kad gautume naujausią pranešimų skaičių
    fetch('/notifications/get-count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            console.error("Serverio atsakymas nepavyko:", response.status, response.statusText);
            throw new Error('Serverio klaida: ' + response.status);
        }
        console.debug("Gautas atsakymas iš serverio:", response.status);
        return response.json();
    })
    .then(data => {
        const currentCount = data.count;
        const badge = document.getElementById('notifications-badge');
        console.debug("Gauta pranešimų:", currentCount, "Ankstesnis skaičius:", lastNotificationCount);
        
        // Atnaujiname pranešimų skaičių 
        if (badge) {
            badge.textContent = currentCount;
            badge.style.display = currentCount > 0 ? 'inline-block' : 'none';
            console.debug("Atnaujintas pranešimų skaičius ekrane:", currentCount);
        } else {
            console.warn("Nerastas pranešimų ženkliukas (badge) DOM'e");
        }
        
        // Jei pranešimų padaugėjo, grojame garsą ir rodome pop-up
        if (lastNotificationCount !== null && currentCount > lastNotificationCount) {
            console.debug("Aptikti nauji pranešimai! Paleidžiamas garsas ir rodomas pop-up");
            playNotificationSound();
            
            // Rodome pop-up pranešimą
            showNotificationPopup("Jūs turite naujų užduočių");
            
            // Atnaujiname pranešimų sąrašą
            updateNotificationsList();
        }
        
        // Išsaugome naują skaičių
        lastNotificationCount = currentCount;
    })
    .catch(error => {
        console.error('Klaida tikrinant pranešimus:', error);
    });
}

// Pop-up pranešimų funkcija
function showNotificationPopup(message) {
    // Sukuriame pop-up elementą
    const popup = document.createElement('div');
    popup.className = 'notification-popup';
    popup.innerHTML = `
        <div class="notification-popup-content">
            <div class="notification-popup-header">
                <i class="fas fa-bell me-2"></i>
                <span class="notification-title">Pranešimas</span>
                <button type="button" class="btn-close ms-3" aria-label="Close"></button>
            </div>
            <div class="notification-popup-body">
                ${message}
            </div>
        </div>
    `;
    
    // Pridedame stilių
    popup.style.position = 'fixed';
    popup.style.top = '50%';
    popup.style.left = '50%';
    popup.style.transform = 'translate(-50%, -50%)';
    popup.style.backgroundColor = 'white';
    popup.style.color = 'var(--bs-dark, #212529)';
    popup.style.padding = '0';
    popup.style.borderRadius = '8px';
    popup.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.3)';
    popup.style.zIndex = '9999';
    popup.style.minWidth = '400px';
    popup.style.maxWidth = '80%';
    popup.style.opacity = '0';
    popup.style.transition = 'opacity 0.3s ease-in-out';
    popup.style.border = '1px solid rgba(0, 0, 0, 0.1)';
    
    // Stiliai vidiniams elementams
    const content = popup.querySelector('.notification-popup-content');
    content.style.display = 'flex';
    content.style.flexDirection = 'column';
    
    const header = popup.querySelector('.notification-popup-header');
    header.style.display = 'flex';
    header.style.alignItems = 'center';
    header.style.padding = '15px 20px';
    header.style.borderBottom = '1px solid rgba(0, 0, 0, 0.1)';
    header.style.backgroundColor = 'var(--primary-color, #0d6efd)';
    header.style.color = 'white';
    header.style.borderTopLeftRadius = '8px';
    header.style.borderTopRightRadius = '8px';
    
    const title = popup.querySelector('.notification-title');
    title.style.fontWeight = 'bold';
    title.style.fontSize = '1.2rem';
    title.style.flex = '1';
    
    const closeBtn = popup.querySelector('.btn-close');
    closeBtn.style.filter = 'invert(1)';
    
    const body = popup.querySelector('.notification-popup-body');
    body.style.padding = '20px';
    body.style.fontSize = '1.1rem';
    body.style.textAlign = 'center';
    
    // Pridedame prie body
    document.body.appendChild(popup);
    
    // Animacija - parodome
    setTimeout(() => {
        popup.style.opacity = '1';
    }, 100);
    
    // Pridedame įvykio klausytoją "Uždaryti" mygtukui
    popup.querySelector('.btn-close').addEventListener('click', function() {
        // Animacija - paslepiame
        popup.style.opacity = '0';
        setTimeout(() => {
            // Pašaliname iš DOM
            document.body.removeChild(popup);
        }, 300);
    });
}

function updateNotificationsList() {
    const dropdownMenu = document.querySelector('#notificationsDropdown + .dropdown-menu');
    if (!dropdownMenu) return;
    
    fetch('/notifications/get-list/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        // Atnaujiname pranešimų sąrašą
        if (data.html) {
            dropdownMenu.innerHTML = data.html;
            
            // Pridedame įvykių klausytojus naujiems pranešimams
            dropdownMenu.querySelectorAll('[data-notification-id]').forEach(notification => {
                notification.addEventListener('click', function(e) {
                    e.preventDefault();
                    const notificationId = this.dataset.notificationId;
                    markNotificationAsRead(notificationId);
                });
            });
            
            // Pridedame įvykio klausytoją "Pažymėti visus kaip perskaitytus" mygtukui
            const markAllBtn = dropdownMenu.querySelector('#markAllAsRead');
            if (markAllBtn) {
                markAllBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    markAllNotificationsAsRead();
                });
            }
        }
    })
    .catch(error => console.error('Klaida atnaujinant pranešimų sąrašą:', error));
}

function updateColumnTaskCount(column) {
    const taskCount = column.children.length;
    const badge = column.closest('.kanban-column').querySelector('.badge');
    if (badge) {
        badge.textContent = taskCount;
    }
}

function sortTasks(columnId, sortBy, sortOrder) {
    const column = document.querySelector(`.task-list[data-column-id="${columnId}"]`);
    if (!column) return;
    
    // Add sorting class for visual effect
    column.classList.add('sorting');
    
    // Get all tasks in this column
    const tasks = Array.from(column.querySelectorAll('.task'));
    
    // Sort tasks based on criteria
    tasks.sort((a, b) => {
        let valueA, valueB;
        
        if (sortBy === 'title') {
            valueA = a.querySelector('h6 a').textContent.trim().toLowerCase();
            valueB = b.querySelector('h6 a').textContent.trim().toLowerCase();
            return sortOrder === 'asc' ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
        } 
        else if (sortBy === 'due_date') {
            const dueDateA = a.querySelector('.due-date');
            const dueDateB = b.querySelector('.due-date');
            
            // Handle cases where due date might not exist
            valueA = dueDateA ? new Date(dueDateA.textContent.trim()) : new Date(0);
            valueB = dueDateB ? new Date(dueDateB.textContent.trim()) : new Date(0);
            
            // Special case: if one has due date and the other doesn't
            if (!dueDateA && dueDateB) return sortOrder === 'asc' ? -1 : 1;
            if (dueDateA && !dueDateB) return sortOrder === 'asc' ? 1 : -1;
            
            return sortOrder === 'asc' ? valueA - valueB : valueB - valueA;
        }
        else if (sortBy === 'priority') {
            // Convert priority to numeric value
            const getPriorityValue = (element) => {
                if (element.classList.contains('border-danger')) return 3; // high
                if (element.classList.contains('border-warning')) return 2; // medium
                return 1; // low
            };
            
            valueA = getPriorityValue(a);
            valueB = getPriorityValue(b);
            
            return sortOrder === 'asc' ? valueA - valueB : valueB - valueA;
        }
        else if (sortBy === 'created_at' || sortBy === 'position') {
            // For these we need to fetch data from data attributes
            // Assuming they're stored or can be derived from the task ID
            // As a fallback, revert to the default order
            valueA = parseInt(a.dataset.taskId);
            valueB = parseInt(b.dataset.taskId);
            
            return sortOrder === 'asc' ? valueA - valueB : valueB - valueA;
        }
        
        // Default case
        return 0;
    });
    
    // Reorder tasks in the DOM
    tasks.forEach(task => {
        column.appendChild(task);
    });
    
    // Remove sorting effect after animation
    setTimeout(() => {
        column.classList.remove('sorting');
    }, 300);
    
    // Disable drag and drop temporarily if we're sorting by anything other than position
    if (sortBy !== 'position') {
        tasks.forEach(task => {
            task.setAttribute('draggable', 'false');
        });
    } else {
        // Re-enable drag and drop for the default sorting
        tasks.forEach(task => {
            const userId = task.dataset.createdById;
            const assignedToId = task.dataset.assignedToId;
            const currentUserId = document.body.dataset.userId;
            
            if (userId === currentUserId || assignedToId === currentUserId) {
                task.setAttribute('draggable', 'true');
            }
        });
    }
}

function updateSortingIndicator(columnId, sortBy, sortOrder) {
    // Find the column header
    const columnHeader = document.querySelector(`.kanban-column .task-list[data-column-id="${columnId}"]`)
                          .closest('.kanban-column')
                          .querySelector('.column-header .dropdown button');
    
    // Update icon based on current sort
    if (columnHeader) {
        // Remove all existing sort classes
        columnHeader.querySelector('i').className = '';
        
        // Add appropriate icon based on sort type
        if (sortBy === 'title') {
            columnHeader.querySelector('i').className = sortOrder === 'asc' ? 
                'fas fa-sort-alpha-down' : 'fas fa-sort-alpha-up-alt';
        } 
        else if (sortBy === 'due_date') {
            columnHeader.querySelector('i').className = sortOrder === 'asc' ?
                'fas fa-sort-numeric-down' : 'fas fa-sort-numeric-up-alt';
        }
        else if (sortBy === 'priority') {
            columnHeader.querySelector('i').className = sortOrder === 'asc' ?
                'fas fa-sort-amount-up-alt' : 'fas fa-sort-amount-down';
        }
        else if (sortBy === 'created_at') {
            columnHeader.querySelector('i').className = sortOrder === 'asc' ?
                'fas fa-history' : 'fas fa-clock';
        }
        else {
            columnHeader.querySelector('i').className = 'fas fa-sort';
        }
    }
} 