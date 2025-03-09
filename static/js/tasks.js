/**
 * Tasks Module for Taski App
 * Handles task listing, creation, editing, and deletion
 */

const Tasks = {
    // DOM elements
    elements: {
        taskList: document.getElementById('task-list'),
        emptyState: document.getElementById('empty-state'),
        taskModal: document.getElementById('task-modal'),
        taskForm: document.getElementById('task-form'),
        modalTitle: document.getElementById('modal-title'),
        deleteTaskBtn: document.getElementById('delete-task-btn'),
        createTaskBtn: document.getElementById('create-task-btn'),
        confirmModal: document.getElementById('confirm-modal'),
        confirmAction: document.getElementById('confirm-action'),
        confirmCancel: document.getElementById('confirm-cancel'),
        confirmTitle: document.getElementById('confirm-title'),
        confirmMessage: document.getElementById('confirm-message'),
        assignedToSelect: document.getElementById('task-assigned-to'),
        searchBtn: document.getElementById('search-btn'),
        taskSearch: document.getElementById('task-search'),
        statusFilter: document.getElementById('status-filter'),
        priorityFilter: document.getElementById('priority-filter'),
        tagFilter: document.getElementById('tag-filter'),
        commentsSection: document.getElementById('task-comments'),
        commentsList: document.getElementById('comments-list'),
        commentForm: document.getElementById('comment-form')
    },
    
    // Current filters
    filters: {
        status: '',
        priority: '',
        search: '',
        tag: ''
    },
    
    // Current tasks and comments
    tasks: [],
    comments: [],
    currentTaskId: null,
    editingCommentId: null,
    
    // Current users
    users: [],
    
    /**
     * Initialize the tasks module
     */
    init() {
        this.addEventListeners();
    },
    
    /**
     * Add event listeners for task-related elements
     */
    addEventListeners() {
        // Create new task button
        this.elements.createTaskBtn.addEventListener('click', () => this.showTaskModal());
        
        // Task form submission
        this.elements.taskForm.addEventListener('submit', (e) => this.handleTaskSubmit(e));
        
        // Delete task button
        this.elements.deleteTaskBtn.addEventListener('click', () => this.showDeleteConfirmation());
        
        // Close modal buttons
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => {
                this.elements.taskModal.classList.add('hidden');
                this.elements.confirmModal.classList.add('hidden');
            });
        });
        
        // Confirm modal actions
        this.elements.confirmCancel.addEventListener('click', () => {
            this.elements.confirmModal.classList.add('hidden');
        });
        
        this.elements.confirmAction.addEventListener('click', () => {
            this.confirmDelete();
        });
        
        // Filter listeners
        this.elements.searchBtn.addEventListener('click', () => this.applyFilters());
        this.elements.taskSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });
        
        this.elements.statusFilter.addEventListener('change', () => this.applyFilters());
        this.elements.priorityFilter.addEventListener('change', () => this.applyFilters());
        this.elements.tagFilter.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });
        
        // Comment form submission
        this.elements.commentForm.addEventListener('submit', (e) => this.handleCommentSubmit(e));
    },
    
    /**
     * Apply current filters and reload tasks
     */
    applyFilters() {
        this.filters.search = this.elements.taskSearch.value.trim();
        this.filters.status = this.elements.statusFilter.value;
        this.filters.priority = this.elements.priorityFilter.value;
        this.filters.tag = this.elements.tagFilter.value.trim();
        
        this.loadTasks();
    },
    
    /**
     * Load tasks from API
     */
    async loadTasks() {
        try {
            this.showLoader();
            
            // Load users for assign dropdown
            if (this.users.length === 0) {
                await this.loadUsers();
            }
            
            // Load tasks with current filters
            this.tasks = await API.getTasks(this.filters);
            
            // Render tasks
            this.renderTasks();
        } catch (error) {
            console.error('Error loading tasks:', error);
            alert('Failed to load tasks. Please try again.');
        } finally {
            this.hideLoader();
        }
    },
    
    /**
     * Render tasks to the UI
     */
    renderTasks() {
        const taskList = this.elements.taskList;
        
        // Clear current tasks
        taskList.innerHTML = '';
        
        if (this.tasks.length === 0) {
            // Show empty state
            this.elements.emptyState.classList.remove('hidden');
            taskList.classList.add('hidden');
            return;
        }
        
        // Hide empty state, show task list
        this.elements.emptyState.classList.add('hidden');
        taskList.classList.remove('hidden');
        
        // Render each task
        this.tasks.forEach(task => {
            const taskElement = this.createTaskElement(task);
            taskList.appendChild(taskElement);
        });
    },
    
    /**
     * Create a task card element
     */
    createTaskElement(task) {
        const taskCard = document.createElement('div');
        taskCard.className = `task-card priority-${task.priority}`;
        taskCard.dataset.id = task.id;
        
        // Format due date
        const dueDate = new Date(task.due_date);
        const isPastDue = dueDate < new Date();
        const formattedDate = dueDate.toLocaleDateString();
        
        // Create tags elements if there are tags
        let tagsHtml = '';
        if (task.tags) {
            const tags = task.tags.split(',').map(tag => tag.trim()).filter(Boolean);
            if (tags.length > 0) {
                tagsHtml = `
                    <div class="task-tags">
                        ${tags.map(tag => `<span class="task-tag">${tag}</span>`).join('')}
                    </div>
                `;
            }
        }
        
        // Duration badge if present
        let durationHtml = '';
        if (task.duration) {
            durationHtml = `
                <div class="task-duration">
                    <i class="fas fa-clock"></i> ${task.duration} ${task.duration === 1 ? 'hour' : 'hours'}
                </div>
            `;
        }
        
        taskCard.innerHTML = `
            <div class="task-header">
                <h3 class="task-title">${task.title}</h3>
                <span class="task-status status-${task.status}">${this.formatStatus(task.status)}</span>
            </div>
            <div class="task-description">${task.description || 'No description provided.'}</div>
            <div class="task-meta">
                <div class="task-meta-row">
                    <div class="task-due-date ${isPastDue ? '' : 'future'}">
                        <i class="far fa-calendar-alt"></i> ${formattedDate}
                    </div>
                    <div class="task-assigned">
                        <i class="far fa-user"></i> ${task.assigned_to_details.username}
                    </div>
                </div>
                ${tagsHtml}
                ${durationHtml}
            </div>
            <div class="task-actions">
                <button class="btn btn-primary task-btn edit-task">Edit</button>
            </div>
        `;
        
        // Add click event for editing
        taskCard.querySelector('.edit-task').addEventListener('click', () => {
            this.showTaskModal(task);
        });
        
        return taskCard;
    },
    
    /**
     * Format task status for display
     */
    formatStatus(status) {
        switch (status) {
            case 'TODO': return 'Todo';
            case 'IN_PROGRESS': return 'In Progress';
            case 'DONE': return 'Done';
            default: return status;
        }
    },
    
    /**
     * Load users from API (for assign dropdown)
     */
    async loadUsers() {
        // In a real app, this would be a separate API call
        // For now, we'll simply include the current user
        this.users = [API.user];
        
        // Update assigned to dropdown
        const select = this.elements.assignedToSelect;
        select.innerHTML = '';
        
        this.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.username;
            select.appendChild(option);
        });
    },
    
    /**
     * Show task modal for create/edit
     */
    showTaskModal(task = null) {
        const isEdit = !!task;
        this.currentTaskId = isEdit ? task.id : null;
        
        // Update modal title
        this.elements.modalTitle.textContent = isEdit ? 'Edit Task' : 'Create New Task';
        
        // Show/hide delete button
        this.elements.deleteTaskBtn.classList.toggle('hidden', !isEdit);
        
        // Reset form
        this.elements.taskForm.reset();
        
        // Fill form if editing
        if (isEdit) {
            document.getElementById('task-id').value = task.id;
            document.getElementById('task-title').value = task.title;
            document.getElementById('task-description').value = task.description || '';
            
            // Format date for input
            const dueDate = new Date(task.due_date);
            const formattedDate = dueDate.toISOString().slice(0, 16);
            document.getElementById('task-due-date').value = formattedDate;
            
            document.getElementById('task-duration').value = task.duration || '';
            document.getElementById('task-status').value = task.status;
            document.getElementById('task-priority').value = task.priority;
            document.getElementById('task-tags').value = task.tags || '';
            document.getElementById('task-assigned-to').value = task.assigned_to;
            
            // Load and show comments for existing task
            this.elements.commentsSection.classList.remove('hidden');
            this.loadComments(task.id);
        } else {
            // Default values for new task
            document.getElementById('task-id').value = '';
            document.getElementById('task-assigned-to').value = API.user.id;
            document.getElementById('task-status').value = 'TODO';
            document.getElementById('task-priority').value = 'MEDIUM';
            
            // Set default due date to tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            document.getElementById('task-due-date').value = tomorrow.toISOString().slice(0, 16);
            
            // Hide comments section for new task
            this.elements.commentsSection.classList.add('hidden');
        }
        
        // Show modal
        this.elements.taskModal.classList.remove('hidden');
    },
    
    /**
     * Handle task form submission
     */
    async handleTaskSubmit(event) {
        event.preventDefault();
        
        // Get task data from form
        const taskId = document.getElementById('task-id').value;
        const taskData = {
            title: document.getElementById('task-title').value,
            description: document.getElementById('task-description').value,
            due_date: document.getElementById('task-due-date').value,
            status: document.getElementById('task-status').value,
            priority: document.getElementById('task-priority').value,
            assigned_to: document.getElementById('task-assigned-to').value,
            tags: document.getElementById('task-tags').value,
        };
        
        // Add duration if provided
        const duration = document.getElementById('task-duration').value;
        if (duration) {
            taskData.duration = parseFloat(duration);
        }
        
        // Add owner for new tasks
        if (!taskId) {
            taskData.owner = API.user.id;
        }
        
        try {
            // Show loader
            this.showModalLoader();
            
            if (taskId) {
                // Update existing task
                await API.updateTask(taskId, taskData);
            } else {
                // Create new task
                await API.createTask(taskData);
            }
            
            // Reload tasks and close modal
            await this.loadTasks();
            this.elements.taskModal.classList.add('hidden');
        } catch (error) {
            console.error('Error saving task:', error);
            alert('Failed to save task. Please try again.');
        } finally {
            this.hideModalLoader();
        }
    },
    
    /**
     * Show delete confirmation
     */
    showDeleteConfirmation() {
        const taskId = document.getElementById('task-id').value;
        if (!taskId) return;
        
        this.elements.confirmTitle.textContent = 'Delete Task';
        this.elements.confirmMessage.textContent = 'Are you sure you want to delete this task? This action cannot be undone.';
        this.elements.confirmAction.textContent = 'Delete';
        
        // Store task ID for deletion
        this.elements.confirmAction.dataset.taskId = taskId;
        
        // Show confirmation modal
        this.elements.confirmModal.classList.remove('hidden');
    },
    
    /**
     * Confirm and execute task deletion
     */
    async confirmDelete() {
        const taskId = this.elements.confirmAction.dataset.taskId;
        if (!taskId) return;
        
        try {
            // Show loader
            this.showModalLoader();
            
            // Delete task
            await API.deleteTask(taskId);
            
            // Reload tasks and close modals
            await this.loadTasks();
            this.elements.confirmModal.classList.add('hidden');
            this.elements.taskModal.classList.add('hidden');
        } catch (error) {
            console.error('Error deleting task:', error);
            alert('Failed to delete task. Please try again.');
        } finally {
            this.hideModalLoader();
        }
    },
    
    /**
     * Show loader in the task list
     */
    showLoader() {
        // Clear current list and show loader
        this.elements.taskList.innerHTML = '';
        this.elements.emptyState.classList.add('hidden');
        
        const loader = document.createElement('div');
        loader.className = 'loader';
        loader.id = 'task-loader';
        this.elements.taskList.appendChild(loader);
        this.elements.taskList.classList.remove('hidden');
    },
    
    /**
     * Hide task list loader
     */
    hideLoader() {
        const loader = document.getElementById('task-loader');
        if (loader) {
            loader.remove();
        }
    },
    
    /**
     * Show loader in the modal
     */
    showModalLoader() {
        // Disable form inputs
        const form = this.elements.taskForm;
        Array.from(form.elements).forEach(el => {
            el.disabled = true;
        });
        
        // Add loader
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<span class="loader-small"></span> Saving...';
    },
    
    /**
     * Hide modal loader
     */
    hideModalLoader() {
        // Re-enable form inputs
        const form = this.elements.taskForm;
        Array.from(form.elements).forEach(el => {
            el.disabled = false;
        });
        
        // Restore button text
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Save Task';
    },
    
    /**
     * Load comments for a task
     */
    async loadComments(taskId) {
        try {
            // Clear existing comments
            this.comments = [];
            this.renderComments();
            
            // Show loading indicator
            this.elements.commentsList.innerHTML = '<div class="loader"></div>';
            
            // Load comments
            this.comments = await API.getTaskComments(taskId);
            
            // Render comments
            this.renderComments();
        } catch (error) {
            console.error('Error loading comments:', error);
            this.elements.commentsList.innerHTML = '<div class="error-message">Failed to load comments</div>';
        }
    },
    
    /**
     * Render comments to the comments list
     */
    renderComments() {
        const commentsList = this.elements.commentsList;
        
        // Clear current comments
        commentsList.innerHTML = '';
        
        if (this.comments.length === 0) {
            commentsList.innerHTML = '<div class="no-comments">No comments yet</div>';
            return;
        }
        
        // Sort comments by created date (oldest first)
        const sortedComments = [...this.comments].sort((a, b) => 
            new Date(a.created_at) - new Date(b.created_at)
        );
        
        // Render each comment
        sortedComments.forEach(comment => {
            const commentElement = this.createCommentElement(comment);
            commentsList.appendChild(commentElement);
        });
    },
    
    /**
     * Create a comment element
     */
    createCommentElement(comment) {
        const commentCard = document.createElement('div');
        commentCard.className = 'comment-card';
        commentCard.dataset.id = comment.id;
        
        // Format date
        const commentDate = new Date(comment.created_at);
        const formattedDate = commentDate.toLocaleString();
        
        // Check if user is the author
        const isAuthor = comment.author === API.user.id;
        
        // If editing this comment, show edit form instead
        if (this.editingCommentId === comment.id) {
            commentCard.className = 'comment-card editing-comment';
            commentCard.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${comment.author_details.username}</span>
                    <span class="comment-date">${formattedDate}</span>
                </div>
                <form class="edit-comment-form">
                    <textarea class="edit-comment-content">${comment.content}</textarea>
                    <div class="comment-actions">
                        <button type="button" class="btn cancel-edit">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save</button>
                    </div>
                </form>
            `;
            
            // Add event listeners for edit form
            const editForm = commentCard.querySelector('.edit-comment-form');
            const cancelBtn = commentCard.querySelector('.cancel-edit');
            
            editForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const content = commentCard.querySelector('.edit-comment-content').value;
                this.updateComment(comment.id, content);
            });
            
            cancelBtn.addEventListener('click', () => {
                this.editingCommentId = null;
                this.renderComments();
            });
            
            return commentCard;
        }
        
        // Standard comment display
        commentCard.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${comment.author_details.username}</span>
                <span class="comment-date">${formattedDate}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            ${isAuthor ? `
                <div class="comment-actions">
                    <button class="btn edit-comment">Edit</button>
                    <button class="btn btn-danger delete-comment">Delete</button>
                </div>
            ` : ''}
        `;
        
        // Add event listeners for actions if user is author
        if (isAuthor) {
            commentCard.querySelector('.edit-comment').addEventListener('click', () => {
                this.editingCommentId = comment.id;
                this.renderComments();
            });
            
            commentCard.querySelector('.delete-comment').addEventListener('click', () => {
                this.deleteComment(comment.id);
            });
        }
        
        return commentCard;
    },
    
    /**
     * Handle comment form submission
     */
    async handleCommentSubmit(event) {
        event.preventDefault();
        
        if (!this.currentTaskId) return;
        
        const content = document.getElementById('comment-content').value;
        if (!content.trim()) return;
        
        try {
            // Disable form
            const submitBtn = this.elements.commentForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Adding...';
            
            // Create comment
            const newComment = await API.createTaskComment(this.currentTaskId, content);
            
            // Add to comments and render
            this.comments.push(newComment);
            this.renderComments();
            
            // Clear form
            document.getElementById('comment-content').value = '';
            
            // Highlight new comment
            setTimeout(() => {
                const newCommentEl = this.elements.commentsList.querySelector(`[data-id="${newComment.id}"]`);
                if (newCommentEl) {
                    newCommentEl.classList.add('new');
                    newCommentEl.scrollIntoView({ behavior: 'smooth' });
                }
            }, 100);
        } catch (error) {
            console.error('Error creating comment:', error);
            alert('Failed to add comment. Please try again.');
        } finally {
            // Re-enable form
            const submitBtn = this.elements.commentForm.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Add Comment';
        }
    },
    
    /**
     * Update an existing comment
     */
    async updateComment(commentId, content) {
        if (!this.currentTaskId || !commentId) return;
        
        try {
            // Update comment in API
            const updatedComment = await API.updateTaskComment(this.currentTaskId, commentId, content);
            
            // Update in local comments array
            const index = this.comments.findIndex(c => c.id === commentId);
            if (index !== -1) {
                this.comments[index] = updatedComment;
            }
            
            // Exit editing mode and re-render
            this.editingCommentId = null;
            this.renderComments();
        } catch (error) {
            console.error('Error updating comment:', error);
            alert('Failed to update comment. Please try again.');
        }
    },
    
    /**
     * Delete a comment
     */
    async deleteComment(commentId) {
        if (!this.currentTaskId || !commentId) return;
        
        if (!confirm('Are you sure you want to delete this comment?')) {
            return;
        }
        
        try {
            // Delete comment from API
            await API.deleteTaskComment(this.currentTaskId, commentId);
            
            // Remove from local comments array
            this.comments = this.comments.filter(c => c.id !== commentId);
            
            // Re-render comments
            this.renderComments();
        } catch (error) {
            console.error('Error deleting comment:', error);
            alert('Failed to delete comment. Please try again.');
        }
    }
};

// Initialize in main.js instead
// Tasks.init(); 