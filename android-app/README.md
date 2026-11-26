# Spotpuls Android App & Home Screen Widget

Native Android Kotlin application + `AppWidgetProvider` home-screen widget displaying:
- Full **Spotpuls** mobile dashboard (`https://spotpuls.app`) via `MainActivity`
- Home screen widget (**SpotpulsWidgetProvider**) showing **Current Hour (`NYT HH:00`)** and **Next Hour (`SEUR. HH:00`)** spot electricity prices, color-coded price tiers, price delta, and 24h min/max directly on the Android home screen, automatically aligned to top-of-hour refreshes via `AlarmManager` + 30-minute `updatePeriodMillis`.

## Build & Install APK
1. Open `android-app/` in **Android Studio** (or run from CLI with Android SDK installed):
   ```bash
   ./gradlew assembleDebug
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```
2. Long-press your Android home screen → **Widgets** → **Spotpuls** → drag to home screen.
