import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useMemo, useState } from 'react'
import { MOODS, type Mood, type RefItem, type SubMood } from './data/moods'
import { MOOD_COLORS, shortLabel } from './concepts/shared'

type Screen =
  | { id: 'name' }
  | { id: 'feeling'; name: string }
  | { id: 'subs'; name: string; mood: Mood }
  | { id: 'list'; name: string; mood: Mood; sub: SubMood }
  | { id: 'read'; name: string; mood: Mood; sub: SubMood; index: number }

const page = {
  initial: { opacity: 0, y: 22, scale: 0.97 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -14, scale: 1.01 },
  transition: { duration: 0.42, ease: [0.22, 1, 0.36, 1] as const },
}

function Back({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      className="back-btn"
      onClick={onClick}
      aria-label="Go back"
      whileTap={{ scale: 0.9 }}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path
          d="M15 6L9 12L15 18"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </motion.button>
  )
}

function MoodFan({
  moods,
  focus,
  setFocus,
  onOpen,
}: {
  moods: Mood[]
  focus: number
  setFocus: (i: number) => void
  onOpen: (mood: Mood) => void
}) {
  return (
    <div className="card-stage calm-fan">
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
                x: active ? 0 : spread * 26,
                y: active ? -40 : Math.abs(spread) * 7,
                rotate: active ? 0 : spread * 8,
                scale: active ? 1.14 : 0.9,
                zIndex: active ? 20 : 10 - Math.abs(spread),
              }}
              transition={{ type: 'spring', stiffness: 300, damping: 22 }}
              onClick={() => (active ? onOpen(mood) : setFocus(i))}
            >
              <span className="fan-sheen" />
              <span className="fan-count">{mood.subs.length}</span>
              <strong>{shortLabel(mood)}</strong>
              <small>{mood.short}</small>
            </motion.button>
          )
        })}
      </div>
      <motion.button
        className="primary-btn fan-enter"
        onClick={() => onOpen(moods[focus])}
        whileTap={{ scale: 0.97 }}
      >
        Open {shortLabel(moods[focus])}
      </motion.button>
    </div>
  )
}

function kindOf(title: string): 'quran' | 'hadith' {
  return title.toLowerCase().includes('quran') ? 'quran' : 'hadith'
}

export default function App() {
  const reduce = useReducedMotion()
  const [screen, setScreen] = useState<Screen>({ id: 'feeling', name: 'Asif' })
  const [draftName, setDraftName] = useState('Asif')
  const [focus, setFocus] = useState(2) // Sad toward center for demo

  const motionProps = useMemo(
    () =>
      reduce
        ? { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 0.2 } }
        : page,
    [reduce],
  )

  // Allow starting from name if they reset
  const goFeeling = (name: string) => setScreen({ id: 'feeling', name })

  return (
    <div className="stage stage-calm">
      <div className="stage-label">
        <h1>Card flow preview</h1>
        <p>Main moods → subcategories → neat Hadith & Quran reading.</p>
      </div>

      <div className="phone-shell phone-calm">
        <div className="phone-notch" />
        <div className="phone-screen phone-screen-calm">
          <div className="ambient ambient-calm" aria-hidden>
            <div className="soft-glow soft-glow-a" />
            <div className="soft-glow soft-glow-b" />
          </div>

          <AnimatePresence mode="wait">
            {screen.id === 'name' && (
              <motion.section key="name" className="screen" {...motionProps}>
                <p className="eyebrow">Welcome</p>
                <h2 className="display display-xl calm-title">What should we call you?</h2>
                <p className="lede">A quiet space for the heart.</p>
                <form
                  className="name-form"
                  onSubmit={(e) => {
                    e.preventDefault()
                    if (!draftName.trim()) return
                    goFeeling(draftName.trim())
                  }}
                >
                  <label htmlFor="name">Your name</label>
                  <input
                    id="name"
                    className="name-input"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    autoFocus
                  />
                  <button className="primary-btn" type="submit">
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
                <MoodFan
                  moods={MOODS}
                  focus={focus}
                  setFocus={setFocus}
                  onOpen={(mood) => setScreen({ id: 'subs', name: screen.name, mood })}
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
                <p className="lede">Choose what fits most closely.</p>
                <div className="sub-grid neat-subs">
                  {screen.mood.subs.map((sub, i) => (
                    <motion.button
                      key={sub.id}
                      className="sub-row"
                      initial={reduce ? false : { opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.05 * i, type: 'spring', stiffness: 280, damping: 20 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() =>
                        setScreen({ id: 'list', name: screen.name, mood: screen.mood, sub })
                      }
                    >
                      <span
                        className="sub-dot"
                        style={{ background: MOOD_COLORS[screen.mood.id] }}
                      />
                      <span className="sub-copy">
                        <strong>{sub.label}</strong>
                        <small>{sub.items.length} passages from Quran & Hadith</small>
                      </span>
                      <span className="sub-chevron">›</span>
                    </motion.button>
                  ))}
                </div>
              </motion.section>
            )}

            {screen.id === 'list' && (
              <motion.section key="list" className="screen" {...motionProps}>
                <div className="top-bar">
                  <Back
                    onClick={() =>
                      setScreen({ id: 'subs', name: screen.name, mood: screen.mood })
                    }
                  />
                  <p className="eyebrow" style={{ margin: 0 }}>
                    {screen.sub.label}
                  </p>
                </div>
                <h2 className="display display-lg">{screen.sub.label}</h2>
                <p className="lede">
                  {screen.sub.items.length} passages · tap any to read
                </p>
                <div className="passage-list">
                  {screen.sub.items.map((item, i) => {
                    const kind = kindOf(item.title)
                    return (
                      <motion.button
                        key={item.id}
                        className="passage-row"
                        initial={reduce ? false : { opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.04 * i, duration: 0.35 }}
                        whileTap={{ scale: 0.985 }}
                        onClick={() =>
                          setScreen({
                            id: 'read',
                            name: screen.name,
                            mood: screen.mood,
                            sub: screen.sub,
                            index: i,
                          })
                        }
                      >
                        <span className={`passage-badge ${kind}`}>
                          {kind === 'quran' ? 'Quran' : 'Hadith'}
                        </span>
                        <h3>{item.title}</h3>
                        {item.preview ? <p>{item.preview}</p> : null}
                      </motion.button>
                    )
                  })}
                </div>
              </motion.section>
            )}

            {screen.id === 'read' && (
              <ReadScreen
                key="read"
                motionProps={motionProps}
                name={screen.name}
                mood={screen.mood}
                sub={screen.sub}
                index={screen.index}
                onBack={() =>
                  setScreen({
                    id: 'list',
                    name: screen.name,
                    mood: screen.mood,
                    sub: screen.sub,
                  })
                }
                onIndex={(index) => setScreen({ ...screen, index })}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

function ReadScreen({
  motionProps,
  sub,
  index,
  onBack,
  onIndex,
}: {
  motionProps: object
  name: string
  mood: Mood
  sub: SubMood
  index: number
  onBack: () => void
  onIndex: (i: number) => void
}) {
  const item: RefItem = sub.items[index]
  const kind = kindOf(item.title)
  const total = sub.items.length

  return (
    <motion.section className="screen read-screen" {...motionProps}>
      <div className="top-bar">
        <Back onClick={onBack} />
        <p className="eyebrow" style={{ margin: 0 }}>
          {index + 1} of {total}
        </p>
      </div>

      <div className="read-progress">
        {sub.items.map((_, i) => (
          <button
            key={i}
            className={`read-pip ${i === index ? 'is-on' : ''}`}
            onClick={() => onIndex(i)}
            aria-label={`Passage ${i + 1}`}
          />
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={item.id}
          className="read-card"
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -24 }}
          transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
        >
          <span className={`passage-badge ${kind}`}>{kind === 'quran' ? 'Quran' : 'Hadith'}</span>
          <h2 className="read-title">{item.title}</h2>
          {item.arabic ? <p className="read-arabic">{item.arabic}</p> : null}
          {item.english ? <p className="read-english">{item.english}</p> : null}
          {item.meaning ? (
            <div className="read-block">
              <p className="read-label">Meaning</p>
              <p className="read-body">{item.meaning}</p>
            </div>
          ) : null}
          {item.reflection ? (
            <div className="read-block">
              <p className="read-label">Reflection</p>
              <p className="read-body">{item.reflection}</p>
            </div>
          ) : null}
        </motion.div>
      </AnimatePresence>

      <div className="read-nav">
        <button
          className="ghost-btn"
          disabled={index <= 0}
          onClick={() => onIndex(index - 1)}
        >
          Previous
        </button>
        <button
          className="primary-btn read-next"
          disabled={index >= total - 1}
          onClick={() => onIndex(index + 1)}
        >
          Next passage
        </button>
      </div>
    </motion.section>
  )
}
