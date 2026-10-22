import { useCallback } from 'react'
import { Platform, Pressable, StyleSheet, Text, View } from 'react-native'
import { useFocusEffect } from '@react-navigation/native'
import { Gesture, GestureDetector } from 'react-native-gesture-handler'
import Animated, {
  Extrapolation,
  SharedValue,
  cancelAnimation,
  interpolate,
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from 'react-native-reanimated'
import type { Mood } from '../types'
import { shortLabel } from '../content'
import { colors, fonts } from '../theme'

const PULL_OPEN = 120
const PULL_MAX = 240
const SWIPE_STEP = 120
const CARD_W = 138
const CARD_H = 188
const REVEAL_MS = 820

type Props = {
  moods: Mood[]
  focus: number
  setFocus: (i: number) => void
  onOpen: (mood: Mood) => void
}

export function CardFan({ moods, focus, setFocus, onOpen }: Props) {
  const pullY = useSharedValue(0)
  const revealing = useSharedValue(0)
  /** Continuous fan position (card index as float) — drives live L/R motion */
  const scroll = useSharedValue(focus)
  const scrollAtStart = useSharedValue(focus)
  const axis = useSharedValue<'none' | 'x' | 'y'>('none')
  const busy = useSharedValue(0)
  const hintIndex = useSharedValue(focus)

  const openMood = (index: number) => onOpen(moods[index])
  const setHintJS = (i: number) => {
    hintIndex.value = i
    setFocus(i)
  }

  const resetFan = useCallback(() => {
    cancelAnimation(pullY)
    cancelAnimation(revealing)
    cancelAnimation(scroll)
    pullY.value = 0
    revealing.value = 0
    busy.value = 0
    axis.value = 'none'
    scroll.value = focus
    scrollAtStart.value = focus
    hintIndex.value = focus
  }, [focus, pullY, revealing, scroll, scrollAtStart, busy, axis, hintIndex])

  useFocusEffect(
    useCallback(() => {
      resetFan()
      return () => {
        cancelAnimation(pullY)
        cancelAnimation(revealing)
        cancelAnimation(scroll)
      }
    }, [resetFan, pullY, revealing, scroll]),
  )

  const pan = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .activeOffsetY([-10, 10])
    .onBegin(() => {
      if (busy.value > 0.5 || revealing.value > 0.05) return
      cancelAnimation(scroll)
      scrollAtStart.value = scroll.value
      axis.value = 'none'
      pullY.value = 0
    })
    .onUpdate((e) => {
      if (busy.value > 0.5 || revealing.value > 0.05) return
      const absX = Math.abs(e.translationX)
      const absY = Math.abs(e.translationY)

      if (axis.value === 'none') {
        if (absX < 10 && absY < 10) return
        axis.value = absY > absX ? 'y' : 'x'
      }

      if (axis.value === 'x') {
        pullY.value = 0
        const next = scrollAtStart.value - e.translationX / SWIPE_STEP
        scroll.value = Math.max(0, Math.min(moods.length - 1, next))
        return
      }

      pullY.value = Math.max(0, Math.min(PULL_MAX, e.translationY))
    })
    .onEnd(() => {
      if (busy.value > 0.5 || revealing.value > 0.05) return
      const wasY = axis.value === 'y'
      const wasX = axis.value === 'x'
      axis.value = 'none'

      if (wasX) {
        const next = Math.max(0, Math.min(moods.length - 1, Math.round(scroll.value)))
        scroll.value = withSpring(next, { damping: 20, stiffness: 260 })
        runOnJS(setHintJS)(next)
        return
      }

      if (wasY && pullY.value >= PULL_OPEN) {
        busy.value = 1
        const idx = Math.max(0, Math.min(moods.length - 1, Math.round(scroll.value)))
        // 1) Finish the downward pull all the way
        pullY.value = withTiming(PULL_MAX, { duration: 280 }, (ok) => {
          if (!ok) return
          // 2) Expand / curtain fully, then navigate — no mid-cut
          revealing.value = withTiming(1, { duration: REVEAL_MS }, (done) => {
            if (done) runOnJS(openMood)(idx)
          })
        })
        return
      }

      pullY.value = withSpring(0, { damping: 18, stiffness: 220 })
    })

  const veilStyle = useAnimatedStyle(() => {
    const p = Math.min(1, pullY.value / PULL_OPEN)
    const r = revealing.value
    return {
      opacity: 0.12 + p * 0.5 + r * 0.35,
      transform: [{ translateY: (1 - p) * 36 }, { scaleY: 0.35 + p * 0.85 + r * 0.4 }],
    }
  })

  const trackStyle = useAnimatedStyle(() => ({
    width: `${Math.min(100, (pullY.value / PULL_OPEN) * 100)}%`,
  }))

  // Only visible while pulling, so it doesn't read as a second home indicator
  const trackWrapStyle = useAnimatedStyle(() => ({
    opacity: interpolate(pullY.value, [0, 12], [0, 1], Extrapolation.CLAMP),
  }))

  const curtainStyle = useAnimatedStyle(() => {
    const r = revealing.value
    const p = Math.min(1, pullY.value / PULL_OPEN)
    return {
      opacity: interpolate(r, [0, 0.25, 1], [0, 0.5, 1], Extrapolation.CLAMP),
      transform: [
        { translateY: interpolate(r, [0, 1], [48, 0], Extrapolation.CLAMP) },
        { scale: interpolate(r, [0, 1], [0.5 + p * 0.12, 1.4], Extrapolation.CLAMP) },
      ],
    }
  })

  const active = moods[Math.max(0, Math.min(moods.length - 1, focus))]
  const isWeb = Platform.OS === 'web'

  const browseBy = (dir: number) => {
    // Use live scroll (same source as pan), not possibly-stale React focus
    const base = Math.round(scroll.value)
    const next = Math.max(0, Math.min(moods.length - 1, base + dir))
    if (next === base) return
    scroll.value = withSpring(next, { damping: 20, stiffness: 260 })
    setHintJS(next)
  }

  const openWithReveal = () => {
    const idx = Math.max(0, Math.min(moods.length - 1, Math.round(scroll.value)))
    busy.value = 1
    pullY.value = withTiming(PULL_MAX, { duration: 280 }, (ok) => {
      if (!ok) return
      revealing.value = withTiming(1, { duration: REVEAL_MS }, (done) => {
        if (done) runOnJS(openMood)(idx)
      })
    })
  }

  return (
    <View style={styles.stage}>
      {isWeb ? null : (
        <Text style={styles.hint}>
          Swipe left or right to browse · pull{' '}
          <Text style={styles.hintStrong}>{shortLabel(active)}</Text> down to open
        </Text>
      )}
      <Animated.View style={[styles.track, trackWrapStyle]}>
        <Animated.View style={[styles.trackFill, trackStyle as object]} />
      </Animated.View>
      <GestureDetector gesture={pan}>
        <View style={styles.fan} collapsable={false}>
          <Animated.View pointerEvents="none" style={[styles.veil, veilStyle]} />
          <Animated.View
            pointerEvents="none"
            style={[styles.curtain, { backgroundColor: active.color }, curtainStyle]}
          />

          {moods.map((mood, i) => (
            <FanCard
              key={mood.id}
              mood={mood}
              index={i}
              scroll={scroll}
              pullY={pullY}
              revealing={revealing}
            />
          ))}
        </View>
      </GestureDetector>

      {isWeb ? (
        <View style={styles.webBar}>
          <Pressable
            style={[styles.webBtn, focus <= 0 && styles.webBtnDisabled]}
            disabled={focus <= 0}
            onPress={() => browseBy(-1)}
            accessibilityLabel="Previous mood"
          >
            <Text style={styles.webBtnText}>‹</Text>
          </Pressable>
          <Pressable style={styles.webOpen} onPress={openWithReveal} accessibilityLabel="Open mood">
            <Text style={styles.webOpenText}>Open {shortLabel(active)}</Text>
          </Pressable>
          <Pressable
            style={[styles.webBtn, focus >= moods.length - 1 && styles.webBtnDisabled]}
            disabled={focus >= moods.length - 1}
            onPress={() => browseBy(1)}
            accessibilityLabel="Next mood"
          >
            <Text style={styles.webBtnText}>›</Text>
          </Pressable>
        </View>
      ) : null}
    </View>
  )
}

function FanCard({
  mood,
  index,
  scroll,
  pullY,
  revealing,
}: {
  mood: Mood
  index: number
  scroll: SharedValue<number>
  pullY: SharedValue<number>
  revealing: SharedValue<number>
}) {
  const style = useAnimatedStyle(() => {
    const offset = index - scroll.value
    const p = Math.min(1, pullY.value / PULL_OPEN)
    const r = revealing.value
    const isActive = Math.abs(offset) < 0.5

    if (r > 0 && isActive) {
      const fromY = -40 + pullY.value
      return {
        transform: [
          { translateX: 0 },
          { translateY: interpolate(r, [0, 1], [fromY, -52]) },
          { rotate: `${interpolate(r, [0, 1], [p * 2, 0])}deg` },
          { scale: interpolate(r, [0, 1], [1.12 + p * 0.14, 2.6]) },
        ],
        zIndex: 40,
        opacity: 1,
      }
    }

    if (r > 0) {
      return {
        transform: [
          { translateX: interpolate(r, [0, 1], [offset * 30, offset * 58]) },
          {
            translateY: interpolate(r, [0, 1], [Math.abs(offset) * 8, 40 + Math.abs(offset) * 12]),
          },
          { rotate: `${interpolate(r, [0, 1], [offset * 9, offset * 18])}deg` },
          { scale: interpolate(r, [0, 1], [0.9, 0.58]) },
        ],
        zIndex: 10 - Math.round(Math.abs(offset)),
        opacity: interpolate(r, [0, 0.8, 1], [1, 0.15, 0]),
      }
    }

    const x = offset * 30
    const y = isActive ? -40 + pullY.value : Math.abs(offset) * 8
    const rot = isActive ? p * 2.5 : offset * 9
    const scale = isActive
      ? 1.14 + p * 0.12
      : interpolate(Math.abs(offset), [0, 1, 2.5], [1.14, 0.9, 0.82], Extrapolation.CLAMP)

    return {
      transform: [{ translateX: x }, { translateY: y }, { rotate: `${rot}deg` }, { scale }],
      zIndex: isActive ? 20 : 10 - Math.round(Math.abs(offset)),
      opacity: interpolate(Math.abs(offset), [0, 2, 3.2], [1, 0.75, 0], Extrapolation.CLAMP),
    }
  })

  // Titles on cards behind the front one overlap into noise, so fade them out
  const textStyle = useAnimatedStyle(() => ({
    opacity: interpolate(Math.abs(index - scroll.value), [0, 0.6, 1.2], [1, 0.25, 0], Extrapolation.CLAMP),
  }))

  const cueStyle = useAnimatedStyle(() => {
    const isActive = Math.abs(index - scroll.value) < 0.5
    const p = Math.min(1, pullY.value / PULL_OPEN)
    return {
      opacity: isActive && revealing.value < 0.12 ? 0.35 + p * 0.65 : 0,
    }
  })

  return (
    <Animated.View style={[styles.card, { backgroundColor: mood.color }, style]}>
      <View style={styles.whiteWash} />
      <Animated.Text style={[styles.cue, cueStyle]}>Pull down</Animated.Text>
      <Animated.View style={textStyle}>
        <Text style={styles.title} numberOfLines={1} adjustsFontSizeToFit minimumFontScale={0.6}>
          {shortLabel(mood)}
        </Text>
        <Text style={styles.sub}>{mood.short}</Text>
      </Animated.View>
    </Animated.View>
  )
}

const styles = StyleSheet.create({
  stage: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 14,
    // Leaves room under the fan for the card to travel during the pull
    paddingBottom: 160,
    minHeight: 320,
  },
  fan: {
    width: '100%',
    height: 300,
    alignItems: 'center',
    justifyContent: 'center',
  },
  veil: {
    position: 'absolute',
    left: '10%',
    right: '10%',
    bottom: '8%',
    height: '70%',
    borderRadius: 28,
    backgroundColor: 'rgba(255,255,255,0.85)',
    zIndex: 5,
  },
  curtain: {
    ...StyleSheet.absoluteFill,
    borderRadius: 28,
    zIndex: 35,
  },
  card: {
    position: 'absolute',
    width: CARD_W,
    height: CARD_H,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 18,
    justifyContent: 'flex-end',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.85)',
    shadowColor: '#3c5064',
    shadowOpacity: 0.16,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 12 },
    elevation: 6,
    overflow: 'hidden',
  },
  whiteWash: {
    ...StyleSheet.absoluteFill,
    backgroundColor: 'rgba(255,255,255,0.42)',
  },
  cue: {
    position: 'absolute',
    top: 16,
    left: 16,
    fontSize: 11,
    fontFamily: fonts.bodyExtra,
    letterSpacing: 0.4,
    textTransform: 'uppercase',
    color: colors.ink,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 22,
    color: colors.ink,
  },
  sub: {
    fontFamily: fonts.bodyBold,
    fontSize: 13,
    color: colors.inkSoft,
    marginTop: 2,
    opacity: 0.75,
  },
  hint: {
    textAlign: 'center',
    fontFamily: fonts.bodyBold,
    fontSize: 13,
    color: colors.mist,
    lineHeight: 18,
    maxWidth: 280,
  },
  hintStrong: {
    color: colors.ink,
    fontFamily: fonts.bodyExtra,
  },
  track: {
    width: 200,
    height: 4,
    borderRadius: 999,
    backgroundColor: 'rgba(36,48,68,0.1)',
    overflow: 'hidden',
  },
  trackFill: {
    height: '100%',
    backgroundColor: colors.accent,
    borderRadius: 999,
  },
  webBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    maxWidth: 320,
  },
  webBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.9)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  webBtnDisabled: { opacity: 0.35 },
  webBtnText: {
    fontSize: 28,
    lineHeight: 30,
    color: colors.ink,
    fontFamily: fonts.bodyBold,
  },
  webOpen: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 999,
    backgroundColor: colors.ink,
    alignItems: 'center',
  },
  webOpenText: {
    color: colors.white,
    fontFamily: fonts.bodyBold,
    fontSize: 15,
  },
})
