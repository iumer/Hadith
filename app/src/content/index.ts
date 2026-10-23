import raw from './catalog.json'
import type { Catalog, Mood, SubMood } from '../types'

export const catalog = raw as Catalog

export function getMood(moodId: string): Mood {
  const mood = catalog.moods.find((m) => m.id === moodId)
  if (!mood) throw new Error(`Unknown mood: ${moodId}`)
  return mood
}

export function getSub(moodId: string, subId: string): { mood: Mood; sub: SubMood } {
  const mood = getMood(moodId)
  const sub = mood.subs.find((s) => s.id === subId)
  if (!sub) throw new Error(`Unknown sub: ${subId}`)
  return { mood, sub }
}

export function shortLabel(mood: Mood) {
  return mood.label.split(' ')[0]
}
