import { useState } from 'react'
import { motion } from 'framer-motion'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

/** Fanned deck — tap to pull a card forward */
export function CardFan({ moods, name, onSelect, onBack }: ConceptProps) {
  const [focus, setFocus] = useState(Math.floor(moods.length / 2))

  return (
    <section className="screen concept-cards">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Card fan
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Tap a card to pull it · tap again to enter</p>
      <div className="concept-stage card-stage">
        <div className="card-fan">
          {moods.map((mood, i) => {
            const mid = (moods.length - 1) / 2
            const spread = i - mid
            const active = i === focus
            return (
              <motion.button
                key={mood.id}
                className={`fan-card ${active ? 'is-active' : ''}`}
                style={{ ['--c' as string]: MOOD_COLORS[mood.id] }}
                animate={{
                  x: active ? 0 : spread * 28,
                  y: active ? -36 : Math.abs(spread) * 8,
                  rotate: active ? 0 : spread * 9,
                  scale: active ? 1.12 : 0.92,
                  zIndex: active ? 20 : 10 - Math.abs(spread),
                }}
                transition={{ type: 'spring', stiffness: 280, damping: 20 }}
                onClick={() => (active ? onSelect(mood) : setFocus(i))}
              >
                <span className="fan-sheen" />
                <strong>{shortLabel(mood)}</strong>
                <small>{mood.short}</small>
              </motion.button>
            )
          })}
        </div>
        <p className="orbit-hint">Pull {shortLabel(moods[focus])} toward you</p>
      </div>
    </section>
  )
}
