export const mod = (n, m) => ((n % m) + m) % m
export function makeTrack(track) {
  const coordinates = track.coordinates
  const lat = coordinates.reduce((sum, p) => sum + p[1], 0) / coordinates.length
  const raw = coordinates.map(p => [p[0] * Math.cos(lat * Math.PI / 180), -p[1]])
  const xs = raw.map(p => p[0]), ys = raw.map(p => p[1])
  const minX = Math.min(...xs), minY = Math.min(...ys)
  const width = Math.max(...xs) - minX, height = Math.max(...ys) - minY
  const scale = Math.min(840 / width, 460 / height)
  const points = raw.map(p => [(p[0] - minX) * scale + (1000 - width * scale) / 2, (p[1] - minY) * scale + (600 - height * scale) / 2])
  if (Math.hypot(points[0][0] - points.at(-1)[0], points[0][1] - points.at(-1)[1]) > .01) points.push(points[0])
  const segments = [], distances = [0]
  for (let i = 0; i < points.length - 1; i++) {
    const length = Math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
    if (length > .001) { segments.push({ a: points[i], b: points[i + 1], start: distances.at(-1), length }); distances.push(distances.at(-1) + length) }
  }
  return { ...track, points, segments, total: distances.at(-1) }
}
export function sample(track, distance, lane = 0) {
  const d = mod(distance, track.total)
  const s = track.segments.find(s => d < s.start + s.length) || track.segments.at(-1)
  const t = (d - s.start) / s.length
  const angle = Math.atan2(s.b[1] - s.a[1], s.b[0] - s.a[0])
  return { x: s.a[0] + (s.b[0] - s.a[0]) * t - Math.sin(angle) * lane, y: s.a[1] + (s.b[1] - s.a[1]) * t + Math.cos(angle) * lane, angle }
}
export function cornerSpeed(track, distance) {
  const a = sample(track, distance).angle, b = sample(track, distance + 24).angle
  const turn = Math.abs(Math.atan2(Math.sin(b - a), Math.cos(b - a)))
  return Math.max(48, 135 - turn * 62)
}
export function createRace(track, driver, roster) {
  const opponents = roster.filter(d => d.number !== driver.number).slice(0, 5)
  return { track, phase: 'countdown', countdown: 3, elapsed: 0, energy: 100, lapTimes: [], lapStart: 0, warning: '',
    cars: [...opponents, driver].map((d, i) => ({ ...d, player: i === 5, progress: -i * 19, speed: 0, lane: i % 2 ? 5 : -5, finish: null })) }
}
export function order(race) {
  return [...race.cars].sort((a, b) => a.finish != null && b.finish != null ? a.finish - b.finish : a.finish != null ? -1 : b.finish != null ? 1 : b.progress - a.progress)
}
export function step(race, keys, dt) {
  if (race.phase === 'paused' || race.phase === 'finished') return
  if (race.phase === 'countdown') { race.countdown -= dt; if (race.countdown <= 0) race.phase = 'racing'; return }
  race.elapsed += dt
  race.warning = ''
  for (const [index, car] of race.cars.entries()) {
    if (car.finish != null) continue
    const safe = cornerSpeed(race.track, car.progress)
    if (car.player) {
      const steering = Number(!!keys.right) - Number(!!keys.left)
      car.lane = Math.max(-24, Math.min(24, car.lane + steering * dt * 24))
      const boost = keys.boost && race.energy > 0 && keys.gas && !keys.brake
      race.energy = Math.max(0, Math.min(100, race.energy + (boost ? -32 : 10) * dt))
      car.speed = Math.max(0, Math.min(boost ? 175 : 142, car.speed + (keys.brake ? -180 : keys.gas ? 65 : -28) * dt))
      if (car.speed > safe + 18) {
        car.speed = Math.max(safe, car.speed - 85 * dt)
        car.lane = Math.min(24, car.lane + 9 * dt)
        race.warning = 'Too fast into the corner — brake!'
      }
      if (Math.abs(car.lane) > 12) { car.speed = Math.min(car.speed, 43); race.warning = 'Off track — steer back onto the asphalt' }
    } else {
      const target = safe * (.82 + index * .025)
      car.speed += Math.max(-150 * dt, Math.min(54 * dt, target - car.speed))
      car.lane = Math.sin(car.progress / 180 + index) * 7
    }
    // Prevent driving straight through another car; change lane to overtake.
    const ahead = race.cars.find(other => other !== car && other.finish == null && mod(other.progress - car.progress, race.track.total) < 17 && Math.abs(other.lane - car.lane) < 6)
    if (ahead) car.speed = Math.min(car.speed, Math.max(12, ahead.speed - 8))
    const oldLap = Math.floor(Math.max(0, car.progress) / race.track.total)
    car.progress += car.speed * dt
    const newLap = Math.floor(Math.max(0, car.progress) / race.track.total)
    if (car.player && newLap > oldLap) { race.lapTimes.push(race.elapsed - race.lapStart); race.lapStart = race.elapsed }
    if (car.progress >= race.track.total * 2) { car.progress = race.track.total * 2; car.finish = race.elapsed }
  }
  if (race.cars.find(c => c.player).finish != null) race.phase = 'finished'
}
