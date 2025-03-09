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
        commentsTab: document.getElementById('comments-tab'),
        commentsList: document.getElementById('comments-list'),
        commentForm: document.getElementById('comment-form'),
        checklistTab: document.getElementById('checklist-tab'),
        checklistItems: document.getElementById('checklist-items'),
        checklistForm: document.getElementById('checklist-form'),
        checklistProgressValue: document.getElementById('checklist-progress-value'),
        checklistProgressText: document.getElementById('checklist-progress-text')
    },
    
    // Current filters
    filters: {
        status: '',
        priority: '',
        search: '',
        tag: ''
    },
    
    // Current tasks, comments, and checklist items
    tasks: [],
    comments: [],
    currentTaskId: null,
    editingCommentId: null,
    checklistItems: [],
    editingChecklistItemId: null,
    
    // Current users
    users: [],
    
    /**
     * Initialize the tasks module
     */
    init() {
        this.addEventListeners();
        this.initDragAndDrop();
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
        
        // Checklist form submission
        this.elements.checklistForm.addEventListener('submit', (e) => this.handleChecklistSubmit(e));
    },
    
    /**
     * Initialize drag and drop for checklist items
     */
    initDragAndDrop() {
        // This will be initialized when checklist items are loaded
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
        
        // Render each task with staggered animation
        this.tasks.forEach((task, index) => {
            const taskElement = this.createTaskElement(task);
            
            // Apply staggered animation delay
            taskElement.style.animationDelay = `${index * 0.05}s`;
            
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
                // Limit to maximum 4 tags to avoid overflow
                const displayTags = tags.slice(0, 4);
                const remainingCount = tags.length - 4;
                
                tagsHtml = `
                    <div class="task-tags">
                        ${displayTags.map(tag => `<span class="task-tag">${tag}</span>`).join('')}
                        ${remainingCount > 0 ? `<span class="task-tag">+${remainingCount} more</span>` : ''}
                    </div>
                `;
            }
        }
        
        // Create badges container for duration and checklist
        let badgesHtml = '';
        
        // Duration badge if present
        if (task.duration) {
            badgesHtml += `
                <div class="task-duration">
                    <i class="fas fa-clock"></i> ${task.duration} ${task.duration === 1 ? 'hour' : 'hours'}
                </div>
            `;
        }
        
        // Checklist progress badge if present
        if (task.checklist_items && task.checklist_items.length > 0) {
            const completionPercentage = task.checklist_completion || 0;
            badgesHtml += `
                <div class="task-checklist-badge" data-tab="checklist">
                    <i class="fas fa-tasks"></i> ${completionPercentage}% complete
                </div>
            `;
        }
        
        // Wrap badges in container if any exist
        if (badgesHtml) {
            badgesHtml = `<div class="badges-container">${badgesHtml}</div>`;
        }
        
        taskCard.innerHTML = `
            <div class="task-header">
                <h3 class="task-title" title="${task.title}">${task.title}</h3>
                <span class="task-status status-${task.status}">${this.formatStatus(task.status)}</span>
            </div>
            <div class="task-description">${task.description || 'No description provided.'}</div>
            <div class="task-meta">
                <div class="task-meta-row">
                    <div class="task-due-date ${isPastDue ? '' : 'future'}" title="Due date">
                        <i class="far fa-calendar-alt"></i> ${formattedDate}
                    </div>
                    <div class="task-assigned" title="Assigned to: ${task.assigned_to_details.username}">
                        <i class="far fa-user"></i> ${task.assigned_to_details.username}
                    </div>
                </div>
                ${tagsHtml}
                ${badgesHtml}
            </div>
            <div class="task-actions">
                <button class="btn btn-primary task-btn edit-task">
                    <i class="fas fa-edit"></i> Edit
                </button>
            </div>
        `;
        
        // Add click event for editing
        taskCard.querySelector('.edit-task').addEventListener('click', () => {
            this.showTaskModal(task);
        });
        
        // Add click event for checklist badge
        const checklistBadge = taskCard.querySelector('.task-checklist-badge');
        if (checklistBadge) {
            checklistBadge.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent card click
                this.showTaskModal(task, 'checklist');
            });
        }
        
        // Make the entire card clickable for convenience
        taskCard.addEventListener('click', (e) => {
            // Don't trigger if clicked on the edit button or checklist badge
            if (!e.target.closest('.edit-task') && !e.target.closest('.task-checklist-badge')) {
                this.showTaskModal(task);
            }
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
    showTaskModal(task = null, activeTab = 'details') {
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
            
            // Load comments and checklist data
            this.loadComments(task.id);
            this.loadChecklist(task.id);
            
            // Make all tabs visible for existing tasks
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.style.display = 'flex';
            });
            
            // Activate the specified tab (defaults to details)
            this.activateTab(activeTab);
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
            
            // Hide checklist and comments tabs for new tasks
            document.querySelectorAll('.tab-btn:not([data-tab="details"])').forEach(btn => {
                btn.style.display = 'none';
            });
            
            // Make sure we're on the details tab
            this.activateTab('details');
        }
        
        // Set up tab event listeners
        this.setupTabNavigation();
        
        // Show modal
        this.elements.taskModal.classList.remove('hidden');
    },
    
    /**
     * Set up tab navigation event listeners
     */
    setupTabNavigation() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        // Remove existing event listeners (to prevent duplicates)
        tabBtns.forEach(btn => {
            btn.replaceWith(btn.cloneNode(true));
        });
        
        // Add event listeners to fresh buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.getAttribute('data-tab');
                this.activateTab(tabName);
            });
        });
    },
    
    /**
     * Activate a specific tab
     */
    activateTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
        });
        
        // Show active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            const isActive = content.id === `${tabName}-tab`;
            content.classList.toggle('active', isActive);
        });
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
            
            // Get more detailed error info if available
            let errorMessage = 'Failed to add comment. Please try again.';
            if (error.message) {
                errorMessage = `Error: ${error.message}`;
            }
            
            alert(errorMessage);
            
            // Log detailed information for debugging
            console.log('Comment content:', content);
            console.log('Content length:', content.length);
            console.log('Content encoding:', encodeURIComponent(content));
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
    },
    
    /**
     * Load checklist for a task
     */
    async loadChecklist(taskId) {
        try {
            // Clear existing checklist items
            this.checklistItems = [];
            this.renderChecklist();
            
            // Show loading indicator
            this.elements.checklistItems.innerHTML = '<div class="loader"></div>';
            
            // Load checklist items
            this.checklistItems = await API.getTaskChecklist(taskId);
            
            // Render checklist
            this.renderChecklist();
            this.updateChecklistProgress();
            
            // Initialize drag and drop
            this.initChecklistDragAndDrop();
        } catch (error) {
            console.error('Error loading checklist:', error);
            this.elements.checklistItems.innerHTML = '<div class="error-message">Failed to load checklist</div>';
        }
    },
    
    /**
     * Render checklist items to the DOM
     */
    renderChecklist() {
        const checklistContainer = this.elements.checklistItems;
        
        // Clear current checklist
        checklistContainer.innerHTML = '';
        
        if (this.checklistItems.length === 0) {
            checklistContainer.innerHTML = '<div class="no-items">No checklist items yet</div>';
            return;
        }
        
        // Sort items by position
        const sortedItems = [...this.checklistItems].sort((a, b) => a.position - b.position);
        
        // Render each item
        sortedItems.forEach(item => {
            const checklistElement = this.createChecklistElement(item);
            checklistContainer.appendChild(checklistElement);
        });
    },
    
    /**
     * Create a checklist item element
     */
    createChecklistElement(item) {
        const itemElement = document.createElement('div');
        itemElement.className = 'checklist-item';
        itemElement.dataset.id = item.id;
        
        // If currently editing this item, show edit form instead
        if (this.editingChecklistItemId === item.id) {
            itemElement.innerHTML = `
                <div class="checklist-item-drag"><i class="fas fa-grip-lines"></i></div>
                <form class="checklist-edit-form">
                    <input type="text" class="edit-checklist-text" value="${item.text}" required>
                    <button type="button" class="btn cancel-edit">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save</button>
                </form>
            `;
            
            // Add event listeners for edit form
            const editForm = itemElement.querySelector('.checklist-edit-form');
            const cancelBtn = itemElement.querySelector('.cancel-edit');
            
            editForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const text = itemElement.querySelector('.edit-checklist-text').value;
                this.updateChecklistItem(item.id, { text });
            });
            
            cancelBtn.addEventListener('click', () => {
                this.editingChecklistItemId = null;
                this.renderChecklist();
            });
            
            return itemElement;
        }
        
        // Standard checklist item display
        itemElement.innerHTML = `
            <div class="checklist-item-drag"><i class="fas fa-grip-lines"></i></div>
            <input type="checkbox" class="checklist-item-checkbox" ${item.is_completed ? 'checked' : ''}>
            <div class="checklist-item-text ${item.is_completed ? 'completed' : ''}">${item.text}</div>
            <div class="checklist-item-actions">
                <button type="button" class="edit-item"><i class="fas fa-edit"></i></button>
                <button type="button" class="delete-item"><i class="fas fa-trash-alt"></i></button>
            </div>
        `;
        
        // Add event listeners
        const checkbox = itemElement.querySelector('.checklist-item-checkbox');
        const editBtn = itemElement.querySelector('.edit-item');
        const deleteBtn = itemElement.querySelector('.delete-item');
        
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                this.completeChecklistItem(item.id);
            } else {
                this.incompleteChecklistItem(item.id);
            }
        });
        
        editBtn.addEventListener('click', () => {
            this.editingChecklistItemId = item.id;
            this.renderChecklist();
        });
        
        deleteBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this checklist item?')) {
                this.deleteChecklistItem(item.id);
            }
        });
        
        return itemElement;
    },
    
    /**
     * Initialize drag and drop for checklist items
     */
    initChecklistDragAndDrop() {
        const container = this.elements.checklistItems;
        const items = container.querySelectorAll('.checklist-item');
        
        if (!items.length) return;
        
        items.forEach(item => {
            const dragHandle = item.querySelector('.checklist-item-drag');
            
            dragHandle.addEventListener('mousedown', (e) => {
                e.preventDefault();
                
                const startY = e.clientY;
                const itemHeight = item.offsetHeight;
                const itemInitialIndex = Array.from(container.children).indexOf(item);
                
                item.classList.add('dragging');
                
                const onMouseMove = (e) => {
                    const currentY = e.clientY;
                    const deltaY = currentY - startY;
                    const moveCount = Math.round(deltaY / itemHeight);
                    
                    let newIndex = itemInitialIndex + moveCount;
                    newIndex = Math.max(0, Math.min(newIndex, container.children.length - 1));
                    
                    if (newIndex !== Array.from(container.children).indexOf(item)) {
                        // Move item in the DOM
                        if (newIndex === 0) {
                            container.prepend(item);
                        } else if (newIndex === container.children.length - 1) {
                            container.appendChild(item);
                        } else {
                            const referenceNode = container.children[newIndex];
                            container.insertBefore(item, referenceNode);
                        }
                    }
                };
                
                const onMouseUp = () => {
                    item.classList.remove('dragging');
                    document.removeEventListener('mousemove', onMouseMove);
                    document.removeEventListener('mouseup', onMouseUp);
                    
                    // Save the new order
                    const newOrder = Array.from(container.children)
                        .map(el => parseInt(el.dataset.id))
                        .filter(id => !isNaN(id));
                    
                    this.reorderChecklistItems(newOrder);
                };
                
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            });
        });
    },
    
    /**
     * Handle checklist form submission
     */
    async handleChecklistSubmit(event) {
        event.preventDefault();
        
        if (!this.currentTaskId) return;
        
        const text = document.getElementById('checklist-text').value;
        if (!text.trim()) return;
        
        try {
            // Disable form
            const submitBtn = this.elements.checklistForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Create checklist item
            const newItem = await API.createChecklistItem(this.currentTaskId, text);
            
            // Add to checklist and render
            this.checklistItems.push(newItem);
            this.renderChecklist();
            this.updateChecklistProgress();
            this.initChecklistDragAndDrop();
            
            // Clear form
            document.getElementById('checklist-text').value = '';
        } catch (error) {
            console.error('Error creating checklist item:', error);
            alert('Failed to add checklist item. Please try again.');
        } finally {
            // Re-enable form
            const submitBtn = this.elements.checklistForm.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-plus"></i>';
        }
    },
    
    /**
     * Update a checklist item
     */
    async updateChecklistItem(itemId, data) {
        if (!this.currentTaskId) return;
        
        try {
            // Update item in API
            const updatedItem = await API.updateChecklistItem(this.currentTaskId, itemId, data);
            
            // Update in local array
            const index = this.checklistItems.findIndex(item => item.id === itemId);
            if (index !== -1) {
                this.checklistItems[index] = updatedItem;
            }
            
            // Exit editing mode and re-render
            this.editingChecklistItemId = null;
            this.renderChecklist();
            this.updateChecklistProgress();
        } catch (error) {
            console.error('Error updating checklist item:', error);
            alert('Failed to update checklist item. Please try again.');
        }
    },
    
    /**
     * Mark a checklist item as complete
     */
    async completeChecklistItem(itemId) {
        if (!this.currentTaskId) return;
        
        try {
            // Update item in API
            const updatedItem = await API.completeChecklistItem(this.currentTaskId, itemId);
            
            // Update in local array
            const index = this.checklistItems.findIndex(item => item.id === itemId);
            if (index !== -1) {
                this.checklistItems[index] = updatedItem;
            }
            
            // Update UI
            this.updateChecklistProgress();
            
            // No need to re-render, just update the item's appearance
            const itemElement = this.elements.checklistItems.querySelector(`[data-id="${itemId}"]`);
            if (itemElement) {
                const textElement = itemElement.querySelector('.checklist-item-text');
                if (textElement) {
                    textElement.classList.add('completed');
                }
            }
        } catch (error) {
            console.error('Error completing checklist item:', error);
            
            // Revert checkbox state
            const itemElement = this.elements.checklistItems.querySelector(`[data-id="${itemId}"]`);
            if (itemElement) {
                const checkbox = itemElement.querySelector('.checklist-item-checkbox');
                if (checkbox) {
                    checkbox.checked = false;
                }
            }
        }
    },
    
    /**
     * Mark a checklist item as incomplete
     */
    async incompleteChecklistItem(itemId) {
        if (!this.currentTaskId) return;
        
        try {
            // Update item in API
            const updatedItem = await API.incompleteChecklistItem(this.currentTaskId, itemId);
            
            // Update in local array
            const index = this.checklistItems.findIndex(item => item.id === itemId);
            if (index !== -1) {
                this.checklistItems[index] = updatedItem;
            }
            
            // Update UI
            this.updateChecklistProgress();
            
            // No need to re-render, just update the item's appearance
            const itemElement = this.elements.checklistItems.querySelector(`[data-id="${itemId}"]`);
            if (itemElement) {
                const textElement = itemElement.querySelector('.checklist-item-text');
                if (textElement) {
                    textElement.classList.remove('completed');
                }
            }
        } catch (error) {
            console.error('Error incompleting checklist item:', error);
            
            // Revert checkbox state
            const itemElement = this.elements.checklistItems.querySelector(`[data-id="${itemId}"]`);
            if (itemElement) {
                const checkbox = itemElement.querySelector('.checklist-item-checkbox');
                if (checkbox) {
                    checkbox.checked = true;
                }
            }
        }
    },
    
    /**
     * Reorder checklist items
     */
    async reorderChecklistItems(newOrder) {
        if (!this.currentTaskId || !newOrder.length) return;
        
        try {
            // Update items in API
            const updatedItems = await API.reorderChecklistItems(this.currentTaskId, newOrder);
            
            // Update local array
            this.checklistItems = updatedItems;
            
            // No need to re-render as the DOM is already in the correct order
        } catch (error) {
            console.error('Error reordering checklist items:', error);
            // Re-render to restore original order
            this.renderChecklist();
        }
    },
    
    /**
     * Delete a checklist item
     */
    async deleteChecklistItem(itemId) {
        if (!this.currentTaskId) return;
        
        try {
            // Delete item from API
            await API.deleteChecklistItem(this.currentTaskId, itemId);
            
            // Remove from local array
            this.checklistItems = this.checklistItems.filter(item => item.id !== itemId);
            
            // Re-render checklist
            this.renderChecklist();
            this.updateChecklistProgress();
            this.initChecklistDragAndDrop();
        } catch (error) {
            console.error('Error deleting checklist item:', error);
            alert('Failed to delete checklist item. Please try again.');
        }
    },
    
    /**
     * Update checklist progress display
     */
    updateChecklistProgress() {
        const items = this.checklistItems;
        
        if (!items.length) {
            this.elements.checklistProgressValue.style.width = '0%';
            this.elements.checklistProgressText.textContent = '0%';
            return;
        }
        
        const completed = items.filter(item => item.is_completed).length;
        const percentage = Math.round((completed / items.length) * 100);
        
        this.elements.checklistProgressValue.style.width = `${percentage}%`;
        this.elements.checklistProgressText.textContent = `${percentage}%`;
    }
};

// Initialize in main.js instead
// Tasks.init(); 