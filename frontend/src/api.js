/* api.js — Centralised fetch helpers for the FastAPI backend */

const BASE = '/api'

async function get(path, method = 'GET') {
  const res = await fetch(`${BASE}${path}`, { method })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  sessions:    ()                  => get('/sessions'),
  timing:      key                 => get(`/sessions/${key}/timing`),
  refresh:     ()                  => get('/data/refresh', 'POST'),
  predict:     ()                  => get('/predict'),
  constructors:()                  => get('/constructors'),
  races:       ()                  => get('/races'),
  weather:     (year, round)       => get(`/race/${year}/${round}/weather`),
  telemetry:   (year, round)       => get(`/race/${year}/${round}/telemetry`),
  results:     (year, round)       => get(`/race/${year}/${round}/results`),
  health:      ()                  => get('/health'),
}
