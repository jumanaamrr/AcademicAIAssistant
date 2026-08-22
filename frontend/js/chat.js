const input = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const messages = document.querySelector(".chat-messages");

sendButton.addEventListener("click", sendMessage);

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {

    const question = input.value.trim();

    if (question === "") {
        return;
    }

    // Add user's message
    const userMessage = document.createElement("div");

    userMessage.classList.add("message");
    userMessage.classList.add("user-message");

    userMessage.textContent = question;

    messages.appendChild(userMessage);

    // Clear input
    input.value = "";

    // Temporary response
    setTimeout(function () {

        const assistantMessage = document.createElement("div");

        assistantMessage.classList.add("message");
        assistantMessage.classList.add("assistant-message");

        assistantMessage.textContent =
            "I'm processing your question. The AI backend will be connected next.";

        messages.appendChild(assistantMessage);

        messages.scrollTop = messages.scrollHeight;

    }, 500);
}