import { useEffect, useState } from 'react'
import './PodiumCard.css'

const MEDALS  = ['🥇', '🥈', '🥉']
const LABELS  = ['Winner', '2nd Place', '3rd Place']
const ACCENTS = ['gold', 'silver', 'bronze']

export default function PodiumCard({ driver, position }) {
  const [visible, setVisible] = useState(false)
  const idx = position - 1

  useEffect(() => {
    // Staggered reveal: each card animates in with a delay
    const t = setTimeout(() => setVisible(true), 150 + idx * 200)
    return () => clearTimeout(t)
  }, [idx])

  if (!driver) return null

  const accent = ACCENTS[idx]

  return (
    <div
      className={`podium-card podium-card--${accent} ${visible ? 'podium-card--visible' : ''}`}
      aria-label={`${LABELS[idx]}: ${driver.driver}`}
    >
      <div className="podium-card__medal">{MEDALS[idx]}</div>
      <div className="podium-card__label">{LABELS[idx]}</div>

      <div className="podium-card__team-bar" style={{ '--team-color': driver.teamColour }} />

      <div className="podium-card__driver">{driver.driver}</div>
      <div className="podium-card__team">{driver.team}</div>

      <div className="podium-card__score">
        <span className="podium-card__score-value">{driver.score}</span>
        <span className="podium-card__score-label">pts</span>
      </div>

      <div className="podium-card__meta">
        <span>P{driver.qualifying} quali</span>
        <span>·</span>
        <span>P{driver.previousFinish} prev</span>
      </div>
    </div>
  )
}
