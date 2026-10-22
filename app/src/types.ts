export type Grade = 'sahih' | 'hasan' | 'daif' | 'mawdu'

export type Passage = {
  id: string
  title: string
  kind: 'quran' | 'hadith'
  /** Surah name line, Quran only */
  source?: string
  arabic?: string
  urdu?: string
  english?: string
  meaning?: string
  reflection?: string
  /** Authenticity, hadith only */
  grade?: Grade
  gradedBy?: string
  gradings?: { grader: string; grade: Grade }[]
  disputed?: boolean
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
  Name: { current?: string } | undefined
  Feeling: { name: string }
  Subs: { name: string; moodId: string }
  Threads: { name: string; moodId: string; subId: string }
  Read: { name: string; moodId: string; subId: string; index: number }
}
