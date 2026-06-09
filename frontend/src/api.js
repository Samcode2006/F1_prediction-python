/* api.js — Centralised fetch helpers for the FastAPI backend */

const BASE = import.meta.env.DEV ? 'http://localhost:8000/api' : '/api'

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  predict:     ()                  => get('/predict'),
  constructors:()                  => get('/constructors'),
  races:       ()                  => get('/races'),
  weather:     (year, round)       => get(`/race/${year}/${round}/weather`),
  telemetry:   (year, round)       => get(`/race/${year}/${round}/telemetry`),
  results:     (year, round)       => get(`/race/${year}/${round}/results`),
  health:      ()                  => get('/health'),
}
