import { useState } from 'react'
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native'
import type { NativeStackScreenProps } from '@react-navigation/native-stack'
import { Ambient } from '../components/Ambient'
import type { RootStackParamList } from '../types'
import { colors, fonts } from '../theme'

type Props = NativeStackScreenProps<RootStackParamList, 'Name'>

export function NameScreen({ navigation }: Props) {
  const [name, setName] = useState('')

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <Ambient />
      <View style={styles.inner}>
        <Text style={styles.eyebrow}>Welcome</Text>
        <Text style={styles.title}>What should we call you?</Text>
        <Text style={styles.lede}>A quiet space for the heart.</Text>
        <Text style={styles.label}>Your name</Text>
        <TextInput
          style={styles.input}
          value={name}
          onChangeText={setName}
          autoFocus
          placeholder="Asif"
          placeholderTextColor={colors.mist}
          returnKeyType="done"
          onSubmitEditing={() => {
            if (name.trim()) navigation.replace('Feeling', { name: name.trim() })
          }}
        />
        <Pressable
          style={[styles.btn, !name.trim() && { opacity: 0.4 }]}
          disabled={!name.trim()}
          onPress={() => navigation.replace('Feeling', { name: name.trim() })}
        >
          <Text style={styles.btnText}>Continue</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.cream,
  },
  inner: {
    flex: 1,
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
