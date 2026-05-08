// src/api.ts

// ----------------------
// UNIFIED API BASE URL
// ----------------------
const API_BASE =
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000"; // FastAPI backend

// ----------------------
// USERS
// ----------------------
export async function fetchUsers() {
  const res = await fetch(`${API_BASE}/users`);
  if (!res.ok) throw new Error("Failed to fetch users");
  return res.json();
}

export async function createUser(user: { username: string; email: string }) {
  const res = await fetch(`${API_BASE}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(user),
  });
  if (!res.ok) throw new Error("Failed to create user");
  return res.json();
}

export async function deleteUser(id: number) {
  const res = await fetch(`${API_BASE}/users/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete user");
  return res.json();
}

// ----------------------
// TEAMS
// ----------------------
export async function fetchTeams() {
  const res = await fetch(`${API_BASE}/teams`);
  if (!res.ok) throw new Error("Failed to fetch teams");
  return res.json();
}

export async function createTeam(team: { name: string; description: string }) {
  const res = await fetch(`${API_BASE}/teams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(team),
  });
  if (!res.ok) throw new Error("Failed to create team");
  return res.json();
}

export async function deleteTeam(id: number) {
  const res = await fetch(`${API_BASE}/teams/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete team");
  return res.json();
}

// ----------------------
// MATCHES
// ----------------------
export async function fetchMatches() {
  const res = await fetch(`${API_BASE}/matches`);
  if (!res.ok) throw new Error("Failed to fetch matches");
  return res.json();
}

export async function createMatch(match: { team_a: string; team_b: string; score: string }) {
  const res = await fetch(`${API_BASE}/matches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(match),
  });
  if (!res.ok) throw new Error("Failed to create match");
  return res.json();
}

export async function deleteMatch(id: number) {
  const res = await fetch(`${API_BASE}/matches/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete match");
  return res.json();
}

// ----------------------
// ML STATUS
// ----------------------
export async function getMLStatus() {
  const res = await fetch(`${API_BASE}/ml/status`);
  if (!res.ok) throw new Error("Failed to fetch ML status");
  return res.json();
}

// ----------------------
// TRAINING HISTORY
// ----------------------
export async function getTrainingHistory() {
  const res = await fetch(`${API_BASE}/train/history`);
  if (!res.ok) throw new Error("Failed to fetch training history");
  return res.json();
}

// ----------------------
// MANUAL RETRAIN
// ----------------------
export async function retrainModel() {
  const res = await fetch(`${API_BASE}/train/retrain`, { method: "POST" });
  if (!res.ok) throw new Error("Retrain failed");
  return res.json();
}

// ----------------------
// EXPORT TRAINING CSV
// ----------------------
export function exportTrainingCSV() {
  window.location.href = `${API_BASE}/train/data/export`;
}

// ----------------------
// RAG - EXPLAIN
// ----------------------
export async function explainWithRAG(question: string) {
  const res = await fetch(`${API_BASE}/rag/api/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("Failed to get RAG explanation");
  return res.json();
}

// ----------------------
// EVENTS
// ----------------------
export async function fetchEvents(limit: number = 10) {
  const res = await fetch(`${API_BASE}/events?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch events");
  return res.json();
}

// ----------------------
// BLOCKS
// ----------------------
export async function fetchBlocks() {
  const res = await fetch(`${API_BASE}/blocks`);
  if (!res.ok) throw new Error("Failed to fetch blocks");
  return res.json();
}

export async function addBlock(ip: string, reason: string) {
  const res = await fetch(`${API_BASE}/blocks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip, reason }),
  });
  if (!res.ok) throw new Error("Failed to add block");
  return res.json();
}

export async function removeBlock(ip: string) {
  const res = await fetch(`${API_BASE}/blocks/${ip}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to remove block");
  return res.json();
}
