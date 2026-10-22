import { useState } from 'react'
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native'
import type { Grade, Passage } from '../types'
import { colors, fonts } from '../theme'

export const GRADE_INFO: Record<Grade, { label: string; term: string; fill: number; color: string }> = {
  sahih: { label: 'Authentic', term: 'Sahih', fill: 1, color: colors.gradeSahih },
  hasan: { label: 'Good', term: 'Hasan', fill: 0.75, color: colors.gradeHasan },
  daif: { label: 'Weak', term: "Da'if", fill: 0.35, color: colors.gradeDaif },
  mawdu: { label: 'Fabricated', term: "Mawdu'", fill: 0.1, color: colors.gradeMawdu },
}

export function GradeBar({ item }: { item: Passage }) {
  const [open, setOpen] = useState(false)
  if (item.kind !== 'hadith' || !item.grade) return null
  const info = GRADE_INFO[item.grade]

  return (
    <>
      <Pressable
        onPress={() => setOpen(true)}
        style={({ pressed }) => [styles.wrap, pressed && { opacity: 0.7 }]}
        accessibilityRole="button"
        accessibilityLabel={`Authenticity: ${info.label}, ${info.term}. Tap for details`}
      >
        <View style={styles.row}>
          <Text style={[styles.label, { color: info.color }]}>
            {info.label} · {info.term}
          </Text>
          <Text style={styles.by} numberOfLines={1}>
            {item.gradedBy}
            {item.disputed ? ' · scholars differ' : ''} ⓘ
          </Text>
        </View>
        <View style={styles.track}>
          <View style={[styles.fill, { width: `${info.fill * 100}%`, backgroundColor: info.color }]} />
        </View>
      </Pressable>

      <Modal visible={open} animationType="fade" transparent onRequestClose={() => setOpen(false)}>
        <View style={styles.modalWrap}>
          <Pressable style={styles.backdrop} onPress={() => setOpen(false)} />
          <View style={styles.panel}>
            <Text style={styles.title}>How authentic is this hadith?</Text>
            <ScrollView style={{ maxHeight: 420 }} contentContainerStyle={{ gap: 12 }}>
              <Text style={styles.body}>
                Hadith scholars grade each narration by the strength of its chain of narrators
                (isnad): whether every narrator was trustworthy, had precise memory, and truly heard
                it from the one before them.
              </Text>
              <View style={styles.legend}>
                {(Object.keys(GRADE_INFO) as Grade[]).map((g) => (
                  <View key={g} style={styles.legendRow}>
                    <View style={[styles.legendTrack]}>
                      <View
                        style={[
                          styles.fill,
                          { width: `${GRADE_INFO[g].fill * 100}%`, backgroundColor: GRADE_INFO[g].color },
                        ]}
                      />
                    </View>
                    <Text style={[styles.legendText, g === item.grade && styles.legendOn]}>
                      {GRADE_INFO[g].label} ({GRADE_INFO[g].term})
                    </Text>
                  </View>
                ))}
              </View>
              {item.gradings && item.gradings.length > 0 ? (
                <View style={{ gap: 6 }}>
                  <Text style={styles.section}>Gradings for {item.title}</Text>
                  {item.gradings.map((g, i) => (
                    <Text key={i} style={styles.body}>
                      {g.grader}: <Text style={{ color: GRADE_INFO[g.grade].color, fontFamily: fonts.bodyExtra }}>{GRADE_INFO[g.grade].label}</Text>
                    </Text>
                  ))}
                  {item.disputed ? (
                    <Text style={styles.note}>
                      Scholars differ on this narration. Most graders, including {item.gradedBy},
                      accept it, so it is included here.
                    </Text>
                  ) : null}
                </View>
              ) : (
                <Text style={styles.body}>
                  {item.gradedBy}: every hadith in this collection is accepted as authentic by the
                  agreement of the scholars.
                </Text>
              )}
              <Text style={styles.note}>This app only includes hadith graded Authentic or Good.</Text>
            </ScrollView>
            <Pressable onPress={() => setOpen(false)} style={styles.close}>
              <Text style={styles.closeText}>Close</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
    </>
  )
}

const styles = StyleSheet.create({
  wrap: { gap: 6 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 8 },
  label: { fontFamily: fonts.bodyExtra, fontSize: 13 },
  by: { flexShrink: 1, fontFamily: fonts.body, fontSize: 12, color: colors.mist },
  track: {
    height: 6,
    borderRadius: 999,
    backgroundColor: 'rgba(36,48,68,0.1)',
    overflow: 'hidden',
  },
  fill: { height: '100%', borderRadius: 999 },
  modalWrap: { flex: 1, justifyContent: 'flex-end' },
  backdrop: { ...StyleSheet.absoluteFill, backgroundColor: 'rgba(36,48,68,0.35)' },
  panel: {
    backgroundColor: colors.paper,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    paddingBottom: 32,
    gap: 12,
  },
  title: { fontFamily: fonts.display, fontSize: 22, color: colors.ink },
  section: { fontFamily: fonts.bodyExtra, fontSize: 12, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.mist },
  body: { fontFamily: fonts.body, fontSize: 14, lineHeight: 21, color: colors.ink },
  note: { fontFamily: fonts.body, fontSize: 13, lineHeight: 19, color: colors.inkSoft },
  legend: { gap: 8 },
  legendRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  legendTrack: {
    width: 72,
    height: 6,
    borderRadius: 999,
    backgroundColor: 'rgba(36,48,68,0.1)',
    overflow: 'hidden',
  },
  legendText: { fontFamily: fonts.body, fontSize: 13, color: colors.inkSoft },
  legendOn: { fontFamily: fonts.bodyExtra, color: colors.ink },
  close: {
    alignSelf: 'flex-end',
    backgroundColor: colors.ink,
    paddingHorizontal: 22,
    paddingVertical: 12,
    borderRadius: 999,
  },
  closeText: { fontFamily: fonts.bodyBold, color: colors.white },
})
