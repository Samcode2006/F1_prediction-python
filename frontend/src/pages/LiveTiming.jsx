import { useEffect, useState } from 'react'
import { Radio, Flag } from 'lucide-react'
import { api } from '../api'
import './LiveTiming.css'

const localTime = value => new Date(value).toLocaleString(undefined, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })
function duration(value) {
  if (Array.isArray(value)) return value.map(duration).join(' / ')
  if (value == null) return '—'
  return `${Math.floor(value / 60)}:${(value % 60).toFixed(3).padStart(6, '0')}`
}
const labels = { upcoming: 'Not started', completed: 'Session results', live: 'Live timing', waiting: 'Waiting for updates', pending: 'Results pending', access_required: 'Live timing not connected', cancelled: 'Cancelled' }

export default function LiveTiming() {
  const [sessions, setSessions] = useState([])
  const [meeting, setMeeting] = useState('')
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let active = true
    api.sessions().then(({ sessions: rows }) => {
      if (!active) return
      setSessions(rows)
      const next = rows.find(s => !s.is_cancelled && new Date(s.date_end) > new Date()) || rows.at(-1)
      if (next) { setMeeting(String(next.meeting_key)); setSelected(next.session_key) }
      setError('')
    }).catch(e => active && setError(e.message))
    return () => { active = false }
  }, [attempt])
  const meetings = [...new Map(sessions.map(s => [String(s.meeting_key), s])).values()]
  const weekend = sessions.filter(s => String(s.meeting_key) === meeting)
  return <div className="page-wrapper session-page">
    <header className="session-heading"><div><span className="session-eyebrow"><Radio size={15} /> RACE WEEKEND</span><h1>Session Centre</h1><p>Practice. Qualifying. Lights out.</p></div>
      {meetings.length > 0 && <label>Race weekend<select value={meeting} onChange={e => {
        setMeeting(e.target.value)
        const weekendRows = sessions.filter(s => String(s.meeting_key) === e.target.value)
        setSelected((weekendRows.find(s => !s.is_cancelled && new Date(s.date_end) > new Date()) || weekendRows.at(-1)).session_key)
      }}>{meetings.map(s => <option key={s.meeting_key} value={s.meeting_key}>{s.location} · {new Date(s.date_start).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}</option>)}</select></label>}
    </header>
    {error ? <div role="alert" className="card session-empty"><p>{error}</p><button className="btn btn-primary" onClick={() => setAttempt(a => a + 1)}>Retry</button></div> : !sessions.length ? <p role="status">Loading session schedule…</p> : <>
      <div className="session-tabs" aria-label="Weekend sessions">{weekend.map(s => <button key={s.session_key} className={selected === s.session_key ? 'selected' : ''} aria-pressed={selected === s.session_key} onClick={() => setSelected(s.session_key)}>
        <strong>{s.session_name === 'Race' ? 'Grand Prix' : s.session_name}</strong><small>{localTime(s.date_start)}</small>
      </button>)}</div>
      {selected && <TimingBoard key={selected} sessionKey={selected} />}
    </>}
    <p className="session-credit">Timing by <a href="https://openf1.org/" target="_blank" rel="noreferrer">OpenF1</a> · Session times shown in your local timezone.</p>
  </div>
}

function TimingBoard({ sessionKey }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    let timer
    async function update() {
      try {
        const next = await api.timing(sessionKey)
        if (active) { setData(next); setError('') }
      } catch (e) { if (active) setError(e.message) }
      finally { if (active) timer = setTimeout(update, 30000) }
    }
    update()
    return () => { active = false; clearTimeout(timer) }
  }, [sessionKey])
  if (!data) return <div className="card session-empty" role="status">{error || 'Loading timing…'}</div>
  return <section className="card timing-board">
    <header><h2><Flag size={20} /> {data.session.session_name === 'Race' ? 'Grand Prix' : data.session.session_name}</h2><span className={data.status === 'live' && !error ? 'timing-live' : ''}>{error ? 'Connection interrupted · saved timing' : labels[data.status]}</span></header>
    {error && <p className="error-text" role="alert">{error}</p>}
    {!data.rows.length ? <div className="session-empty">
      <Radio size={34} /><h3>{labels[data.status]}</h3>
      <p>{data.status === 'upcoming' ? `Starts ${localTime(data.session.date_start)}` : data.status === 'access_required' ? 'Live coverage requires an OpenF1 subscription. Completed-session results will appear when released.' : data.status === 'cancelled' ? 'This session has been cancelled.' : 'Timing will appear here when the provider publishes it.'}</p>
    </div> : <div className="timing-scroll"><table className="f1-table"><thead><tr><th>Pos</th><th>Driver</th><th>Team</th><th>{data.session.session_type === 'Qualifying' && data.status === 'completed' ? 'Q1 / Q2 / Q3' : data.session.session_type === 'Race' && data.status === 'completed' ? 'Race time' : 'Best lap'}</th><th>Laps</th></tr></thead><tbody>
      {data.rows.map(row => <tr key={row.driver_number}><td className="mono">{row.position || '—'}</td><td><span className="timing-driver" style={{ borderColor: `#${row.colour}` }}>{row.name}</span>{row.dsq ? ' · DSQ' : row.dns ? ' · DNS' : row.dnf ? ' · DNF' : ''}</td><td>{row.team}</td><td className="mono">{duration(row.duration)}</td><td className="mono">{row.number_of_laps ?? '—'}</td></tr>)}
    </tbody></table></div>}
    <footer>Checks every 30 seconds · Last checked {localTime(data.updatedAt)}{data.lastEventAt && ` · Last timing event ${localTime(data.lastEventAt)}`}</footer>
  </section>
}
