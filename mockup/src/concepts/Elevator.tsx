import { useRef, useState, type PointerEvent as PE, type WheelEvent } from 'react'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

/** Vertical feel elevator — flick through mood floors */
export function Elevator({ moods, name, onSelect, onBack }: ConceptProps) {
  const [index, setIndex] = useState(0)
  const drag = useRef<{ y: number; i: number } | null>(null)

  const nudge = (dir: number) => {
    setIndex((i) => Math.max(0, Math.min(moods.length - 1, i + dir)))
  }

  const onDown = (e: PE) => {
    drag.current = { y: e.clientY, i: index }
    ;(e.currentTarget as Element).setPointerCapture?.(e.pointerId)
  }
  const onMove = (e: PE) => {
    if (!drag.current) return
    const dy = e.clientY - drag.current.y
    if (Math.abs(dy) > 42) {
      const next = Math.max(0, Math.min(moods.length - 1, drag.current.i + Math.sign(dy)))
      setIndex(next)
      drag.current = { y: e.clientY, i: next }
    }
  }
  const onWheel = (e: WheelEvent) => {
    if (Math.abs(e.deltaY) < 8) return
    nudge(e.deltaY > 0 ? 1 : -1)
  }

  const mood = moods[index]

  return (
    <section className="screen concept-elevator">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Feel elevator
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Flick up / down · open the floor</p>
      <div className="concept-stage elevator-stage" onPointerDown={onDown} onPointerMove={onMove} onPointerUp={() => (drag.current = null)} onWheel={onWheel}>
        <div className="elev-shaft">
          <div className="elev-cab" style={{ ['--c' as string]: MOOD_COLORS[mood.id] }}>
            <p className="elev-floor">Floor {index + 1}</p>
            <h3>{shortLabel(mood)}</h3>
            <p>{mood.short}</p>
            <button className="primary-btn" onClick={() => onSelect(mood)}>
              Open doors
            </button>
          </div>
          <div className="elev-rail">
            {moods.map((m, i) => (
              <button
                key={m.id}
                className={`elev-dot ${i === index ? 'is-active' : ''}`}
                style={{ background: MOOD_COLORS[m.id] }}
                onClick={() => setIndex(i)}
                aria-label={shortLabel(m)}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
