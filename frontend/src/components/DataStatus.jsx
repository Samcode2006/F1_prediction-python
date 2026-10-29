export default function DataStatus({ data }) {
  const meta = data.metadata || {}
  const date = meta.targetDate && new Date(`${meta.targetDate}T12:00:00`).toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' })
  return <section className="card" style={{ padding: '22px 26px', marginBottom: 28 }} aria-label="Upcoming race">
    <strong>{meta.targetRace ? `Next: ${meta.targetRace} · ${date}` : 'Upcoming race to be announced'}</strong>
  </section>
}
