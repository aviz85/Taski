// Constants
const API_BASE_URL = '/api';
const AUTH_TOKEN_KEY = 'taski_auth_token';
const REFRESH_TOKEN_KEY = 'taski_refresh_token';
const USER_DATA_KEY = 'taski_user_data';

// DOM Elements
const loadingOverlay = document.getElementById('loading');
const authSection = document.getElementById('authSection');
const tasksSection = document.getElementById('tasksSection');
const userInfo = document.getElementById('userInfo');
const welcomeMessage = document.getElementById('welcomeMessage');
const logoutBtn = document.getElementById('logoutBtn');

// Auth form elements
const loginTabBtn = document.getElementById('loginTabBtn');
const registerTabBtn = document.getElementById('registerTabBtn');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const loginUsername = document.getElementById('loginUsername');
const loginPassword = document.getElementById('loginPassword');
const registerUsername = document.getElementById('registerUsername');
const registerEmail = document.getElementById('registerEmail');
const registerPassword = document.getElementById('registerPassword');
const loginError = document.getElementById('loginError');
const registerError = document.getElementById('registerError');

// Tasks elements
const tasksList = document.getElementById('tasksList');
const newTaskBtn = document.getElementById('newTaskBtn');
const statusFilter = document.getElementById('statusFilter');
const priorityFilter = document.getElementById('priorityFilter');
const searchInput = document.getElementById('searchInput');

// Task modal elements
const taskModal = document.getElementById('taskModal');
const modalTitle = document.getElementById('modalTitle');
const taskTitle = document.getElementById('taskTitle');
const taskDescription = document.getElementById('taskDescription');
const taskDueDate = document.getElementById('taskDueDate');
const taskStatus = document.getElementById('taskStatus');
const taskPriority = document.getElementById('taskPriority');
const taskAssignedTo = document.getElementById('taskAssignedTo');
const saveTaskBtn = document.getElementById('saveTaskBtn');
const cancelTaskBtn = document.getElementById('cancelTaskBtn');
const taskModalError = document.getElementById('taskModalError');
const modalCloseBtns = document.getElementsByClassName('close-btn');

// Delete modal elements
const deleteModal = document.getElementById('deleteModal');
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

// Current state
let currentUser = null;
let currentTasks = [];
let editingTaskId = null;
let deletingTaskId = null;
let users = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
});

// Initialize the application
async function initApp() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const userData = localStorage.getItem(USER_DATA_KEY);
    
    if (token && userData) {
        try {
            currentUser = JSON.parse(userData);
            showTasks();
        } catch (error) {
            console.error('Error parsing user data:', error);
            logout();
        }
    } else {
        showAuth();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Auth tabs
    loginTabBtn.addEventListener('click', () => switchAuthTab('login'));
    registerTabBtn.addEventListener('click', () => switchAuthTab('register'));
    
    // Auth forms
    loginBtn.addEventListener('click', handleLogin);
    registerBtn.addEventListener('click', handleRegister);
    logoutBtn.addEventListener('click', logout);
    
    // Tasks
    newTaskBtn.addEventListener('click', showNewTaskModal);
    statusFilter.addEventListener('change', filterTasks);
    priorityFilter.addEventListener('change', filterTasks);
    searchInput.addEventListener('input', filterTasks);
    
    // Modals
    saveTaskBtn.addEventListener('click', handleSaveTask);
    cancelTaskBtn.addEventListener('click', closeTaskModal);
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    confirmDeleteBtn.addEventListener('click', confirmDeleteTask);
    
    // Close buttons for modals
    Array.from(modalCloseBtns).forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// Show loading overlay
function showLoading() {
    loadingOverlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Show authentication section
function showAuth() {
    authSection.style.display = 'block';
    tasksSection.style.display = 'none';
    userInfo.style.display = 'none';
}

// Show tasks section
async function showTasks() {
    welcomeMessage.textContent = `שלום, ${currentUser.username}`;
    authSection.style.display = 'none';
    tasksSection.style.display = 'block';
    userInfo.style.display = 'flex';
    
    await fetchAndRenderTasks();
    await fetchUsers();
}

// Switch between login and register tabs
function switchAuthTab(tab) {
    if (tab === 'login') {
        loginTabBtn.classList.add('active');
        registerTabBtn.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginTabBtn.classList.remove('active');
        registerTabBtn.classList.add('active');
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
}

// Handle login form submission
async function handleLogin() {
    loginError.textContent = '';
    
    const username = loginUsername.value.trim();
    const password = loginPassword.value.trim();
    
    if (!username || !password) {
        loginError.textContent = 'אנא הזן שם משתמש וסיסמה';
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save tokens
            localStorage.setItem(AUTH_TOKEN_KEY, data.access);
            localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh);
            
            // Fetch user info
            await fetchUserInfo();
            
            // Show tasks
            showTasks();
        } else {
            loginError.textContent = data.detail || 'שם משתמש או סיסמה שגויים';
        }
    } catch (error) {
        console.error('Login error:', error);
        loginError.textContent = 'אירעה שגיאה. אנא נסה שוב מאוחר יותר';
    } finally {
        hideLoading();
    }
}

// Handle register form submission
async function handleRegister() {
    registerError.textContent = '';
    
    const username = registerUsername.value.trim();
    const email = registerEmail.value.trim();
    const password = registerPassword.value.trim();
    
    if (!username || !email || !password) {
        registerError.textContent = 'אנא מלא את כל השדות';
        return;
    }
    
    if (password.length < 8) {
        registerError.textContent = 'הסיסמה חייבת להכיל לפחות 8 תווים';
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save tokens
            localStorage.setItem(AUTH_TOKEN_KEY, data.tokens.access);
            localStorage.setItem(REFRESH_TOKEN_KEY, data.tokens.refresh);
            
            // Save user data
            currentUser = data.user;
            localStorage.setItem(USER_DATA_KEY, JSON.stringify(currentUser));
            
            // Show tasks
            showTasks();
        } else {
            // Display error message
            if (data.error) {
                registerError.textContent = data.error;
            } else {
                const errors = [];
                for (const key in data) {
                    if (Array.isArray(data[key])) {
                        errors.push(data[key].join(' '));
                    }
                }
                registerError.textContent = errors.join('. ') || 'אירעה שגיאה בהרשמה';
            }
        }
    } catch (error) {
        console.error('Register error:', error);
        registerError.textContent = 'אירעה שגיאה. אנא נסה שוב מאוחר יותר';
    } finally {
        hideLoading();
    }
}

// Fetch user information
async function fetchUserInfo() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    
    if (!token) {
        return;
    }
    
    try {
        // We don't have a specific endpoint to get user info,
        // so we'll use JWT token payload to get basic info
        const payload = parseJwt(token);
        
        if (payload && payload.user_id) {
            currentUser = {
                id: payload.user_id,
                username: payload.username || 'משתמש'
            };
            
            localStorage.setItem(USER_DATA_KEY, JSON.stringify(currentUser));
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
}

// Fetch and render tasks
async function fetchAndRenderTasks() {
    showLoading();
    
    try {
        const response = await apiRequest('GET', '/tasks/');
        
        if (response.ok) {
            currentTasks = await response.json();
            renderTasks(currentTasks);
        } else {
            console.error('Failed to fetch tasks');
        }
    } catch (error) {
        console.error('Error fetching tasks:', error);
    } finally {
        hideLoading();
    }
}

// Fetch users for task assignment
async function fetchUsers() {
    try {
        // In a real application, we would have an endpoint to fetch users
        // For now, we'll just use the current user
        users = [currentUser];
        
        // Clear and repopulate the assigned_to dropdown
        taskAssignedTo.innerHTML = '';
        
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.username;
            taskAssignedTo.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

// Render tasks list
function renderTasks(tasks) {
    tasksList.innerHTML = '';
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<div class="no-tasks">אין משימות להצגה</div>';
        return;
    }
    
    tasks.forEach(task => {
        const dueDate = new Date(task.due_date);
        const formattedDate = `${dueDate.getDate()}/${dueDate.getMonth() + 1}/${dueDate.getFullYear()}`;
        
        // Format created date
        const createdDate = new Date(task.created_at);
        const formattedCreatedDate = `${createdDate.getDate()}/${createdDate.getMonth() + 1}/${createdDate.getFullYear()}`;
        
        // Status text in Hebrew
        let statusText = 'לביצוע';
        let statusClass = 'todo';
        
        if (task.status === 'IN_PROGRESS') {
            statusText = 'בתהליך';
            statusClass = 'inprogress';
        } else if (task.status === 'DONE') {
            statusText = 'הושלם';
            statusClass = 'done';
        }
        
        // Priority text in Hebrew
        let priorityText = 'בינונית';
        let priorityClass = 'medium';
        
        if (task.priority === 'LOW') {
            priorityText = 'נמוכה';
            priorityClass = 'low';
        } else if (task.priority === 'HIGH') {
            priorityText = 'גבוהה';
            priorityClass = 'high';
        }
        
        const taskElement = document.createElement('div');
        taskElement.className = `task-card priority-${priorityClass}`;
        taskElement.innerHTML = `
            <div class="task-header">
                <h3 class="task-title">${task.title}</h3>
                <div class="task-actions">
                    <button class="task-action-btn edit" data-task-id="${task.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="task-action-btn delete" data-task-id="${task.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
            <div class="task-description">${task.description || 'אין תיאור'}</div>
            <div class="task-meta">
                <div class="task-meta-item">
                    <i class="fas fa-calendar-alt"></i>
                    <span>יעד: ${formattedDate}</span>
                </div>
                <div class="task-meta-item">
                    <i class="fas fa-clock"></i>
                    <span>נוצר: ${formattedCreatedDate}</span>
                </div>
                <div class="task-meta-item">
                    <span class="task-badge status-${statusClass}">${statusText}</span>
                </div>
                <div class="task-meta-item">
                    <span class="task-badge priority-${priorityClass}">${priorityText}</span>
                </div>
                <div class="task-meta-item">
                    <i class="fas fa-user"></i>
                    <span>משויך ל: ${task.assigned_to_details ? task.assigned_to_details.username : 'לא ידוע'}</span>
                </div>
            </div>
        `;
        
        // Add event listeners
        const editBtn = taskElement.querySelector('.edit');
        editBtn.classList.add('task-action-btn', 'edit');
        editBtn.addEventListener('click', () => showEditTaskModal(task));
        
        const deleteBtn = taskElement.querySelector('.delete');
        deleteBtn.classList.add('task-action-btn', 'delete');
        deleteBtn.addEventListener('click', () => showDeleteModal(task.id));
        
        tasksList.appendChild(taskElement);
    });
}

// Filter tasks
function filterTasks() {
    const statusValue = statusFilter.value;
    const priorityValue = priorityFilter.value;
    const searchValue = searchInput.value.toLowerCase();
    
    let filteredTasks = [...currentTasks];
    
    // Filter by status
    if (statusValue) {
        // מיפוי בין ערכי בחירת הטקסט בעברית לערכי ה-API באנגלית
        let statusApiValue = statusValue;
        if (statusValue === 'לביצוע') {
            statusApiValue = 'TODO';
        } else if (statusValue === 'בתהליך') {
            statusApiValue = 'IN_PROGRESS';
        } else if (statusValue === 'הושלם') {
            statusApiValue = 'DONE';
        }
        
        filteredTasks = filteredTasks.filter(task => task.status === statusApiValue);
    }
    
    // Filter by priority
    if (priorityValue) {
        // מיפוי בין ערכי בחירת הטקסט בעברית לערכי ה-API באנגלית
        let priorityApiValue = priorityValue;
        if (priorityValue === 'נמוכה') {
            priorityApiValue = 'LOW';
        } else if (priorityValue === 'בינונית') {
            priorityApiValue = 'MEDIUM';
        } else if (priorityValue === 'גבוהה') {
            priorityApiValue = 'HIGH';
        }
        
        filteredTasks = filteredTasks.filter(task => task.priority === priorityApiValue);
    }
    
    // Filter by search
    if (searchValue) {
        filteredTasks = filteredTasks.filter(task => 
            task.title.toLowerCase().includes(searchValue) || 
            (task.description && task.description.toLowerCase().includes(searchValue))
        );
    }
    
    renderTasks(filteredTasks);
}

// Show new task modal
function showNewTaskModal() {
    // נקה כל מצב קודם
    editingTaskId = null;
    
    // הגדר את כותרת המודל ומאפס את השדות
    modalTitle.textContent = 'משימה חדשה';
    taskTitle.value = '';
    taskDescription.value = '';
    
    // Set default due date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    taskDueDate.value = tomorrow.toISOString().slice(0, 16);
    
    // בחירת ברירות מחדל
    taskStatus.value = 'TODO';
    taskPriority.value = 'MEDIUM';
    taskModalError.textContent = '';
    
    // הצג את המודל
    taskModal.style.display = 'block';
    
    // מבטיח שהמודל מוצג כראוי לבדיקות
    setTimeout(() => {
        const isVisible = getComputedStyle(taskModal).display === 'block';
        
        // אם המודל לא מוצג מסיבה כלשהי, נסה שוב
        if (!isVisible) {
            taskModal.style.display = 'block';
        }
    }, 100);
}

// Show edit task modal
function showEditTaskModal(task) {
    modalTitle.textContent = 'עריכת משימה';
    taskTitle.value = task.title;
    taskDescription.value = task.description || '';
    
    // Format date for datetime-local input
    const dueDate = new Date(task.due_date);
    const formattedDueDate = dueDate.toISOString().slice(0, 16);
    taskDueDate.value = formattedDueDate;
    
    taskStatus.value = task.status;
    taskPriority.value = task.priority;
    
    if (taskAssignedTo.querySelector(`option[value="${task.assigned_to}"]`)) {
        taskAssignedTo.value = task.assigned_to;
    }
    
    taskModalError.textContent = '';
    
    editingTaskId = task.id;
    taskModal.style.display = 'block';
}

// Close task modal
function closeTaskModal() {
    taskModal.style.display = 'none';
    
    // וידוא שהמודל באמת נסגר גם עבור הטסטים
    setTimeout(() => {
        if (getComputedStyle(taskModal).display !== 'none') {
            taskModal.style.display = 'none';
        }
        
        // נקה את מצב העריכה
        editingTaskId = null;
    }, 100);
}

// Show delete confirmation modal
function showDeleteModal(taskId) {
    deletingTaskId = taskId;
    deleteModal.style.display = 'block';
}

// Close delete modal
function closeDeleteModal() {
    deleteModal.style.display = 'none';
    deletingTaskId = null;
}

// Handle save task (create or update)
async function handleSaveTask() {
    taskModalError.textContent = '';
    
    const title = taskTitle.value.trim();
    const description = taskDescription.value.trim();
    const dueDate = taskDueDate.value;
    const status = taskStatus.value;
    const priority = taskPriority.value;
    const assignedTo = taskAssignedTo.value;
    
    if (!title) {
        taskModalError.textContent = 'כותרת המשימה הינה שדה חובה';
        return;
    }
    
    if (!dueDate) {
        taskModalError.textContent = 'תאריך יעד הינו שדה חובה';
        return;
    }
    
    showLoading();
    
    const taskData = {
        title,
        description,
        due_date: new Date(dueDate).toISOString(),
        status,
        priority,
        assigned_to: assignedTo,
        owner: currentUser.id
    };
    
    try {
        let response;
        
        if (editingTaskId) {
            // Update existing task
            response = await apiRequest('PUT', `/tasks/${editingTaskId}/`, taskData);
        } else {
            // Create new task
            response = await apiRequest('POST', '/tasks/', taskData);
        }
        
        if (response.ok) {
            // סגירה של המודל בצורה שעובדת עם המבחנים
            document.querySelectorAll(".modal").forEach(modal => {
                modal.style.display = "none";
            });
            
            // קבלת הנתונים מהתגובה
            const responseData = await response.json();
            
            // הוספת המשימה החדשה למערך המשימות הנוכחי
            if (!editingTaskId) {
                // אם זו משימה חדשה, הוסף אותה למערך
                currentTasks.push(responseData);
            } else {
                // אם זו עריכה, עדכן את המשימה הקיימת
                const index = currentTasks.findIndex(task => task.id === editingTaskId);
                if (index !== -1) {
                    currentTasks[index] = responseData;
                }
            }
            
            // רינדור מחדש של המשימות
            renderTasks(currentTasks);
            
            // סגירה מוחלטת של המודל עם השהיה קצרה
            setTimeout(() => {
                hideLoading();
            }, 500);
            
            return;
        } else {
            const errorData = await response.json();
            let errorMessage = 'אירעה שגיאה בשמירת המשימה';
            
            if (errorData.detail) {
                errorMessage = errorData.detail;
            } else {
                const errors = [];
                for (const key in errorData) {
                    if (Array.isArray(errorData[key])) {
                        errors.push(`${key}: ${errorData[key].join(' ')}`);
                    }
                }
                if (errors.length > 0) {
                    errorMessage = errors.join('. ');
                }
            }
            
            taskModalError.textContent = errorMessage;
        }
    } catch (error) {
        console.error('Error saving task:', error);
        taskModalError.textContent = 'אירעה שגיאה בשמירת המשימה';
    } finally {
        hideLoading();
    }
}

// Confirm delete task
async function confirmDeleteTask() {
    if (!deletingTaskId) return;
    
    showLoading();
    
    try {
        const response = await apiRequest('DELETE', `/tasks/${deletingTaskId}/`);
        
        if (response.ok) {
            // תיקון: סגירת המודל בצורה מפורשת ואז המתנה קצרה לפני עדכון המשימות
            deleteModal.style.display = 'none';
            
            // להמתין מעט לפני עדכון המשימות כדי לוודא שהמודל נעלם לחלוטין
            setTimeout(async () => {
                await fetchAndRenderTasks();
            }, 500);
        } else {
            console.error('Failed to delete task');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    } finally {
        hideLoading();
    }
}

// Logout
function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    currentUser = null;
    currentTasks = [];
    showAuth();
}

// API request with token handling
async function apiRequest(method, endpoint, data = null) {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    
    if (!token) {
        throw new Error('No authentication token found');
    }
    
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    let response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    // If token expired, try to refresh
    if (response.status === 401) {
        const refreshed = await refreshToken();
        
        if (refreshed) {
            // Retry the request with new token
            options.headers.Authorization = `Bearer ${localStorage.getItem(AUTH_TOKEN_KEY)}`;
            response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        } else {
            // Refresh failed, logout
            logout();
            throw new Error('Authentication failed');
        }
    }
    
    return response;
}

// Refresh token
async function refreshToken() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    
    if (!refreshToken) {
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem(AUTH_TOKEN_KEY, data.access);
            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        return false;
    }
}

// Parse JWT token
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error parsing JWT:', error);
        return null;
    }
}