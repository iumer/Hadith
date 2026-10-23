import { Pressable, StyleSheet, Text } from 'react-native'
import { colors, fonts } from '../theme'

export function BackButton({ onPress }: { onPress: () => void }) {
  return (
    <Pressable onPress={onPress} style={styles.btn} hitSlop={12} accessibilityLabel="Go back">
      <Text style={styles.chev}>‹</Text>
    </Pressable>
  )
}

const styles = StyleSheet.create({
  btn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.78)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  chev: {
    fontSize: 28,
    lineHeight: 30,
    color: colors.ink,
    fontFamily: fonts.bodyBold,
    marginTop: -2,
  },
})
