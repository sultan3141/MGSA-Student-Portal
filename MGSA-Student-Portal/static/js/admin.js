// Admin-specific functionality

class AdminDashboard {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadAdminStats();
        await this.loadRecentActivity();
        this.setupEventListeners();
    }

    async loadAdminStats() {
        try {
            const stats = await window.mgsaApp.apiCall('/analytics/dashboard-stats/');
            
            document.getElementById('totalUsers').textContent = stats.total_users || 0;
            document.getElementById('activeTutorials').textContent = stats.active_tutorials || 0;
            document.getElementById('monthlyFeedback').textContent = stats.monthly_feedback || 0;
            document.getElementById('totalDownloads').textContent = stats.total_downloads || 0;
        } catch (error) {
            console.error('Error loading admin stats:', error);
        }
    }

    async loadRecentActivity() {
        try {
            const activity = await window.mgsaApp.apiCall('/analytics/user-activity-logs/');
            this.renderRecentActivity(activity);
        } catch (error) {
            console.error('Error loading recent activity:', error);
            this.renderRecentActivityError();
        }
    }

    renderRecentActivity(activity) {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        if (!activity || activity.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No recent activity</p>';
            return;
        }

        container.innerHTML = activity.slice(0, 10).map(item => `
            <div class="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div class="flex items-center">
                    <div class="bg-gray-100 rounded-full p-2 mr-3">
                        <i class="fas fa-${this.getActivityIcon(item.action)} text-gray-600 text-sm"></i>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-900">${item.description}</p>
                        <p class="text-xs text-gray-500">${new Date(item.timestamp).toLocaleString()}</p>
                    </div>
                </div>
                <span class="px-2 py-1 text-xs rounded-full ${this.getActivityBadgeColor(item.action)}">
                    ${item.action}
                </span>
            </div>
        `).join('');
    }

    getActivityIcon(action) {
        const icons = {
            'login': 'sign-in-alt',
            'logout': 'sign-out-alt',
            'create': 'plus',
            'update': 'edit',
            'delete': 'trash',
            'download': 'download',
            'register': 'user-plus'
        };
        return icons[action] || 'circle';
    }

    getActivityBadgeColor(action) {
        const colors = {
            'login': 'bg-green-100 text-green-800',
            'logout': 'bg-gray-100 text-gray-800',
            'create': 'bg-blue-100 text-blue-800',
            'update': 'bg-yellow-100 text-yellow-800',
            'delete': 'bg-red-100 text-red-800',
            'download': 'bg-purple-100 text-purple-800',
            'register': 'bg-indigo-100 text-indigo-800'
        };
        return colors[action] || 'bg-gray-100 text-gray-800';
    }

    renderRecentActivityError() {
        const container = document.getElementById('recentActivity');
        if (container) {
            container.innerHTML = '<p class="text-red-500 text-center py-4">Failed to load recent activity</p>';
        }
    }

    setupEventListeners() {
        // Admin-specific event listeners
    }
}

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('totalUsers')) {
        new AdminDashboard();
    }
});