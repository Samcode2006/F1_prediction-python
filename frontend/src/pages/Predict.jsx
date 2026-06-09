import React, { useEffect, useState } from 'react'
import { api } from '../api'
import './Predict.css'

const MAX_SCORE = 40  // max possible score from predictor

export default function Predict() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    api.predict()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-wrapper"><p className="loading-text">Loading predictions…</p></div>
  if (error)   return <div className="page-wrapper"><p className="error-text">Error: {error}</p></div>

  const { fullField } = data

  return (
    <div className="page-wrapper predict-page">
      <header className="predict-header">
        <h1>Full Driver Rankings</h1>
        <p className="predict-sub">
          Prediction score from 9 weighted factors. Click a driver to see the breakdown.
        </p>
      </header>

      <div className="card predict-card">
        <table className="f1-table">
          <thead>
            <tr>
              <th>Pos</th>
              <th>Driver</th>
              <th>Team</th>
              <th>Quali</th>
              <th>Prev</th>
              <th>Score</th>
              <th>Win %</th>
            </tr>
          </thead>
          <tbody>
            {fullField.map(driver => {
              const isOpen = expanded === driver.driver
              const pct    = Math.min(100, Math.round((driver.score / MAX_SCORE) * 100))
              const bd     = driver.breakdown

              return (
                <React.Fragment key={driver.driver}>
                  <tr
                    className={`predict-row ${isOpen ? 'predict-row--open' : ''}`}
                    onClick={() => setExpanded(isOpen ? null : driver.driver)}
                    id={`driver-row-${driver.driver.toLowerCase().replace(/\s+/g,'-')}`}
                    role="button"
                    tabIndex={0}
                    onKeyDown={e => e.key === 'Enter' && setExpanded(isOpen ? null : driver.driver)}
                  >
                    <td>
                      <PosBadge pos={driver.position} />
                    </td>
                    <td>
                      <div className="driver-cell">
                        <div className="driver-cell__bar" style={{ background: driver.teamColour }} />
                        <span className="driver-cell__name">{driver.driver}</span>
                      </div>
                    </td>
                    <td className="text-muted">{driver.team}</td>
                    <td className="mono">P{driver.qualifying}</td>
                    <td className="mono">P{driver.previousFinish}</td>
                    <td>
                      <div className="score-cell">
                        <span className="score-cell__val mono">{driver.score}</span>
                        <div className="progress-bar score-bar">
                          <div
                            className="progress-fill score-fill"
                            style={{
                              width: `${pct}%`,
                              background: `linear-gradient(90deg, ${driver.teamColour || 'var(--red)'}, ${driver.teamColour || 'var(--red)'}aa)`
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="mono">{pct}%</td>
                  </tr>

                  {/* Expandable breakdown row */}
                  {isOpen && (
                    <tr className="breakdown-row">
                      <td colSpan={7}>
                        <div className="breakdown">
                          <div className="breakdown-grid">
                            {Object.entries(bd)
                              .filter(([k]) => k !== 'Total')
                              .map(([key, val]) => (
                                <div key={key} className="breakdown-item">
                                  <span className="breakdown-item__label">{key}</span>
                                  <span className={`breakdown-item__val mono ${val > 0 ? 'positive' : val < 0 ? 'negative' : ''}`}>
                                    {val > 0 ? '+' : ''}{val}
                                  </span>
                                </div>
                              ))
                            }
                          </div>
                          <div className="breakdown-total">
                            Total: <span className="mono">{bd.Total} pts</span>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function PosBadge({ pos }) {
  const map = { 1: '🥇', 2: '🥈', 3: '🥉' }
  if (map[pos]) return <span className="pos-emoji">{map[pos]}</span>
  return (
    <span className="pos-num">P{pos}</span>
  )
}
