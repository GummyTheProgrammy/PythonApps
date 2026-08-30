(() => {
  "use strict";

  // ---------- Estado ----------
  const state = {
    storedName: null,
    originalName: null,
    duration: 0,
    markIn: 0,
    markOut: 0,
    cuts: [], // {start, end, batch, segment}
    outputFolder: "",
  };

  // ---------- Elementos ----------
  const btnChooseFile = document.getElementById("btnChooseFile");
  const pickStatus = document.getElementById("pickStatus");
  const playerWrap = document.getElementById("playerWrap");
  const video = document.getElementById("videoPlayer");

  const tlCurrent = document.getElementById("tlCurrent");
  const tlDuration = document.getElementById("tlDuration");
  const timeline = document.getElementById("timeline");
  const tlProgress = document.getElementById("tlProgress");
  const tlSelection = document.getElementById("tlSelection");
  const tlHandleStart = document.getElementById("tlHandleStart");
  const tlHandleEnd = document.getElementById("tlHandleEnd");
  const tlPlayhead = document.getElementById("tlPlayhead");

  const btnMarkIn = document.getElementById("btnMarkIn");
  const btnMarkOut = document.getElementById("btnMarkOut");
  const markInLabel = document.getElementById("markInLabel");
  const markOutLabel = document.getElementById("markOutLabel");
  const markDurLabel = document.getElementById("markDurLabel");

  const batchToggle = document.getElementById("batchToggle");
  const batchOptions = document.getElementById("batchOptions");
  const batchSeconds = document.getElementById("batchSeconds");
  const reencodeToggle = document.getElementById("reencodeToggle");

  const btnAddCut = document.getElementById("btnAddCut");
  const cutsList = document.getElementById("cutsList");
  const btnExport = document.getElementById("btnExport");

  const btnChooseFolder = document.getElementById("btnChooseFolder");
  const outputFolderLabel = document.getElementById("outputFolderLabel");

  const exportResult = document.getElementById("exportResult");
  const exportSummary = document.getElementById("exportSummary");
  const btnOpenExportFolder = document.getElementById("btnOpenExportFolder");
  const exportFilesList = document.getElementById("exportFilesList");
  const statusBox = document.getElementById("statusBox");

  const btnShowLog = document.getElementById("btnShowLog");
  const btnCloseLog = document.getElementById("btnCloseLog");
  const btnOpenLogFolder = document.getElementById("btnOpenLogFolder");
  const logModal = document.getElementById("logModal");
  const logContent = document.getElementById("logContent");

  let lastExportFolder = null;

  // ---------- Utilidades ----------
  function fmtTime(totalSeconds, withMs = false) {
    totalSeconds = Math.max(0, totalSeconds || 0);
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    if (withMs) {
      return `${String(m).padStart(2, "0")}:${s.toFixed(2).padStart(5, "0")}`;
    }
    return `${String(m).padStart(2, "0")}:${String(Math.floor(s)).padStart(2, "0")}`;
  }

  function setStatus(msg, type) {
    statusBox.textContent = msg || "";
    statusBox.className = "status-box" + (type ? " " + type : "");
  }

  function pct(value) {
    if (!state.duration) return 0;
    return Math.min(100, Math.max(0, (value / state.duration) * 100));
  }

  // ---------- Seleção de vídeo (diálogo nativo via Python) ----------
  btnChooseFile.addEventListener("click", async () => {
    pickStatus.textContent = "Abrindo seletor de arquivo...";
    setStatus("");
    try {
      const result = await eel.pick_video()();
      if (result.cancelled) {
        pickStatus.textContent = state.storedName ? pickStatus.textContent : "Nenhum vídeo carregado";
        return;
      }
      if (result.error) {
        pickStatus.textContent = "Falha ao carregar vídeo.";
        setStatus(result.error, "error");
        return;
      }

      state.storedName = result.stored_name;
      state.originalName = result.original_name;
      state.duration = result.duration;
      state.markIn = 0;
      state.markOut = Math.min(20, result.duration);
      state.cuts = [];

      video.src = result.url;
      playerWrap.classList.remove("hidden");
      pickStatus.textContent = `Carregado: ${result.original_name} (${fmtTime(result.duration)})`;

      renderCutsList();
      exportResult.classList.add("hidden");
      updateSelectionUI();
      tlDuration.textContent = fmtTime(state.duration);
    } catch (err) {
      pickStatus.textContent = "Falha ao carregar vídeo.";
      setStatus(String(err), "error");
    }
  });

  // ---------- Timeline: playhead / progresso ----------
  video.addEventListener("loadedmetadata", () => {
    if (!state.duration) state.duration = video.duration;
    tlDuration.textContent = fmtTime(state.duration);
  });

  video.addEventListener("timeupdate", () => {
    tlCurrent.textContent = fmtTime(video.currentTime);
    tlProgress.style.width = pct(video.currentTime) + "%";
    tlPlayhead.style.left = pct(video.currentTime) + "%";
  });

  timeline.addEventListener("click", (e) => {
    if (e.target === tlHandleStart || e.target === tlHandleEnd) return;
    const rect = timeline.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    const t = Math.min(state.duration, Math.max(0, ratio * state.duration));
    video.currentTime = t;
  });

  // ---------- Marcação de início/fim ----------
  function updateSelectionUI() {
    const startPct = pct(state.markIn);
    const endPct = pct(state.markOut);
    tlSelection.style.left = startPct + "%";
    tlSelection.style.width = Math.max(0, endPct - startPct) + "%";
    tlHandleStart.style.left = startPct + "%";
    tlHandleEnd.style.left = endPct + "%";

    markInLabel.textContent = fmtTime(state.markIn, true);
    markOutLabel.textContent = fmtTime(state.markOut, true);
    markDurLabel.textContent = Math.max(0, state.markOut - state.markIn).toFixed(2) + "s";
  }

  btnMarkIn.addEventListener("click", () => {
    state.markIn = video.currentTime;
    if (state.markIn > state.markOut) state.markOut = Math.min(state.duration, state.markIn + 1);
    updateSelectionUI();
  });

  btnMarkOut.addEventListener("click", () => {
    state.markOut = Math.max(video.currentTime, 0);
    if (state.markOut < state.markIn) state.markIn = Math.max(0, state.markOut - 1);
    updateSelectionUI();
  });

  // arrastar handles
  function dragHandle(handleEl, isStart) {
    handleEl.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      const rect = timeline.getBoundingClientRect();

      function onMove(ev) {
        const ratio = (ev.clientX - rect.left) / rect.width;
        const t = Math.min(state.duration, Math.max(0, ratio * state.duration));
        if (isStart) {
          state.markIn = Math.max(0, Math.min(t, state.markOut - 0.05));
        } else {
          state.markOut = Math.min(state.duration, Math.max(t, state.markIn + 0.05));
        }
        updateSelectionUI();
      }
      function onUp() {
        document.removeEventListener("pointermove", onMove);
        document.removeEventListener("pointerup", onUp);
      }
      document.addEventListener("pointermove", onMove);
      document.addEventListener("pointerup", onUp);
    });
  }
  dragHandle(tlHandleStart, true);
  dragHandle(tlHandleEnd, false);

  // ---------- Batch toggle ----------
  batchToggle.addEventListener("change", () => {
    batchOptions.classList.toggle("hidden", !batchToggle.checked);
  });

  // ---------- Lista de cortes ----------
  function renderCutsList() {
    cutsList.innerHTML = "";
    if (state.cuts.length === 0) {
      cutsList.innerHTML = '<li class="cuts-empty">Nenhum corte adicionado ainda.</li>';
      btnExport.disabled = true;
      return;
    }
    btnExport.disabled = false;

    state.cuts.forEach((cut, idx) => {
      const li = document.createElement("li");
      li.className = "cut-item";
      const dur = (cut.end - cut.start).toFixed(2);
      const badge = cut.batch ? `<span class="cut-badge">BATCH ${cut.segment}s</span>` : "";
      li.innerHTML = `
        <div class="cut-info">
          Corte ${idx + 1}: ${fmtTime(cut.start, true)} → ${fmtTime(cut.end, true)} (${dur}s) ${badge}
        </div>
        <button data-idx="${idx}" title="Remover">✕</button>
      `;
      li.querySelector("button").addEventListener("click", () => {
        state.cuts.splice(idx, 1);
        renderCutsList();
      });
      cutsList.appendChild(li);
    });
  }

  btnAddCut.addEventListener("click", () => {
    if (!state.storedName) {
      setStatus("Selecione um vídeo primeiro.", "error");
      return;
    }
    if (state.markOut - state.markIn < 0.1) {
      setStatus("Selecione um intervalo válido na timeline antes de adicionar.", "error");
      return;
    }
    const cut = {
      start: state.markIn,
      end: state.markOut,
      batch: batchToggle.checked,
      segment: batchToggle.checked ? (parseFloat(batchSeconds.value) || 20) : null,
    };
    state.cuts.push(cut);
    renderCutsList();
    setStatus("Corte adicionado à lista.", "success");
  });

  // ---------- Pasta de destino ----------
  btnChooseFolder.addEventListener("click", async () => {
    try {
      const result = await eel.pick_output_folder()();
      if (result.error) {
        setStatus(result.error, "error");
        return;
      }
      if (result.folder) {
        state.outputFolder = result.folder;
        outputFolderLabel.textContent = result.folder;
      }
    } catch (err) {
      setStatus(String(err), "error");
    }
  });

  // ---------- Exportar ----------
  btnExport.addEventListener("click", async () => {
    if (!state.cuts.length) return;
    btnExport.disabled = true;
    setStatus("Exportando... isso pode levar alguns instantes.", "");
    exportResult.classList.add("hidden");

    try {
      const result = await eel.export_cuts({
        stored_name: state.storedName,
        original_name: state.originalName,
        reencode: reencodeToggle.checked,
        output_folder: state.outputFolder,
        cuts: state.cuts,
      })();

      if (result.error) throw new Error(result.error);

      lastExportFolder = result.output_folder;
      exportResult.classList.remove("hidden");
      exportSummary.textContent = `${result.files.length} arquivo(s) gerado(s) em: ${result.output_folder}` +
        (result.errors && result.errors.length ? ` (${result.errors.length} aviso(s)/erro(s))` : "");
      exportFilesList.innerHTML = "";
      result.files.forEach((f) => {
        const li = document.createElement("li");
        li.textContent = f;
        exportFilesList.appendChild(li);
      });
      if (result.errors && result.errors.length) {
        setStatus("Avisos:\n" + result.errors.join("\n"), "error");
      } else {
        setStatus("Exportação concluída com sucesso.", "success");
      }
    } catch (err) {
      setStatus(String(err.message || err), "error");
    } finally {
      btnExport.disabled = false;
    }
  });

  btnOpenExportFolder.addEventListener("click", async () => {
    if (!lastExportFolder) return;
    await eel.open_path(lastExportFolder)();
  });

  // ---------- Log ----------
  btnShowLog.addEventListener("click", async () => {
    logModal.classList.remove("hidden");
    logContent.textContent = "Carregando...";
    try {
      logContent.textContent = await eel.get_log_text()();
      logContent.scrollTop = logContent.scrollHeight;
    } catch (err) {
      logContent.textContent = "Erro ao carregar o log.";
    }
  });
  btnCloseLog.addEventListener("click", () => logModal.classList.add("hidden"));

  btnOpenLogFolder.addEventListener("click", async () => {
    const logsDir = await eel.get_logs_dir()();
    await eel.open_path(logsDir)();
  });

  // ---------- Atalhos de teclado ----------
  document.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT") return;
    if (!state.storedName) return;
    if (e.key.toLowerCase() === "i") btnMarkIn.click();
    if (e.key.toLowerCase() === "o") btnMarkOut.click();
  });
})();
