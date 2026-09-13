const API_BASE_URL = localStorage.getItem("apiBaseUrl") || "http://localhost:8000";

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (response.status === 204) {
    return null;
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.detail || payload.message || `HTTP ${response.status}`;
    throw new Error(message);
  }
  return payload;
}

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function money(value) {
  return new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits: 0,
  }).format(value);
}

function riskClass(label) {
  if (label === "высокий риск") return "risk-high";
  if (label === "средний риск") return "risk-mid";
  return "risk-low";
}

function setStatus(element, message, isError = false) {
  if (!element) return;
  element.textContent = message || "";
  element.classList.toggle("error", isError);
}

window.api = {
  request: apiRequest,
  formatDate,
  money,
  riskClass,
  setStatus,
};

