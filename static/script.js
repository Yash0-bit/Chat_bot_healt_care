document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const userMessage = userInput.value.trim();

        // Add the user message to the chat
        chatMessages.innerHTML += `<div class="user-message">${userMessage}</div>`;

        // Send the user message to the Flask server
        fetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ user_message: userMessage }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Handle the chatbot's response
            chatMessages.innerHTML += `<div class="bot-message">${data.bot_response}</div>`;
        })
        .catch(error => console.error('Error:', error));

        // Clear the input field
        userInput.value = '';
    });
});
