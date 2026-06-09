import { useEffect, useState } from 'react'
import { fetchCircuitImage } from '../circuitImages'
import './CircuitCard.css'

/**
 * CircuitCard
 * Fetches and displays the track map image from Wikipedia for a given Grand Prix name.
 * Props:
 *   trackName  (string) — e.g. "Australian Grand Prix"
 *   compact    (bool)   — show a smaller version (for RaceHistory cards)
 */
export default function CircuitCard({ trackName, compact = false }) {
  const [info, setInfo]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [imgError, setImgError] = useState(false)

  useEffect(() => {
    if (!trackName) return
    setLoading(true)
    setInfo(null)
    setImgError(false)

    fetchCircuitImage(trackName)
      .then(setInfo)
      .finally(() => setLoading(false))
  }, [trackName])

  if (loading) {
    return (
      <div className={`circuit-card ${compact ? 'circuit-card--compact' : ''}`}>
        <div className="skeleton circuit-card__skeleton" />
      </div>
    )
  }

  if (!info?.thumbUrl || imgError) {
    return (
      <div className={`circuit-card circuit-card--empty ${compact ? 'circuit-card--compact' : ''}`}>
        <span className="circuit-card__empty-icon">🏎️</span>
        <span className="circuit-card__empty-label">Circuit image unavailable</span>
      </div>
    )
  }

  const imgSrc = compact ? info.thumbUrl : (info.imageUrl ?? info.thumbUrl)

  return (
    <div className={`circuit-card ${compact ? 'circuit-card--compact' : ''}`}>
      <div className="circuit-card__image-wrap">
        <img
          src={imgSrc}
          alt={`${trackName} circuit map`}
          className="circuit-card__image"
          onError={() => setImgError(true)}
        />
        <div className="circuit-card__overlay">
          <span className="circuit-card__overlay-name">{info.title}</span>
        </div>
      </div>

      {!compact && info.extract && (
        <div className="circuit-card__extract">
          <p>{info.extract.split('.').slice(0, 2).join('.') + '.'}</p>
          {info.wikiUrl && (
            <a
              href={info.wikiUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="circuit-card__wiki-link"
            >
              Wikipedia →
            </a>
          )}
        </div>
      )}
    </div>
  )
}
