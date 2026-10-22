import { useState } from 'react'
import {
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { colors, fonts } from '../theme'

const REPORT_OPTIONS = [
  { id: 'ref-wrong', label: 'Issue in the reference (wrong book / number)' },
  { id: 'ref-mismatch', label: 'Reference differs from the original book' },
  { id: 'translation', label: 'The translation is not correct' },
  { id: 'arabic', label: 'The Arabic text looks incorrect' },
  { id: 'meaning', label: 'The explanation / meaning is not correct' },
  { id: 'reflection', label: 'The reflection feels off or misleading' },
  { id: 'other', label: 'Something else' },
] as const

const STORAGE_KEY = 'hadith.reports.v1'

type Props = {
  visible: boolean
  refTitle: string
  onClose: () => void
}

export function ReportSheet({ visible, refTitle, onClose }: Props) {
  const [selected, setSelected] = useState<string[]>([])
  const [note, setNote] = useState('')
  const [sent, setSent] = useState(false)

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const reset = () => {
    setSelected([])
    setNote('')
    setSent(false)
  }

  const close = () => {
    reset()
    onClose()
  }

  const submit = async () => {
    if (!selected.length) return
    const entry = {
      at: new Date().toISOString(),
      ref: refTitle,
      selected,
      note: note.trim() || undefined,
    }
    try {
      const raw = await AsyncStorage.getItem(STORAGE_KEY)
      const list = raw ? (JSON.parse(raw) as unknown[]) : []
      list.push(entry)
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(list))
    } catch {
      // keep UX flowing even if storage fails
    }
    setSent(true)
    setTimeout(close, 1100)
  }

  return (
    <Modal visible={visible} animationType="fade" transparent onRequestClose={close}>
      <View style={styles.wrap}>
        <Pressable style={styles.backdrop} onPress={close} />
        <View style={styles.panel}>
          {sent ? (
            <View style={styles.thanks}>
              <Text style={styles.title}>Thank you</Text>
              <Text style={styles.lede}>Your report helps us improve these passages.</Text>
            </View>
          ) : (
            <>
              <Text style={styles.title}>Report an issue</Text>
              <Text style={styles.lede}>Select all that apply for “{refTitle}”.</Text>
              <ScrollView style={styles.options} contentContainerStyle={{ gap: 8 }}>
                {REPORT_OPTIONS.map((opt) => {
                  const on = selected.includes(opt.id)
                  return (
                    <Pressable
                      key={opt.id}
                      onPress={() => toggle(opt.id)}
                      style={[styles.option, on && styles.optionOn]}
                    >
                      <Text style={styles.check}>{on ? '✓' : ''}</Text>
                      <Text style={styles.optionLabel}>{opt.label}</Text>
                    </Pressable>
                  )
                })}
              </ScrollView>
              <Text style={styles.noteLabel}>Optional note</Text>
              <TextInput
                style={styles.note}
                multiline
                placeholder="Anything else we should know?"
                placeholderTextColor={colors.mist}
                value={note}
                onChangeText={setNote}
              />
              <View style={styles.actions}>
                <Pressable onPress={close} style={styles.ghost}>
                  <Text style={styles.ghostText}>Cancel</Text>
                </Pressable>
                <Pressable
                  onPress={submit}
                  disabled={!selected.length}
                  style={[styles.primary, !selected.length && { opacity: 0.35 }]}
                >
                  <Text style={styles.primaryText}>Submit report</Text>
                </Pressable>
              </View>
            </>
          )}
        </View>
      </View>
    </Modal>
  )
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFill,
    backgroundColor: 'rgba(36,48,68,0.35)',
  },
  panel: {
    backgroundColor: colors.paper,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    paddingBottom: 28,
    maxHeight: '88%',
    gap: 10,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 24,
    color: colors.ink,
  },
  lede: {
    fontFamily: fonts.body,
    fontSize: 14,
    color: colors.mist,
    lineHeight: 20,
  },
  options: {
    maxHeight: 280,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 12,
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.9)',
    borderWidth: 1,
    borderColor: 'rgba(36,48,68,0.08)',
  },
  optionOn: {
    borderColor: colors.accent,
    backgroundColor: 'rgba(224,138,106,0.12)',
  },
  check: {
    width: 22,
    textAlign: 'center',
    fontFamily: fonts.bodyExtra,
    color: colors.accent,
  },
  optionLabel: {
    flex: 1,
    fontFamily: fonts.body,
    fontSize: 14,
    color: colors.ink,
  },
  noteLabel: {
    fontFamily: fonts.bodyBold,
    fontSize: 13,
    color: colors.inkSoft,
  },
  note: {
    minHeight: 72,
    borderRadius: 14,
    padding: 12,
    backgroundColor: colors.white,
    fontFamily: fonts.body,
    color: colors.ink,
    textAlignVertical: 'top',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 10,
    marginTop: 4,
  },
  ghost: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  ghostText: {
    fontFamily: fonts.bodyBold,
    color: colors.inkSoft,
  },
  primary: {
    backgroundColor: colors.ink,
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 999,
  },
  primaryText: {
    fontFamily: fonts.bodyBold,
    color: colors.white,
  },
  thanks: {
    paddingVertical: 28,
    alignItems: 'center',
    gap: 8,
  },
})
