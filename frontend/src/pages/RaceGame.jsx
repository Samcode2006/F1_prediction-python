import { useEffect, useRef, useState } from 'react'
import { Flag, Play, RotateCcw, Pause, Trophy } from 'lucide-react'
import tracks from '../game/tracks.json'
import drivers from '../game/drivers.json'
import { makeTrack, createRace, step, order } from '../game/engine'
import { background, drawCar, render } from '../game/render'
import './RaceGame.css'

const time = seconds => `${Math.floor(seconds / 60)}:${(seconds % 60).toFixed(2).padStart(5, '0')}`
function CarPreview({ driver }) {
  const ref = useRef(null)
  useEffect(() => { const ctx = ref.current.getContext('2d'); ctx.clearRect(0, 0, 320, 110); drawCar(ctx, 160, 55, 0, driver.colour, driver.number, false, 5) }, [driver])
  return <canvas ref={ref} width="320" height="110" className="garage-car" role="img" aria-label={`${driver.team} car number ${driver.number}`} />
}
function TrackPreview({ track }) {
  const path = makeTrack(track).points.map(p => p.join(',')).join(' ')
  return <svg viewBox="0 0 1000 600" aria-hidden="true"><polyline points={path} fill="none" stroke="currentColor" strokeWidth="14" strokeLinejoin="round" /></svg>
}

export default function RaceGame() {
  const [driverNumber, setDriverNumber] = useState(16)
  const [trackId, setTrackId] = useState('it-1922')
  const [race, setRace] = useState(null)
  const [run, setRun] = useState(0)
  const driver = drivers.find(d => d.number === driverNumber) || drivers[0]
  const track = tracks.find(t => t.id === trackId)
  function start() { setRace({ driver, track }); setRun(n => n + 1) }
  return <div className="page-wrapper game-page">
    <header className="game-heading"><div><span className="game-eyebrow"><Flag size={14} /> LIGHTS OUT</span><h1>Race your way.</h1><p>Real circuits. Your driver. Two laps to make it count.</p></div><span className="game-format">2D ARCADE / 2026 GRID</span></header>
    {race ? <Race key={run} configuration={race} onRestart={() => setRun(n => n + 1)} onGarage={() => setRace(null)} /> : <div className="garage">
      <section className="card driver-picker"><span className="game-step">01 / CHOOSE YOUR DRIVER</span>
        <div className="driver-feature" style={{ '--livery': driver.colour }}><span className="driver-number">{driver.number}</span><CarPreview driver={driver}/><h2>{driver.name}</h2><p><span className="livery-dot" />{driver.team}</p></div>
        <label htmlFor="game-driver">2026 driver roster</label><select id="game-driver" value={driverNumber} onChange={e => setDriverNumber(Number(e.target.value))}>{drivers.map(d => <option key={d.number} value={d.number}>#{d.number} · {d.name} — {d.team}</option>)}</select>
        <div className="driver-facts"><span>CAR<strong>#{driver.number}</strong></span><span>CODE<strong>{driver.code}</strong></span><span>GRID<strong>22 drivers</strong></span></div>
      </section>
      <section className="card circuit-picker"><span className="game-step">02 / PICK YOUR CIRCUIT</span><div className="game-circuits">{tracks.map(t => <button key={t.id} className={t.id === trackId ? 'chosen' : ''} onClick={() => setTrackId(t.id)} aria-pressed={t.id === trackId}><TrackPreview track={t}/><strong>{t.location === 'Sakhir' ? 'Bahrain' : t.location}</strong><small>{(t.length / 1000).toFixed(3)} km</small></button>)}</div><h2>{track.name}</h2><p>Two laps · six cars · start from P6</p>
        <div className="game-controls-guide"><span><kbd>W / ↑</kbd> Accelerate</span><span><kbd>S / ↓</kbd> Brake</span><span><kbd>A D / ← →</kbd> Move across track</span><span><kbd>Space</kbd> Boost</span><span><kbd>P</kbd> Pause</span></div>
        <p className="game-tip">Cornering is assisted. Brake before tight turns, steer to pass, and keep off the grass.</p><button className="btn btn-primary game-start" onClick={start}>Start two-lap race <Play size={18}/></button>
      </section>
    </div>}
    <p className="game-credit">Arcade handling and illustrated team liveries, not a physics simulation. Circuit geometry: <a href="https://github.com/bacinger/f1-circuits" target="_blank" rel="noreferrer">Tomislav Bacinger (MIT)</a>. Driver names, numbers and teams: OpenF1, United States GP 2026.</p>
  </div>
}

function Race({ configuration, onRestart, onGarage }) {
  const canvas = useRef(null), model = useRef(null), inputs = useRef({}), pauseAction = useRef(null)
  const [hud, setHud] = useState(null)
  useEffect(() => {
    const track = makeTrack(configuration.track)
    const race = createRace(track, configuration.driver, drivers)
    model.current = race
    const ctx = canvas.current.getContext('2d')
    const scenery = document.createElement('canvas'); scenery.width = 1000; scenery.height = 600
    background(scenery.getContext('2d'), track)
    let frame, last = 0, report = 0
    const publish = () => {
      const car = race.cars.find(c => c.player)
      setHud({ phase: race.phase, countdown: Math.max(1, Math.ceil(race.countdown)), speed: Math.round(car.speed * 2.2), lap: Math.min(2, Math.floor(Math.max(0, car.progress) / track.total) + 1), position: order(race).findIndex(c => c.player) + 1, energy: race.energy, elapsed: race.elapsed, lapTimes: [...race.lapTimes], warning: race.warning, standings: order(race).map(c => ({ ...c })) })
    }
    function pause() {
      if (race.phase === 'finished') return
      if (race.phase === 'paused') race.phase = race.resumePhase
      else { race.resumePhase = race.phase; race.phase = 'paused'; inputs.current = {} }
      publish()
    }
    pauseAction.current = pause
    const keyMap = { ArrowUp: 'gas', w: 'gas', ArrowDown: 'brake', s: 'brake', ArrowLeft: 'left', a: 'left', ArrowRight: 'right', d: 'right', ' ': 'boost' }
    function key(event, pressed) {
      if (['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON', 'A'].includes(event.target.tagName)) return
      const name = event.key.length === 1 ? event.key.toLowerCase() : event.key
      if (keyMap[name]) { event.preventDefault(); inputs.current[keyMap[name]] = pressed }
      if (name === 'p' && pressed && !event.repeat) pause()
    }
    const down = e => key(e, true), up = e => key(e, false)
    const blur = () => { inputs.current = {}; if (race.phase !== 'paused' && race.phase !== 'finished') pause() }
    const visibility = () => { if (document.hidden) blur() }
    window.addEventListener('keydown', down); window.addEventListener('keyup', up); window.addEventListener('blur', blur); document.addEventListener('visibilitychange', visibility)
    function loop(stamp) {
      const dt = last ? Math.min((stamp - last) / 1000, .05) : 0; last = stamp
      // Fixed-sized substeps keep collisions and lap crossings stable.
      let remaining = dt
      while (remaining > 0) { const increment = Math.min(remaining, 1 / 120); step(race, inputs.current, increment); remaining -= increment }
      render(ctx, race, scenery)
      if (stamp - report > 100) { publish(); report = stamp }
      frame = requestAnimationFrame(loop)
    }
    publish(); canvas.current.focus({ preventScroll: true }); frame = requestAnimationFrame(loop)
    return () => { cancelAnimationFrame(frame); inputs.current = {}; window.removeEventListener('keydown', down); window.removeEventListener('keyup', up); window.removeEventListener('blur', blur); document.removeEventListener('visibilitychange', visibility) }
  }, [configuration])
  function touch(name, pressed, event) { event.preventDefault(); inputs.current[name] = pressed; if (pressed) event.currentTarget.setPointerCapture(event.pointerId) }
  return <section className="race-shell">
    <div className="race-toolbar"><strong>{configuration.track.location} <span> / {configuration.driver.name}</span></strong><div><button onClick={() => pauseAction.current?.()} aria-label={hud?.phase === 'paused' ? 'Resume race' : 'Pause race'}><Pause size={17}/></button><button onClick={onRestart} aria-label="Restart race"><RotateCcw size={17}/></button><button onClick={onGarage}>Garage</button></div></div>
    <div className="race-hud"><span>LAP<strong>{hud?.lap || 1}<small> / 2</small></strong></span><span>POSITION<strong>P{hud?.position || 6}<small> / 6</small></strong></span><span>TIME<strong>{time(hud?.elapsed || 0)}</strong></span><span>SPEED<strong>{hud?.speed || 0}<small> km/h</small></strong></span><span>BOOST<strong>{Math.round(hud?.energy || 0)}%</strong></span></div>
    <div className="race-view"><canvas ref={canvas} width="1000" height="600" tabIndex={0} aria-label="Racing game. W or up to accelerate, S or down to brake, left and right to change lane, Space to boost, P to pause."/>
      {hud?.phase === 'countdown' && <div className="race-overlay countdown" aria-live="polite"><div className="start-lights">{[1, 2, 3].map(n => <i key={n} className={n <= 4 - hud.countdown ? 'lit' : ''}/>)}</div><strong>{hud.countdown}</strong><p>Get ready. Hold W or ↑ to accelerate.</p></div>}
      {hud?.phase === 'paused' && <div className="race-overlay"><h2>Race paused</h2><button className="btn btn-primary" onClick={() => { pauseAction.current?.(); canvas.current.focus() }}>Resume race</button></div>}
      {hud?.phase === 'finished' && <div className="race-overlay finish" role="status"><Trophy size={36}/><h2>Chequered flag. P{hud.position}.</h2><p>{configuration.driver.name} · {time(hud.elapsed)}</p><div className="lap-results">{hud.lapTimes.map((lap, i) => <span key={i}>LAP {i + 1}<strong>{time(lap)}</strong></span>)}</div><div className="finish-actions"><button className="btn btn-primary" onClick={onRestart}>Race again</button><button onClick={onGarage}>Change driver / circuit</button></div></div>}
    </div>
    <div className="race-feedback" aria-live="polite">{hud?.warning || 'Hold throttle · brake before corners · move sideways to overtake'}</div>
    <div className="touch-controls" aria-label="Driving controls">{[['left', '←'], ['right', '→'], ['brake', 'Brake'], ['gas', 'Throttle'], ['boost', 'Boost']].map(([name, label]) => <button key={name} onPointerDown={e => touch(name, true, e)} onPointerUp={e => touch(name, false, e)} onPointerCancel={e => touch(name, false, e)} onLostPointerCapture={() => { inputs.current[name] = false }} onKeyDown={e => { if ([' ', 'Enter'].includes(e.key)) { e.preventDefault(); inputs.current[name] = true } }} onKeyUp={e => { if ([' ', 'Enter'].includes(e.key)) inputs.current[name] = false }} aria-label={name}>{label}</button>)}</div>
    <ol className="race-order">{hud?.standings.map(c => <li key={c.number} className={c.player ? 'is-player' : ''}><span style={{ color: c.colour }}>{c.code}</span>{c.player && ' YOU'}<small>{c.finish != null ? time(c.finish) : 'Racing'}</small></li>)}</ol>
  </section>
}
