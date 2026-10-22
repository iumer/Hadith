import { useState } from 'react'
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ambient } from '../components/Ambient'
import { BackButton } from '../components/BackButton'
import { ReportSheet } from '../components/ReportSheet'
import { getSub } from '../content'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Read'>

export function ReadScreen({ navigation, route }: Props) {
  const insets = useSafeAreaInsets()
  const { sub } = getSub(route.params.moodId, route.params.subId)
  const index = route.params.index
  const item = sub.items[index]
  const [reportOpen, setReportOpen] = useState(false)

  const go = (next: number) => {
    navigation.setParams({ index: next })
  }

  return (
    <View style={[styles.root, { paddingTop: insets.top + 8 }]}>
      <Ambient />
      <View style={styles.top}>
        <BackButton onPress={() => navigation.goBack()} />
        <Text style={styles.eyebrow}>
          {index + 1} of {sub.items.length}
        </Text>
        <Pressable onPress={() => setReportOpen(true)} style={styles.reportBtn}>
          <Text style={styles.reportText}>Report</Text>
        </Pressable>
      </View>

      <View style={styles.pips}>
        {sub.items.map((_, i) => (
          <Pressable
            key={i}
            onPress={() => go(i)}
            style={[styles.pip, i === index && styles.pipOn]}
            accessibilityLabel={`Passage ${i + 1}`}
          />
        ))}
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.card}
        showsVerticalScrollIndicator={false}
      >
        <View style={[styles.badge, item.kind === 'quran' ? styles.quran : styles.hadith]}>
          <Text style={styles.badgeText}>{item.kind === 'quran' ? 'Quran' : 'Hadith'}</Text>
        </View>
        <Text style={styles.title}>{item.title}</Text>
        {item.arabic ? <Text style={styles.arabic}>{item.arabic}</Text> : null}
        {item.english ? <Text style={styles.english}>{item.english}</Text> : null}
        {item.meaning ? (
          <View style={styles.block}>
            <Text style={styles.label}>Meaning</Text>
            <Text style={styles.body}>{item.meaning}</Text>
          </View>
        ) : null}
        {item.reflection ? (
          <View style={styles.block}>
            <Text style={styles.label}>Reflection</Text>
            <Text style={styles.body}>{item.reflection}</Text>
          </View>
        ) : null}
      </ScrollView>

      <View style={[styles.nav, { paddingBottom: Math.max(insets.bottom, 12) }]}>
        <Pressable
          disabled={index <= 0}
          onPress={() => go(index - 1)}
          style={[styles.ghost, index <= 0 && { opacity: 0.35 }]}
        >
          <Text style={styles.ghostText}>Previous</Text>
        </Pressable>
        <Pressable
          disabled={index >= sub.items.length - 1}
          onPress={() => go(index + 1)}
          style={[styles.primary, index >= sub.items.length - 1 && { opacity: 0.35 }]}
        >
          <Text style={styles.primaryText}>Next</Text>
        </Pressable>
      </View>

      <ReportSheet
        visible={reportOpen}
        refTitle={item.title}
        onClose={() => setReportOpen(false)}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.cream,
    paddingHorizontal: 20,
  },
  top: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  eyebrow: {
    fontFamily: fonts.bodyExtra,
    fontSize: 12,
    letterSpacing: 1,
    textTransform: 'uppercase',
    color: colors.mist,
  },
  reportBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.78)',
  },
  reportText: {
    fontFamily: fonts.bodyBold,
    fontSize: 13,
    color: colors.accent,
  },
  pips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 12,
  },
  pip: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(36,48,68,0.15)',
  },
  pipOn: {
    backgroundColor: colors.ink,
    width: 18,
  },
  scroll: {
    flex: 1,
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.86)',
    borderRadius: 22,
    padding: 18,
    gap: 12,
    paddingBottom: 28,
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  quran: { backgroundColor: 'rgba(106,167,196,0.22)' },
  hadith: { backgroundColor: 'rgba(224,138,106,0.22)' },
  badgeText: {
    fontFamily: fonts.bodyExtra,
    fontSize: 11,
    color: colors.ink,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 26,
    color: colors.ink,
  },
  arabic: {
    fontSize: 22,
    lineHeight: 40,
    textAlign: 'right',
    writingDirection: 'rtl',
    color: colors.ink,
    fontFamily: fonts.body,
  },
  english: {
    fontFamily: fonts.body,
    fontSize: 16,
    lineHeight: 24,
    color: colors.inkSoft,
  },
  block: {
    gap: 6,
    marginTop: 4,
  },
  label: {
    fontFamily: fonts.bodyExtra,
    fontSize: 12,
    letterSpacing: 0.8,
    textTransform: 'uppercase',
    color: colors.mist,
  },
  body: {
    fontFamily: fonts.body,
    fontSize: 15,
    lineHeight: 22,
    color: colors.ink,
  },
  nav: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
    paddingTop: 12,
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
    paddingHorizontal: 22,
    paddingVertical: 12,
    borderRadius: 999,
  },
  primaryText: {
    fontFamily: fonts.bodyBold,
    color: colors.white,
  },
})
