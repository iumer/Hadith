import { type ComponentRef, useEffect, useRef, useState } from 'react'
import { Platform, Pressable, ScrollView, StyleSheet, Text, View, useWindowDimensions } from 'react-native'
import { Gesture, GestureDetector } from 'react-native-gesture-handler'
import Animated, {
  Easing,
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from 'react-native-reanimated'
import * as Haptics from 'expo-haptics'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ambient } from '../components/Ambient'
import { BackButton } from '../components/BackButton'
import { GradeBar } from '../components/GradeBar'
import { ReportSheet } from '../components/ReportSheet'
import { getSub } from '../content'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Read'>

// Left edge stays free for the iOS swipe-back gesture (and both edges for Android's
// system back), so a swipe that starts there goes back instead of paging.
const EDGE = 28
const OUT_MS = 170

export function ReadScreen({ navigation, route }: Props) {
  const insets = useSafeAreaInsets()
  const { sub } = getSub(route.params.moodId, route.params.subId)
  const index = route.params.index
  const item = sub.items[index]
  const [reportOpen, setReportOpen] = useState(false)
  const scrollRef = useRef<ComponentRef<typeof ScrollView>>(null)
  const { width } = useWindowDimensions()
  const last = sub.items.length - 1
  const dragX = useSharedValue(0)
  const fade = useSharedValue(1)

  // Each passage starts at the top, not where the previous one was scrolled to
  useEffect(() => {
    scrollRef.current?.scrollTo({ y: 0, animated: false })
  }, [index])

  const showIndex = (next: number, dir: number) => {
    navigation.setParams({ index: next })
    // New passage glides in from the side it is coming from
    dragX.value = dir * width * 0.28
    fade.value = 0
    dragX.value = withSpring(0, { damping: 26, stiffness: 240, mass: 0.9 })
    fade.value = withTiming(1, { duration: 220 })
  }

  /** dir 1 = forward (content leaves to the left), -1 = back */
  const page = (dir: 1 | -1, next = index + dir) => {
    if (next < 0 || next > last) return
    Haptics.selectionAsync().catch(() => {})
    dragX.value = withTiming(-dir * width * 0.6, { duration: OUT_MS, easing: Easing.in(Easing.quad) })
    fade.value = withTiming(0, { duration: OUT_MS }, (done) => {
      if (done) runOnJS(showIndex)(next, dir)
    })
  }

  const swipe = Gesture.Pan()
    .activeOffsetX([-16, 16])
    .failOffsetY([-12, 12])
    .hitSlop({ left: -EDGE, right: Platform.OS === 'android' ? -EDGE : 0 })
    .onUpdate((e) => {
      const blocked = (e.translationX > 0 && index <= 0) || (e.translationX < 0 && index >= last)
      // Rubber-band when there is nothing further in that direction
      dragX.value = blocked ? e.translationX * 0.22 : e.translationX
      fade.value = 1 - Math.min(0.35, Math.abs(dragX.value) / width)
    })
    .onEnd((e) => {
      const dir = e.translationX < 0 ? 1 : -1
      const target = index + dir
      const far = Math.abs(e.translationX) > width * 0.22 || Math.abs(e.velocityX) > 650
      if (far && target >= 0 && target <= last) {
        runOnJS(page)(dir)
      } else {
        dragX.value = withSpring(0, { damping: 20, stiffness: 260 })
        fade.value = withTiming(1, { duration: 160 })
      }
    })

  const cardStyle = useAnimatedStyle(() => ({
    opacity: fade.value,
    transform: [{ translateX: dragX.value }],
  }))

  const go = (next: number) => {
    if (next !== index) page(next > index ? 1 : -1, next)
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

      <GestureDetector gesture={swipe}>
      <Animated.View style={[styles.scroll, cardStyle]}>
      <ScrollView
        ref={scrollRef}
        style={styles.scroll}
        contentContainerStyle={styles.card}
        showsVerticalScrollIndicator={false}
      >
        <View style={[styles.badge, item.kind === 'quran' ? styles.quran : styles.hadith]}>
          <Text style={styles.badgeText}>{item.kind === 'quran' ? 'Quran' : 'Hadith'}</Text>
        </View>
        <View style={styles.titleBlock}>
          <Text style={styles.title}>{item.title}</Text>
          {item.source ? <Text style={styles.source}>{item.source}</Text> : null}
        </View>
        <GradeBar item={item} />
        {item.arabic ? (
          <Text style={[styles.arabic, item.kind === 'quran' ? styles.arabicQuran : styles.arabicHadith]}>
            {item.arabic}
          </Text>
        ) : null}
        {item.urdu ? (
          <View style={styles.translation}>
            <Text style={styles.label}>
              Urdu{item.kind === 'quran' ? ' · Muhammad Junagarhi' : ''}
            </Text>
            <Text style={styles.urdu}>{item.urdu}</Text>
          </View>
        ) : null}
        {item.english ? (
          <View style={styles.translation}>
            <Text style={styles.label}>
              English{item.kind === 'quran' ? ' · Saheeh International' : ''}
            </Text>
            <Text style={styles.english}>{item.english}</Text>
          </View>
        ) : null}
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
      </Animated.View>
      </GestureDetector>

      <View style={[styles.nav, { paddingBottom: Math.max(insets.bottom, 12) }]}>
        <Pressable
          disabled={index <= 0}
          onPress={() => page(-1)}
          style={[styles.ghost, index <= 0 && { opacity: 0.35 }]}
        >
          <Text style={styles.ghostText}>Previous</Text>
        </Pressable>
        <Pressable
          disabled={index >= sub.items.length - 1}
          onPress={() => page(1)}
          style={[styles.primary, index >= sub.items.length - 1 && { opacity: 0.35 }]}
        >
          <Text style={styles.primaryText}>Next</Text>
        </Pressable>
      </View>

      <ReportSheet
        visible={reportOpen}
        passage={item}
        moodId={route.params.moodId}
        subId={route.params.subId}
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
  titleBlock: {
    gap: 2,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 26,
    color: colors.ink,
  },
  source: {
    fontFamily: fonts.body,
    fontSize: 13,
    color: colors.mist,
  },
  arabic: {
    textAlign: 'right',
    writingDirection: 'rtl',
    color: colors.ink,
  },
  arabicQuran: {
    fontFamily: fonts.quran,
    fontSize: 24,
    lineHeight: 52,
  },
  arabicHadith: {
    fontFamily: fonts.arabic,
    fontSize: 22,
    lineHeight: 42,
  },
  translation: {
    gap: 6,
  },
  urdu: {
    fontFamily: fonts.urdu,
    fontSize: 18,
    lineHeight: 44,
    textAlign: 'right',
    writingDirection: 'rtl',
    color: colors.ink,
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
