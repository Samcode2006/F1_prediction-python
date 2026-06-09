import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import PodiumCard from '../components/PodiumCard'
import WeatherPanel from '../components/WeatherPanel'
import heroLogo from '../assets/Formula_1_Logo_5.png'
import './Dashboard.css'

export default function Dashboard() {
  const [prediction, setPrediction] = useState(null)
  const [constructors, setConstructors] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.predict(), api.constructors()])
      .then(([pred, cons]) => {
        setPrediction(pred)
        setConstructors(cons.standings)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} />

  const { podium, fullField } = prediction

  return (
    <div className="page-wrapper dashboard">
      {/* Hero Container */}
      <section className="dashboard-hero-container">
        <div className="dashboard-hero">
          <div className="dashboard-hero__eyebrow">
            <span className="badge badge-red">🏎️ Prediction Engine</span>
            <span className="badge badge-gray">Rule-based Scoring v2</span>
          </div>
          <h1 className="display dashboard-hero__title">
            Next Race<br />
            <span className="dashboard-hero__title-accent">Predictions</span>
          </h1>
          <p className="dashboard-hero__sub">
            Based on qualifying position, recent form, team strength,
            tyre strategy and championship standings.
          </p>
          <Link to="/predict" className="btn btn-primary">
            Full Driver Rankings →
          </Link>
        </div>
        <div className="dashboard-hero-banner">
          <img src={heroLogo} alt="Formula 1 Logo" className="hero-banner-img" />
        </div>
      </section>

      {/* Podium */}
      <section>
        <h2 className="section-title">🏆 Predicted Podium</h2>
        <div className="podium-grid">
          {podium.map(driver => (
            <PodiumCard
              key={driver.driver}
              driver={driver}
              position={driver.position}
            />
          ))}
        </div>
      </section>

      <div className="divider" />

      {/* Constructor standings */}
      <section>
        <h2 className="section-title">Constructor Standings</h2>
        <div className="card">
          <table className="f1-table">
            <thead>
              <tr>
                <th>Pos</th>
                <th>Team</th>
                <th>Score</th>
                <th>Drivers</th>
                <th>Strength</th>
              </tr>
            </thead>
            <tbody>
              {constructors?.map((t, i) => (
                <tr key={t.Team}>
                  <td>
                    <span className={`pos-badge pos-badge--${i < 3 ? ['gold','silver','bronze'][i] : 'normal'}`}>
                      {i + 1}
                    </span>
                  </td>
                  <td>
                    <div className="team-cell">
                      <div className="team-dot" style={{ background: '#888' }} />
                      <strong>{t.Team}</strong>
                    </div>
                  </td>
                  <td className="mono">{t.ConstructorScore}</td>
                  <td>{t.DriverCount}</td>
                  <td>
                    <div className="inline-bar">
                      <div className="inline-bar-fill" style={{ width: `${(t.TeamStrength / 10) * 100}%` }} />
                      <span>{t.TeamStrength}/10</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function StatCard({ icon, label, value }) {
  return (
    <div className="card stat-card">
      <span className="stat-card__icon">{icon}</span>
      <span className="stat-card__value mono">{value}</span>
      <span className="stat-card__label">{label}</span>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="page-wrapper">
      <div className="loading-grid">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 280, borderRadius: 'var(--r-xl)' }} />
        ))}
      </div>
    </div>
  )
}

function ErrorState({ message }) {
  return (
    <div className="page-wrapper">
      <div className="error-state card">
        <span className="error-state__icon">⚠️</span>
        <h2>Could not load predictions</h2>
        <p>{message}</p>
        <p className="error-state__hint">
          Make sure the backend is running: <code>python backend/run.py</code>
          <br />and that <code>drivers.csv</code> exists: <code>python fetch_data.py</code>
        </p>
      </div>
    </div>
  )
}
