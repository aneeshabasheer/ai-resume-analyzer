/**
 * AI Resume Analyzer - Custom Client-side Scripts
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // 1. CAREER CHATBOT LOGIC
    // ==========================================
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');

    if (chatForm && chatInput && chatContainer) {
        
        // Scroll chatbot container to the bottom immediately on load
        scrollChatToBottom();

        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const messageText = chatInput.value.trim();
            if (!messageText) return;

            // 1. Append User Message to UI
            appendChatBubble(messageText, 'user');
            chatInput.value = '';
            scrollChatToBottom();

            // Show temporary loading indicator
            const loadingId = appendLoadingBubble();
            scrollChatToBottom();

            // 2. AJAX request to Django views
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const formData = new FormData();
            formData.append('message', messageText);
            formData.append('csrfmiddlewaretoken', csrfToken);

            fetch('/chatbot/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading bubble
                removeLoadingBubble(loadingId);
                
                if (data.response) {
                    // Append Bot Response to UI
                    appendChatBubble(data.response, 'bot');
                } else {
                    appendChatBubble("Sorry, I encountered an error. Please try again.", 'bot');
                }
                scrollChatToBottom();
            })
            .catch(error => {
                console.error('Chat Error:', error);
                removeLoadingBubble(loadingId);
                appendChatBubble("Network error! Could not connect to the career assistant.", 'bot');
                scrollChatToBottom();
            });
        });
    }

    // Chatbot Helper Functions
    function scrollChatToBottom() {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    function appendChatBubble(text, sender) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        
        // Use innerHTML since bot responses contain HTML formatting tags like <b>, <br>, <ul>
        if (sender === 'bot') {
            bubble.innerHTML = text;
        } else {
            // Escape user text to prevent XSS injection
            bubble.textContent = text;
        }
        
        chatContainer.appendChild(bubble);
    }

    function appendLoadingBubble() {
        const loadingId = 'loading-' + Date.now();
        const bubble = document.createElement('div');
        bubble.id = loadingId;
        bubble.className = 'chat-bubble bot text-muted';
        bubble.innerHTML = '<span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span> Thinking...';
        chatContainer.appendChild(bubble);
        return loadingId;
    }

    function removeLoadingBubble(id) {
        const bubble = document.getElementById(id);
        if (bubble) {
            bubble.remove();
        }
    }
});


function clearChat() {
    // Call backend endpoint to clear session history
    fetch('/clear-chat/', { method: 'POST', headers: {'X-CSRFToken': '{{ csrf_token }}'} })
    .then(response => response.json())
    .then(data => {
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            chatContainer.innerHTML = `
                <div class="bot-message p-2 mb-2 rounded bg-light">
                    Chat history cleared! How can I help you today?
                </div>
            `;
        }
    });
}
