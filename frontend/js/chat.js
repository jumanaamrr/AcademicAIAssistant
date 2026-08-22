const API_BASE_URL = "http://localhost:8001";

const input = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const messages = document.querySelector(".chat-messages");

let sessionId = localStorage.getItem("chat_session_id");

if (!sessionId) {
    sessionId = "user_" + Date.now();
    localStorage.setItem("chat_session_id", sessionId);
}

sendButton.addEventListener("click", sendMessage);
input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {
    const question = input.value.trim();
    
    if (question === "") {
        return;
    }
    
    // Add user's message
    addMessageToUI("user", question);
    input.value = "";
    
    // Show loading
    const loadingMessage = addLoadingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question: question,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        loadingMessage.remove();
        
        if (response.ok) {
            addMessageToUI("assistant", data.answer);
        } else {
            addMessageToUI("assistant", `Error: ${data.detail || "Something went wrong"}`);
        }
    } catch (error) {
        loadingMessage.remove();
        addMessageToUI("assistant", `Error: ${error.message}`);
    }
}

function addMessageToUI(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    
    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("assistant-message");
    }
    
    messageDiv.textContent = content;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function addLoadingIndicator() {
    const loadingDiv = document.createElement("div");
    loadingDiv.classList.add("message", "assistant-message");
    loadingDiv.textContent = "Thinking...";
    messages.appendChild(loadingDiv);
    messages.scrollTop = messages.scrollHeight;
    return loadingDiv;
}