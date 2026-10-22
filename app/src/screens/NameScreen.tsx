import { useState } from 'react'
import {
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
} from 'react-native'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { Ambient } from '../components/Ambient'
import { saveName } from '../storage'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Name'>

// Only shown on first launch (App skips it once a name is saved), or when the
// user long-presses their name on the greeting to change it.
export function NameScreen({ navigation, route }: Props) {
  const [name, setName] = useState(route.params?.current ?? '')

  const submit = () => {
    const trimmed = name.trim()
    if (!trimmed) return
    saveName(trimmed)
    navigation.replace('Feeling', { name: trimmed })
  }

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <Ambient />
      <ScrollView contentContainerStyle={styles.inner} keyboardShouldPersistTaps="handled">
        <Image source={require('../../assets/logo.png')} style={styles.logo} accessibilityLabel="Sakinah" />
        <Text style={styles.eyebrow}>Welcome to Sakinah</Text>
        <Text style={styles.title}>What should we call you?</Text>
        <Text style={styles.lede}>A quiet space for the heart.</Text>
        <Text style={styles.label}>Your name</Text>
        <TextInput
          style={styles.input}
          value={name}
          onChangeText={setName}
          autoFocus
          placeholder="Type your name"
          placeholderTextColor={colors.mist}
          returnKeyType="done"
          onSubmitEditing={submit}
        />
        <Pressable
          style={[styles.btn, !name.trim() && { opacity: 0.4 }]}
          disabled={!name.trim()}
          onPress={submit}
        >
          <Text style={styles.btnText}>Continue</Text>
        </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  logo: {
    width: 96,
    height: 96,
    marginLeft: -14,
    marginBottom: 4,
  },
  root: {
    flex: 1,
    backgroundColor: colors.cream,
  },
  inner: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 72,
    gap: 10,
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
    fontSize: 34,
    lineHeight: 40,
    color: colors.ink,
  },
  lede: {
    fontFamily: fonts.body,
    fontSize: 16,
    color: colors.mist,
    marginBottom: 18,
  },
  label: {
    fontFamily: fonts.bodyBold,
    fontSize: 13,
    color: colors.inkSoft,
  },
  input: {
    backgroundColor: 'rgba(255,255,255,0.88)',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontFamily: fonts.body,
    fontSize: 18,
    color: colors.ink,
  },
  btn: {
    marginTop: 12,
    backgroundColor: colors.ink,
    borderRadius: 999,
    paddingVertical: 14,
    alignItems: 'center',
  },
  btnText: {
    fontFamily: fonts.bodyBold,
    color: colors.white,
    fontSize: 16,
  },
})
