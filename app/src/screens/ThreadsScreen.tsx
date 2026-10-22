import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ambient } from '../components/Ambient'
import { BackButton } from '../components/BackButton'
import { getSub } from '../content'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Threads'>

export function ThreadsScreen({ navigation, route }: Props) {
  const insets = useSafeAreaInsets()
  const { sub } = getSub(route.params.moodId, route.params.subId)

  return (
    <View style={[styles.root, { paddingTop: insets.top + 8 }]}>
      <Ambient />
      <View style={styles.top}>
        <BackButton onPress={() => navigation.goBack()} />
        <Text style={styles.eyebrow}>{sub.label}</Text>
      </View>
      <Text style={styles.title}>{sub.label}</Text>
      <Text style={styles.lede}>Threads · open a reference to read</Text>
      <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
        {sub.items.map((item, i) => (
          <Pressable
            key={item.id}
            style={styles.row}
            onPress={() =>
              navigation.navigate('Read', {
                name: route.params.name,
                moodId: route.params.moodId,
                subId: route.params.subId,
                index: i,
              })
            }
          >
            <View style={[styles.badge, item.kind === 'quran' ? styles.quran : styles.hadith]}>
              <Text style={styles.badgeText}>{item.kind === 'quran' ? 'Quran' : 'Hadith'}</Text>
            </View>
            <Text style={styles.ref}>{item.title}</Text>
            <Text style={styles.chev}>›</Text>
          </Pressable>
        ))}
      </ScrollView>
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
    gap: 12,
    marginBottom: 8,
  },
  eyebrow: {
    fontFamily: fonts.bodyExtra,
    fontSize: 12,
    letterSpacing: 1,
    textTransform: 'uppercase',
    color: colors.mist,
  },
  title: {
    fontFamily: fonts.display,
    fontSize: 28,
    color: colors.ink,
  },
  lede: {
    fontFamily: fonts.body,
    fontSize: 15,
    color: colors.mist,
    marginTop: 4,
    marginBottom: 14,
  },
  list: {
    gap: 8,
    paddingBottom: 28,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.78)',
  },
  badge: {
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
  ref: {
    flex: 1,
    fontFamily: fonts.bodyBold,
    fontSize: 15,
    color: colors.ink,
  },
  chev: {
    fontSize: 20,
    color: colors.mist,
  },
})
