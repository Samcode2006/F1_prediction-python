import './WeatherPanel.css'

const MAX_TEMP = 50

function TempBar({ value, label }) {
  if (value === 'N/A') return null
  const pct = Math.min(100, (value / MAX_TEMP) * 100)
  return (
    <div className="weather-row">
      <span className="weather-label">{label}</span>
      <div className="weather-bar-wrap">
        <div className="progress-bar">
          <div
            className="progress-fill weather-fill"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="weather-value">{value}°C</span>
      </div>
    </div>
  )
}

export default function WeatherPanel({ weather }) {
  if (!weather) {
    return (
      <div className="weather-panel weather-panel--empty">
        <span>⚠️</span> Weather data not available
      </div>
    )
  }

  return (
    <div className="weather-panel">
      <div className="weather-conditions">
        <div className={`weather-condition ${weather.rainfall ? 'wet' : 'dry'}`}>
          <span className="weather-icon">{weather.rainfall ? '🌧️' : '☀️'}</span>
          <span>{weather.rainfall ? 'Wet Race' : 'Dry Race'}</span>
        </div>
      </div>

      <div className="weather-stats">
        <TempBar value={weather.air_temp}   label="Air Temp" />
        <TempBar value={weather.track_temp} label="Track Temp" />

        {weather.humidity !== 'N/A' && (
          <div className="weather-row">
            <span className="weather-label">Humidity</span>
            <div className="weather-bar-wrap">
              <div className="progress-bar">
                <div
                  className="progress-fill weather-fill humidity-fill"
                  style={{ width: `${Math.min(100, weather.humidity)}%` }}
                />
              </div>
              <span className="weather-value">{weather.humidity}%</span>
            </div>
          </div>
        )}

        {weather.wind_speed !== 'N/A' && (
          <div className="weather-row">
            <span className="weather-label">Wind Speed</span>
            <span className="weather-value">{weather.wind_speed} km/h</span>
          </div>
        )}
      </div>
    </div>
  )
}
