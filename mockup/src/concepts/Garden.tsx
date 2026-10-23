import { useRef, useState, type PointerEvent as PE } from 'react'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

/** Horizontal stepping-stone islands */
export function Garden({ moods, name, onSelect, onBack }: ConceptProps) {
  const [index, setIndex] = useState(0)
  const drag = useRef<{ x: number; i: number } | null>(null)
  const mood = moods[index]

  const onDown = (e: PE) => {
    drag.current = { x: e.clientX, i: index }
    ;(e.currentTarget as Element).setPointerCapture?.(e.pointerId)
  }
  const onMove = (e: PE) => {
    if (!drag.current) return
    const dx = e.clientX - drag.current.x
    if (Math.abs(dx) > 50) {
      const next = Math.max(0, Math.min(moods.length - 1, drag.current.i - Math.sign(dx)))
      setIndex(next)
      drag.current = { x: e.clientX, i: next }
    }
  }

  return (
    <section className="screen concept-garden">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Mood garden
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Swipe the path · tap the island ahead</p>
      <div className="concept-stage garden-stage" onPointerDown={onDown} onPointerMove={onMove} onPointerUp={() => (drag.current = null)}>
        <div className="garden-path" />
        <div className="garden-row" style={{ transform: `translateX(calc(50% - ${index * 140 + 70}px))` }}>
          {moods.map((m, i) => {
            const active = i === index
            const c = MOOD_COLORS[m.id]
            return (
              <button
                key={m.id}
                className={`garden-island ${active ? 'is-active' : ''}`}
                style={{ ['--c' as string]: c }}
                onClick={() => (active ? onSelect(m) : setIndex(i))}
              >
                <span className="island-disc" />
                <strong>{shortLabel(m)}</strong>
                <small>{m.short}</small>
              </button>
            )
          })}
        </div>
        <button className="primary-btn garden-cta" onClick={() => onSelect(mood)}>
          Enter {shortLabel(mood)}
        </button>
      </div>
    </section>
  )
}
