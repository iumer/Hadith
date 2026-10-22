import { motion } from 'framer-motion'
import type { ConceptId } from './index'

const CARDS: { id: ConceptId; title: string; blurb: string; swatch: string[] }[] = [
  {
    id: 'orbit',
    title: '1 · Circular orbit',
    blurb: 'Your idea — spinning mood nodes you drag & tap.',
    swatch: ['#FF7A8A', '#FFE566', '#7EC8FF'],
  },
  {
    id: 'constellation',
    title: '2 · Constellation',
    blurb: 'Stars in a night sky — drag the sky, tap a star.',
    swatch: ['#1a1430', '#7EC8FF', '#FFE566'],
  },
  {
    id: 'garden',
    title: '3 · Mood garden',
    blurb: 'Floating islands on a path — swipe, then enter.',
    swatch: ['#7DFFB3', '#FFE566', '#FFB4A2'],
  },
  {
    id: 'prism',
    title: '4 · Emotion prism',
    blurb: 'A crystal fans color beams — rotate into a mood.',
    swatch: ['#C4B5FD', '#FF7A8A', '#7EC8FF'],
  },
  {
    id: 'cards',
    title: '5 · Card fan',
    blurb: 'A fanned deck — pull a card toward you.',
    swatch: ['#FFB347', '#FF7A8A', '#7DFFB3'],
  },
  {
    id: 'pond',
    title: '6 · Ripple pond',
    blurb: 'Lanterns on water — tap ripples, pick a light.',
    swatch: ['#7EC8FF', '#80E5FF', '#FFE566'],
  },
  {
    id: 'elevator',
    title: '7 · Feel elevator',
    blurb: 'Mood floors in a shaft — flick up and down.',
    swatch: ['#C4B5FD', '#FFB4A2', '#FFE566'],
  },
  {
    id: 'aura',
    title: '8 · Aura rings',
    blurb: 'A heart orb washes color as you change auras.',
    swatch: ['#FF7A8A', '#FFB4A2', '#C4B5FD'],
  },
]

type Props = {
  name: string
  onPick: (id: ConceptId) => void
  onEditName: () => void
}

export function Gallery({ name, onPick, onEditName }: Props) {
  return (
    <section className="screen gallery-screen">
      <p className="eyebrow">Compare concepts</p>
      <h2 className="display display-lg">How should moods feel?</h2>
      <p className="lede">
        Hi {name} — open each idea below. Pick a favorite after you try them.
      </p>
      <button className="name-chip" onClick={onEditName}>
        Change name
      </button>
      <div className="gallery-grid">
        {CARDS.map((card, i) => (
          <motion.button
            key={card.id}
            className="gallery-card"
            initial={{ opacity: 0, y: 18, scale: 0.94 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.04 * i, type: 'spring', stiffness: 260, damping: 18 }}
            whileHover={{ y: -3, scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onPick(card.id)}
          >
            <div className="gallery-swatch">
              {card.swatch.map((c) => (
                <span key={c} style={{ background: c }} />
              ))}
            </div>
            <strong>{card.title}</strong>
            <p>{card.blurb}</p>
          </motion.button>
        ))}
      </div>
    </section>
  )
}
