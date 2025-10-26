// Main JavaScript file with common utilities

const API_BASE = '/api';

class MGSAApp {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupCSRF();
        this.loadCurrentUser();
        this.setupEventListeners();
    }

    setupCSRF() {
        // Get CSRF token from cookies
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

        const csrftoken = getCookie('csrftoken');
        
        // Set up AJAX requests to include CSRF token
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    async loadCurrentUser() {
        try {
            const response = await this.apiCall('/auth/me/');
            this.currentUser = response;
            this.updateUIForUser();
        } catch (error) {
            console.log('User not authenticated');
        }
    }

    updateUIForUser() {
        // Update UI based on user role and authentication status
        if (this.currentUser) {
            const userElements = document.querySelectorAll('[data-user]');
            userElements.forEach(el => {
                el.style.display = 'block';
            });
            
            const guestElements = document.querySelectorAll('[data-guest]');
            guestElements.forEach(el => {
                el.style.display = 'none';
            });
        } else {
            const userElements = document.querySelectorAll('[data-user]');
            userElements.forEach(el => {
                el.style.display = 'none';
            });
            
            const guestElements = document.querySelectorAll('[data-guest]');
            guestElements.forEach(el => {
                el.style.display = 'block';
            });
        }
    }

    async apiCall(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                throw new Error(`API call failed: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    setupEventListeners() {
        // Global event listeners
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-logout]')) {
                this.handleLogout();
            }
        });
    }

    async handleLogout() {
        try {
            await this.apiCall('/auth/logout/', { method: 'POST' });
            window.location.href = '/login/';
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mgsaApp = new MGSAApp();
});