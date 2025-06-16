class QuizPublisher {
    constructor() {
        this.init();
    }

    init() {
        const confirmBtn = document.getElementById('confirmPublishBtn');
        const finalBtn = document.getElementById('finalConfirmBtn');
        
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.showFinalConfirm());
        }
        
        if (finalBtn) {
            finalBtn.addEventListener('click', () => this.handleFinalPublish());
        }
    }

    showFinalConfirm() {
        // Hide the first modal
        const firstModal = bootstrap.Modal.getInstance(document.getElementById('publishQuizModal'));
        if (firstModal) {
            firstModal.hide();
        }
        
        // Show the final confirmation modal
        const finalModal = new bootstrap.Modal(document.getElementById('finalConfirmModal'));
        finalModal.show();
    }

    async handleFinalPublish() {
        const quizId = this.getQuizId();
        const authorId = this.getAuthorId();
        
        if (!quizId || !authorId) {
            alert('Missing quiz or author information');
            return;
        }

        // Disable the button to prevent double-clicks
        const finalBtn = document.getElementById('finalConfirmBtn');
        const originalText = finalBtn.innerHTML;
        finalBtn.disabled = true;
        finalBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publishing...';

        try {
            await this.publishQuiz(quizId, authorId);
        } catch (error) {
            console.error('Error during publish:', error);
            // Re-enable button on error
            finalBtn.disabled = false;
            finalBtn.innerHTML = originalText;
        }
    }

    getQuizId() {
        // Method 1: Try to get from hidden input
        const hiddenInput = document.getElementById('quiz-id');
        if (hiddenInput) {
            return hiddenInput.value;
        }
        
        // Method 2: Try to get from URL or form action
        const forms = document.querySelectorAll('form[action*="quiz_id"]');
        if (forms.length > 0) {
            const actionUrl = forms[0].action;
            const match = actionUrl.match(/\/(\d+)\/\d+\/\d+\/\d+$/);
            if (match) {
                return match[1];
            }
        }
        
        // Method 3: Try to extract from current URL
        const urlParts = window.location.pathname.split('/');
        const quizIndex = urlParts.indexOf('create_questions');
        if (quizIndex !== -1 && urlParts[quizIndex + 1]) {
            return urlParts[quizIndex + 1];
        }
        
        return null;
    }

    getAuthorId() {
        // Method 1: Try to get from hidden input
        const hiddenInput = document.getElementById('author-id');
        if (hiddenInput) {
            return hiddenInput.value;
        }
        
        // Method 2: Try to get from form action
        const forms = document.querySelectorAll('form[action*="author_id"]');
        if (forms.length > 0) {
            const actionUrl = forms[0].action;
            const match = actionUrl.match(/\/\d+\/\d+\/(\d+)\/\d+$/);
            if (match) {
                return match[1];
            }
        }
        
        return null;
    }

    async publishQuiz(quizId, authorId) {
        try {
            const response = await fetch('/quiz/publish_quiz', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ 
                    quiz_id: quizId,
                    author_id: authorId 
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Success - hide modal and redirect
                const modal = bootstrap.Modal.getInstance(document.getElementById('finalConfirmModal'));
                if (modal) {
                    modal.hide();
                }
                
                // Show success message briefly before redirect
                alert(data.message || 'Quiz published successfully!');
                
                // Build dashboard URL with required parameters
                const dashboardUrl = this.buildDashboardUrl(authorId);
                window.location.href = dashboardUrl;
            } else {
                // Error from server
                throw new Error(data.message || 'Failed to publish quiz');
            }
        } catch (error) {
            console.error('Publish error:', error);
            alert('Error publishing quiz: ' + error.message);
            throw error; // Re-throw to be caught by handleFinalPublish
        }
    }

    buildDashboardUrl(authorId) {
        // Try to get user data from the current page URL or hidden inputs
        const userName = this.getUserName();
        const userRole = this.getUserRole();
        
        if (userName && userRole) {
            return `/author/dashboard?user_id=${authorId}&user_role=${userRole}&user_name=${encodeURIComponent(userName)}`;
        } else {
            // Fallback - try to get from current URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const currentUserId = urlParams.get('user_id') || authorId;
            const currentUserRole = urlParams.get('user_role') || 'author';
            const currentUserName = urlParams.get('user_name') || 'Author';
            
            return `/author/dashboard?user_id=${currentUserId}&user_role=${currentUserRole}&user_name=${encodeURIComponent(currentUserName)}`;
        }
    }

    getUserName() {
        // Try to get from hidden input
        const hiddenInput = document.getElementById('user-name');
        if (hiddenInput) {
            return hiddenInput.value;
        }
        
        // Try to get from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('user_name');
    }

    getUserRole() {
        // Try to get from hidden input
        const hiddenInput = document.getElementById('user-role');
        if (hiddenInput) {
            return hiddenInput.value;
        }
        
        // Try to get from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('user_role') || 'author';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new QuizPublisher();
});