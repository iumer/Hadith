import { useRef, useState, type PointerEvent as PE } from 'react'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

/** Moods as stars in a draggable night sky */
export function Constellation({ moods, name, onSelect, onBack }: ConceptProps) {
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const drag = useRef<{ x: number; y: number; ox: number; oy: number } | null>(null)
  const moved = useRef(false)

  const positions = moods.map((_, i) => {
    const a = (i / moods.length) * Math.PI * 2 - Math.PI / 2
    const r = 95 + (i % 3) * 18
    return { x: 160 + Math.cos(a) * r, y: 170 + Math.sin(a) * r * 0.85 }
  })

  const onDown = (e: PE) => {
    moved.current = false
    drag.current = { x: e.clientX, y: e.clientY, ox: offset.x, oy: offset.y }
    ;(e.currentTarget as Element).setPointerCapture?.(e.pointerId)
  }
  const onMove = (e: PE) => {
    if (!drag.current) return
    const dx = e.clientX - drag.current.x
    const dy = e.clientY - drag.current.y
    if (Math.hypot(dx, dy) > 6) moved.current = true
    setOffset({ x: drag.current.ox + dx, y: drag.current.oy + dy })
  }
  const onUp = () => {
    drag.current = null
  }

  return (
    <section className="screen concept-sky">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Constellation
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Drag the sky · tap a star</p>
      <div
        className="concept-stage sky-stage"
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
      >
        <div className="sky-drift" style={{ transform: `translate(${offset.x}px, ${offset.y}px)` }}>
          {Array.from({ length: 40 }).map((_, i) => (
            <span
              key={i}
              className="sky-dust"
              style={{
                left: `${(i * 47) % 100}%`,
                top: `${(i * 31) % 100}%`,
                animationDelay: `${(i % 7) * 0.3}s`,
              }}
            />
          ))}
          <svg className="sky-lines" viewBox="0 0 320 340">
            {positions.map((p, i) => {
              const n = positions[(i + 1) % positions.length]
              return (
                <line
                  key={i}
                  x1={p.x}
                  y1={p.y}
                  x2={n.x}
                  y2={n.y}
                  stroke="rgba(255,255,255,0.25)"
                  strokeWidth="1"
                />
              )
            })}
            {moods.map((mood, i) => {
              const p = positions[i]
              const c = MOOD_COLORS[mood.id]
              return (
                <g
                  key={mood.id}
                  transform={`translate(${p.x} ${p.y})`}
                  style={{ cursor: 'pointer' }}
                  onClick={(e) => {
                    e.stopPropagation()
                    if (moved.current) return
                    onSelect(mood)
                  }}
                >
                  <circle r="22" fill={c} opacity="0.25" className="star-halo" />
                  <circle r="10" fill={c} stroke="#fff" strokeWidth="2" />
                  <text y="28" textAnchor="middle" fill="#fff" fontSize="11" fontFamily="Nunito, sans-serif" fontWeight="800">
                    {shortLabel(mood)}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>
      </div>
    </section>
  )
}
