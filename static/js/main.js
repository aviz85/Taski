/**
 * Main Module for Taski App
 * Initializes and coordinates other modules
 */

const App = {
    /**
     * Initialize the application
     */
    init() {
        console.log('Initializing Taski App...');
        
        // Initialize modules after DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            this.initModules();
        });
    },
    
    /**
     * Initialize all app modules
     */
    initModules() {
        try {
            // Initialize Auth module
            Auth.init();
            
            // Initialize Tasks module
            Tasks.init();
            
            // Add window event listeners
            this.addEventListeners();
            
            console.log('Taski App initialized successfully');
        } catch (error) {
            console.error('Error initializing app:', error);
        }
    },
    
    /**
     * Add app-wide event listeners
     */
    addEventListeners() {
        // Close modals when clicking outside content
        window.addEventListener('click', (event) => {
            const taskModal = document.getElementById('task-modal');
            const confirmModal = document.getElementById('confirm-modal');
            
            if (event.target === taskModal) {
                taskModal.classList.add('hidden');
            }
            
            if (event.target === confirmModal) {
                confirmModal.classList.add('hidden');
            }
        });
        
        // Handle keyboard events
        document.addEventListener('keydown', (event) => {
            // Close modals on Escape key
            if (event.key === 'Escape') {
                const modals = document.querySelectorAll('.modal');
                modals.forEach(modal => {
                    modal.classList.add('hidden');
                });
            }
        });
    },
    
    /**
     * Handle global errors
     */
    handleError(error, source) {
        console.error(`Error in ${source}:`, error);
        
        // For critical errors that should be visible to the user
        if (error.critical) {
            alert(`An error occurred: ${error.message}`);
        }
    }
};

// Initialize the app
App.init(); 