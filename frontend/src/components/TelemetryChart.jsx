import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid
} from 'recharts'
import './TelemetryChart.css'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__driver">{d.Abbreviation || label}</div>
      {d.FullName && <div className="chart-tooltip__name">{d.FullName}</div>}
      <div className="chart-tooltip__stat">Fastest: <strong>{d.FastestLap}</strong></div>
      <div className="chart-tooltip__stat">Avg: <strong>{fmtSec(d.AvgLapTime)}</strong></div>
      <div className="chart-tooltip__stat">Laps: <strong>{d.LapCount}</strong></div>
      {d.TyreCompounds?.length > 0 && (
        <div className="chart-tooltip__tyres">
          {d.TyreCompounds.map(c => (
            <span key={c} className={`tyre-badge tyre-badge--${c.toLowerCase()}`}>{c}</span>
          ))}
        </div>
      )}
    </div>
  )
}

function fmtSec(sec) {
  if (!sec) return 'N/A'
  const m = Math.floor(sec / 60)
  const s = (sec % 60).toFixed(3)
  return `${m}:${String(s).padStart(6,'0')}`
}

export default function TelemetryChart({ data }) {
  if (!data || data.length === 0) {
    return <p className="chart-empty">No lap data available for this race.</p>
  }

  const minFastest = Math.min(...data.map(d => d.FastestLapSec))

  return (
    <div className="telemetry-chart">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 60 }}>
          <CartesianGrid vertical={false} stroke="rgba(0,0,0,0.06)" />
          <XAxis
            dataKey="Abbreviation"
            tick={{ fill: 'var(--text-muted)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            angle={-45}
            textAnchor="end"
            interval={0}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={fmtSec}
            tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
            tickLine={false}
            axisLine={false}
            width={65}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />
          <Bar dataKey="FastestLapSec" radius={[4, 4, 0, 0]} maxBarSize={40}>
            {data.map((entry, i) => (
              <Cell
                key={entry.Abbreviation || i}
                fill={entry.FastestLapSec === minFastest ? 'var(--gold)' : (entry.TeamColour || '#444')}
                opacity={entry.FastestLapSec === minFastest ? 1 : 0.7}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Fastest lap label */}
      {data[0] && (
        <div className="telemetry-fl">
          <span className="tyre-badge tyre-badge--soft">⚡ Fastest Lap</span>
          <strong>{data[0].Abbreviation}</strong> — {data[0].FastestLap}
        </div>
      )}
    </div>
  )
}
