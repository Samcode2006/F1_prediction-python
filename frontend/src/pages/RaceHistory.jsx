import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import './RaceHistory.css'

export default function RaceHistory() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.races()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-wrapper"><p className="loading-text">Loading races…</p></div>
  if (error)   return <div className="page-wrapper"><p className="error-text">Error: {error}</p></div>
  if (!data?.years?.length) {
    return (
      <div className="page-wrapper">
        <p className="loading-text">
          No cached races found. Run <code>python bulk_fetch.py</code> first.
        </p>
      </div>
    )
  }

  return (
    <div className="page-wrapper race-history">
      <header className="page-header">
        <h1>Race History</h1>
        <p>All cached race sessions. Click to view lap times, weather and driver info.</p>
      </header>

      {data.years.map(year => (
        <section key={year} className="year-section">
          <h2 className="section-title">{year} Season</h2>
          <div className="races-grid">
            {data.races[year].map(race => (
              <RaceCard key={race.folderName} year={year} race={race} />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}

function RaceCard({ year, race }) {
  const hasRace  = race.sessions.some(s => s.includes('Race'))
  const hasQuali = race.sessions.some(s => s.includes('Qualifying'))

  return (
    <Link
      to={`/races/${year}/${race.round}`}
      className="race-card"
      id={`race-card-${year}-${race.round}`}
    >
      <div className="race-card__round">Round {race.round}</div>
      <div className="race-card__name">{race.trackName}</div>
      <div className="race-card__date">{race.date}</div>
      <div className="race-card__sessions">
        {hasQuali && <span className="badge badge-blue">Q</span>}
        {hasRace  && <span className="badge badge-red">R</span>}
      </div>
      <span className="race-card__arrow">→</span>
    </Link>
  )
}
