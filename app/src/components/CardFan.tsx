import { useEffect } from 'react'
import { StyleSheet, Text, View } from 'react-native'
import { Gesture, GestureDetector } from 'react-native-gesture-handler'
import Animated, {
  Extrapolation,
  SharedValue,
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

const PULL_OPEN = 110
const CARD_W = 138
const CARD_H = 188

type Props = {
  moods: Mood[]
  focus: number
  setFocus: (i: number) => void
  onOpen: (mood: Mood) => void
}

export function CardFan({ moods, focus, setFocus, onOpen }: Props) {
  const pullY = useSharedValue(0)
  const revealing = useSharedValue(0)
  const focusSV = useSharedValue(focus)
  const startFocus = useSharedValue(focus)
  const axis = useSharedValue<'none' | 'x' | 'y'>('none')

  useEffect(() => {
    focusSV.value = focus
  }, [focus, focusSV])

  const openMood = (index: number) => {
    onOpen(moods[index])
  }

  const setFocusJS = (i: number) => {
    setFocus(i)
  }

  const finishReveal = (index: number) => {
    setTimeout(() => openMood(index), 560)
  }

  const pan = Gesture.Pan()
    .onBegin(() => {
      if (revealing.value > 0.5) return
      startFocus.value = focusSV.value
      axis.value = 'none'
      pullY.value = 0
    })
    .onUpdate((e) => {
      if (revealing.value > 0.5) return
      const absX = Math.abs(e.translationX)
      const absY = Math.abs(e.translationY)

      if (axis.value === 'none') {
        if (absX < 8 && absY < 8) return
        axis.value = absY > absX ? 'y' : 'x'
      }

      if (axis.value === 'x') {
        pullY.value = 0
        const steps = Math.round(-e.translationX / 72)
        const next = Math.max(0, Math.min(moods.length - 1, startFocus.value + steps))
        if (next !== focusSV.value) {
          focusSV.value = next
          runOnJS(setFocusJS)(next)
        }
        return
      }

      pullY.value = Math.max(0, Math.min(160, e.translationY))
    })
    .onEnd(() => {
      if (revealing.value > 0.5) return
      const wasY = axis.value === 'y'
      axis.value = 'none'
      if (wasY && pullY.value >= PULL_OPEN) {
        revealing.value = withTiming(1, { duration: 520 })
        pullY.value = withTiming(180, { duration: 200 })
        runOnJS(finishReveal)(focusSV.value)
        return
      }
      pullY.value = withSpring(0, { damping: 18, stiffness: 220 })
    })

  const veilStyle = useAnimatedStyle(() => {
    const p = Math.min(1, pullY.value / PULL_OPEN)
    const r = revealing.value
    return {
      opacity: 0.15 + p * 0.55 + r * 0.25,
      transform: [{ translateY: (1 - p) * 40 }, { scaleY: 0.4 + p * 0.8 + r * 0.35 }],
    }
  })

  const trackStyle = useAnimatedStyle(() => ({
    width: `${Math.min(100, (pullY.value / PULL_OPEN) * 100)}%`,
  }))

  const curtainStyle = useAnimatedStyle(() => ({
    opacity: interpolate(revealing.value, [0, 0.15, 1], [0, 0.55, 1], Extrapolation.CLAMP),
    transform: [
      { scale: interpolate(revealing.value, [0, 1], [0.55, 1.2], Extrapolation.CLAMP) },
    ],
  }))

  const active = moods[focus]

  return (
    <View style={styles.stage}>
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
              count={moods.length}
              focusSV={focusSV}
              pullY={pullY}
              revealing={revealing}
            />
          ))}
        </View>
      </GestureDetector>

      <Text style={styles.hint}>
        Swipe left or right to browse · pull{' '}
        <Text style={styles.hintStrong}>{shortLabel(active)}</Text> down to open
      </Text>
      <View style={styles.track}>
        <Animated.View style={[styles.trackFill, trackStyle as object]} />
      </View>
    </View>
  )
}

function FanCard({
  mood,
  index,
  count,
  focusSV,
  pullY,
  revealing,
}: {
  mood: Mood
  index: number
  count: number
  focusSV: SharedValue<number>
  pullY: SharedValue<number>
  revealing: SharedValue<number>
}) {
  const style = useAnimatedStyle(() => {
    const mid = (count - 1) / 2
    const spread = index - mid
    const isActive = index === Math.round(focusSV.value)
    const baseY = isActive ? -40 : Math.abs(spread) * 7
    const p = Math.min(1, pullY.value / PULL_OPEN)
    const r = revealing.value

    if (r > 0 && isActive) {
      return {
        transform: [
          { translateX: 0 },
          { translateY: interpolate(r, [0, 1], [baseY + pullY.value, -28]) },
          { rotate: `${interpolate(r, [0, 1], [p * 2, 0])}deg` },
          { scale: interpolate(r, [0, 1], [1.14 + p * 0.08, 2.25]) },
        ],
        zIndex: 40,
        opacity: 1,
      }
    }

    if (r > 0) {
      return {
        transform: [
          { translateX: interpolate(r, [0, 1], [spread * 26, spread * 42]) },
          { translateY: interpolate(r, [0, 1], [baseY, baseY + 28]) },
          { rotate: `${interpolate(r, [0, 1], [spread * 8, spread * 12])}deg` },
          { scale: interpolate(r, [0, 1], [0.9, 0.7]) },
        ],
        zIndex: 10 - Math.abs(spread),
        opacity: interpolate(r, [0, 1], [1, 0]),
      }
    }

    return {
      transform: [
        { translateX: isActive ? 0 : spread * 26 },
        { translateY: isActive ? baseY + pullY.value : baseY },
        { rotate: `${isActive ? p * 2 : spread * 8}deg` },
        { scale: isActive ? 1.14 + p * 0.08 : 0.9 },
      ],
      zIndex: isActive ? 20 : 10 - Math.abs(spread),
      opacity: 1,
    }
  })

  const cueStyle = useAnimatedStyle(() => {
    const isActive = index === Math.round(focusSV.value)
    const p = Math.min(1, pullY.value / PULL_OPEN)
    return {
      opacity: isActive && revealing.value < 0.2 ? 0.35 + p * 0.65 : 0,
    }
  })

  return (
    <Animated.View style={[styles.card, { backgroundColor: mood.color }, style]}>
      <View style={styles.whiteWash} />
      <View style={styles.count}>
        <Text style={styles.countText}>{mood.subs.length}</Text>
      </View>
      <Animated.Text style={[styles.cue, cueStyle]}>Pull down</Animated.Text>
      <Text style={styles.title}>{shortLabel(mood)}</Text>
      <Text style={styles.sub}>{mood.short}</Text>
    </Animated.View>
  )
}

const styles = StyleSheet.create({
  stage: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: 14,
    paddingBottom: 4,
    minHeight: 320,
  },
  fan: {
    width: '100%',
    height: 290,
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
  count: {
    position: 'absolute',
    top: 14,
    right: 14,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.75)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  countText: {
    fontFamily: fonts.bodyExtra,
    fontSize: 12,
    color: colors.inkSoft,
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
})
