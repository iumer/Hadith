import { Platform } from 'react-native'
import AsyncStorage from '@react-native-async-storage/async-storage'
import * as Device from 'expo-device'
import * as Network from 'expo-network'
import appJson from '../app.json'
import { loadName } from './storage'

// Reports are appended to one Markdown file in a private repo. The token is a
// fine-grained GitHub token limited to Contents: write on that repo only, read
// from app/.env.local at build time (never committed).
const REPO = process.env.EXPO_PUBLIC_FEEDBACK_REPO ?? 'iumer/sakinah-feedback'
const FILE = process.env.EXPO_PUBLIC_FEEDBACK_FILE ?? 'REPORTS.md'
const TOKEN = process.env.EXPO_PUBLIC_FEEDBACK_TOKEN ?? ''
const API = `https://api.github.com/repos/${REPO}/contents/${FILE}`

/** Reports that could not be sent yet (offline, no token); retried on the next report. */
const QUEUE_KEY = 'hadith.reports.pending.v1'

export type ReportInput = {
  passageRef: string
  passageId: string
  moodId: string
  subId: string
  reasons: string[]
  note?: string
}

type Report = ReportInput & {
  id: string
  createdAt: string
  name: string
  device: string
  os: string
  appVersion: string
  localIp: string
  publicIp: string
}

async function withTimeout<T>(p: Promise<T>, ms: number, fallback: T): Promise<T> {
  return Promise.race([p, new Promise<T>((r) => setTimeout(() => r(fallback), ms))]).catch(() => fallback)
}

async function publicIp(): Promise<string> {
  const res = await fetch('https://api.ipify.org?format=json')
  return ((await res.json()) as { ip?: string }).ip ?? 'unknown'
}

async function describe(input: ReportInput): Promise<Report> {
  const [name, localIp, ip] = await Promise.all([
    loadName(),
    withTimeout(Network.getIpAddressAsync(), 3000, 'unknown'),
    withTimeout(publicIp(), 4000, 'unknown'),
  ])
  return {
    ...input,
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: new Date().toISOString(),
    name: name ?? 'unknown',
    device: [Device.deviceName, Device.manufacturer, Device.modelName].filter(Boolean).join(' · ') || 'unknown',
    os: `${Device.osName ?? Platform.OS} ${Device.osVersion ?? ''}`.trim(),
    appVersion: appJson.expo.version,
    localIp,
    publicIp: ip,
  }
}

function toMarkdown(r: Report, labels: Record<string, string>): string {
  const cell = (s: string) => s.replace(/\|/g, '\\|').replace(/\r?\n/g, '<br>')
  const rows: [string, string][] = [
    ['Passage', r.passageRef],
    ['Where', `${r.moodId} › ${r.subId} (${r.passageId})`],
    ['Reasons', r.reasons.map((x) => labels[x] ?? x).join('; ')],
    ['Note', r.note ?? '—'],
    ['Name', r.name],
    ['Device', r.device],
    ['OS', r.os],
    ['App', r.appVersion],
    ['Public IP', r.publicIp],
    ['Local IP', r.localIp],
  ]
  return [
    '',
    `## ${r.createdAt.replace('T', ' ').slice(0, 16)} UTC — ${cell(r.passageRef)}`,
    '',
    '| | |',
    '|---|---|',
    ...rows.map(([k, v]) => `| ${k} | ${cell(v)} |`),
    '',
    `<sub>id ${r.id}</sub>`,
    '',
  ].join('\n')
}

// --- base64 for UTF-8 text (Arabic/Urdu in notes, ﷺ in titles) -------------
const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
function toBase64(text: string): string {
  const bytes = new TextEncoder().encode(text)
  let out = ''
  for (let i = 0; i < bytes.length; i += 3) {
    const n = (bytes[i] << 16) | ((bytes[i + 1] ?? 0) << 8) | (bytes[i + 2] ?? 0)
    out += B64[(n >> 18) & 63] + B64[(n >> 12) & 63]
    out += i + 1 < bytes.length ? B64[(n >> 6) & 63] : '='
    out += i + 2 < bytes.length ? B64[n & 63] : '='
  }
  return out
}

const headers = () => ({
  Authorization: `Bearer ${TOKEN}`,
  'X-GitHub-Api-Version': '2022-11-28',
})

/** Appends entries to the report file; retries if someone else wrote at the same moment. */
async function append(markdown: string): Promise<void> {
  for (let attempt = 0; attempt < 3; attempt++) {
    const meta = await fetch(`${API}?t=${Date.now()}`, { headers: { ...headers(), Accept: 'application/vnd.github+json' } })
    if (!meta.ok) throw new Error(`GitHub ${meta.status}`)
    const { sha, download_url } = (await meta.json()) as { sha: string; download_url: string }
    const raw = await fetch(`${API}?t=${Date.now()}`, { headers: { ...headers(), Accept: 'application/vnd.github.raw' } })
    if (!raw.ok) throw new Error(`GitHub ${raw.status} ${download_url}`)
    const current = await raw.text()
    const put = await fetch(API, {
      method: 'PUT',
      headers: { ...headers(), Accept: 'application/vnd.github+json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'New report from Sakinah app', content: toBase64(current + markdown), sha }),
    })
    if (put.ok) return
    if (put.status !== 409 && put.status !== 422) throw new Error(`GitHub ${put.status}`)
  }
  throw new Error('GitHub: file kept changing, try later')
}

async function readQueue(): Promise<Report[]> {
  try {
    return JSON.parse((await AsyncStorage.getItem(QUEUE_KEY)) ?? '[]') as Report[]
  } catch {
    return []
  }
}

/**
 * Sends a report (plus any earlier ones that failed). Returns true when it
 * reached GitHub, false when it was kept on the phone to retry later.
 */
export async function sendReport(input: ReportInput, labels: Record<string, string>): Promise<boolean> {
  const report = await describe(input)
  const pending = [...(await readQueue()), report]
  try {
    if (!TOKEN) throw new Error('No feedback token in this build')
    await append(pending.map((r) => toMarkdown(r, labels)).join(''))
    await AsyncStorage.removeItem(QUEUE_KEY)
    return true
  } catch {
    await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(pending)).catch(() => {})
    return false
  }
}
