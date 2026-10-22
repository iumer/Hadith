import { StyleSheet, View } from 'react-native'
import { colors } from '../theme'

export function Ambient() {
  return (
    <View pointerEvents="none" style={StyleSheet.absoluteFill}>
      <View style={[styles.glow, styles.glowA]} />
      <View style={[styles.glow, styles.glowB]} />
    </View>
  )
}

const styles = StyleSheet.create({
  glow: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.55,
  },
  glowA: {
    width: 280,
    height: 280,
    top: -60,
    left: -40,
    backgroundColor: colors.sky,
  },
  glowB: {
    width: 260,
    height: 260,
    bottom: 40,
    right: -50,
    backgroundColor: colors.peach,
  },
})
