import type { ConceptProps } from './shared'
import { MoodOrbit } from '../MoodOrbit'

/** Your original spinning circle — wrapped for the gallery */
export function OrbitConcept({ moods, name, onSelect, onBack }: ConceptProps) {
  return (
    <section className="screen">
      <div className="top-bar">
        <button className="back-btn" onClick={onBack} aria-label="Back">
          ‹
        </button>
        <p className="eyebrow" style={{ margin: 0 }}>
          Circular orbit
        </p>
      </div>
      <h2 className="display display-lg">Assalamoalikum {name}</h2>
      <p className="lede">Your original idea — drag, hold, tap</p>
      <MoodOrbit moods={moods} onSelect={onSelect} />
    </section>
  )
}
