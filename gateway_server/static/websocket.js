const chatbox = document.getElementById('chatbox');
const userinput = document.getElementById('userinput');
const sendbtn = document.getElementById('sendbtn');

let ws = new WebSocket(`ws://${location.host}/ws/chat`);
//let customer_id = "customer123"; // Hardcoded for now; can be dynamic
let customer_id = localStorage.getItem("customer_id");
if (!customer_id) {
    customer_id = crypto.randomUUID();
    localStorage.setItem("customer_id", customer_id);
}

let assistantResponse = `<span class="assistant">Assistant:</span> `;

// Handle incoming messages from server
ws.onmessage = (event) => {
    if (event.data === "[[DONE]]") {
        chatbox.innerHTML += `<div class="message">${assistantResponse}</div>`;
        assistantResponse = `<span class="assistant">Assistant:</span> `;
        chatbox.scrollTop = chatbox.scrollHeight;
    } else {
        assistantResponse += event.data;
    }
};

// Send message on button click
sendbtn.onclick = () => {
    const message = userinput.value.trim();
    if (message === "") return;

    chatbox.innerHTML += `<div class="message"><span class="user">You:</span> ${message}</div>`;
    ws.send(`${customer_id}|${message}`);
    userinput.value = "";
    chatbox.scrollTop = chatbox.scrollHeight;
};

// Optionally allow pressing "Enter" to send
userinput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendbtn.click();
    }
});
