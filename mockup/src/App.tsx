import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useMemo, useState } from 'react'
import { MOODS, type Mood, type RefItem, type SubMood } from './data/moods'
import { MoodOrbit } from './MoodOrbit'

type Screen =
  | { id: 'name' }
  | { id: 'feeling'; name: string }
  | { id: 'subs'; name: string; mood: Mood }
  | { id: 'list'; name: string; mood: Mood; sub: SubMood }
  | { id: 'detail'; name: string; mood: Mood; sub: SubMood; item: RefItem }

const page = {
  initial: { opacity: 0, y: 36, scale: 0.94, rotate: -1.2 },
  animate: { opacity: 1, y: 0, scale: 1, rotate: 0 },
  exit: { opacity: 0, y: -28, scale: 1.03, rotate: 1.2 },
  transition: { duration: 0.55, ease: [0.34, 1.4, 0.64, 1] as const },
}

function Ambient() {
  return (
    <div className="ambient" aria-hidden>
      <div className="blob blob-a" />
      <div className="blob blob-b" />
      <div className="blob blob-c" />
      <div className="blob blob-d" />
      <span className="sparkle" style={{ top: '12%', left: '18%', animationDelay: '0s' }} />
      <span className="sparkle" style={{ top: '22%', right: '16%', animationDelay: '0.6s' }} />
      <span className="sparkle" style={{ top: '48%', left: '10%', animationDelay: '1.1s' }} />
      <span className="sparkle" style={{ bottom: '18%', right: '22%', animationDelay: '1.7s' }} />
      <span className="sparkle" style={{ bottom: '28%', left: '28%', animationDelay: '0.3s' }} />
    </div>
  )
}

function StageSparks() {
  const spots = [
    { top: '8%', left: '12%' },
    { top: '18%', right: '10%' },
    { top: '40%', left: '6%' },
    { top: '55%', right: '8%' },
    { bottom: '12%', left: '18%' },
    { bottom: '20%', right: '16%' },
  ]
  return (
    <>
      {spots.map((s, i) => (
        <span key={i} className="stage-spark" style={{ ...s, animationDelay: `${i * 0.35}s` }} />
      ))}
    </>
  )
}

function Back({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      className="back-btn"
      onClick={onClick}
      aria-label="Go back"
      whileHover={{ scale: 1.08, rotate: -6 }}
      whileTap={{ scale: 0.9, rotate: 0 }}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path
          d="M15 6L9 12L15 18"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </motion.button>
  )
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
      {!reduce && <StageSparks />}
      <div className="stage-label">
        <motion.h1
          initial={reduce ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.34, 1.4, 0.64, 1] }}
        >
          Interactive mockup
        </motion.h1>
        <p>Bright, bouncy, anime-clean motion — explore the full flow before we build the real app.</p>
      </div>

      <div className="phone-shell">
        <div className="phone-notch" />
        <div className="phone-screen">
          <Ambient />
          <AnimatePresence mode="wait">
            {screen.id === 'name' && (
              <motion.section key="name" className="screen" {...motionProps}>
                <motion.p
                  className="eyebrow"
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15 }}
                >
                  Welcome
                </motion.p>
                <motion.h2
                  className="display display-xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, type: 'spring', stiffness: 220, damping: 16 }}
                >
                  What should we call you?
                </motion.h2>
                <motion.p
                  className="lede"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.35 }}
                >
                  A bright little space for the heart — Quran and Hadith for how you feel right now.
                </motion.p>
                <form
                  className="name-form"
                  onSubmit={(e) => {
                    e.preventDefault()
                    const name = draftName.trim()
                    if (!name) return
                    setScreen({ id: 'feeling', name })
                  }}
                >
                  <label htmlFor="name">Your name</label>
                  <input
                    id="name"
                    className="name-input"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    placeholder="Asif"
                    autoComplete="given-name"
                    autoFocus
                  />
                  <motion.button
                    className="primary-btn"
                    type="submit"
                    disabled={!draftName.trim()}
                    whileHover={{ scale: 1.03, y: -2 }}
                    whileTap={{ scale: 0.96 }}
                  >
                    Continue
                  </motion.button>
                </form>
              </motion.section>
            )}

            {screen.id === 'feeling' && (
              <motion.section key="feeling" className="screen" {...motionProps}>
                <div className="top-bar">
                  <Back onClick={() => setScreen({ id: 'name' })} />
                </div>
                <motion.p className="eyebrow" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  Salaam
                </motion.p>
                <motion.h2
                  className="display display-lg"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: 'spring', stiffness: 240, damping: 14 }}
                >
                  Assalamoalikum {screen.name}
                </motion.h2>
                <motion.p
                  className="lede"
                  animate={{ opacity: [0.7, 1, 0.7] }}
                  transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
                >
                  How are you feeling today?
                </motion.p>
                <MoodOrbit
                  moods={MOODS}
                  onSelect={(mood) => setScreen({ id: 'subs', name: screen.name, mood })}
                />
              </motion.section>
            )}

            {screen.id === 'subs' && (
              <motion.section key="subs" className="screen" {...motionProps}>
                <div className="top-bar">
                  <Back onClick={() => setScreen({ id: 'feeling', name: screen.name })} />
                  <p className="eyebrow" style={{ margin: 0 }}>
                    {screen.mood.label}
                  </p>
                </div>
                <h2 className="display display-lg">{screen.mood.label}</h2>
                <p className="lede">Choose what fits most closely right now.</p>
                <div className="sub-grid">
                  {screen.mood.subs.map((sub, i) => (
                    <motion.button
                      key={sub.id}
                      className="sub-chip"
                      initial={reduce ? false : { opacity: 0, y: 24, scale: 0.9, rotate: -2 }}
                      animate={{ opacity: 1, y: 0, scale: 1, rotate: 0 }}
                      transition={{
                        delay: 0.05 * i,
                        type: 'spring',
                        stiffness: 260,
                        damping: 16,
                      }}
                      whileHover={{ scale: 1.03, y: -3 }}
                      whileTap={{ scale: 0.96 }}
                      onClick={() => setScreen({ id: 'list', name: screen.name, mood: screen.mood, sub })}
                    >
                      <strong>{sub.label}</strong>
                      <span>{sub.items.length} passages</span>
                    </motion.button>
                  ))}
                </div>
              </motion.section>
            )}

            {screen.id === 'list' && (
              <motion.section key="list" className="screen" {...motionProps}>
                <div className="top-bar">
                  <Back
                    onClick={() => setScreen({ id: 'subs', name: screen.name, mood: screen.mood })}
                  />
                  <p className="eyebrow" style={{ margin: 0 }}>
                    {screen.mood.label} · {screen.sub.label}
                  </p>
                </div>
                <h2 className="display display-lg">{screen.sub.label}</h2>
                <p className="lede">Hadith and Quranic verses — tap one to read fully.</p>
                <div className="ref-list">
                  {screen.sub.items.map((item, i) => (
                    <motion.button
                      key={item.id}
                      className="ref-card"
                      initial={reduce ? false : { opacity: 0, x: -20, scale: 0.94 }}
                      animate={{ opacity: 1, x: 0, scale: 1 }}
                      transition={{
                        delay: 0.04 * i,
                        type: 'spring',
                        stiffness: 280,
                        damping: 18,
                      }}
                      whileHover={{ scale: 1.025, y: -3 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() =>
                        setScreen({
                          id: 'detail',
                          name: screen.name,
                          mood: screen.mood,
                          sub: screen.sub,
                          item,
                        })
                      }
                    >
                      <h3>{item.title}</h3>
                      {item.preview ? <p>{item.preview}</p> : null}
                    </motion.button>
                  ))}
                </div>
              </motion.section>
            )}

            {screen.id === 'detail' && (
              <motion.section key="detail" className="screen detail" {...motionProps}>
                <div className="top-bar">
                  <Back
                    onClick={() =>
                      setScreen({
                        id: 'list',
                        name: screen.name,
                        mood: screen.mood,
                        sub: screen.sub,
                      })
                    }
                  />
                  <p className="eyebrow" style={{ margin: 0 }}>
                    Reading
                  </p>
                </div>
                <motion.h2
                  className="display display-lg"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ type: 'spring', stiffness: 220, damping: 16 }}
                >
                  {screen.item.title}
                </motion.h2>
                {screen.item.arabic ? (
                  <motion.p
                    className="arabic"
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1, type: 'spring', stiffness: 200, damping: 16 }}
                  >
                    {screen.item.arabic}
                  </motion.p>
                ) : null}
                {screen.item.english ? (
                  <motion.p
                    className="english"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.18 }}
                  >
                    {screen.item.english}
                  </motion.p>
                ) : null}
                {screen.item.meaning ? (
                  <>
                    <p className="section-label">Meaning</p>
                    <p className="body">{screen.item.meaning}</p>
                  </>
                ) : null}
                {screen.item.reflection ? (
                  <>
                    <p className="section-label">Reflection</p>
                    <p className="body">{screen.item.reflection}</p>
                  </>
                ) : null}
              </motion.section>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
