import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { makeTrack, sample, createRace, step, cornerSpeed, order } from './engine.js'
const tracks = JSON.parse(readFileSync(new URL('./tracks.json', import.meta.url)))
const drivers = JSON.parse(readFileSync(new URL('./drivers.json', import.meta.url)))

test('real circuit paths close and wrap without jumping', () => {
  for (const source of tracks) {
    const t = makeTrack(source)
    assert.ok(t.total > 1000)
    const start = sample(t, 0), end = sample(t, t.total)
    assert.ok(Math.hypot(start.x - end.x, start.y - end.y) < .001)
    assert.ok(t.points.every(p => p.every(Number.isFinite)))
  }
})
test('countdown and pause do not move the grid', () => {
  const r = createRace(makeTrack(tracks[0]), drivers[0], drivers)
  const before = r.cars.map(c => c.progress)
  step(r, { gas: true }, 1)
  assert.deepEqual(r.cars.map(c => c.progress), before)
  r.phase = 'paused'; step(r, { gas: true }, 10)
  assert.deepEqual(r.cars.map(c => c.progress), before)
})
for (const source of tracks) test(`can complete exactly two laps at ${source.location}`, () => {
  const r = createRace(makeTrack(source), drivers[0], drivers)
  r.phase = 'racing'
  for (let i = 0; i < 120 * 240 && r.phase !== 'finished'; i++) {
    const player = r.cars.find(c => c.player)
    const safe = cornerSpeed(r.track, player.progress)
    step(r, { gas: true, brake: player.speed > safe + 10, left: player.lane > -7, right: player.lane < -8 }, 1 / 120)
  }
  assert.equal(r.phase, 'finished')
  assert.equal(r.lapTimes.length, 2)
  assert.equal(r.cars.find(c => c.player).progress, r.track.total * 2)
  assert.equal(order(r).length, 6)
  const elapsed = r.elapsed
  step(r, { gas: true }, 1)
  assert.equal(r.elapsed, elapsed)
})
test('off-track running slows the car and boost cannot go negative', () => {
  const r = createRace(makeTrack(tracks[0]), drivers[0], drivers)
  r.phase = 'racing'; r.energy = 0
  const player = r.cars.find(c => c.player)
  player.lane = 23; player.speed = 100
  step(r, { gas: true, boost: true }, .01)
  assert.ok(player.speed <= 43)
  assert.ok(r.energy >= 0)
})
