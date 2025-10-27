// Student-specific functionality

class StudentDashboard {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadDashboardStats();
        await this.loadTutorials();
        await this.loadPosts();
        this.setupEventListeners();
    }

    async loadDashboardStats() {
        try {
            const stats = await window.mgsaApp.apiCall('/student/dashboard-stats/');
            
            document.getElementById('tutorialsCount').textContent = stats.registered_tutorials || 0;
            document.getElementById('resourcesCount').textContent = stats.downloaded_resources || 0;
            document.getElementById('feedbackCount').textContent = stats.feedback_submitted || 0;
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    async loadTutorials() {
        try {
            const tutorials = await window.mgsaApp.apiCall('/tutorials/');
            this.renderTutorials(tutorials.results || tutorials);
        } catch (error) {
            console.error('Error loading tutorials:', error);
        }
    }

    async loadPosts() {
        try {
            const posts = await window.mgsaApp.apiCall('/posts/');
            this.renderPosts(posts.results || posts);
        } catch (error) {
            console.error('Error loading posts:', error);
        }
    }

    renderTutorials(tutorials) {
        const container = document.getElementById('tutorialsList');
        if (!container) return;

        if (tutorials.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">No tutorials available.</p>';
            return;
        }

        container.innerHTML = tutorials.slice(0, 5).map(tutorial => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-semibold text-lg">${tutorial.title}</h4>
                        <p class="text-gray-600 text-sm mt-1">${tutorial.description || 'No description'}</p>
                        <div class="flex items-center mt-2 text-sm text-gray-500">
                            <i class="fas fa-calendar mr-1"></i>
                            <span>${new Date(tutorial.date).toLocaleDateString()}</span>
                            <i class="fas fa-users ml-4 mr-1"></i>
                            <span>${tutorial.registered_count || 0} registered</span>
                        </div>
                    </div>
                    <button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm transition-colors register-tutorial" data-tutorial-id="${tutorial.id}">
                        Register
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderPosts(posts) {
        const container = document.getElementById('postsList');
        if (!container) return;

        if (posts.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">No posts available.</p>';
            return;
        }

        container.innerHTML = posts.slice(0, 5).map(post => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <h4 class="font-semibold text-lg">${post.title}</h4>
                <p class="text-gray-600 mt-2">${post.content.substring(0, 150)}...</p>
                <div class="flex items-center justify-between mt-3 text-sm text-gray-500">
                    <div class="flex items-center space-x-4">
                        <span class="flex items-center">
                            <i class="fas fa-heart mr-1"></i>
                            ${post.likes_count || 0}
                        </span>
                        <span class="flex items-center">
                            <i class="fas fa-comment mr-1"></i>
                            ${post.comments_count || 0}
                        </span>
                    </div>
                    <span>${new Date(post.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('register-tutorial')) {
                const tutorialId = e.target.dataset.tutorialId;
                await this.registerForTutorial(tutorialId);
            }
        });
    }

    async registerForTutorial(tutorialId) {
        try {
            const response = await window.mgsaApp.apiCall('/tutorials/registrations/', {
                method: 'POST',
                body: JSON.stringify({ tutorial: tutorialId })
            });

            window.mgsaApp.showNotification('Successfully registered for tutorial!', 'success');
            await this.loadDashboardStats();
        } catch (error) {
            console.error('Error registering for tutorial:', error);
            window.mgsaApp.showNotification('Failed to register for tutorial', 'error');
        }
    }
}

// Initialize student dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('tutorialsList')) {
        new StudentDashboard();
    }
});