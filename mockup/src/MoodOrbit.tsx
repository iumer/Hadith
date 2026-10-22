import { useEffect, useRef, useState, type PointerEvent as RPointerEvent } from 'react'
import type { Mood } from './data/moods'

type Props = {
  moods: Mood[]
  onSelect: (mood: Mood) => void
}

const TAU = Math.PI * 2

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
  const nodeR = 38

  const angleRef = useRef(-Math.PI / 2) // start with first mood near top
  const velRef = useRef(0.008)
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
          velRef.current *= 0.9
        } else {
          const cruise = holdBoostRef.current ? 0.07 : 0.0075
          velRef.current += (cruise - velRef.current) * (holdBoostRef.current ? 0.1 : 0.025)
          velRef.current *= holdBoostRef.current ? 0.995 : 0.994
          if (Math.abs(velRef.current) < 0.003 && !holdBoostRef.current) {
            velRef.current = 0.0075
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

    // Pause spin so the user can aim a second tap if needed
    pauseUntilRef.current = performance.now() + (wasTap ? 1600 : 900)

    if (wasTap) {
      const { index, distance } = nearestMoodIndex(e.clientX, e.clientY)
      // Only select if the tap was aimed near a mood node (not the empty center)
      if (distance < 0.55) {
        onSelect(moods[index])
        setActiveIndex(index)
      }
    }
  }

  const ringPulse = 0.5 + 0.5 * Math.sin(performance.now() / 900)

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
            <stop offset="0%" stopColor="rgba(212,180,131,0.35)" />
            <stop offset="55%" stopColor="rgba(126,168,148,0.12)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0)" />
          </radialGradient>
          <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="3.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <circle cx={cx} cy={cy} r={radius + 28} fill="url(#coreGlow)" />

        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={`rgba(212,180,131,${0.18 + ringPulse * 0.12})`}
          strokeWidth="1.25"
          strokeDasharray="4 10"
        />
        <circle
          cx={cx}
          cy={cy}
          r={radius - 42}
          fill="none"
          stroke="rgba(232,236,228,0.08)"
          strokeWidth="1"
        />

        <circle cx={cx} cy={cy} r={34} fill="rgba(11,18,16,0.85)" stroke="rgba(212,180,131,0.4)" strokeWidth="1" />
        <text
          x={cx}
          y={cy - 4}
          textAnchor="middle"
          fill="#d4b483"
          fontFamily="Cormorant Garamond, Georgia, serif"
          fontSize="13"
          letterSpacing="2"
        >
          FEEL
        </text>
        <text
          x={cx}
          y={cy + 14}
          textAnchor="middle"
          fill="rgba(232,236,228,0.55)"
          fontFamily="Sora, sans-serif"
          fontSize="8"
          letterSpacing="1.5"
        >
          {holding ? 'FASTER' : 'TAP · DRAG'}
        </text>

        {moods.map((mood, i) => {
          const a = angleRef.current + (i / moods.length) * TAU
          const x = cx + Math.cos(a) * radius
          const y = cy + Math.sin(a) * radius
          const depth = (Math.sin(a) + 1) / 2
          const scale = 0.84 + depth * 0.26
          const active = i === activeIndex
          const fill = `hsl(${mood.hue} 42% ${active ? 48 : 38}% / ${0.55 + depth * 0.35})`
          const stroke = active ? 'rgba(232,236,228,0.85)' : 'rgba(232,236,228,0.22)'
          const r = nodeR * scale
          // Slightly shorter labels for ring fit
          const label = mood.label === 'Shame Guilt' ? 'Shame' : mood.label.split(' ')[0]

          return (
            <g key={mood.id} transform={`translate(${x} ${y})`} filter={active ? 'url(#softGlow)' : undefined}>
              {/* Large invisible hit halo — selection still uses nearest-angle logic */}
              <circle r={r + 14} fill="transparent" />
              <circle r={r + 6} fill={`hsl(${mood.hue} 50% 50% / ${active ? 0.18 : 0.06})`} />
              <circle r={r} fill={fill} stroke={stroke} strokeWidth={active ? 1.6 : 1} />
              <text
                y={-2}
                textAnchor="middle"
                fill="#f4f1ea"
                fontFamily="Cormorant Garamond, Georgia, serif"
                fontSize={active ? 13.5 : 12}
                fontWeight={600}
              >
                {label}
              </text>
              <text
                y={12}
                textAnchor="middle"
                fill="rgba(244,241,234,0.65)"
                fontFamily="Sora, sans-serif"
                fontSize="7.5"
                letterSpacing="0.5"
              >
                {mood.short}
              </text>
            </g>
          )
        })}
      </svg>
      <p className="orbit-hint">Drag to spin · hold to speed up · tap a mood (pauses briefly)</p>
    </div>
  )
}
