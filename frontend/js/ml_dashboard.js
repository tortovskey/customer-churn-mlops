const versionNode = document.querySelector("[data-model-version]");
const metricsNode = document.querySelector("[data-model-metrics]");
const logsNode = document.querySelector("[data-ml-logs]");
const mlStatus = document.querySelector("[data-ml-status]");
const trainButton = document.querySelector("[data-train-model]");

function renderVersion(version) {
  if (!versionNode) return;
  versionNode.innerHTML = `
    <div class="detail-list">
      <div class="detail-item"><span>Название</span>${version.model_name}</div>
      <div class="detail-item"><span>Версия</span>${version.model_version || "нет активной версии"}</div>
      <div class="detail-item"><span>Статус</span>${version.is_active ? "Активна" : "Не активирована"}</div>
      <div class="detail-item"><span>Создана</span>${window.api.formatDate(version.created_at)}</div>
    </div>`;
}

function renderMetrics(metrics) {
  if (!metricsNode) return;
  if (!metrics) {
    metricsNode.innerHTML = `<div class="empty">Метрики отсутствуют</div>`;
    return;
  }
  metricsNode.innerHTML = `
    <div class="grid three">
      <div class="metric"><span class="muted">Accuracy</span><span class="value">${metrics.accuracy}</span></div>
      <div class="metric"><span class="muted">Precision</span><span class="value">${metrics.precision}</span></div>
      <div class="metric"><span class="muted">Recall</span><span class="value">${metrics.recall}</span></div>
      <div class="metric"><span class="muted">F1-score</span><span class="value">${metrics.f1_score}</span></div>
      <div class="metric"><span class="muted">ROC-AUC</span><span class="value">${metrics.roc_auc || "-"}</span></div>
      <div class="metric"><span class="muted">Test size</span><span class="value">${metrics.test_size || "-"}</span></div>
    </div>`;
}

function renderLogs(logs) {
  if (!logsNode) return;
  if (!logs.length) {
    logsNode.innerHTML = `<div class="empty">Журнал пуст</div>`;
    return;
  }
  logsNode.innerHTML = logs
    .map(
      (log) => `
      <div class="log-item">
        <strong>${log.event_type}</strong>
        <div>${log.message}</div>
        <span class="muted">${window.api.formatDate(log.created_at)}</span>
      </div>`
    )
    .join("");
}

async function loadDashboard() {
  try {
    const dashboard = await window.api.request("/ml/dashboard");
    renderVersion(dashboard.version);
    renderMetrics(dashboard.metrics);
    renderLogs(dashboard.logs);
  } catch (error) {
    window.api.setStatus(mlStatus, error.message, true);
  }
}

trainButton?.addEventListener("click", async () => {
  trainButton.disabled = true;
  window.api.setStatus(mlStatus, "Обучение модели запущено...");
  try {
    await window.api.request("/ml/train", { method: "POST" });
    await loadDashboard();
    window.api.setStatus(mlStatus, "Новая версия модели активирована");
  } catch (error) {
    window.api.setStatus(mlStatus, error.message, true);
  } finally {
    trainButton.disabled = false;
  }
});

loadDashboard();

