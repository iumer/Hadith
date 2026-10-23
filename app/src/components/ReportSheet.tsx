import { useState } from 'react'
import {
  Keyboard,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native'
import { sendReport } from '../reports'
import type { Passage } from '../types'
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

type Props = {
  visible: boolean
  passage: Passage
  moodId: string
  subId: string
  onClose: () => void
}

export function ReportSheet({ visible, passage, moodId, subId, onClose }: Props) {
  const refTitle = passage.title
  const [selected, setSelected] = useState<string[]>([])
  const [note, setNote] = useState('')
  const [sent, setSent] = useState(false)
  const [sending, setSending] = useState(false)
  const [queued, setQueued] = useState(false)

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const reset = () => {
    setSelected([])
    setNote('')
    setSent(false)
    setQueued(false)
  }

  const close = () => {
    reset()
    onClose()
  }

  const submit = async () => {
    if (!selected.length || sending) return
    setSending(true)
    const labels = Object.fromEntries(REPORT_OPTIONS.map((o) => [o.id, o.label]))
    const delivered = await sendReport(
      { passageRef: refTitle, passageId: passage.id, moodId, subId, reasons: selected, note: note.trim() || undefined },
      labels,
    )
    setSending(false)
    setQueued(!delivered)
    setSent(true)
    setTimeout(close, delivered ? 1100 : 2200)
  }

  return (
    <Modal visible={visible} animationType="fade" transparent onRequestClose={close}>
      <KeyboardAvoidingView
        style={styles.wrap}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* First tap with the keyboard up only hides it, so a half-written report isn't lost */}
        <Pressable
          style={styles.backdrop}
          onPress={() => (Keyboard.isVisible() ? Keyboard.dismiss() : close())}
        />
        <View style={styles.panel}>
          {sent ? (
            <View style={styles.thanks}>
              <Text style={styles.title}>Thank you</Text>
              <Text style={styles.lede}>
                {queued
                  ? "Saved on your phone. It will be sent next time you're online."
                  : 'Your report helps us improve these passages.'}
              </Text>
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
                      <View style={[styles.box, on && styles.boxOn]}>
                        <Text style={styles.check}>{on ? '✓' : ''}</Text>
                      </View>
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
                submitBehavior="blurAndSubmit"
                returnKeyType="done"
              />
              <Text style={styles.privacy}>
                Sent with your report: the name you entered, your device model and IP address.
              </Text>
              <View style={styles.actions}>
                <Pressable onPress={close} style={styles.ghost}>
                  <Text style={styles.ghostText}>Cancel</Text>
                </Pressable>
                <Pressable
                  onPress={submit}
                  disabled={!selected.length || sending}
                  style={[styles.primary, (!selected.length || sending) && { opacity: 0.35 }]}
                >
                  <Text style={styles.primaryText}>{sending ? 'Sending…' : 'Submit report'}</Text>
                </Pressable>
              </View>
            </>
          )}
        </View>
      </KeyboardAvoidingView>
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
    flexGrow: 0,
    flexShrink: 1,
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
  box: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1.5,
    borderColor: 'rgba(36,48,68,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  boxOn: {
    borderColor: colors.accent,
    backgroundColor: colors.accent,
  },
  check: {
    fontFamily: fonts.bodyExtra,
    fontSize: 13,
    color: colors.white,
  },
  optionLabel: {
    flex: 1,
    fontFamily: fonts.body,
    fontSize: 14,
    color: colors.ink,
  },
  privacy: {
    fontFamily: fonts.body,
    fontSize: 12,
    lineHeight: 17,
    color: colors.mist,
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
