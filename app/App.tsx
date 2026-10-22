import { useCallback } from 'react'
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
import * as SplashScreen from 'expo-splash-screen'
import { NameScreen } from './src/screens/NameScreen'
import { FeelingScreen } from './src/screens/FeelingScreen'
import { SubsScreen } from './src/screens/SubsScreen'
import { ThreadsScreen } from './src/screens/ThreadsScreen'
import { ReadScreen } from './src/screens/ReadScreen'
import type { RootStackParamList } from './src/types'
import { colors } from './src/theme'

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
  })

  const onLayout = useCallback(() => {
    if (loaded) SplashScreen.hideAsync().catch(() => {})
  }, [loaded])

  if (!loaded) {
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
            initialRouteName="Name"
            screenOptions={{
              headerShown: false,
              animation: 'fade_from_bottom',
              contentStyle: { backgroundColor: colors.cream },
            }}
          >
            <Stack.Screen name="Name" component={NameScreen} />
            <Stack.Screen name="Feeling" component={FeelingScreen} />
            <Stack.Screen name="Subs" component={SubsScreen} />
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
