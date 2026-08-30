/* ---------------------------------------------------------------------
   Analisador de Diretórios - Frontend
   Responsável por: seleção de pasta, acompanhamento de progresso,
   renderização do gráfico de rosca e navegação drill-down.
   --------------------------------------------------------------------- */

const state = {
  rootPath: null,
  currentPath: null,
  currentParent: null,
  isRoot: true,
  chart: null,
  navHistory: [],
  pollTimer: null,
  finalRefreshDone: false,
};

const COLORS = [
  "#4e9af1", "#2ecc71", "#f5b041", "#e74c3c", "#9b59b6",
  "#1abc9c", "#e67e22", "#5dade2", "#af7ac5", "#f1948a",
  "#48c9b0", "#f7dc6f", "#85c1e9", "#82e0aa", "#d7bde2",
];

const els = {
  btnSelect: document.getElementById("btn-select"),
  btnBack: document.getElementById("btn-back"),
  mainLayout: document.getElementById("main-layout"),
  emptyState: document.getElementById("empty-state"),
  breadcrumb: document.getElementById("breadcrumb"),
  currentFolderName: document.getElementById("current-folder-name"),
  chartCenterLabel: document.getElementById("chart-center-label"),
  listContainer: document.getElementById("list-container"),
  progressDock: document.getElementById("progress-dock"),
  progressFill: document.getElementById("progress-fill"),
  progressLabel: document.getElementById("progress-label"),
};

/* Captura erros de JavaScript não tratados e registra no log do backend,
   além de exibir no console para depuração imediata. */
window.addEventListener("error", (event) => {
  const message = `${event.message} (${event.filename}:${event.lineno})`;
  console.error(message);
  if (window.eel && eel.log_frontend_error) {
    eel.log_frontend_error(message)();
  }
});

/* ----------------------------- Utilidades ----------------------------- */

function formatSize(bytes) {
  const value = Number(bytes) || 0.0;
  const units = [
    { limit: 1024 ** 4, label: "TB", cls: "size-tb" },
    { limit: 1024 ** 3, label: "GB", cls: "size-gb" },
    { limit: 1024 ** 2, label: "MB", cls: "size-mb" },
    { limit: 1024, label: "KB", cls: "size-kb" },
  ];

  for (const unit of units) {
    if (value >= unit.limit) {
      return {
        text: `${(value / unit.limit).toFixed(2)} ${unit.label}`,
        cls: unit.cls,
      };
    }
  }
  return { text: `${value.toFixed(0)} Bytes`, cls: "size-bytes" };
}

/* Trunca o nome mantendo a extensão visível, ex:
   "Esse arquivo tem o nome muito grande.mp3" ->
   "Esse arquivo tem o nom...mp3"                                   */
function truncateMiddle(name, maxChars) {
  if (name.length <= maxChars) return name;

  const dotIndex = name.lastIndexOf(".");
  const hasExt = dotIndex > 0 && dotIndex > name.length - 8;
  const ext = hasExt ? name.slice(dotIndex + 1) : "";
  const reserved = 3 + ext.length; // "..." + extensão
  const keep = Math.max(maxChars - reserved, 4);

  const head = name.slice(0, keep);
  return hasExt ? `${head}...${ext}` : `${head}...`;
}

function setProgressVisible(visible) {
  els.progressDock.style.display = visible ? "block" : "none";
}

function updateProgressBar(value, done = false) {
  const v = Math.max(0, Math.min(100, Number(value)));
  els.progressFill.style.width = `${v}%`;
  if (done || v >= 100) {
    els.progressLabel.textContent = "Concluído: 100.0%";
  } else {
    els.progressLabel.textContent = `Processando: ${v.toFixed(1)}%`;
  }
}

function showErrorInList(message) {
  els.listContainer.innerHTML = "";
  const row = document.createElement("div");
  row.className = "list-item";
  row.textContent = message;
  els.listContainer.appendChild(row);
}

/* -------------------------- Funções expostas -------------------------- */
/* Chamadas pelo backend Python durante a varredura. */

function update_progress(value) {
  setProgressVisible(true);
  updateProgressBar(value);
}
eel.expose(update_progress);

function update_folder_size(_path, _size) {
  // O refresco da tela é feito pelo laço de polling (ver startProgressPolling),
  // que já recarrega a pasta atual periodicamente durante a varredura.
}
eel.expose(update_folder_size);

function scan_complete() {
  updateProgressBar(100, true);
}
eel.expose(scan_complete);

function scan_error(message) {
  console.error("Erro na varredura:", message);
  updateProgressBar(100, true);
}
eel.expose(scan_error);

/* ------------------------------ Navegação ------------------------------ */

async function selectFolder() {
  const result = await eel.select_folder_dialog()();
  if (!result || !result.ok) {
    if (result && result.error) {
      console.error(result.error);
    }
    return;
  }

  state.rootPath = result.path;
  state.currentPath = null;
  state.currentParent = null;
  state.navHistory = [];
  state.finalRefreshDone = false;

  els.emptyState.style.display = "none";
  els.mainLayout.style.display = "grid";

  const scanResult = await eel.start_scan(result.path)();
  if (!scanResult || !scanResult.ok) {
    showErrorInList(scanResult ? scanResult.error : "Falha ao iniciar a varredura.");
    return;
  }

  setProgressVisible(true);
  updateProgressBar(0);
  startProgressPolling();

  // A pasta raiz já é registrada de forma síncrona pelo backend antes de
  // start_scan retornar, então já pode ser carregada imediatamente.
  await loadFolder(result.path, false);
}

function startProgressPolling() {
  if (state.pollTimer) clearInterval(state.pollTimer);

  state.pollTimer = setInterval(async () => {
    const p = await eel.get_progress()();
    if (!p) return;

    updateProgressBar(p.progress, p.finished);

    // Enquanto a varredura roda, recarrega a pasta atualmente exibida para
    // que novas subpastas/arquivos descobertos apareçam automaticamente.
    if (state.currentPath) {
      await loadFolder(state.currentPath, false);
    }

    if (p.finished) {
      if (!state.finalRefreshDone) {
        state.finalRefreshDone = true;
        if (state.currentPath) {
          await loadFolder(state.currentPath, false);
        }
      }
      clearInterval(state.pollTimer);
      state.pollTimer = null;
      setTimeout(() => setProgressVisible(false), 1800);
    }
  }, 700);
}

async function loadFolder(path, pushHistory = true) {
  const data = await eel.get_folder_data(path)();
  if (!data || !data.ok) {
    // Diretório ainda não indexado (ex.: clique muito rápido durante a
    // varredura) - tenta novamente em breve, sem travar a interface.
    if (data && data.error === "Diretório ainda não indexado.") {
      setTimeout(() => loadFolder(path, pushHistory), 400);
    }
    return;
  }

  if (pushHistory && state.currentPath) {
    state.navHistory.push(state.currentPath);
  }

  state.currentPath = data.path;
  state.currentParent = data.parent;
  state.isRoot = data.is_root;

  renderBreadcrumb(data.path);
  renderCurrentFolder(data);
  renderChart(data.children);
  renderList(data.children);

  els.btnBack.disabled = data.is_root && state.navHistory.length === 0;
}

function goBack() {
  let target = null;
  if (state.navHistory.length > 0) {
    target = state.navHistory.pop();
  } else if (state.currentParent) {
    target = state.currentParent;
  }
  if (target) {
    loadFolder(target, false);
  }
}

function renderBreadcrumb(path) {
  els.breadcrumb.textContent = path;
  els.breadcrumb.title = path;
}

function renderCurrentFolder(data) {
  els.currentFolderName.textContent = data.name || data.path;
  els.currentFolderName.title = data.path;

  const totalFormatted = formatSize(data.size);
  els.chartCenterLabel.innerHTML = `<strong>${totalFormatted.text}</strong>${data.children.length} item(ns)`;
}

/* -------------------------------- Gráfico -------------------------------- */

function renderChart(children) {
  const dirsAndFiles = children
    .filter((c) => c.size > 0 || c.is_dir)
    .sort((a, b) => b.size - a.size);

  const top = dirsAndFiles.slice(0, 12);
  const rest = dirsAndFiles.slice(12);
  const restSum = rest.reduce((acc, c) => acc + c.size, 0);

  const labels = top.map((c) => c.name);
  const values = top.map((c) => c.size);
  const refs = top.map((c) => c);

  if (restSum > 0) {
    labels.push("Outros");
    values.push(restSum);
    refs.push(null);
  }

  if (values.length === 0) {
    if (state.chart) {
      state.chart.destroy();
      state.chart = null;
    }
    return;
  }

  const ctx = document.getElementById("donut-chart").getContext("2d");
  if (state.chart) {
    state.chart.destroy();
  }

  state.chart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: labels.map((_, i) => COLORS[i % COLORS.length]),
        borderColor: "#e6e9ef",
        borderWidth: 3,
        hoverOffset: 10,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "62%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 12, font: { size: 11 } },
        },
        tooltip: {
          callbacks: {
            label: (ctx2) => {
              const f = formatSize(ctx2.raw);
              return ` ${ctx2.label}: ${f.text}`;
            },
          },
        },
      },
      onClick: (_evt, elements) => {
        if (!elements.length) return;
        const idx = elements[0].index;
        const ref = refs[idx];
        if (ref && ref.is_dir) {
          loadFolder(ref.path, true);
        }
      },
    },
  });
}

/* --------------------------------- Lista --------------------------------- */

function renderList(children) {
  els.listContainer.innerHTML = "";

  const sorted = [...children].sort((a, b) => b.size - a.size);

  if (sorted.length === 0) {
    const empty = document.createElement("div");
    empty.className = "list-item";
    empty.textContent = "Diretório vazio.";
    els.listContainer.appendChild(empty);
    return;
  }

  sorted.forEach((item, idx) => {
    const row = document.createElement("div");
    row.className = `list-item${item.is_dir ? " is-dir" : ""}`;

    const dot = document.createElement("span");
    dot.className = "list-item-icon";
    dot.style.background = item.is_dir ? COLORS[idx % COLORS.length] : "#b8bcc4";

    const name = document.createElement("span");
    name.className = "list-item-name";
    name.textContent = truncateMiddle(item.name, 42);
    name.title = item.name;

    const sizeInfo = formatSize(item.size);
    const size = document.createElement("span");
    size.className = `list-item-size ${sizeInfo.cls}`;
    size.textContent = item.size_ready ? sizeInfo.text : "calculando...";

    row.appendChild(dot);
    row.appendChild(name);
    row.appendChild(size);

    if (item.is_dir) {
      row.addEventListener("click", () => loadFolder(item.path, true));
    }

    els.listContainer.appendChild(row);
  });
}

/* -------------------------------- Eventos -------------------------------- */

els.btnSelect.addEventListener("click", selectFolder);
els.btnBack.addEventListener("click", goBack);