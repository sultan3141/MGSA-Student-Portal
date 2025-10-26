// Authentication functionality

class AuthManager {
    constructor() {
        this.loginForm = document.getElementById('loginForm');
        this.registerForm = document.getElementById('registerForm');
        this.init();
    }

    init() {
        if (this.loginForm) {
            this.setupLoginForm();
        }
        if (this.registerForm) {
            this.setupRegisterForm();
        }
    }

    setupLoginForm() {
        this.loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });
    }

    setupRegisterForm() {
        this.registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });
    }

    async handleLogin() {
        const formData = new FormData(this.loginForm);
        const data = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        this.setLoadingState(true);

        try {
            const response = await fetch('/login/submit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Login successful! Redirecting...', 'success');
                
                setTimeout(() => {
                    window.location.href = result.redirect_url || '/student-dashboard/';
                }, 1000);
            } else {
                this.showError(result.message || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('An error occurred during login');
        } finally {
            this.setLoadingState(false);
        }
    }

    async handleRegister() {
        const formData = new FormData(this.registerForm);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            password_confirm: formData.get('password_confirm')
        };

        // Basic validation
        if (data.password !== data.password_confirm) {
            this.showError('Passwords do not match');
            return;
        }

        if (data.password.length < 6) {
            this.showError('Password must be at least 6 characters long');
            return;
        }

        this.setLoadingState(true);

        try {
            const response = await fetch('/register/submit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showNotification('Registration successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = result.redirect_url || '/student-dashboard/';
                }, 1000);
            } else {
                this.showError(result.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('An error occurred during registration');
        } finally {
            this.setLoadingState(false);
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
            
            setTimeout(() => {
                errorDiv.classList.add('hidden');
            }, 5000);
        } else {
            this.showNotification(message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Use the main app's notification system if available
        if (window.mgsaApp && window.mgsaApp.showNotification) {
            window.mgsaApp.showNotification(message, type);
        } else {
            // Fallback notification
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
    }

    setLoadingState(loading) {
        const buttons = document.querySelectorAll('button[type="submit"]');
        buttons.forEach(button => {
            if (loading) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
            } else {
                button.disabled = false;
                if (this.loginForm) {
                    button.textContent = 'Sign in';
                } else if (this.registerForm) {
                    button.textContent = 'Create Account';
                }
            }
        });
    }
}

// Initialize auth manager
document.addEventListener('DOMContentLoaded', () => {
    new AuthManager();
});