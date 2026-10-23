import AsyncStorage from '@react-native-async-storage/async-storage'

const NAME_KEY = 'hadith.name.v1'

export async function loadName(): Promise<string | null> {
  try {
    return await AsyncStorage.getItem(NAME_KEY)
  } catch {
    return null
  }
}

export function saveName(name: string) {
  AsyncStorage.setItem(NAME_KEY, name).catch(() => {})
}
