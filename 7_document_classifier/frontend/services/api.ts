// src/services/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function apiGet(path: string) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Erro na API: ${res.status}`);
  }
  return res.json();
}