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
    let message = typeof payload?.detail === "string" ? payload.detail : "";
    if (Array.isArray(payload?.detail)) {
      message = payload.detail
        .filter((issue) => typeof issue?.msg === "string")
        .map((issue) => {
          const location = Array.isArray(issue.loc) ? issue.loc : [];
          const path = (location[0] === "body" ? location.slice(1) : location).join(".");
          return path ? `${path}: ${issue.msg}` : issue.msg;
        })
        .join("; ");
    }
    if (!message && typeof payload?.message === "string") message = payload.message;
    throw new Error(message || `HTTP ${response.status}`);
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

