import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useMemo, useState, type CSSProperties } from 'react'
import { MOODS, type Mood } from './data/moods'
import {
  Aura,
  CardFan,
  Constellation,
  Elevator,
  Gallery,
  Garden,
  OrbitConcept,
  Prism,
  RipplePond,
  type ConceptId,
} from './concepts'

type Screen =
  | { id: 'name' }
  | { id: 'gallery'; name: string }
  | { id: 'concept'; name: string; concept: ConceptId }
  | { id: 'picked'; name: string; concept: ConceptId; mood: Mood }

const page = {
  initial: { opacity: 0, y: 28, scale: 0.96 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -20, scale: 1.02 },
  transition: { duration: 0.45, ease: [0.34, 1.4, 0.64, 1] as const },
}

function Ambient() {
  return (
    <div className="ambient" aria-hidden>
      <div className="blob blob-a" />
      <div className="blob blob-b" />
      <div className="blob blob-c" />
      <div className="blob blob-d" />
      <span className="sparkle" style={{ top: '12%', left: '18%' }} />
      <span className="sparkle" style={{ top: '22%', right: '16%', animationDelay: '0.6s' }} />
      <span className="sparkle" style={{ bottom: '18%', right: '22%', animationDelay: '1.2s' }} />
    </div>
  )
}

function ConceptView({
  concept,
  name,
  onBack,
  onSelect,
}: {
  concept: ConceptId
  name: string
  onBack: () => void
  onSelect: (mood: Mood) => void
}) {
  const props = { moods: MOODS, name, onBack, onSelect }
  switch (concept) {
    case 'orbit':
      return <OrbitConcept {...props} />
    case 'constellation':
      return <Constellation {...props} />
    case 'garden':
      return <Garden {...props} />
    case 'prism':
      return <Prism {...props} />
    case 'cards':
      return <CardFan {...props} />
    case 'pond':
      return <RipplePond {...props} />
    case 'elevator':
      return <Elevator {...props} />
    case 'aura':
      return <Aura {...props} />
  }
}

export default function App() {
  const reduce = useReducedMotion()
  const [screen, setScreen] = useState<Screen>({ id: 'name' })
  const [draftName, setDraftName] = useState('Asif')

  const motionProps = useMemo(
    () =>
      reduce
        ? { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 0.2 } }
        : page,
    [reduce],
  )

  return (
    <div className="stage">
      <div className="stage-label">
        <h1>Mood picker concepts</h1>
        <p>Eight basic mockups — your circle plus seven alternatives. Open each, then tell me which direction to polish.</p>
      </div>

      <div className="phone-shell">
        <div className="phone-notch" />
        <div className="phone-screen">
          <Ambient />
          <AnimatePresence mode="wait">
            {screen.id === 'name' && (
              <motion.section key="name" className="screen" {...motionProps}>
                <p className="eyebrow">Welcome</p>
                <h2 className="display display-xl">What should we call you?</h2>
                <p className="lede">Then we will browse mood-picker concepts together.</p>
                <form
                  className="name-form"
                  onSubmit={(e) => {
                    e.preventDefault()
                    const name = draftName.trim()
                    if (!name) return
                    setScreen({ id: 'gallery', name })
                  }}
                >
                  <label htmlFor="name">Your name</label>
                  <input
                    id="name"
                    className="name-input"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    placeholder="Asif"
                    autoFocus
                  />
                  <motion.button
                    className="primary-btn"
                    type="submit"
                    disabled={!draftName.trim()}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.96 }}
                  >
                    See concepts
                  </motion.button>
                </form>
              </motion.section>
            )}

            {screen.id === 'gallery' && (
              <motion.div key="gallery" className="screen-wrap" {...motionProps}>
                <Gallery
                  name={screen.name}
                  onEditName={() => setScreen({ id: 'name' })}
                  onPick={(concept) => setScreen({ id: 'concept', name: screen.name, concept })}
                />
              </motion.div>
            )}

            {screen.id === 'concept' && (
              <motion.div key={`concept-${screen.concept}`} className="screen-wrap" {...motionProps}>
                <ConceptView
                  concept={screen.concept}
                  name={screen.name}
                  onBack={() => setScreen({ id: 'gallery', name: screen.name })}
                  onSelect={(mood) =>
                    setScreen({ id: 'picked', name: screen.name, concept: screen.concept, mood })
                  }
                />
              </motion.div>
            )}

            {screen.id === 'picked' && (
              <motion.section key="picked" className="screen picked-screen" {...motionProps}>
                <p className="eyebrow">Preview only</p>
                <h2 className="display display-lg">You chose {screen.mood.label}</h2>
                <p className="lede">
                  In the real app this would open subcategories like Sorrow, Grief, and so on. For now we
                  are only comparing how moods are presented.
                </p>
                <div
                  className="picked-blob"
                  style={{ background: `radial-gradient(circle, ${moodColor(screen.mood.id)}, transparent 70%)` } as CSSProperties}
                />
                <div className="picked-actions">
                  <button
                    className="primary-btn"
                    onClick={() =>
                      setScreen({ id: 'concept', name: screen.name, concept: screen.concept })
                    }
                  >
                    Try this concept again
                  </button>
                  <button
                    className="ghost-btn"
                    onClick={() => setScreen({ id: 'gallery', name: screen.name })}
                  >
                    Back to all concepts
                  </button>
                </div>
              </motion.section>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

function moodColor(id: string) {
  const map: Record<string, string> = {
    happy: '#FFE566',
    confident: '#7DFFB3',
    sad: '#7EC8FF',
    overwhelmed: '#C4B5FD',
    anxious: '#FFB347',
    angry: '#FF7A8A',
    'shame-guilt': '#FFB4A2',
    confused: '#80E5FF',
  }
  return map[id] ?? '#FFB4A2'
}
