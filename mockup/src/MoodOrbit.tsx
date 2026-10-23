import { useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import type { Mood } from './data/moods'

type Props = {
  moods: Mood[]
  onSelect: (mood: Mood) => void
}

const TAU = Math.PI * 2

/** Happy candy palette — vivid but soft */
const MOOD_COLORS: Record<string, { fill: string; glow: string }> = {
  happy: { fill: '#FFE566', glow: '#FFD000' },
  confident: { fill: '#7DFFB3', glow: '#3DFF95' },
  sad: { fill: '#7EC8FF', glow: '#4AAFFF' },
  overwhelmed: { fill: '#C4B5FD', glow: '#A78BFA' },
  anxious: { fill: '#FFB347', glow: '#FF9F1C' },
  angry: { fill: '#FF7A8A', glow: '#FF4D6D' },
  'shame-guilt': { fill: '#FFB4A2', glow: '#FF8FA3' },
  confused: { fill: '#80E5FF', glow: '#22D3EE' },
}

function normAngle(a: number) {
  let x = a % TAU
  if (x < 0) x += TAU
  return x
}

function angleDelta(a: number, b: number) {
  let d = normAngle(a) - normAngle(b)
  if (d > Math.PI) d -= TAU
  if (d < -Math.PI) d += TAU
  return d
}

export function MoodOrbit({ moods, onSelect }: Props) {
  const size = 320
  const cx = size / 2
  const cy = size / 2
  const radius = 118
  const nodeR = 40

  const angleRef = useRef(-Math.PI / 2)
  const velRef = useRef(0.01)
  const draggingRef = useRef(false)
  const lastPtrRef = useRef<{ angle: number; t: number } | null>(null)
  const movedRef = useRef(0)
  const holdBoostRef = useRef(false)
  const pauseUntilRef = useRef(typeof performance !== 'undefined' ? performance.now() + 2800 : 0)
  const rafRef = useRef(0)
  const svgRef = useRef<SVGSVGElement>(null)
  const [, setTick] = useState(0)
  const [activeIndex, setActiveIndex] = useState(0)
  const [holding, setHolding] = useState(false)
  const [burst, setBurst] = useState(0)

  useEffect(() => {
    let alive = true
    let last = performance.now()

    const frame = (now: number) => {
      if (!alive) return
      const dt = Math.min(0.032, (now - last) / 1000)
      last = now
      const paused = now < pauseUntilRef.current

      if (!draggingRef.current) {
        if (paused) {
          velRef.current *= 0.88
        } else {
          const cruise = holdBoostRef.current ? 0.08 : 0.01
          velRef.current += (cruise - velRef.current) * (holdBoostRef.current ? 0.12 : 0.03)
          velRef.current *= holdBoostRef.current ? 0.994 : 0.993
          if (Math.abs(velRef.current) < 0.004 && !holdBoostRef.current) {
            velRef.current = 0.01
          }
        }
      }

      if (!paused || draggingRef.current) {
        angleRef.current = normAngle(angleRef.current + velRef.current * dt * 60)
      }

      let best = 0
      let bestScore = Infinity
      moods.forEach((_, i) => {
        const a = angleRef.current + (i / moods.length) * TAU
        const score = Math.abs(Math.sin(a) - 1)
        if (score < bestScore) {
          bestScore = score
          best = i
        }
      })
      setActiveIndex(best)
      setTick((t) => (t + 1) % 100000)
      rafRef.current = requestAnimationFrame(frame)
    }

    rafRef.current = requestAnimationFrame(frame)
    return () => {
      alive = false
      cancelAnimationFrame(rafRef.current)
    }
  }, [moods])

  const pointerAngle = (clientX: number, clientY: number) => {
    const el = svgRef.current
    if (!el) return 0
    const rect = el.getBoundingClientRect()
    const x = clientX - (rect.left + rect.width / 2)
    const y = clientY - (rect.top + rect.height / 2)
    return Math.atan2(y, x)
  }

  const nearestMoodIndex = (clientX: number, clientY: number) => {
    const pointerA = pointerAngle(clientX, clientY)
    let best = 0
    let bestAbs = Infinity
    moods.forEach((_, i) => {
      const a = angleRef.current + (i / moods.length) * TAU
      const d = Math.abs(angleDelta(pointerA, a))
      if (d < bestAbs) {
        bestAbs = d
        best = i
      }
    })
    return { index: best, distance: bestAbs }
  }

  const onPointerDown = (e: RPointerEvent) => {
    svgRef.current?.setPointerCapture?.(e.pointerId)
    draggingRef.current = true
    holdBoostRef.current = true
    setHolding(true)
    movedRef.current = 0
    lastPtrRef.current = { angle: pointerAngle(e.clientX, e.clientY), t: performance.now() }
  }

  const onPointerMove = (e: RPointerEvent) => {
    if (!draggingRef.current || !lastPtrRef.current) return
    const a = pointerAngle(e.clientX, e.clientY)
    const delta = angleDelta(a, lastPtrRef.current.angle)
    angleRef.current = normAngle(angleRef.current + delta)
    const now = performance.now()
    const dt = Math.max(8, now - lastPtrRef.current.t)
    velRef.current = (delta / dt) * 16
    movedRef.current += Math.abs(delta)
    lastPtrRef.current = { angle: a, t: now }
  }

  const endDrag = (e: RPointerEvent) => {
    const wasTap = movedRef.current <= 0.14
    draggingRef.current = false
    holdBoostRef.current = false
    setHolding(false)
    velRef.current = Math.max(-0.18, Math.min(0.18, velRef.current))
    lastPtrRef.current = null
    pauseUntilRef.current = performance.now() + (wasTap ? 1600 : 900)

    if (wasTap) {
      const { index, distance } = nearestMoodIndex(e.clientX, e.clientY)
      if (distance < 0.55) {
        setBurst((b) => b + 1)
        onSelect(moods[index])
        setActiveIndex(index)
      }
    }
  }

  const t = performance.now()
  const pulse = 0.5 + 0.5 * Math.sin(t / 700)
  const ringSpin = (t / 40) % 360

  return (
    <div className="orbit-wrap" aria-label="Mood circle. Drag to spin, tap a mood.">
      <svg
        ref={svgRef}
        width="100%"
        viewBox={`0 0 ${size} ${size}`}
        style={{ maxWidth: size, touchAction: 'none', cursor: holding ? 'grabbing' : 'grab' }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
      >
        <defs>
          <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255,229,102,0.55)" />
            <stop offset="40%" stopColor="rgba(255,180,162,0.28)" />
            <stop offset="100%" stopColor="rgba(126,200,255,0)" />
          </radialGradient>
          <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF7A8A" />
            <stop offset="40%" stopColor="#FFE566" />
            <stop offset="70%" stopColor="#7DFFB3" />
            <stop offset="100%" stopColor="#7EC8FF" />
          </linearGradient>
        </defs>

        <circle cx={cx} cy={cy} r={radius + 36} fill="url(#coreGlow)" />

        {/* Outer rainbow dash ring — slow anime spin */}
        <g transform={`rotate(${ringSpin * 0.15} ${cx} ${cy})`}>
          <circle
            cx={cx}
            cy={cy}
            r={radius + 8}
            fill="none"
            stroke="url(#ringGrad)"
            strokeWidth="3"
            strokeDasharray="10 14"
            opacity={0.55 + pulse * 0.25}
          />
        </g>

        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={`rgba(255,255,255,${0.35 + pulse * 0.25})`}
          strokeWidth="2"
        />

        {/* Orbit sparkles */}
        {Array.from({ length: 10 }).map((_, i) => {
          const a = angleRef.current * 1.3 + (i / 10) * TAU
          const rr = radius - 28 + (i % 3) * 10
          return (
            <circle
              key={i}
              cx={cx + Math.cos(a) * rr}
              cy={cy + Math.sin(a) * rr}
              r={1.6 + (i % 3)}
              fill="#fff"
              opacity={0.35 + 0.45 * ((Math.sin(t / 300 + i) + 1) / 2)}
            />
          )
        })}

        {/* Center seal */}
        <circle
          cx={cx}
          cy={cy}
          r={38}
          fill="#fff"
          stroke="url(#ringGrad)"
          strokeWidth="3"
          filter="url(#softGlow)"
        />
        <text
          x={cx}
          y={cy - 2}
          textAnchor="middle"
          fill="#FF6B8A"
          fontFamily="Fraunces, Georgia, serif"
          fontSize="15"
          fontWeight={700}
        >
          feel
        </text>
        <text
          x={cx}
          y={cy + 14}
          textAnchor="middle"
          fill="rgba(42,33,64,0.55)"
          fontFamily="Nunito, sans-serif"
          fontSize="8"
          fontWeight={800}
          letterSpacing="1"
        >
          {holding ? 'WHOOSH!' : 'TAP · SPIN'}
        </text>

        {/* Selection burst rings */}
        {burst > 0 && (
          <circle
            key={burst}
            cx={cx}
            cy={cy}
            r={20}
            fill="none"
            stroke="#FFE566"
            strokeWidth="3"
            opacity="0.8"
          >
            <animate attributeName="r" from="20" to="140" dur="0.55s" fill="freeze" />
            <animate attributeName="opacity" from="0.8" to="0" dur="0.55s" fill="freeze" />
          </circle>
        )}

        {moods.map((mood, i) => {
          const a = angleRef.current + (i / moods.length) * TAU
          const x = cx + Math.cos(a) * radius
          const y = cy + Math.sin(a) * radius
          const depth = (Math.sin(a) + 1) / 2
          const bob = Math.sin(t / 400 + i) * 2.2
          const scale = 0.86 + depth * 0.28
          const active = i === activeIndex
          const colors = MOOD_COLORS[mood.id] ?? { fill: '#FFB4A2', glow: '#FF8FA3' }
          const r = nodeR * scale
          const label = mood.label === 'Shame Guilt' ? 'Shame' : mood.label.split(' ')[0]

          return (
            <g key={mood.id} transform={`translate(${x} ${y + bob})`} filter={active ? 'url(#softGlow)' : undefined}>
              <circle r={r + 16} fill={colors.glow} opacity={active ? 0.28 : 0.1} />
              <circle r={r + 14} fill="transparent" />
              <circle
                r={r}
                fill={colors.fill}
                stroke={active ? '#fff' : 'rgba(255,255,255,0.65)'}
                strokeWidth={active ? 3 : 2}
              />
              <text
                y={-1}
                textAnchor="middle"
                fill="#2A2140"
                fontFamily="Fraunces, Georgia, serif"
                fontSize={active ? 14 : 12.5}
                fontWeight={700}
              >
                {label}
              </text>
              <text
                y={13}
                textAnchor="middle"
                fill="rgba(42,33,64,0.62)"
                fontFamily="Nunito, sans-serif"
                fontSize="7.5"
                fontWeight={800}
                letterSpacing="0.4"
              >
                {mood.short}
              </text>
            </g>
          )
        })}
      </svg>
      <p className="orbit-hint">Drag to spin · hold for whoosh · tap a mood</p>
    </div>
  )
}
