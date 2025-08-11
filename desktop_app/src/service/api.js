const BASE = "http://localhost:8000";

export async function chat({ message, provider, model }) {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, provider, model }),
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function getModels(provider) {
  // If endpoint not yet implemented, fallback to default models
  const res = await fetch(`${BASE}/models?provider=${encodeURIComponent(provider)}`);
  if (!res.ok) return [];
  return await res.json();
}

export async function getScratchpad() {
  const res = await fetch(`${BASE}/scratchpad`);
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function clearScratchpad() {
  const res = await fetch(`${BASE}/scratchpad/clear`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function startAutoTest(target) {
  const res = await fetch(`${BASE}/auto-test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target }),
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

export async function setConfig(provider, apiKey) {
  const res = await fetch(`${BASE}/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, api_key: apiKey }),
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}