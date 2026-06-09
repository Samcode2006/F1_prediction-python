/**
 * circuitImages.js
 *
 * Maps race/event names (as they appear in FastF1 cache folder names)
 * to their Wikipedia circuit article titles.
 *
 * The Wikipedia REST API is used to fetch circuit images:
 *   GET https://en.wikipedia.org/api/rest_v1/page/summary/{articleTitle}
 * Returns: { thumbnail: { source }, originalimage: { source }, extract, ... }
 *
 * No API key required. CORS-enabled for browser use.
 */

export const CIRCUIT_WIKI_TITLES = {
  // ── 2024–2026 seasons (all cached circuits) ──────────────────────
  'Australian Grand Prix':      'Albert_Park_Circuit',
  'Bahrain Grand Prix':         'Bahrain_International_Circuit',
  'Chinese Grand Prix':         'Shanghai_International_Circuit',
  'Japanese Grand Prix':        'Suzuka_Circuit',
  'Saudi Arabian Grand Prix':   'Jeddah_Corniche_Circuit',
  'Miami Grand Prix':           'Miami_International_Autodrome',
  'Emilia Romagna Grand Prix':  'Autodromo_Enzo_e_Dino_Ferrari',
  'Monaco Grand Prix':          'Circuit_de_Monaco',

  // ── Rest of the full 2025/2026 calendar ─────────────────────────
  'Canadian Grand Prix':        'Circuit_Gilles_Villeneuve',
  'Spanish Grand Prix':         'Circuit_de_Barcelona-Catalunya',
  'Austrian Grand Prix':        'Red_Bull_Ring',
  'British Grand Prix':         'Silverstone_Circuit',
  'Hungarian Grand Prix':       'Hungaroring',
  'Belgian Grand Prix':         'Circuit_de_Spa-Francorchamps',
  'Dutch Grand Prix':           'Circuit_Zandvoort',
  'Italian Grand Prix':         'Autodromo_Nazionale_Monza',
  'Azerbaijan Grand Prix':      'Baku_City_Circuit',
  'Singapore Grand Prix':       'Marina_Bay_Street_Circuit',
  'United States Grand Prix':   'Circuit_of_the_Americas',
  'Mexico City Grand Prix':     'Autodromo_Hermanos_Rodriguez',
  'São Paulo Grand Prix':       'Autodromo_Jose_Carlos_Pace',
  'Las Vegas Grand Prix':       'Las_Vegas_Street_Circuit',
  'Qatar Grand Prix':           'Losail_International_Circuit',
  'Abu Dhabi Grand Prix':       'Yas_Marina_Circuit',
}

/**
 * Fetches the circuit image and summary for a given track name.
 * Falls back to progressively shorter partial names if not found.
 *
 * @param {string} trackName - e.g. "Australian Grand Prix"
 * @returns {Promise<{ imageUrl: string|null, thumbUrl: string|null, extract: string|null }>}
 */
export async function fetchCircuitImage(trackName) {
  // Try exact match first, then try stripping "Grand Prix" suffix
  const candidates = [
    CIRCUIT_WIKI_TITLES[trackName],
    // Fuzzy: try to find a partial key match (handles slight name differences)
    Object.entries(CIRCUIT_WIKI_TITLES).find(
      ([k]) => trackName.toLowerCase().includes(k.split(' ')[0].toLowerCase())
    )?.[1],
  ].filter(Boolean)

  for (const wikiTitle of candidates) {
    try {
      const res = await fetch(
        `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(wikiTitle)}`,
        { headers: { Accept: 'application/json' } }
      )
      if (!res.ok) continue
      const data = await res.json()
      return {
        imageUrl:  data.originalimage?.source ?? null,
        thumbUrl:  data.thumbnail?.source      ?? null,
        extract:   data.extract                ?? null,
        wikiUrl:   data.content_urls?.desktop?.page ?? null,
        title:     data.title                  ?? wikiTitle.replace(/_/g, ' '),
      }
    } catch {
      // network error — try next candidate
    }
  }

  return { imageUrl: null, thumbUrl: null, extract: null, wikiUrl: null, title: trackName }
}
