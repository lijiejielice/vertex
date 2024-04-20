document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('user-input');

    // Event listener for the Enter key in the input field
    input.addEventListener('keydown', function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent the default action to avoid form submission
            sendMessage(); // Call the sendMessage function
        }
    });
});

function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const userText = input.value.trim();

    if (!userText) return;

    displayMessage(userText, 'user-message');
    input.value = ''; // Clear the input after sending

    fetch(`/predict?query=${encodeURIComponent(userText)}`)
        .then(response => response.json())
        .then(data => displayMessage(data.message, 'system-message'))
        .catch(error => console.error('Error:', error));
}

function displayMessage(message, className) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = message;
    messageDiv.className = `message ${className}`;
    document.getElementById('chat-box').appendChild(messageDiv);
    messageDiv.scrollIntoView(); // Ensure the latest message is visible
}