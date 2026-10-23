import { type ComponentRef, useCallback, useEffect, useRef, useState } from 'react'
import { Platform, Pressable, StyleSheet, Text, View, useWindowDimensions } from 'react-native'
import { useFocusEffect } from '@react-navigation/native'
import { Gesture, GestureDetector } from 'react-native-gesture-handler'
import Animated, {
  Easing,
  Extrapolation,
  SharedValue,
  cancelAnimation,
  interpolate,
  runOnJS,
  useAnimatedReaction,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withSequence,
  withSpring,
  withTiming,
} from 'react-native-reanimated'
import * as Haptics from 'expo-haptics'
import type { Mood } from '../types'
import { shortLabel } from '../content'
import { colors, fonts } from '../theme'

const CARD_W = 172
const CARD_H = 236
const SPREAD = 34 // px between neighbouring cards
const LIFT = -28 // front card sits slightly above the fan
const PULL_OPEN = 110
const PULL_MAX = 190
const SWIPE_STEP = 120
const OPEN_MS = 560
const IDLE_HINT_MS = 4500
// iOS-style "ease out" used by system sheet/app-open animations
const IOS_EASE = Easing.bezier(0.32, 0.72, 0, 1)
// Card face = mood colour under a white wash; Subs uses the same tint so the
// expanded card hands over to the next screen without a colour jump.
export const WASH = 0.42

type Props = {
  /** Question shown right above the cards */
  heading?: string
  moods: Mood[]
  focus: number
  setFocus: (i: number) => void
  onOpen: (mood: Mood) => void
}

/** Past the open threshold the pull resists, like iOS overscroll. */
function rubber(y: number) {
  'worklet'
  if (y <= PULL_MAX) return Math.max(0, y)
  return PULL_MAX + (y - PULL_MAX) * 0.25
}

export function CardFan({ heading, moods, focus, setFocus, onOpen }: Props) {
  const { width: winW, height: winH } = useWindowDimensions()
  const last = moods.length - 1

  /** Continuous fan position (card index as float), follows the finger */
  const scroll = useSharedValue(focus)
  const scrollAtStart = useSharedValue(focus)
  const axis = useSharedValue<'none' | 'x' | 'y'>('none')
  const pullY = useSharedValue(0)
  const armed = useSharedValue(0)
  const open = useSharedValue(0)
  const busy = useSharedValue(0)
  const dance = useSharedValue(0) // drives the tap / idle hint wiggle
  const bubble = useSharedValue(0)
  const settle = useSharedValue(1) // >1 while the card settles back after returning

  // Where the stage sits on screen, so the opening card can grow to cover it
  const stageRef = useRef<ComponentRef<typeof View>>(null)
  const stageWin = useSharedValue({ x: 0, y: 0 })
  const fanBox = useSharedValue({ x: 0, y: 0, w: 0, h: 0 })
  const from = useSharedValue({ x: 0, y: 0, w: CARD_W, h: CARD_H })

  const [openIndex, setOpenIndex] = useState(focus)
  const [isArmed, setIsArmed] = useState(false)
  const wasOpened = useRef(false)
  const resetTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const idleTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const hintsShown = useRef(0)

  const active = moods[Math.max(0, Math.min(last, focus))]
  const openMood = moods[openIndex] ?? active

  const measureStage = () => {
    stageRef.current?.measureInWindow((x, y) => {
      stageWin.value = { x, y }
    })
  }

  // --- hint: wiggle + "Pull me down" -------------------------------------------
  const playHint = useCallback(() => {
    if (busy.value > 0.5) return
    cancelAnimation(dance)
    dance.value = 0
    dance.value = withTiming(1, { duration: 900, easing: Easing.linear }, () => {
      dance.value = 0
    })
    bubble.value = withSequence(
      withTiming(1, { duration: 220, easing: IOS_EASE }),
      withDelay(1500, withTiming(0, { duration: 260 })),
    )
  }, [busy, dance, bubble])

  const clearIdle = () => {
    if (idleTimer.current) clearTimeout(idleTimer.current)
    idleTimer.current = null
  }
  const scheduleIdle = useCallback(() => {
    clearIdle()
    if (hintsShown.current >= 2) return
    idleTimer.current = setTimeout(() => {
      hintsShown.current += 1
      playHint()
    }, IDLE_HINT_MS)
  }, [playHint])

  // --- reset / focus handling ----------------------------------------------------
  const resetFan = useCallback(() => {
    cancelAnimation(pullY)
    cancelAnimation(open)
    cancelAnimation(scroll)
    pullY.value = 0
    open.value = 0
    armed.value = 0
    busy.value = 0
    axis.value = 'none'
    scroll.value = focus
    scrollAtStart.value = focus
    setIsArmed(false)
  }, [focus, pullY, open, scroll, armed, busy, axis, scrollAtStart])

  useFocusEffect(
    useCallback(() => {
      if (resetTimer.current) {
        clearTimeout(resetTimer.current)
        resetTimer.current = null
        resetFan()
      }
      if (wasOpened.current) {
        // Coming back: the card you opened settles into the fan
        wasOpened.current = false
        settle.value = 1.08
        settle.value = withSpring(1, { damping: 16, stiffness: 180 })
      }
      hintsShown.current = 0
      scheduleIdle()
      return () => {
        clearIdle()
        // Reset only once the next screen fully covers this one, so the user
        // never sees the expanded card snap back (or find it still big on return).
        resetTimer.current = setTimeout(() => {
          resetTimer.current = null
          resetFan()
        }, 450)
      }
    }, [resetFan, scheduleIdle, settle]),
  )

  useEffect(() => () => {
    clearIdle()
    if (resetTimer.current) clearTimeout(resetTimer.current)
  }, [])

  // --- JS callbacks from gestures ----------------------------------------------------
  const setFocusJS = (i: number) => setFocus(i)
  const touched = () => scheduleIdle()
  const tick = () => Haptics.selectionAsync().catch(() => {})
  const armedChanged = (on: boolean) => {
    setIsArmed(on)
    if (on) Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light).catch(() => {})
  }
  const finishOpen = (idx: number) => {
    wasOpened.current = true
    onOpen(moods[idx])
  }
  const beginOpen = (idx: number) => {
    setOpenIndex(idx)
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium).catch(() => {})
  }
  const tapAt = (relX: number) => {
    scheduleIdle()
    const base = Math.round(scroll.value)
    if (Math.abs(relX) <= CARD_W / 2) {
      tick()
      playHint()
      return
    }
    // Tapped a card peeking out on the side: bring it to the front, then hint
    const steps = Math.max(1, Math.ceil((Math.abs(relX) - CARD_W / 2) / SPREAD))
    const next = Math.max(0, Math.min(last, base + Math.sign(relX) * steps))
    if (next === base) return
    tick()
    scroll.value = withSpring(next, { damping: 20, stiffness: 220 })
    setFocus(next)
  }

  useAnimatedReaction(
    () => Math.round(scroll.value),
    (now, prev) => {
      if (prev !== null && now !== prev && axis.value === 'x') runOnJS(tick)()
    },
  )

  const startOpen = () => {
    'worklet'
    busy.value = 1
    const idx = Math.max(0, Math.min(last, Math.round(scroll.value)))
    const f = fanBox.value
    const s = 1.04
    from.value = {
      x: f.x + f.w / 2 - (CARD_W * s) / 2,
      y: f.y + f.h / 2 + LIFT + rubber(pullY.value) - (CARD_H * s) / 2,
      w: CARD_W * s,
      h: CARD_H * s,
    }
    runOnJS(beginOpen)(idx)
    open.value = withTiming(1, { duration: OPEN_MS, easing: IOS_EASE }, (done) => {
      if (done) runOnJS(finishOpen)(idx)
    })
  }

  // --- gestures ---------------------------------------------------------------
  const pan = Gesture.Pan()
    .activeOffsetX([-10, 10])
    .activeOffsetY([-10, 10])
    .onBegin(() => {
      if (busy.value > 0.5) return
      cancelAnimation(scroll)
      scrollAtStart.value = scroll.value
      axis.value = 'none'
      runOnJS(touched)()
    })
    .onUpdate((e) => {
      if (busy.value > 0.5) return
      if (axis.value === 'none') {
        if (Math.abs(e.translationX) < 10 && Math.abs(e.translationY) < 10) return
        axis.value = Math.abs(e.translationY) > Math.abs(e.translationX) ? 'y' : 'x'
      }
      if (axis.value === 'x') {
        const next = scrollAtStart.value - e.translationX / SWIPE_STEP
        // Soft edges instead of a hard stop at the first/last card
        scroll.value =
          next < 0 ? next * 0.3 : next > last ? last + (next - last) * 0.3 : next
        return
      }
      pullY.value = Math.max(0, e.translationY)
      const on = pullY.value >= PULL_OPEN ? 1 : 0
      if (on !== armed.value) {
        armed.value = on
        runOnJS(armedChanged)(on === 1)
      }
    })
    .onEnd((e) => {
      if (busy.value > 0.5) return
      if (axis.value === 'x') {
        // Flick momentum carries a little, then snaps to the nearest card
        const projected = scroll.value - e.velocityX / SWIPE_STEP / 6
        const next = Math.max(0, Math.min(last, Math.round(projected)))
        scroll.value = withSpring(next, { damping: 22, stiffness: 240, mass: 0.8 })
        runOnJS(setFocusJS)(next)
      } else if (axis.value === 'y' && pullY.value >= PULL_OPEN) {
        startOpen()
      } else {
        pullY.value = withSpring(0, { damping: 18, stiffness: 240 })
      }
      axis.value = 'none'
      if (armed.value) {
        armed.value = 0
        runOnJS(armedChanged)(false)
      }
    })

  const tap = Gesture.Tap()
    .maxDuration(260)
    .onEnd((e, ok) => {
      if (!ok || busy.value > 0.5) return
      runOnJS(tapAt)(e.x - fanBox.value.w / 2)
    })

  const gesture = Gesture.Race(pan, tap)

  // --- animated styles --------------------------------------------------------------
  const othersStyle = useAnimatedStyle(() => ({
    opacity: interpolate(open.value, [0, 0.5], [1, 0], Extrapolation.CLAMP),
    transform: [{ scale: interpolate(open.value, [0, 1], [1, 0.92]) }],
  }))

  const expanderStyle = useAnimatedStyle(() => {
    const p = open.value
    const f = from.value
    const w = stageWin.value
    return {
      opacity: p > 0 ? 1 : 0,
      left: interpolate(p, [0, 1], [f.x, -w.x]),
      top: interpolate(p, [0, 1], [f.y, -w.y]),
      width: interpolate(p, [0, 1], [f.w, winW]),
      height: interpolate(p, [0, 1], [f.h, winH]),
      borderRadius: interpolate(p, [0, 0.85, 1], [24, 36, 0]),
    }
  })

  const expanderTextStyle = useAnimatedStyle(() => ({
    opacity: interpolate(open.value, [0, 0.35], [1, 0], Extrapolation.CLAMP),
    transform: [{ translateY: interpolate(open.value, [0, 0.35], [0, -12], Extrapolation.CLAMP) }],
  }))

  const browseHintStyle = useAnimatedStyle(() => ({
    opacity: interpolate(pullY.value, [0, 60], [1, 0.25], Extrapolation.CLAMP) *
      interpolate(open.value, [0, 0.3], [1, 0], Extrapolation.CLAMP),
  }))
  const pullHintStyle = useAnimatedStyle(() => ({
    opacity: interpolate(open.value, [0, 0.3], [1, 0], Extrapolation.CLAMP),
    transform: [{ scale: interpolate(armed.value, [0, 1], [1, 1.04]) }],
  }))

  const bubbleStyle = useAnimatedStyle(() => ({
    opacity: bubble.value,
    transform: [
      { translateY: interpolate(bubble.value, [0, 1], [8, 0]) },
      { scale: interpolate(bubble.value, [0, 1], [0.92, 1]) },
    ],
  }))

  const isWeb = Platform.OS === 'web'
  const browseBy = (dir: number) => {
    const base = Math.round(scroll.value)
    const next = Math.max(0, Math.min(last, base + dir))
    if (next === base) return
    scroll.value = withSpring(next, { damping: 22, stiffness: 240 })
    setFocus(next)
  }

  return (
    <View
      ref={stageRef}
      style={styles.stage}
      onLayout={measureStage}
      collapsable={false}
    >
      {heading ? (
        <Animated.Text style={[styles.heading, browseHintStyle]} accessibilityRole="header">
          {heading}
        </Animated.Text>
      ) : null}
      <Animated.View style={[styles.browseHint, browseHintStyle]}>
        <Chevron dir={-1} />
        <Text style={styles.browseText}>Swipe to browse</Text>
        <Chevron dir={1} />
      </Animated.View>

      <GestureDetector gesture={gesture}>
        <View
          style={styles.fan}
          collapsable={false}
          onLayout={(e) => {
            const { x, y, width, height } = e.nativeEvent.layout
            fanBox.value = { x, y, w: width, h: height }
            measureStage()
          }}
          accessible
          accessibilityRole="adjustable"
          accessibilityLabel={`${shortLabel(active)}. Swipe to browse, pull down to open`}
          accessibilityActions={[
            { name: 'increment' },
            { name: 'decrement' },
            { name: 'activate' },
          ]}
          onAccessibilityAction={(e) => {
            if (e.nativeEvent.actionName === 'increment') browseBy(1)
            else if (e.nativeEvent.actionName === 'decrement') browseBy(-1)
            else onOpen(active)
          }}
        >
          <Animated.View style={[StyleSheet.absoluteFill, styles.center, othersStyle]} pointerEvents="none">
            {moods.map((mood, i) => (
              <FanCard
                key={mood.id}
                mood={mood}
                index={i}
                scroll={scroll}
                pullY={pullY}
                open={open}
                dance={dance}
                settle={settle}
              />
            ))}
          </Animated.View>
          <Animated.View pointerEvents="none" style={[styles.bubble, bubbleStyle]}>
            <Text style={styles.bubbleText}>Pull me down</Text>
            <Text style={styles.bubbleArrow}>↓</Text>
          </Animated.View>
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
          <Pressable
            style={styles.webOpen}
            onPress={() => {
              pullY.value = PULL_OPEN
              startOpen()
            }}
            accessibilityLabel="Open mood"
          >
            <Text style={styles.webOpenText}>Open {shortLabel(active)}</Text>
          </Pressable>
          <Pressable
            style={[styles.webBtn, focus >= last && styles.webBtnDisabled]}
            disabled={focus >= last}
            onPress={() => browseBy(1)}
            accessibilityLabel="Next mood"
          >
            <Text style={styles.webBtnText}>›</Text>
          </Pressable>
        </View>
      ) : (
        <Animated.View style={[styles.pullHint, isArmed && styles.pullHintArmed, pullHintStyle]}>
          {isArmed ? (
            <Text style={styles.pullText}>Release to open</Text>
          ) : (
            <>
              <BobArrow />
              <Text style={styles.pullText}>
                Pull <Text style={styles.pullStrong}>{shortLabel(active)}</Text> down to open
              </Text>
            </>
          )}
        </Animated.View>
      )}

      {/* The front card growing into the next screen. Last child so it covers everything. */}
      <Animated.View
        pointerEvents="none"
        style={[styles.expander, { backgroundColor: openMood.color }, expanderStyle]}
      >
        <View style={styles.whiteWash} />
        <Animated.View style={[styles.expanderLabel, expanderTextStyle]}>
          <Text style={styles.title} numberOfLines={1} adjustsFontSizeToFit minimumFontScale={0.6}>
            {shortLabel(openMood)}
          </Text>
          <Text style={styles.sub}>{openMood.short}</Text>
        </Animated.View>
      </Animated.View>
    </View>
  )
}

function Chevron({ dir }: { dir: 1 | -1 }) {
  const t = useSharedValue(0)
  useEffect(() => {
    t.value = withRepeat(withTiming(1, { duration: 900, easing: Easing.inOut(Easing.sin) }), -1, true)
  }, [t])
  const style = useAnimatedStyle(() => ({
    transform: [{ translateX: dir * t.value * 3 }],
    opacity: 0.55 + t.value * 0.45,
  }))
  return <Animated.Text style={[styles.chevron, style]}>{dir < 0 ? '‹' : '›'}</Animated.Text>
}

function BobArrow() {
  const t = useSharedValue(0)
  useEffect(() => {
    t.value = withRepeat(withTiming(1, { duration: 800, easing: Easing.inOut(Easing.sin) }), -1, true)
  }, [t])
  const style = useAnimatedStyle(() => ({ transform: [{ translateY: t.value * 3 }] }))
  return <Animated.Text style={[styles.pullArrow, style]}>↓</Animated.Text>
}

function FanCard({
  mood,
  index,
  scroll,
  pullY,
  open,
  dance,
  settle,
}: {
  mood: Mood
  index: number
  scroll: SharedValue<number>
  pullY: SharedValue<number>
  open: SharedValue<number>
  dance: SharedValue<number>
  settle: SharedValue<number>
}) {
  const style = useAnimatedStyle(() => {
    const offset = index - scroll.value
    const dist = Math.abs(offset)
    const front = interpolate(dist, [0, 0.5], [1, 0], Extrapolation.CLAMP)
    const pull = rubber(pullY.value) * front
    const p = Math.min(1, pullY.value / PULL_OPEN) * front
    const d = dance.value * front
    // Hint: a quick tug downward plus a small wiggle, like the card asks to be pulled
    const tug = interpolate(d, [0, 0.2, 0.45, 0.7, 1], [0, 26, -6, 4, 0])
    const wiggle = interpolate(d, [0, 0.15, 0.3, 0.45, 0.6, 1], [0, -3, 3, -2, 1.5, 0])

    const x = offset * SPREAD
    const y = interpolate(dist, [0, 1], [LIFT, 10], Extrapolation.CLAMP) + pull + tug
    const rot = offset * 8 * (1 - front) + p * 1.5 + wiggle
    const scale =
      interpolate(dist, [0, 1, 2.5], [1, 0.86, 0.8], Extrapolation.CLAMP) * (1 + p * 0.04) *
      (front > 0.5 ? settle.value : 1)

    return {
      transform: [{ translateX: x }, { translateY: y }, { rotate: `${rot}deg` }, { scale }],
      zIndex: Math.round(100 - dist * 10),
      // The expander takes over the front card while opening
      opacity:
        interpolate(dist, [0, 2, 3.2], [1, 0.75, 0], Extrapolation.CLAMP) *
        (open.value > 0 && front > 0.5 ? 0 : 1),
    }
  })

  // Titles on cards behind the front one overlap into noise, so fade them out
  const textStyle = useAnimatedStyle(() => ({
    opacity: interpolate(Math.abs(index - scroll.value), [0, 0.6, 1.2], [1, 0.25, 0], Extrapolation.CLAMP),
  }))

  const cueStyle = useAnimatedStyle(() => {
    const front = Math.abs(index - scroll.value) < 0.5
    const p = Math.min(1, pullY.value / PULL_OPEN)
    return { opacity: front ? 0.45 + p * 0.55 : 0 }
  })

  return (
    <Animated.View style={[styles.card, { backgroundColor: mood.color }, style]}>
      <View style={styles.whiteWash} />
      <Animated.Text style={[styles.cue, cueStyle]}>Pull down ↓</Animated.Text>
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
    gap: 18,
    paddingBottom: 24,
  },
  fan: {
    width: '100%',
    height: CARD_H + 110,
  },
  center: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  card: {
    position: 'absolute',
    width: CARD_W,
    height: CARD_H,
    borderRadius: 26,
    paddingHorizontal: 18,
    paddingVertical: 20,
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
    backgroundColor: `rgba(255,255,255,${WASH})`,
  },
  cue: {
    position: 'absolute',
    top: 18,
    left: 18,
    fontSize: 11,
    fontFamily: fonts.bodyExtra,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: colors.ink,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 26,
    color: colors.ink,
  },
  sub: {
    fontFamily: fonts.bodyBold,
    fontSize: 14,
    color: colors.inkSoft,
    marginTop: 2,
    opacity: 0.75,
  },
  heading: {
    fontFamily: fonts.display,
    fontSize: 27,
    lineHeight: 33,
    color: colors.ink,
    textAlign: 'center',
    marginBottom: -4,
  },
  browseHint: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.8)',
  },
  browseText: {
    fontFamily: fonts.bodyExtra,
    fontSize: 15,
    color: colors.ink,
  },
  chevron: {
    fontFamily: fonts.bodyExtra,
    fontSize: 22,
    lineHeight: 24,
    color: colors.ink,
  },
  pullHint: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 999,
    backgroundColor: colors.ink,
    shadowColor: '#243044',
    shadowOpacity: 0.18,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 3,
  },
  pullHintArmed: {
    backgroundColor: colors.accent,
  },
  pullArrow: {
    fontFamily: fonts.bodyExtra,
    fontSize: 17,
    color: colors.white,
  },
  pullText: {
    fontFamily: fonts.bodyBold,
    fontSize: 15,
    color: 'rgba(255,255,255,0.88)',
  },
  pullStrong: {
    fontFamily: fonts.bodyExtra,
    color: colors.white,
  },
  bubble: {
    position: 'absolute',
    alignSelf: 'center',
    top: 0,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: colors.ink,
    zIndex: 200,
    elevation: 12,
  },
  bubbleText: {
    fontFamily: fonts.bodyExtra,
    fontSize: 14,
    color: colors.white,
  },
  bubbleArrow: {
    fontFamily: fonts.bodyExtra,
    fontSize: 14,
    color: colors.white,
  },
  expander: {
    position: 'absolute',
    overflow: 'hidden',
    justifyContent: 'flex-end',
    paddingHorizontal: 18,
    paddingVertical: 20,
    zIndex: 1000,
    elevation: 30,
  },
  expanderLabel: {
    position: 'absolute',
    left: 18,
    bottom: 20,
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
