const API_BASE_URL = "http://localhost:8001";

let sessionId = localStorage.getItem("chat_session_id");
if (!sessionId) {
    sessionId = "user_" + Date.now();
    localStorage.setItem("chat_session_id", sessionId);
}

document.addEventListener("DOMContentLoaded", function () {
    const input       = document.getElementById("chat-input");
    const sendButton  = document.getElementById("send-button");
    const messages    = document.querySelector(".chat-messages");
    const chatPage    = document.querySelector(".chat-page");
    const chatContainer = document.querySelector(".chat-container");

    // Inject "New Chat" button before the chat container
    const newChatBtn = document.createElement("button");
    newChatBtn.id        = "new-chat-btn";
    newChatBtn.className = "primary-button";
    newChatBtn.textContent = "New Chat";
    newChatBtn.addEventListener("click", function () {
        sessionId = "user_" + Date.now();
        localStorage.setItem("chat_session_id", sessionId);
        messages.innerHTML = "";
        addMessageToUI(messages, "assistant", "New chat started. How can I help you?");
    });
    chatPage.insertBefore(newChatBtn, chatContainer);

    // Send on button click
    sendButton.addEventListener("click", function () {
        sendMessage(input, messages);
    });

    // Send on Enter key
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            sendMessage(input, messages);
        }
    });
});

async function sendMessage(input, messages) {
    const question = input.value.trim();
    if (question === "") return;

    addMessageToUI(messages, "user", question);
    input.value = "";

    const loadingDiv = addLoadingIndicator(messages);

    try {
        const response = await fetch(API_BASE_URL + "/chat/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question, session_id: sessionId })
        });

        const data = await response.json();
        loadingDiv.remove();

        if (response.ok) {
            addMessageToUI(messages, "assistant", data.answer);
        } else {
            addMessageToUI(messages, "assistant", "Error: " + (data.detail || "Something went wrong"));
        }
    } catch (error) {
        loadingDiv.remove();
        addMessageToUI(messages, "assistant", "Error: " + error.message);
    }
}

function addMessageToUI(messages, role, content) {
    const div = document.createElement("div");
    div.classList.add("message");
    div.classList.add(role === "user" ? "user-message" : "assistant-message");
    div.textContent = content;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function addLoadingIndicator(messages) {
    const div = document.createElement("div");
    div.classList.add("message", "assistant-message", "loading-message");
    div.textContent = "Thinking...";
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
}