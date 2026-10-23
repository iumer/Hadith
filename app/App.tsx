import { useCallback, useEffect, useState } from 'react'
import { ActivityIndicator, StyleSheet, View } from 'react-native'
import { StatusBar } from 'expo-status-bar'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'
import { GestureHandlerRootView } from 'react-native-gesture-handler'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { useFonts, Fraunces_600SemiBold, Fraunces_700Bold } from '@expo-google-fonts/fraunces'
import {
  Nunito_600SemiBold,
  Nunito_700Bold,
  Nunito_800ExtraBold,
} from '@expo-google-fonts/nunito'
import { Amiri_400Regular } from '@expo-google-fonts/amiri'
import { AmiriQuran_400Regular } from '@expo-google-fonts/amiri-quran'
import { NotoNastaliqUrdu_400Regular } from '@expo-google-fonts/noto-nastaliq-urdu'
import * as SplashScreen from 'expo-splash-screen'
import { NameScreen } from './src/screens/NameScreen'
import { FeelingScreen } from './src/screens/FeelingScreen'
import { SubsScreen } from './src/screens/SubsScreen'
import { ThreadsScreen } from './src/screens/ThreadsScreen'
import { ReadScreen } from './src/screens/ReadScreen'
import type { RootStackParamList } from './src/types'
import { colors } from './src/theme'
import { loadName } from './src/storage'

SplashScreen.preventAutoHideAsync().catch(() => {})

const Stack = createNativeStackNavigator<RootStackParamList>()

export default function App() {
  const [loaded] = useFonts({
    Fraunces_600SemiBold,
    Fraunces_700Bold,
    Nunito_600SemiBold,
    Nunito_700Bold,
    Nunito_800ExtraBold,
    Amiri_400Regular,
    AmiriQuran_400Regular,
    NotoNastaliqUrdu_400Regular,
  })
  // undefined = still reading storage; null = first launch (ask for a name once)
  const [savedName, setSavedName] = useState<string | null | undefined>(undefined)

  useEffect(() => {
    loadName().then(setSavedName)
  }, [])

  const ready = loaded && savedName !== undefined

  const onLayout = useCallback(() => {
    if (ready) SplashScreen.hideAsync().catch(() => {})
  }, [ready])

  if (!ready) {
    return (
      <View style={styles.boot}>
        <ActivityIndicator color={colors.ink} />
      </View>
    )
  }

  return (
    <GestureHandlerRootView style={styles.root} onLayout={onLayout}>
      <SafeAreaProvider>
        <NavigationContainer>
          <StatusBar style="dark" />
          <Stack.Navigator
            initialRouteName={savedName ? 'Feeling' : 'Name'}
            screenOptions={{
              headerShown: false,
              // Platform push/pop (iOS keeps its edge swipe-back)
              animation: 'default',
              contentStyle: { backgroundColor: colors.cream },
            }}
          >
            <Stack.Screen name="Name" component={NameScreen} options={{ animation: 'fade' }} />
            <Stack.Screen
              name="Feeling"
              component={FeelingScreen}
              initialParams={savedName ? { name: savedName } : undefined}
              options={{ animation: 'fade' }}
            />
            {/* The opened card already filled the screen in its colour; Subs fades in on top */}
            <Stack.Screen
              name="Subs"
              component={SubsScreen}
              options={{ animation: 'fade', animationDuration: 200 }}
            />
            <Stack.Screen name="Threads" component={ThreadsScreen} />
            <Stack.Screen name="Read" component={ReadScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  )
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  boot: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.cream,
  },
})
