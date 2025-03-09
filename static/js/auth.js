/**
 * Authentication Module for Taski App
 * Handles login, register, and auth state
 */

const Auth = {
    // DOM elements
    elements: {
        authSection: document.getElementById('auth-section'),
        loginTab: document.getElementById('login-tab'),
        registerTab: document.getElementById('register-tab'),
        loginForm: document.getElementById('login-form'),
        registerForm: document.getElementById('register-form'),
        loginError: document.getElementById('login-error'),
        registerError: document.getElementById('register-error'),
        navContainer: document.getElementById('main-nav'),
        dashboardSection: document.getElementById('dashboard-section')
    },
    
    /**
     * Initialize the authentication module
     */
    init() {
        this.addEventListeners();
        this.updateAuthState();
    },
    
    /**
     * Add event listeners for auth forms and buttons
     */
    addEventListeners() {
        // Tab switching
        this.elements.loginTab.addEventListener('click', () => this.showLoginForm());
        this.elements.registerTab.addEventListener('click', () => this.showRegisterForm());
        
        // Form submissions
        this.elements.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.elements.registerForm.addEventListener('submit', (e) => this.handleRegister(e));
    },
    
    /**
     * Show the login form
     */
    showLoginForm() {
        this.elements.loginTab.classList.add('active');
        this.elements.registerTab.classList.remove('active');
        this.elements.loginForm.classList.remove('hidden');
        this.elements.registerForm.classList.add('hidden');
        this.elements.loginError.textContent = '';
    },
    
    /**
     * Show the register form
     */
    showRegisterForm() {
        this.elements.registerTab.classList.add('active');
        this.elements.loginTab.classList.remove('active');
        this.elements.registerForm.classList.remove('hidden');
        this.elements.loginForm.classList.add('hidden');
        this.elements.registerError.textContent = '';
    },
    
    /**
     * Handle login form submission
     */
    async handleLogin(event) {
        event.preventDefault();
        
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        this.elements.loginError.textContent = '';
        
        try {
            const result = await API.login(username, password);
            
            if (result.success) {
                this.updateAuthState();
                this.clearForms();
            } else {
                this.elements.loginError.textContent = result.error;
            }
        } catch (error) {
            console.error('Login error:', error);
            this.elements.loginError.textContent = 'An unexpected error occurred. Please try again.';
        }
    },
    
    /**
     * Handle register form submission
     */
    async handleRegister(event) {
        event.preventDefault();
        
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        
        this.elements.registerError.textContent = '';
        
        try {
            const result = await API.register(username, email, password);
            
            if (result.success) {
                this.updateAuthState();
                this.clearForms();
            } else {
                this.elements.registerError.textContent = result.error;
            }
        } catch (error) {
            console.error('Register error:', error);
            this.elements.registerError.textContent = 'An unexpected error occurred. Please try again.';
        }
    },
    
    /**
     * Update UI based on authentication state
     */
    updateAuthState() {
        if (API.isAuthenticated() && API.user) {
            // User is logged in
            this.showAuthenticatedUI();
        } else {
            // User is not logged in
            this.showUnauthenticatedUI();
        }
    },
    
    /**
     * Show UI for authenticated users
     */
    showAuthenticatedUI() {
        // Hide auth section, show dashboard
        this.elements.authSection.classList.add('hidden');
        this.elements.dashboardSection.classList.remove('hidden');
        
        // Update navigation
        this.updateNavigation(true);
        
        // Initialize task list (via Tasks module)
        if (typeof Tasks !== 'undefined') {
            Tasks.loadTasks();
        }
    },
    
    /**
     * Show UI for unauthenticated users
     */
    showUnauthenticatedUI() {
        // Show auth section, hide dashboard
        this.elements.authSection.classList.remove('hidden');
        this.elements.dashboardSection.classList.add('hidden');
        
        // Update navigation
        this.updateNavigation(false);
        
        // Reset to login form
        this.showLoginForm();
    },
    
    /**
     * Update navigation based on auth state
     */
    updateNavigation(authenticated) {
        const navContainer = this.elements.navContainer;
        navContainer.innerHTML = '';
        
        if (authenticated) {
            // Create user info and logout button
            const userInfo = document.createElement('div');
            userInfo.id = 'user-info';
            userInfo.innerHTML = `
                <span>Welcome, ${API.user.username}</span>
            `;
            
            const logoutBtn = document.createElement('a');
            logoutBtn.href = '#';
            logoutBtn.textContent = 'Logout';
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
            
            navContainer.appendChild(userInfo);
            navContainer.appendChild(logoutBtn);
        } else {
            // Nothing needed in nav for unauthenticated state
        }
    },
    
    /**
     * Handle user logout
     */
    handleLogout() {
        API.logout();
        this.updateAuthState();
    },
    
    /**
     * Clear auth forms
     */
    clearForms() {
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
        document.getElementById('register-username').value = '';
        document.getElementById('register-email').value = '';
        document.getElementById('register-password').value = '';
        this.elements.loginError.textContent = '';
        this.elements.registerError.textContent = '';
    }
};

// Initialize in main.js instead
// Auth.init(); 