import { useState } from 'react'
import { Image, StyleSheet, Text, View } from 'react-native'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ambient } from '../components/Ambient'
import { CardFan } from '../components/CardFan'
import { catalog } from '../content'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Feeling'>

export function FeelingScreen({ navigation, route }: Props) {
  const insets = useSafeAreaInsets()
  const [focus, setFocus] = useState(2)
  const { name } = route.params

  return (
    <View style={[styles.root, { paddingTop: insets.top + 24 }]}>
      <Ambient />
      <View style={styles.brandRow}>
        <Image source={require('../../assets/logo.png')} style={styles.logo} accessibilityLabel="Sakinah" />
        <Text style={styles.eyebrow}>Salaam</Text>
      </View>
      <Text
        style={styles.title}
        onLongPress={() => navigation.replace('Name', { current: name })}
        accessibilityHint="Long press to change your name"
      >
        Assalamoalikum {name}
      </Text>
      <CardFan
        heading="How are you feeling today?"
        moods={catalog.moods}
        focus={focus}
        setFocus={setFocus}
        onOpen={(mood) =>
          navigation.navigate('Subs', { name, moodId: mood.id })
        }
      />
    </View>
  )
}

const styles = StyleSheet.create({
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginLeft: -8,
  },
  logo: {
    width: 40,
    height: 40,
  },
  root: {
    flex: 1,
    backgroundColor: colors.cream,
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  eyebrow: {
    fontFamily: fonts.bodyExtra,
    fontSize: 12,
    letterSpacing: 1.2,
    textTransform: 'uppercase',
    color: colors.mist,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 30,
    lineHeight: 36,
    color: colors.ink,
    marginTop: 4,
  },
})
