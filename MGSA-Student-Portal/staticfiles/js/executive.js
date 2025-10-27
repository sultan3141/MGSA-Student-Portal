// Executive-specific functionality

class ExecutiveDashboard {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadExecutiveStats();
        await this.loadMyPosts();
        await this.loadMyResources();
        await this.loadMyTutorials();
        this.setupEventListeners();
    }

    async loadExecutiveStats() {
        try {
            const stats = await window.mgsaApp.apiCall('/executive/dashboard/');
            
            document.getElementById('myPostsCount').textContent = stats.my_posts || 0;
            document.getElementById('myResourcesCount').textContent = stats.my_resources || 0;
            document.getElementById('myTutorialsCount').textContent = stats.my_tutorials || 0;
            document.getElementById('totalRegistrations').textContent = stats.total_registrations || 0;
        } catch (error) {
            console.error('Error loading executive stats:', error);
        }
    }

    async loadMyPosts() {
        try {
            const posts = await window.mgsaApp.apiCall('/executive/posts/');
            this.renderMyPosts(posts.results || posts);
        } catch (error) {
            console.error('Error loading executive posts:', error);
        }
    }

    async loadMyResources() {
        try {
            const resources = await window.mgsaApp.apiCall('/executive/resources/');
            this.renderMyResources(resources.results || resources);
        } catch (error) {
            console.error('Error loading executive resources:', error);
        }
    }

    async loadMyTutorials() {
        try {
            const tutorials = await window.mgsaApp.apiCall('/executive/tutorials/');
            this.renderMyTutorials(tutorials.results || tutorials);
        } catch (error) {
            console.error('Error loading executive tutorials:', error);
        }
    }

    renderMyPosts(posts) {
        const container = document.getElementById('myPostsList');
        if (!container) return;

        if (posts.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No posts created yet</p>';
            return;
        }

        container.innerHTML = posts.map(post => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-lg">${post.title}</h4>
                        <p class="text-gray-600 text-sm mt-1">${post.content.substring(0, 100)}...</p>
                        <div class="flex items-center mt-2 text-sm text-gray-500">
                            <span class="flex items-center mr-4">
                                <i class="fas fa-eye mr-1"></i>
                                ${post.views || 0} views
                            </span>
                            <span class="flex items-center">
                                <i class="fas fa-comments mr-1"></i>
                                ${post.comments_count || 0} comments
                            </span>
                        </div>
                    </div>
                    <div class="flex space-x-2 ml-4">
                        <button class="text-blue-500 hover:text-blue-700 edit-post" data-post-id="${post.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="text-red-500 hover:text-red-700 delete-post" data-post-id="${post.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderMyResources(resources) {
        const container = document.getElementById('myResourcesList');
        if (!container) return;

        if (resources.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No resources uploaded yet</p>';
            return;
        }

        container.innerHTML = resources.map(resource => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-lg">${resource.title}</h4>
                        <p class="text-gray-600 text-sm mt-1">${resource.description || 'No description'}</p>
                        <div class="flex items-center mt-2 text-sm text-gray-500">
                            <span class="flex items-center mr-4">
                                <i class="fas fa-download mr-1"></i>
                                ${resource.download_count || 0} downloads
                            </span>
                            <span class="flex items-center">
                                <i class="fas fa-calendar mr-1"></i>
                                ${new Date(resource.created_at).toLocaleDateString()}
                            </span>
                        </div>
                    </div>
                    <div class="flex space-x-2 ml-4">
                        <button class="text-blue-500 hover:text-blue-700 edit-resource" data-resource-id="${resource.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="text-red-500 hover:text-red-700 delete-resource" data-resource-id="${resource.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderMyTutorials(tutorials) {
        const container = document.getElementById('myTutorialsList');
        if (!container) return;

        if (tutorials.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">No tutorials created yet</p>';
            return;
        }

        container.innerHTML = tutorials.map(tutorial => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-lg">${tutorial.title}</h4>
                        <p class="text-gray-600 text-sm mt-1">${tutorial.description || 'No description'}</p>
                        <div class="flex items-center mt-2 text-sm text-gray-500">
                            <span class="flex items-center mr-4">
                                <i class="fas fa-calendar mr-1"></i>
                                ${new Date(tutorial.date).toLocaleDateString()}
                            </span>
                            <span class="flex items-center">
                                <i class="fas fa-users mr-1"></i>
                                ${tutorial.registered_count || 0} registered
                            </span>
                        </div>
                    </div>
                    <div class="flex space-x-2 ml-4">
                        <a href="/executive/tutorials/${tutorial.id}/registrations/" 
                           class="text-green-500 hover:text-green-700 view-registrations" 
                           data-tutorial-id="${tutorial.id}">
                            <i class="fas fa-list"></i>
                        </a>
                        <button class="text-blue-500 hover:text-blue-700 edit-tutorial" data-tutorial-id="${tutorial.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="text-red-500 hover:text-red-700 delete-tutorial" data-tutorial-id="${tutorial.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        // Setup form submission for create post
        const createPostForm = document.getElementById('createPostForm');
        if (createPostForm) {
            createPostForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleCreatePost();
            });
        }

        // Setup other event listeners for edit/delete actions
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.delete-post')) {
                const postId = e.target.closest('.delete-post').dataset.postId;
                await this.deletePost(postId);
            }
            // Add similar handlers for resources and tutorials
        });
    }

    async handleCreatePost() {
        const formData = new FormData(document.getElementById('createPostForm'));
        const data = {
            title: formData.get('title'),
            content: formData.get('content')
        };

        try {
            const response = await window.mgsaApp.apiCall('/executive/posts/', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            window.mgsaApp.showNotification('Post created successfully!', 'success');
            closeCreatePostModal();
            document.getElementById('createPostForm').reset();
            await this.loadMyPosts();
            await this.loadExecutiveStats();
        } catch (error) {
            console.error('Error creating post:', error);
            window.mgsaApp.showNotification('Failed to create post', 'error');
        }
    }

    async deletePost(postId) {
        if (!confirm('Are you sure you want to delete this post?')) return;

        try {
            await window.mgsaApp.apiCall(`/executive/posts/${postId}/`, {
                method: 'DELETE'
            });

            window.mgsaApp.showNotification('Post deleted successfully!', 'success');
            await this.loadMyPosts();
            await this.loadExecutiveStats();
        } catch (error) {
            console.error('Error deleting post:', error);
            window.mgsaApp.showNotification('Failed to delete post', 'error');
        }
    }
}

// Initialize executive dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('myPostsCount')) {
        new ExecutiveDashboard();
    }
});