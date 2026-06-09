import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'
import WeatherPanel from '../components/WeatherPanel'
import TelemetryChart from '../components/TelemetryChart'
import CircuitCard from '../components/CircuitCard'
import './RaceDetail.css'

export default function RaceDetail() {
  const { year, round } = useParams()
  const [results, setResults] = useState(null)
  const [telemetry, setTelemetry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('lap')

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      api.results(year, round),
      api.telemetry(year, round),
    ])
      .then(([r, t]) => {
        setResults(r)
        setTelemetry(t)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [year, round])

  if (loading) return <div className="page-wrapper"><p className="loading-text">Loading race data…</p></div>
  if (error) return <div className="page-wrapper"><p className="error-text">Error: {error}</p></div>

  const trackName = results?.trackName || telemetry?.trackName || 'Race'
  const weather = results?.weather

  return (
    <div className="page-wrapper race-detail">
      <div className="detail-back">
        <Link to="/races" className="btn btn-ghost">← Race History</Link>
      </div>

      <header className="detail-header">
        <span className="detail-year">{year}</span>
        <h1 className="detail-title">{trackName}</h1>
        <span className="badge badge-gray mono">{results?.date}</span>
      </header>

      {/* Circuit map + Weather — side by side */}
      <div className="detail-hero-grid">
        <div>
          <h3 className="detail-section-title">🗺️ Circuit Map</h3>
          <CircuitCard trackName={trackName} />
        </div>

        {weather && (
          <div>
            <h3 className="detail-section-title">🌤️ Race Day Weather</h3>
            <div className="card detail-weather">
              <WeatherPanel weather={weather} />
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="detail-tabs">
        {[
          { id: 'lap', label: '⏱️ Lap Times' },
          { id: 'drivers', label: '👤 Drivers' },
        ].map(tab => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            className={`detail-tab ${activeTab === tab.id ? 'detail-tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="detail-content card">
        {activeTab === 'lap' && (
          <div>
            <h3 className="detail-section-title">Fastest Lap Comparison</h3>
            <p className="detail-section-sub">
              Sorted by fastest lap time. Gold bar = race's fastest lap setter.
            </p>
            <TelemetryChart data={telemetry?.lapSummary} />

            {/* Lap summary table */}
            {telemetry?.lapSummary?.length > 0 && (
              <div className="lap-table-wrap">
                <table className="f1-table lap-table">
                  <thead>
                    <tr>
                      <th>Pos</th>
                      <th>Driver</th>
                      <th>Team</th>
                      <th>Fastest Lap</th>
                      <th>Avg Lap</th>
                      <th>Laps</th>
                      <th>Tyres</th>
                    </tr>
                  </thead>
                  <tbody>
                    {telemetry.lapSummary.map((d, i) => (
                      <tr key={d.Abbreviation || i}>
                        <td><span className="lap-pos">P{i + 1}</span></td>
                        <td>
                          <div className="driver-cell">
                            <div
                              className="driver-cell__bar"
                              style={{ background: d.TeamColour }}
                            />
                            <div>
                              <div style={{ fontWeight: 600 }}>{d.Abbreviation}</div>
                              {d.FullName && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{d.FullName}</div>}
                            </div>
                          </div>
                        </td>
                        <td className="text-muted">{d.TeamName}</td>
                        <td className={`mono ${i === 0 ? 'gold-text' : ''}`}>{d.FastestLap}</td>
                        <td className="mono">{fmtSec(d.AvgLapTime)}</td>
                        <td className="mono">{d.LapCount}</td>
                        <td>
                          <div className="tyre-list">
                            {d.TyreCompounds.map(c => (
                              <span key={c} className={`tyre-badge tyre-badge--${c.toLowerCase()}`}>{c}</span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'drivers' && (
          <div>
            <h3 className="detail-section-title">Driver Information</h3>
            <div className="driver-grid">
              {results?.results?.map(d => (
                <div key={d.DriverNumber} className="driver-info-card">
                  <div
                    className="driver-info-card__colour"
                    style={{ background: d.TeamColour }}
                  />
                  <div className="driver-info-card__body">
                    <div className="driver-info-card__abbr">{d.Abbreviation}</div>
                    <div className="driver-info-card__name">{d.FullName}</div>
                    <div className="driver-info-card__team">{d.TeamName}</div>
                  </div>
                  <span className="driver-info-card__num mono">#{d.DriverNumber}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function fmtSec(sec) {
  if (!sec) return 'N/A'
  const m = Math.floor(sec / 60)
  const s = (sec % 60).toFixed(3)
  return `${m}:${String(s).padStart(6, '0')}`
}
