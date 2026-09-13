const predictionsTable = document.querySelector("[data-predictions-table]");
const predictionsStatus = document.querySelector("[data-predictions-status]");

async function loadPredictions() {
  if (!predictionsTable) return;
  try {
    const predictions = await window.api.request("/predictions");
    if (!predictions.length) {
      predictionsTable.innerHTML = `<tr><td colspan="6" class="empty">Прогнозы пока не сохранены</td></tr>`;
      return;
    }

    predictionsTable.innerHTML = predictions
      .map(
        (item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.client ? item.client.full_name : item.client_id}</td>
          <td>${Math.round(item.prediction_value * 100)}%</td>
          <td><span class="pill ${window.api.riskClass(item.prediction_label)}">${item.prediction_label}</span></td>
          <td>${item.model_version}</td>
          <td>${window.api.formatDate(item.created_at)}</td>
        </tr>`
      )
      .join("");
  } catch (error) {
    window.api.setStatus(predictionsStatus, error.message, true);
  }
}

loadPredictions();

