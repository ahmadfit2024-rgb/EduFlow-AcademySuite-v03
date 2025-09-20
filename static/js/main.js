// Custom project-wide JavaScript can be added here.

document.addEventListener("DOMContentLoaded", function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.body.querySelector("#sidebarToggle");
    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", function(event) {
            event.preventDefault();
            document.body.classList.toggle("sb-sidenav-toggled");
        });
    }

    // HTMX Toast Notification Listener
    const toastElement = document.getElementById('appToast');
    if (toastElement) {
        const appToast = new bootstrap.Toast(toastElement);

        document.body.addEventListener('showToast', function(event) {
            const message = event.detail.message || "Action completed successfully!";
            toastElement.querySelector('.toast-body').textContent = message;
            appToast.show();
        });
    }

    // --- AI Assistant Chat Logic ---
    const chatBody = document.getElementById('ai-chat-body');
    const formContainer = document.getElementById('ai-chat-form-container');

    if (chatBody && formContainer) {
        // Listen for HTMX request to append user's question to chat
        document.body.addEventListener('htmx:configRequest', function(evt) {
            if (evt.detail.path.includes('/api/v1/interactions/ai-assistant/ask/')) {
                const questionInput = evt.detail.elt.querySelector('input[name="question"]');
                if (questionInput && questionInput.value) {
                    const userBubble = document.createElement('div');
                    userBubble.className = 'user-bubble';
                    userBubble.textContent = questionInput.value;
                    chatBody.appendChild(userBubble);
                    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
                    questionInput.value = ''; // Clear input
                }
            }
        });

        // Listen for HTMX response to append AI's answer
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            if (evt.detail.pathInfo.path === '/api/v1/interactions/ai-assistant/ask/') {
                const response = JSON.parse(evt.detail.xhr.responseText);
                
                const aiResponseContainer = document.createElement('div');
                aiResponseContainer.className = 'd-flex align-items-start gap-3';
                
                const aiAvatar = document.createElement('div');
                aiAvatar.className = 'ai-avatar';
                aiAvatar.innerHTML = '<i class="bi bi-robot"></i>';

                const aiBubble = document.createElement('div');
                aiBubble.className = 'ai-bubble';
                aiBubble.textContent = response.answer || "Sorry, I couldn't process that.";

                aiResponseContainer.appendChild(aiAvatar);
                aiResponseContainer.appendChild(aiBubble);
                chatBody.appendChild(aiResponseContainer);
                chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
            }
        });
    }
});