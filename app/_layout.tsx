import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#FFF0F2',
          },
          headerTintColor: '#C72C48',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          contentStyle: {
            backgroundColor: '#FFFBFB',
          },
        }}
      >
        <Stack.Screen 
          name="index" 
          options={{ 
            headerShown: false, 
            title: "おかえりなさい！" 
          }} 
        />
        <Stack.Screen 
          name="register" 
          options={{ 
            title: "👋 はじめてのペット登録",
            headerBackVisible: false 
          }} 
        />
        <Stack.Screen 
          name="login" 
          options={{ 
            title: "🔑 ログイン",
            headerBackVisible: false 
          }} 
        />
        <Stack.Screen 
          name="album" 
          options={{ 
            title: "🐾 うちのコ日常アルバム",
            headerBackVisible: false
          }} 
        />
      </Stack>
    </SafeAreaProvider>
  );
}
