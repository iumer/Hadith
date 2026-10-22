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
  initial: { opacity: 0, y: 18, filter: 'blur(6px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  exit: { opacity: 0, y: -12, filter: 'blur(4px)' },
  transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] as const },
}

function Back({ onClick }: { onClick: () => void }) {
  return (
    <button className="back-btn" onClick={onClick} aria-label="Go back">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path
          d="M15 6L9 12L15 18"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
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
      <div className="stage-label">
        <h1>Interactive mockup</h1>
        <p>
          Walk through the full flow — name, spinning mood circle, subcategories, verse/hadith list, then a
          single reading. Design exploration only; not the final app yet.
        </p>
      </div>

      <div className="phone-shell">
        <div className="phone-notch" />
        <div className="phone-screen">
          <div className="ambient" />
          <AnimatePresence mode="wait">
            {screen.id === 'name' && (
              <motion.section key="name" className="screen" {...motionProps}>
                <p className="eyebrow">Welcome</p>
                <h2 className="display display-xl">What should we call you?</h2>
                <p className="lede">A quiet place for the heart — Quran and Hadith for how you feel right now.</p>
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
                  <button className="primary-btn" type="submit" disabled={!draftName.trim()}>
                    Continue
                  </button>
                </form>
              </motion.section>
            )}

            {screen.id === 'feeling' && (
              <motion.section key="feeling" className="screen" {...motionProps}>
                <div className="top-bar">
                  <Back onClick={() => setScreen({ id: 'name' })} />
                </div>
                <p className="eyebrow">Salaam</p>
                <h2 className="display display-lg">Assalamoalikum {screen.name}</h2>
                <p className="lede">How are you feeling today?</p>
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
                      initial={reduce ? false : { opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.04 * i, duration: 0.4, ease: [0.22, 1, 0.36, 1] as const }}
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
                      initial={reduce ? false : { opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.03 * i, duration: 0.35, ease: [0.22, 1, 0.36, 1] as const }}
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
                <h2 className="display display-lg">{screen.item.title}</h2>
                {screen.item.arabic ? <p className="arabic">{screen.item.arabic}</p> : null}
                {screen.item.english ? <p className="english">{screen.item.english}</p> : null}
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
