import { useEffect, useRef, useState, type PointerEvent as PE } from 'react'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

/** Crystal center with rotatable color beams */
export function Prism({ moods, name, onSelect, onBack }: ConceptProps) {
  const angleRef = useRef(0)
  const vel = useRef(0.012)
  const dragging = useRef(false)
  const last = useRef<number | null>(null)
  const moved = useRef(0)
  const [, tick] = useState(0)
  const [active, setActive] = useState(0)

  useEffect(() => {
    let id = 0
    let prev = performance.now()
    const loop = (now: number) => {
      const dt = Math.min(0.033, (now - prev) / 1000)
      prev = now
      if (!dragging.current) {
        vel.current += (0.01 - vel.current) * 0.04
        angleRef.current += vel.current * dt * 60
      }
      const slice = (Math.PI * 2) / moods.length
      const idx = ((Math.round((-angleRef.current + Math.PI / 2) / slice) % moods.length) + moods.length) % moods.length
      setActive(idx)
      tick((t) => t + 1)
      id = requestAnimationFrame(loop)
    }
    id = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(id)
  }, [moods.length])

  const ptrAngle = (e: PE, el: Element) => {
    const r = el.getBoundingClientRect()
    return Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2))
  }

  return (
    <section className="screen concept-prism">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Emotion prism
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Drag to rotate the light · tap the beam</p>
      <div className="concept-stage">
        <svg
          viewBox="0 0 320 320"
          className="prism-svg"
          onPointerDown={(e) => {
            dragging.current = true
            moved.current = 0
            last.current = ptrAngle(e, e.currentTarget)
            e.currentTarget.setPointerCapture(e.pointerId)
          }}
          onPointerMove={(e) => {
            if (!dragging.current || last.current == null) return
            const a = ptrAngle(e, e.currentTarget)
            let d = a - last.current
            if (d > Math.PI) d -= Math.PI * 2
            if (d < -Math.PI) d += Math.PI * 2
            angleRef.current += d
            vel.current = d * 8
            moved.current += Math.abs(d)
            last.current = a
          }}
          onPointerUp={() => {
            dragging.current = false
            last.current = null
          }}
        >
          {moods.map((mood, i) => {
            const slice = (Math.PI * 2) / moods.length
            const a0 = angleRef.current + i * slice
            const a1 = a0 + slice
            const x0 = 160 + Math.cos(a0) * 130
            const y0 = 160 + Math.sin(a0) * 130
            const x1 = 160 + Math.cos(a1) * 130
            const y1 = 160 + Math.sin(a1) * 130
            const selected = i === active
            return (
              <path
                key={mood.id}
                d={`M160 160 L${x0} ${y0} A130 130 0 0 1 ${x1} ${y1} Z`}
                fill={MOOD_COLORS[mood.id]}
                opacity={selected ? 0.85 : 0.35}
                stroke="#fff"
                strokeWidth={selected ? 2 : 0.5}
                style={{ cursor: 'pointer', transition: 'opacity 0.2s' }}
                onClick={(e) => {
                  e.stopPropagation()
                  if (moved.current < 0.2) onSelect(mood)
                }}
              />
            )
          })}
          <polygon points="160,128 188,176 132,176" fill="#fff" stroke="#FF6B8A" strokeWidth="3" />
          <text x="160" y="198" textAnchor="middle" fontFamily="Fraunces, serif" fontSize="18" fontWeight="700" fill="#2A2140">
            {shortLabel(moods[active])}
          </text>
        </svg>
        <button className="primary-btn" onClick={() => onSelect(moods[active])}>
          Choose {shortLabel(moods[active])}
        </button>
      </div>
    </section>
  )
}
