import { sample } from './engine'

export function drawCar(ctx, x, y, angle, colour, number, player = false, size = 1) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.scale(size, size)
  if (player) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(0, 0, 17, 11, 0, 0, Math.PI * 2); ctx.stroke() }
  ctx.shadowColor = '#0009'; ctx.shadowBlur = 2; ctx.shadowOffsetY = 1
  for (const x of [-9, 6]) for (const y of [-8, 4]) {
    ctx.fillStyle = '#101219'; ctx.beginPath(); ctx.roundRect(x, y, x < 0 ? 7 : 6, 4, 1); ctx.fill()
    ctx.strokeStyle = '#68717a'; ctx.lineWidth = .35; ctx.beginPath(); ctx.moveTo(x + 1, y + .7); ctx.lineTo(x + 5, y + .7); ctx.stroke()
  }
  ctx.shadowBlur = 0; ctx.shadowOffsetY = 0
  ctx.strokeStyle = '#77818e'; ctx.lineWidth = .65
  for (const sign of [-1, 1]) { ctx.beginPath(); ctx.moveTo(-4, sign * 2); ctx.lineTo(-7, sign * 6); ctx.moveTo(3, sign * 1.5); ctx.lineTo(8, sign * 6); ctx.stroke() }
  ctx.fillStyle = '#131821'; ctx.fillRect(-12, -7, 3, 14); ctx.fillRect(11, -8, 4, 16)
  ctx.fillStyle = colour; ctx.fillRect(-13, -7, 1.5, 14); ctx.fillRect(13, -8, 1.5, 16)
  ctx.strokeStyle = '#b9c2cc'; ctx.lineWidth = .35
  for (const x of [-11, 12]) { ctx.beginPath(); ctx.moveTo(x, -6.5); ctx.lineTo(x, 6.5); ctx.stroke() }
  ctx.beginPath(); ctx.moveTo(-11, -3); ctx.lineTo(-5, -5); ctx.lineTo(3, -4); ctx.lineTo(12, -1.3); ctx.lineTo(12, 1.3); ctx.lineTo(3, 4); ctx.lineTo(-5, 5); ctx.lineTo(-11, 3); ctx.closePath(); ctx.fill()
  ctx.fillStyle = '#0d1420'; ctx.fillRect(-8, -4.6, 8, 1.2); ctx.fillRect(-8, 3.4, 8, 1.2)
  ctx.fillStyle = '#ffffff65'; ctx.fillRect(-9, -.4, 5, .8); ctx.fillRect(3, -.4, 8, .8)
  ctx.fillStyle = '#11151d'; ctx.beginPath(); ctx.ellipse(-3, 0, 3, 2, 0, 0, Math.PI * 2); ctx.fill()
  ctx.strokeStyle = '#d8dce3'; ctx.lineWidth = .65; ctx.beginPath(); ctx.ellipse(-2, 0, 2.7, 2.1, 0, -Math.PI / 2, Math.PI / 2); ctx.stroke()
  ctx.fillStyle = '#ffe98a'; ctx.beginPath(); ctx.arc(-3, 0, 1.5, 0, Math.PI * 2); ctx.fill()
  ctx.fillStyle = '#fff'; ctx.font = 'bold 4px sans-serif'; ctx.textAlign = 'center'; ctx.fillText(number, 6, 1.5)
  ctx.restore()
}
export function background(ctx, track) {
  ctx.fillStyle = track.location === 'Sakhir' ? '#635943' : '#203e35'; ctx.fillRect(0, 0, 1000, 600)
  // Deterministic scenery stays stable between frames and restarts.
  for (let i = 0; i < 170; i++) {
    ctx.fillStyle = i % 2 ? '#ffffff05' : '#0000000c'; ctx.beginPath(); ctx.arc((i * 137) % 1000, (i * 97) % 600, 12 + i % 15, 0, 7); ctx.fill()
  }
  function path() { ctx.beginPath(); track.points.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.closePath() }
  ctx.lineJoin = 'round'; ctx.lineCap = 'round'; path(); ctx.strokeStyle = '#84918a'; ctx.lineWidth = 41; ctx.stroke()
  path(); ctx.strokeStyle = '#f0eae1'; ctx.lineWidth = 34; ctx.stroke()
  ctx.setLineDash([8, 8]); path(); ctx.strokeStyle = '#db3444'; ctx.stroke(); ctx.setLineDash([])
  path(); ctx.strokeStyle = '#30353e'; ctx.lineWidth = 27; ctx.stroke()
  path(); ctx.strokeStyle = '#ffffff12'; ctx.lineWidth = 1; ctx.setLineDash([6, 14]); ctx.stroke(); ctx.setLineDash([])
  const start = sample(track, 0)
  ctx.save(); ctx.translate(start.x, start.y); ctx.rotate(start.angle)
  for (let row = 0; row < 2; row++) for (let col = 0; col < 8; col++) { ctx.fillStyle = (row + col) % 2 ? '#111' : '#fff'; ctx.fillRect(row * 3, -12 + col * 3, 3, 3) }
  ctx.fillStyle = '#b3bcc6'; ctx.fillRect(-48, 27, 95, 9); ctx.fillStyle = '#64717d'; ctx.fillRect(-48, 36, 95, 5)
  ctx.restore()
  ctx.fillStyle = '#ffffff65'; ctx.font = '600 11px sans-serif'; ctx.textAlign = 'left'; ctx.fillText('START / FINISH', start.x + 25, start.y - 24)
  ctx.fillStyle = '#ffffff70'; ctx.font = 'bold 15px sans-serif'; ctx.fillText(track.location.toUpperCase(), 30, 35)
  ctx.font = '11px sans-serif'; ctx.fillText('2 LAPS  /  6 CARS', 30, 53)
}
export function render(ctx, race, scenery) {
  ctx.clearRect(0, 0, 1000, 600); ctx.drawImage(scenery, 0, 0, 1000, 600)
  for (const car of [...race.cars].sort((a, b) => Number(a.player) - Number(b.player))) {
    const p = sample(race.track, car.progress, car.lane)
    drawCar(ctx, p.x, p.y, p.angle, car.colour, car.number, car.player)
    if (car.player) { ctx.fillStyle = '#fff'; ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'center'; ctx.fillText('YOU', p.x, p.y - 20) }
  }
}
