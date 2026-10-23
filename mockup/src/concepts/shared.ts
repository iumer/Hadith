import type { Mood } from '../data/moods'

export const MOOD_COLORS: Record<string, string> = {
  happy: '#FFE566',
  confident: '#7DFFB3',
  sad: '#7EC8FF',
  overwhelmed: '#C4B5FD',
  anxious: '#FFB347',
  angry: '#FF7A8A',
  'shame-guilt': '#FFB4A2',
  confused: '#80E5FF',
}

export function shortLabel(mood: Mood) {
  return mood.label === 'Shame Guilt' ? 'Shame' : mood.label.split(' ')[0]
}

export type ConceptProps = {
  moods: Mood[]
  name: string
  onSelect: (mood: Mood) => void
  onBack: () => void
}
