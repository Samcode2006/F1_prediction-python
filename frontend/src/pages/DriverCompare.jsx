import { useEffect, useState } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip, Legend
} from 'recharts'
import { api } from '../api'
import './DriverCompare.css'

export default function DriverCompare() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [driverA, setDriverA] = useState('')
  const [driverB, setDriverB] = useState('')

  useEffect(() => {
    api.predict()
      .then(d => {
        setData(d)
        if (d.fullField.length >= 2) {
          setDriverA(d.fullField[0].driver)
          setDriverB(d.fullField[1].driver)
        }
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-wrapper"><p className="loading-text">Loading…</p></div>
  if (error)   return <div className="page-wrapper"><p className="error-text">Error: {error}</p></div>

  const allDrivers = data.fullField
  const dA = allDrivers.find(d => d.driver === driverA)
  const dB = allDrivers.find(d => d.driver === driverB)

  const radarData = dA && dB ? buildRadar(dA, dB) : []

  return (
    <div className="page-wrapper compare-page">
      <header className="page-header">
        <h1>Driver Comparison</h1>
        <p>Compare any two drivers across all scoring factors.</p>
      </header>

      {/* Selectors */}
      <div className="compare-selectors card">
        <div className="selector-group">
          <label htmlFor="select-driver-a">Driver A</label>
          <select
            id="select-driver-a"
            value={driverA}
            onChange={e => setDriverA(e.target.value)}
            className="driver-select"
          >
            {allDrivers.map(d => (
              <option key={d.driver} value={d.driver}>{d.driver} ({d.team})</option>
            ))}
          </select>
        </div>

        <div className="compare-vs">VS</div>

        <div className="selector-group">
          <label htmlFor="select-driver-b">Driver B</label>
          <select
            id="select-driver-b"
            value={driverB}
            onChange={e => setDriverB(e.target.value)}
            className="driver-select"
          >
            {allDrivers.map(d => (
              <option key={d.driver} value={d.driver}>{d.driver} ({d.team})</option>
            ))}
          </select>
        </div>
      </div>

      {dA && dB && (
        <>
          {/* Score heads-up */}
          <div className="compare-hud">
            <ScoreHud driver={dA} colour={dA.teamColour} side="left" />
            <div className="compare-hud__vs">VS</div>
            <ScoreHud driver={dB} colour={dB.teamColour} side="right" />
          </div>

          {/* Radar chart */}
          <div className="card compare-chart-card">
            <h3 className="detail-section-title">Factor Comparison (Radar)</h3>
            <ResponsiveContainer width="100%" height={380}>
              <RadarChart data={radarData} margin={{ top: 20, right: 40, bottom: 20, left: 40 }}>
                <PolarGrid stroke="rgba(0,0,0,0.08)" />
                <PolarAngleAxis
                  dataKey="factor"
                  tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                />
                <Radar
                  name={dA.driver}
                  dataKey="A"
                  stroke={dA.teamColour || 'var(--red)'}
                  fill={dA.teamColour || 'var(--red)'}
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
                <Radar
                  name={dB.driver}
                  dataKey="B"
                  stroke={dB.teamColour || '#3671C6'}
                  fill={dB.teamColour || '#3671C6'}
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-hover)',
                    borderRadius: 'var(--r-md)',
                    fontSize: '0.8rem',
                  }}
                />
                <Legend
                  formatter={(val) => <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{val}</span>}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Factor breakdown table */}
          <div className="card">
            <h3 className="detail-section-title">Factor Breakdown</h3>
            <table className="f1-table compare-table">
              <thead>
                <tr>
                  <th>Factor</th>
                  <th style={{ color: dA.teamColour }}>{dA.driver}</th>
                  <th style={{ color: dB.teamColour }}>{dB.driver}</th>
                  <th>Edge</th>
                </tr>
              </thead>
              <tbody>
                {radarData.map(row => (
                  <tr key={row.factor}>
                    <td>{row.factor}</td>
                    <td className={`mono ${row.A > row.B ? 'winner-val' : ''}`}>{row.A}</td>
                    <td className={`mono ${row.B > row.A ? 'winner-val' : ''}`}>{row.B}</td>
                    <td>
                      {row.A > row.B
                        ? <span className="edge-badge" style={{ color: dA.teamColour }}>▲ {dA.driver}</span>
                        : row.B > row.A
                          ? <span className="edge-badge" style={{ color: dB.teamColour }}>▲ {dB.driver}</span>
                          : <span className="edge-badge tied">Tied</span>
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}

function ScoreHud({ driver, colour, side }) {
  return (
    <div className={`score-hud score-hud--${side}`}>
      <div className="score-hud__bar" style={{ background: colour }} />
      <div className="score-hud__name">{driver.driver}</div>
      <div className="score-hud__team">{driver.team}</div>
      <div className="score-hud__score mono">{driver.score}</div>
      <div className="score-hud__label">Total Score</div>
    </div>
  )
}

function buildRadar(dA, dB) {
  const bA = dA.breakdown
  const bB = dB.breakdown
  const keys = Object.keys(bA).filter(k => k !== 'Total')
  return keys.map(k => ({
    factor: k.replace(' Bonus', '').replace(' Strength', ''),
    A: Math.max(0, bA[k]),
    B: Math.max(0, bB[k]),
  }))
}
