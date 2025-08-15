// SDLC Core Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add fade-in animation to main content
    var mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
});

// API Helper Functions
class APIClient {
    constructor() {
        this.baseURL = '';
    }

    async get(endpoint) {
        try {
            const response = await fetch(this.baseURL + endpoint, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    }

    async post(endpoint, data) {
        try {
            const response = await fetch(this.baseURL + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }

    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        return await response.json();
    }
}

// Initialize API client
const api = new APIClient();

// Authentication Functions
async function loginUser(username, password) {
    try {
        const response = await api.post('/auth/api/login', {
            username: username,
            password: password
        });
        return response;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

async function getUserProfile() {
    try {
        const response = await api.get('/auth/api/user/profile');
        return response;
    } catch (error) {
        console.error('Get profile error:', error);
        throw error;
    }
}

// Admin Functions
async function getUsers() {
    try {
        const response = await api.get('/api/admin/users');
        return response;
    } catch (error) {
        console.error('Get users error:', error);
        throw error;
    }
}

async function getRoles() {
    try {
        const response = await api.get('/api/admin/roles');
        return response;
    } catch (error) {
        console.error('Get roles error:', error);
        throw error;
    }
}

// Utility Functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (alertContainer) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.insertBefore(alert, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
}

function showLoading(element) {
    const originalText = element.innerHTML;
    element.innerHTML = '<span class="spinner"></span> Loading...';
    element.disabled = true;
    
    return function hideLoading() {
        element.innerHTML = originalText;
        element.disabled = false;
    };
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateUsername(username) {
    return username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
}

// Real-time form validation
document.addEventListener('input', function(e) {
    if (e.target.type === 'email') {
        const isValid = validateEmail(e.target.value);
        e.target.classList.toggle('is-valid', isValid && e.target.value !== '');
        e.target.classList.toggle('is-invalid', !isValid && e.target.value !== '');
    }
    
    if (e.target.name === 'password') {
        const isValid = validatePassword(e.target.value);
        e.target.classList.toggle('is-valid', isValid);
        e.target.classList.toggle('is-invalid', !isValid && e.target.value !== '');
    }
    
    if (e.target.name === 'username') {
        const isValid = validateUsername(e.target.value);
        e.target.classList.toggle('is-valid', isValid);
        e.target.classList.toggle('is-invalid', !isValid && e.target.value !== '');
    }
});

// Role badge styling
function styleRoleBadges() {
    const roleBadges = document.querySelectorAll('.badge');
    roleBadges.forEach(badge => {
        const role = badge.textContent.toLowerCase();
        badge.classList.add(`role-${role}`);
    });
}

// Initialize role badge styling
document.addEventListener('DOMContentLoaded', styleRoleBadges);

// Export functions for global use
window.SDLC = {
    api,
    loginUser,
    getUserProfile,
    getUsers,
    getRoles,
    showAlert,
    showLoading,
    validateEmail,
    validatePassword,
    validateUsername,
    styleRoleBadges
};