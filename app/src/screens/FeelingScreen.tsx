import { useState } from 'react'
import { StyleSheet, Text, View } from 'react-native'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ambient } from '../components/Ambient'
import { BackButton } from '../components/BackButton'
import { CardFan } from '../components/CardFan'
import { catalog } from '../content'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Feeling'>

export function FeelingScreen({ navigation, route }: Props) {
  const insets = useSafeAreaInsets()
  const [focus, setFocus] = useState(2)

  return (
    <View style={[styles.root, { paddingTop: insets.top + 8 }]}>
      <Ambient />
      <View style={styles.top}>
        <BackButton onPress={() => navigation.replace('Name')} />
      </View>
      <Text style={styles.eyebrow}>Salaam</Text>
      <Text style={styles.title}>Assalamoalikum {route.params.name}</Text>
      <Text style={styles.lede}>How are you feeling today?</Text>
      <CardFan
        moods={catalog.moods}
        focus={focus}
        setFocus={setFocus}
        onOpen={(mood) =>
          navigation.navigate('Subs', { name: route.params.name, moodId: mood.id })
        }
      />
    </View>
  )
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.cream,
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  top: {
    marginBottom: 8,
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
  lede: {
    fontFamily: fonts.body,
    fontSize: 15,
    color: colors.mist,
    marginTop: 6,
    marginBottom: 8,
  },
})
