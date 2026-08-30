// Elementos da Interface
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadScreen = document.getElementById('upload-screen');
const loadingScreen = document.getElementById('loading-screen');
const resultScreen = document.getElementById('result-screen');
const progressBar = document.getElementById('progress-bar');
const progressPercentage = document.getElementById('progress-percentage');
const progressText = document.getElementById('progress-text');
const fileList = document.getElementById('file-list');

let outputZipPath = "";
let outputDirPath = "";

// Configuração de Eventos de Drag & Drop e Clique
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.opacity = '0.7';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.opacity = '1';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.opacity = '1';
    if (e.dataTransfer.files.length) {
        iniciarFluxo(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        iniciarFluxo(e.target.files[0]);
    }
});

// Fluxo Principal de Envio
function iniciarFluxo(file) {
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert("Formato de arquivo inválido. Insira uma planilha Excel.");
        return;
    }

    // Solicita o diretório ao usuário via painel do Windows
    eel.selecionar_pasta_destino()((folderPath) => {
        if (folderPath) {
            // Converte a planilha para Base64 para contornar segurança de caminho do Chrome
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64Data = e.target.result.split(',')[1];
                
                // Altera a tela para Loading
                uploadScreen.classList.add('hidden');
                loadingScreen.classList.remove('hidden');
                
                // Envia para o processamento no Python
                eel.processar_arquivo_base64(base64Data, folderPath)();
            };
            reader.readAsDataURL(file);
        }
    });
}

// Funções Expostas para o Python (Backend chamando o Frontend)
eel.expose(atualizar_progresso);
function atualizar_progresso(porcentagem, mensagem) {
    progressBar.style.width = `${porcentagem}%`;
    progressPercentage.innerText = `${porcentagem}%`;
    progressText.innerText = mensagem;
}

eel.expose(erro_processamento);
function erro_processamento(mensagem) {
    alert("Ocorreu um erro: " + mensagem);
    resetarInterface();
}

eel.expose(finalizar_processamento);
function finalizar_processamento(arquivos, zipPath, dirPath) {
    loadingScreen.classList.add('hidden');
    resultScreen.classList.remove('hidden');
    
    outputZipPath = zipPath;
    outputDirPath = dirPath;
    fileList.innerHTML = "";

    // Renderiza a lista de arquivos gerados individualmente
    arquivos.forEach(arq => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <span>${arq.nome}</span>
            <button onclick="eel.abrir_caminho('${arq.caminho.replace(/\\/g, '\\\\')}')">Abrir</button>
        `;
        fileList.appendChild(div);
    });
}

// Interações da Tela de Resultados
document.getElementById('btn-open-folder').addEventListener('click', () => eel.abrir_caminho(outputDirPath));
document.getElementById('btn-open-zip').addEventListener('click', () => eel.abrir_caminho(outputZipPath));
document.getElementById('btn-reset').addEventListener('click', resetarInterface);

function resetarInterface() {
    fileInput.value = "";
    progressBar.style.width = "0%";
    progressPercentage.innerText = "0%";
    resultScreen.classList.add('hidden');
    loadingScreen.classList.add('hidden');
    uploadScreen.classList.remove('hidden');
}