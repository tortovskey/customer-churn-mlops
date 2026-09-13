const clientStatus = document.querySelector("[data-client-status]");
const clientsTable = document.querySelector("[data-clients-table]");
const clientForm = document.querySelector("[data-client-form]");
const clientDetail = document.querySelector("[data-client-detail]");
const updateForm = document.querySelector("[data-client-update-form]");
const predictionPanel = document.querySelector("[data-prediction-panel]");

const tariffNames = {
  basic: "Basic",
  standard: "Standard",
  premium: "Premium",
  enterprise: "Enterprise",
};

function serializeClientForm(form) {
  const data = new FormData(form);
  return {
    full_name: data.get("full_name").trim(),
    age: Number(data.get("age")),
    tenure_months: Number(data.get("tenure_months")),
    monthly_payment: Number(data.get("monthly_payment")),
    support_requests: Number(data.get("support_requests")),
    tariff_type: data.get("tariff_type"),
    last_month_activity: Number(data.get("last_month_activity")),
    has_debt: data.get("has_debt") === "on",
  };
}

async function loadClients() {
  if (!clientsTable) return;
  try {
    const clients = await window.api.request("/clients");
    if (!clients.length) {
      clientsTable.innerHTML = `<tr><td colspan="8" class="empty">Клиенты не добавлены</td></tr>`;
      return;
    }
    clientsTable.innerHTML = clients
      .map(
        (client) => `
        <tr>
          <td><a class="button" href="client_detail.html?id=${client.id}">${client.full_name}</a></td>
          <td>${client.age}</td>
          <td>${client.tenure_months}</td>
          <td>${window.api.money(client.monthly_payment)}</td>
          <td>${client.support_requests}</td>
          <td><span class="pill">${tariffNames[client.tariff_type]}</span></td>
          <td>${client.last_month_activity}%</td>
          <td>${client.has_debt ? "Да" : "Нет"}</td>
        </tr>`
      )
      .join("");
  } catch (error) {
    window.api.setStatus(clientStatus, error.message, true);
  }
}

function fillClientForm(form, client) {
  form.full_name.value = client.full_name;
  form.age.value = client.age;
  form.tenure_months.value = client.tenure_months;
  form.monthly_payment.value = client.monthly_payment;
  form.support_requests.value = client.support_requests;
  form.tariff_type.value = client.tariff_type;
  form.last_month_activity.value = client.last_month_activity;
  form.has_debt.checked = client.has_debt;
}

function renderClientDetail(client) {
  if (!clientDetail) return;
  clientDetail.innerHTML = `
    <div class="detail-list">
      <div class="detail-item"><span>Имя</span>${client.full_name}</div>
      <div class="detail-item"><span>Возраст</span>${client.age}</div>
      <div class="detail-item"><span>Срок использования</span>${client.tenure_months} мес.</div>
      <div class="detail-item"><span>Ежемесячный платеж</span>${window.api.money(client.monthly_payment)}</div>
      <div class="detail-item"><span>Обращения</span>${client.support_requests}</div>
      <div class="detail-item"><span>Тариф</span>${tariffNames[client.tariff_type]}</div>
      <div class="detail-item"><span>Активность</span>${client.last_month_activity}%</div>
      <div class="detail-item"><span>Задолженность</span>${client.has_debt ? "Есть" : "Нет"}</div>
    </div>`;
}

async function loadClientDetail() {
  if (!clientDetail) return;
  const id = new URLSearchParams(window.location.search).get("id");
  if (!id) {
    window.api.setStatus(clientStatus, "Клиент не выбран", true);
    return;
  }

  try {
    const client = await window.api.request(`/clients/${id}`);
    renderClientDetail(client);
    if (updateForm) fillClientForm(updateForm, client);
  } catch (error) {
    window.api.setStatus(clientStatus, error.message, true);
  }
}

async function createPrediction() {
  const id = new URLSearchParams(window.location.search).get("id");
  if (!id || !predictionPanel) return;
  window.api.setStatus(clientStatus, "Выполняется прогноз...");
  try {
    const result = await window.api.request(`/predictions/${id}`, { method: "POST" });
    const prediction = result.prediction;
    predictionPanel.innerHTML = `
      <div class="metric">
        <span class="muted">Вероятность оттока</span>
        <span class="value">${Math.round(prediction.prediction_value * 100)}%</span>
        <span class="pill ${window.api.riskClass(prediction.prediction_label)}">${prediction.prediction_label}</span>
        <span class="muted">Модель ${prediction.model_version}</span>
      </div>`;
    window.api.setStatus(clientStatus, "Прогноз сохранен");
  } catch (error) {
    window.api.setStatus(clientStatus, error.message, true);
  }
}

if (clientForm) {
  clientForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    window.api.setStatus(clientStatus, "Сохранение клиента...");
    try {
      await window.api.request("/clients", {
        method: "POST",
        body: JSON.stringify(serializeClientForm(clientForm)),
      });
      clientForm.reset();
      await loadClients();
      window.api.setStatus(clientStatus, "Клиент добавлен");
    } catch (error) {
      window.api.setStatus(clientStatus, error.message, true);
    }
  });
}

if (updateForm) {
  updateForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = new URLSearchParams(window.location.search).get("id");
    window.api.setStatus(clientStatus, "Обновление клиента...");
    try {
      const updated = await window.api.request(`/clients/${id}`, {
        method: "PUT",
        body: JSON.stringify(serializeClientForm(updateForm)),
      });
      renderClientDetail(updated);
      window.api.setStatus(clientStatus, "Карточка обновлена");
    } catch (error) {
      window.api.setStatus(clientStatus, error.message, true);
    }
  });
}

document.querySelector("[data-delete-client]")?.addEventListener("click", async () => {
  const id = new URLSearchParams(window.location.search).get("id");
  window.api.setStatus(clientStatus, "Удаление клиента...");
  try {
    await window.api.request(`/clients/${id}`, { method: "DELETE" });
    window.location.href = "clients.html";
  } catch (error) {
    window.api.setStatus(clientStatus, error.message, true);
  }
});

document.querySelector("[data-predict-client]")?.addEventListener("click", createPrediction);

loadClients();
loadClientDetail();

