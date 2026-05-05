let currentState = "idle"; // idle, recording, playing

const masterBtn = document.getElementById('master-btn');
const btnText = document.getElementById('btn-text');
const statusText = document.getElementById('main-status');
const body = document.body;

async function handleAction(type) {
    // Pulo do gato: transição com blur antes de mudar o estado visual
    body.classList.add('blur-effect');
    
    setTimeout(async () => {
        if (type === "F3") {
            const res = await eel.toggle_recording()();
            currentState = res;
            updateUI();
        } else if (type === "F4") {
            if (currentState === "playing") {
                await eel.stop_playback()();
                currentState = "idle";
            } else {
                const res = await eel.start_playback()();
                if (res === "missing_file") alert("Grave algo primeiro!");
                else currentState = "playing";
            }
            updateUI();
        }
        body.classList.remove('blur-effect');
    }, 1000);
}

function updateUI() {
    masterBtn.className = "neumorphic-btn giant-btn " + currentState;
    if (currentState === "recording") {
        btnText.innerText = "GRAVANDO";
        statusText.innerText = "Pressione F3 para parar";
    } else if (currentState === "playing") {
        btnText.innerText = "REPRODUZINDO";
        statusText.innerText = "Pressione F4 para parar";
    } else {
        btnText.innerText = "PREPARAR";
        statusText.innerText = "Aguardando comando...";
    }
}

// Expor para o Python chamar via Hotkeys
eel.expose(trigger_shortcut);
function trigger_shortcut(key) {
    handleAction(key);
}

eel.expose(update_status);
function update_status(msg) {
    statusText.innerText = msg;
}

eel.expose(finish_process);
function finish_process(type, msg) {
    currentState = "idle";
    updateUI();
    if (type === "error") alert(msg);
}

masterBtn.onclick = () => handleAction(currentState === "recording" ? "F3" : "F4");