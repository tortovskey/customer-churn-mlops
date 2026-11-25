const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../frontend/js/api.js"), "utf8");

function apiWithError(status, payload) {
  const window = {};
  vm.runInNewContext(source, {
    window,
    localStorage: { getItem: () => null },
    fetch: async () => ({ status, ok: false, json: async () => payload }),
  });
  return window.api;
}

test("validation errors identify each field on the customer form", async () => {
  const api = apiWithError(422, { detail: [
    { loc: ["body", "age"], msg: "Must be positive" },
    { loc: ["body", "full_name"], msg: "Field required" },
  ] });
  await assert.rejects(api.request("/clients"), { message: "age: Must be positive; full_name: Field required" });
});

test("ordinary errors keep their message and empty responses use the HTTP status", async () => {
  for (const [payload, message] of [[{detail: "Missing"}, "Missing"], [{message: "Offline"}, "Offline"], [null, "HTTP 404"]]) {
    await assert.rejects(apiWithError(404, payload).request("/clients/1"), { message });
  }
});
