export type Passage = {
  id: string
  title: string
  kind: 'quran' | 'hadith'
  arabic?: string
  english?: string
  meaning?: string
  reflection?: string
}

export type SubMood = {
  id: string
  label: string
  items: Passage[]
}

export type Mood = {
  id: string
  label: string
  short: string
  color: string
  subs: SubMood[]
}

export type Catalog = {
  moods: Mood[]
}

export type RootStackParamList = {
  Name: undefined
  Feeling: { name: string }
  Subs: { name: string; moodId: string }
  Threads: { name: string; moodId: string; subId: string }
  Read: { name: string; moodId: string; subId: string; index: number }
}
