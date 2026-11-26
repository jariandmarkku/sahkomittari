package app.spotpuls

import android.app.AlarmManager
import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.widget.RemoteViews
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale
import java.util.concurrent.Executors

class SpotpulsWidgetProvider : AppWidgetProvider() {

    companion object {
        const val ACTION_REFRESH = "app.spotpuls.ACTION_REFRESH_WIDGET"
        private const val API_URL = "https://spotpuls.app/api/v1/shelly/FI.json?vat=1"
        private val executor = Executors.newSingleThreadExecutor()

        private fun levelColor(level: String): Int = when (level) {
            "cheap" -> Color.parseColor("#2ECC71")
            "high" -> Color.parseColor("#FF5722")
            else -> Color.parseColor("#6EA8FE")
        }

        private fun fmtPrice(obj: JSONObject, key: String): String {
            if (!obj.has(key) || obj.isNull(key)) return "—"
            return String.format(Locale.GERMAN, "%.2f", obj.getDouble(key))
        }

        private fun padHour(obj: JSONObject, key: String): String {
            if (!obj.has(key) || obj.isNull(key)) return "--:00"
            return String.format(Locale.US, "%02d:00", obj.getInt(key))
        }

        fun scheduleNextHourUpdate(context: Context) {
            val am = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
            val intent = Intent(context, SpotpulsWidgetProvider::class.java).apply {
                action = ACTION_REFRESH
            }
            val pi = PendingIntent.getBroadcast(
                context,
                1001,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            val nowMs = System.currentTimeMillis()
            val nextHourMs = ((nowMs / 3_600_000L) + 1L) * 3_600_000L + 10_000L
            am.set(AlarmManager.RTC, nextHourMs, pi)
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        if (intent.action == ACTION_REFRESH) {
            val mgr = AppWidgetManager.getInstance(context)
            val ids = mgr.getAppWidgetIds(ComponentName(context, SpotpulsWidgetProvider::class.java))
            if (ids.isNotEmpty()) {
                onUpdate(context, mgr, ids)
            }
        }
    }

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        val pendingResult = goAsync()
        executor.execute {
            try {
                val conn = (URL(API_URL).openConnection() as HttpURLConnection).apply {
                    connectTimeout = 8000
                    readTimeout = 8000
                    requestMethod = "GET"
                }
                val body = conn.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
                conn.disconnect()
                val json = JSONObject(body)

                val zone = json.optString("z", "FI")
                val unit = json.optString("u", "snt/kWh")
                val curHourLbl = "NYT ${padHour(json, "curHr")}"
                val nextHourLbl = "SEUR. ${padHour(json, "nextHr")}"
                val curVal = fmtPrice(json, "now")
                val nextVal = fmtPrice(json, "next")
                val curCol = levelColor(json.optString("lvl", "normal"))
                val nextCol = levelColor(json.optString("nextLvl", "normal"))
                val min24 = fmtPrice(json, "min24")
                val max24 = fmtPrice(json, "max24")

                val openAppIntent = PendingIntent.getActivity(
                    context,
                    0,
                    Intent(context, MainActivity::class.java),
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                val refreshIntent = PendingIntent.getBroadcast(
                    context,
                    1,
                    Intent(context, SpotpulsWidgetProvider::class.java).apply { action = ACTION_REFRESH },
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )

                for (id in appWidgetIds) {
                    val rv = RemoteViews(context.packageName, R.layout.widget_spotpuls)
                    rv.setTextViewText(R.id.w_header, "SPOTPULS · $zone")
                    rv.setTextViewText(R.id.w_range, "$min24–$max24 $unit")
                    rv.setTextViewText(R.id.w_now_label, curHourLbl)
                    rv.setTextViewText(R.id.w_now_price, curVal)
                    rv.setTextColor(R.id.w_now_price, curCol)
                    rv.setTextViewText(R.id.w_now_unit, unit)
                    rv.setTextViewText(R.id.w_next_label, nextHourLbl)
                    rv.setTextViewText(R.id.w_next_price, nextVal)
                    rv.setTextColor(R.id.w_next_price, nextCol)
                    rv.setTextViewText(R.id.w_next_unit, unit)
                    rv.setOnClickPendingIntent(R.id.w_root, openAppIntent)
                    rv.setOnClickPendingIntent(R.id.w_header, refreshIntent)
                    appWidgetManager.updateAppWidget(id, rv)
                }
                scheduleNextHourUpdate(context)
            } catch (_: Exception) {
                for (id in appWidgetIds) {
                    val rv = RemoteViews(context.packageName, R.layout.widget_spotpuls)
                    rv.setTextViewText(R.id.w_range, "Offline — napauta päivittääksesi")
                    appWidgetManager.updateAppWidget(id, rv)
                }
            } finally {
                pendingResult.finish()
            }
        }
    }
}
