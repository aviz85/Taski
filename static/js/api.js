/**
 * API Service for Taski App
 * Handles all API requests and token management
 */

const API = {
    // Base API URL
    BASE_URL: '/api',
    
    // Storage keys
    TOKEN_KEY: 'taski_access_token',
    REFRESH_TOKEN_KEY: 'taski_refresh_token',
    USER_KEY: 'taski_user',
    
    /**
     * Initialize API - Check for tokens and user data
     */
    init() {
        this.accessToken = localStorage.getItem(this.TOKEN_KEY);
        this.refreshToken = localStorage.getItem(this.REFRESH_TOKEN_KEY);
        
        // Get stored user
        const storedUser = localStorage.getItem(this.USER_KEY);
        this.user = storedUser ? JSON.parse(storedUser) : null;
    },
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.accessToken;
    },
    
    /**
     * Get headers for API requests
     */
    getHeaders(includeToken = true) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (includeToken && this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }
        
        return headers;
    },
    
    /**
     * Handle API fetch with automatic token refresh
     */
    async fetchWithAuth(url, options = {}) {
        // Add auth header if not explicitly set
        if (!options.headers) {
            options.headers = this.getHeaders();
        }
        
        try {
            const response = await fetch(url, options);
            
            if (response.status === 401 && this.refreshToken) {
                // Try to refresh the token
                const refreshed = await this.refreshAccessToken();
                
                if (refreshed) {
                    // Retry with new token
                    options.headers = this.getHeaders();
                    return fetch(url, options);
                } else {
                    // Refresh failed, logout
                    this.logout();
                    throw new Error('Authentication failed. Please log in again.');
                }
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    /**
     * Refresh access token
     */
    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.BASE_URL}/auth/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh: this.refreshToken
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.accessToken = data.access;
                localStorage.setItem(this.TOKEN_KEY, this.accessToken);
                return true;
            } else {
                return false;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    },
    
    /**
     * Authenticate user (login)
     */
    async login(username, password) {
        try {
            const response = await fetch(`${this.BASE_URL}/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.accessToken = data.access;
                this.refreshToken = data.refresh;
                
                localStorage.setItem(this.TOKEN_KEY, this.accessToken);
                localStorage.setItem(this.REFRESH_TOKEN_KEY, this.refreshToken);
                
                await this.getCurrentUser();
                return { success: true };
            } else {
                return { 
                    success: false, 
                    error: data.detail || 'Login failed. Please check your credentials.' 
                };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { 
                success: false, 
                error: 'Login failed. Please try again later.' 
            };
        }
    },
    
    /**
     * Register new user
     */
    async register(username, email, password) {
        try {
            const response = await fetch(`${this.BASE_URL}/auth/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    email,
                    password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.accessToken = data.tokens.access;
                this.refreshToken = data.tokens.refresh;
                this.user = data.user;
                
                localStorage.setItem(this.TOKEN_KEY, this.accessToken);
                localStorage.setItem(this.REFRESH_TOKEN_KEY, this.refreshToken);
                localStorage.setItem(this.USER_KEY, JSON.stringify(this.user));
                
                return { success: true };
            } else {
                return { 
                    success: false, 
                    error: data.error || 'Registration failed. Please try again.' 
                };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { 
                success: false, 
                error: 'Registration failed. Please try again later.' 
            };
        }
    },
    
    /**
     * Get current user data
     */
    async getCurrentUser() {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/auth/user/`);
            
            if (response.ok) {
                const userData = await response.json();
                this.user = userData;
                localStorage.setItem(this.USER_KEY, JSON.stringify(userData));
                return userData;
            } 
            
            return null;
        } catch (error) {
            console.error('Get user data error:', error);
            return null;
        }
    },
    
    /**
     * Logout user
     */
    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.REFRESH_TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    },
    
    /**
     * Get all tasks
     */
    async getTasks(filters = {}) {
        try {
            // Build query params
            const queryParams = new URLSearchParams();
            
            // Add filters if provided
            if (filters.status) queryParams.append('status', filters.status);
            if (filters.priority) queryParams.append('priority', filters.priority);
            if (filters.search) queryParams.append('search', filters.search);
            if (filters.tag) queryParams.append('tag', filters.tag);
            
            const url = `${this.BASE_URL}/tasks/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
            const response = await this.fetchWithAuth(url);
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to fetch tasks');
            }
        } catch (error) {
            console.error('Get tasks error:', error);
            throw error;
        }
    },
    
    /**
     * Get single task by ID
     */
    async getTask(taskId) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/`);
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to fetch task');
            }
        } catch (error) {
            console.error(`Get task ${taskId} error:`, error);
            throw error;
        }
    },
    
    /**
     * Create new task
     */
    async createTask(taskData) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/`, {
                method: 'POST',
                body: JSON.stringify(taskData)
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create task');
            }
        } catch (error) {
            console.error('Create task error:', error);
            throw error;
        }
    },
    
    /**
     * Update existing task
     */
    async updateTask(taskId, taskData) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/`, {
                method: 'PATCH',
                body: JSON.stringify(taskData)
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update task');
            }
        } catch (error) {
            console.error(`Update task ${taskId} error:`, error);
            throw error;
        }
    },
    
    /**
     * Delete task
     */
    async deleteTask(taskId) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                return true;
            } else {
                throw new Error('Failed to delete task');
            }
        } catch (error) {
            console.error(`Delete task ${taskId} error:`, error);
            throw error;
        }
    },
    
    /**
     * Get comments for a task
     */
    async getTaskComments(taskId) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/comments/`);
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to fetch task comments');
            }
        } catch (error) {
            console.error(`Get comments for task ${taskId} error:`, error);
            throw error;
        }
    },
    
    /**
     * Create a new comment for a task
     */
    async createTaskComment(taskId, content) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/comments/`, {
                method: 'POST',
                body: JSON.stringify({
                    content
                })
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create comment');
            }
        } catch (error) {
            console.error(`Create comment for task ${taskId} error:`, error);
            throw error;
        }
    },
    
    /**
     * Update an existing comment
     */
    async updateTaskComment(taskId, commentId, content) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/comments/${commentId}/`, {
                method: 'PUT',
                body: JSON.stringify({
                    content
                })
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update comment');
            }
        } catch (error) {
            console.error(`Update comment ${commentId} error:`, error);
            throw error;
        }
    },
    
    /**
     * Delete a comment
     */
    async deleteTaskComment(taskId, commentId) {
        try {
            const response = await this.fetchWithAuth(`${this.BASE_URL}/tasks/${taskId}/comments/${commentId}/`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                return true;
            } else {
                throw new Error('Failed to delete comment');
            }
        } catch (error) {
            console.error(`Delete comment ${commentId} error:`, error);
            throw error;
        }
    }
};

// Initialize API service
API.init(); 