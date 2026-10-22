import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { ConceptProps } from './shared'
import { MOOD_COLORS, shortLabel } from './shared'

/** Center orb washes with mood auras as you swipe */
export function Aura({ moods, name, onSelect, onBack }: ConceptProps) {
  const [index, setIndex] = useState(0)
  const mood = moods[index]
  const c = MOOD_COLORS[mood.id]

  return (
    <section className="screen concept-aura">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Aura rings
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Swipe auras · tap the heart orb</p>
      <div className="concept-stage aura-stage">
        <AnimatePresence mode="wait">
          <motion.div
            key={mood.id}
            className="aura-wash"
            style={{ background: `radial-gradient(circle at 50% 45%, ${c}, transparent 65%)` }}
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1 }}
            transition={{ duration: 0.45 }}
          />
        </AnimatePresence>

        <motion.button
          className="aura-orb"
          style={{ ['--c' as string]: c }}
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
          onClick={() => onSelect(mood)}
        >
          <strong>{shortLabel(mood)}</strong>
          <small>{mood.short}</small>
        </motion.button>

        <div className="aura-strip">
          {moods.map((m, i) => (
            <button
              key={m.id}
              className={`aura-chip ${i === index ? 'is-active' : ''}`}
              style={{ background: MOOD_COLORS[m.id] }}
              onClick={() => setIndex(i)}
            >
              {shortLabel(m)}
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}
