import { useState, type PointerEvent as PE } from 'react'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

type Ripple = { id: number; x: number; y: number }

/** Lanterns on a pond — tap water for ripples, tap lantern for mood */
export function RipplePond({ moods, name, onSelect, onBack }: ConceptProps) {
  const [ripples, setRipples] = useState<Ripple[]>([])

  const addRipple = (e: PE<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    const id = Date.now()
    setRipples((prev) => [...prev.slice(-4), { id, x: e.clientX - r.left, y: e.clientY - r.top }])
    window.setTimeout(() => setRipples((prev) => prev.filter((x) => x.id !== id)), 1200)
  }

  const spots = moods.map((_, i) => {
    const col = i % 4
    const row = Math.floor(i / 4)
    return { left: 12 + col * 22 + (row % 2) * 8, top: 18 + row * 34 + (i % 3) * 4 }
  })

  return (
    <section className="screen concept-pond">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Ripple pond
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Tap the water · choose a lantern</p>
      <div className="concept-stage pond-stage" onPointerDown={addRipple}>
        {ripples.map((r) => (
          <span key={r.id} className="pond-ripple" style={{ left: r.x, top: r.y }} />
        ))}
        {moods.map((mood, i) => (
          <button
            key={mood.id}
            className="pond-lantern"
            style={{
              left: `${spots[i].left}%`,
              top: `${spots[i].top}%`,
              ['--c' as string]: MOOD_COLORS[mood.id],
              animationDelay: `${i * 0.25}s`,
            }}
            onClick={(e) => {
              e.stopPropagation()
              onSelect(mood)
            }}
          >
            <span className="lantern-glow" />
            <span className="lantern-body" />
            <strong>{shortLabel(mood)}</strong>
          </button>
        ))}
      </div>
    </section>
  )
}
