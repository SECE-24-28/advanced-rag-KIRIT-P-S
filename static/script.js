const chatBox = document.getElementById("chat-box");

function addMessage(text, type){

    const div = document.createElement("div");

    div.className = `message ${type}`;

    div.innerHTML = text;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(){

    const input = document.getElementById("message");

    const message = input.value.trim();

    if(!message) return;

    addMessage(message,"user");

    input.value = "";

    const typing = document.createElement("div");

    typing.className = "message bot";

    typing.innerHTML =
    `<div class="typing">
        <span></span>
        <span></span>
        <span></span>
    </div>`;

    chatBox.appendChild(typing);

    const response = await fetch("/chat",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            message:message
        })
    });

    const data = await response.json();

    typing.remove();

    addMessage(data.response,"bot");
}

document
.getElementById("message")
.addEventListener("keypress", function(e){

    if(e.key==="Enter"){
        sendMessage();
    }
});