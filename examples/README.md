# Spotpuls Smart-Home & Automation Examples (40 European Bidding Zones)

Ready-to-use, copy-paste examples for **Spotpuls** (`https://spotpuls.app`) — free, zero-API-key, CORS-enabled day-ahead electricity spot prices & 7-day regional forecasts.

- **Interactive Docs:** https://spotpuls.app/api-docs/
- **AI / LLM Spec:** https://spotpuls.app/llms.txt
- **OpenAPI 3.1:** https://spotpuls.app/openapi.json

## Included Examples

1. [`shelly-gen2-spotpuls.js`](shelly-gen2-spotpuls.js) — Shelly Gen2 / Gen3 script polling `/api/v1/shelly/FI.json` (ultra-compact `< 500 B` JSON) at the top of every hour (`:00:05`) to switch a boiler / EV relay during the cheapest contiguous 3-hour window.
2. [`home-assistant-configuration.yaml`](home-assistant-configuration.yaml) — Native Home Assistant REST sensor + binary sensors using `/api/v1/ha/FI.json` refreshed at the top of every hour (`minutes: 0, seconds: 5`).
3. [`esphome-spotpuls.yaml`](esphome-spotpuls.yaml) — ESPHome / ESP32 relay controller polling `/api/v1/plain/FI?field=run_now` (`1` or `0`) at the top of every hour (`on_time`).
4. [`evcc-custom-tariff.yaml`](evcc-custom-tariff.yaml) — Open-source `evcc.io` EV / solar charger tariff integration using `/api/v1/evcc/DE-LU.json` (or `FI`, `SE3`, `NO1`, etc.).
5. [`python_spot_controller.py`](python_spot_controller.py) — Python 3 script reading `/api/v1/prices?zone=FI&vat=1&window=3` with current price, 7-day forecast, and optimal load-shifting window.
6. [`ios-scriptable-widget.js`](ios-scriptable-widget.js) — iPhone / iOS Home Screen Widget (Scriptable) displaying both the Current Hour and Next Hour spot electricity prices + 24h min/max.
7. [`../android-app/`](../android-app/README.md) — Native Android app + home-screen `AppWidgetProvider` showing Current Hour and Next Hour spot prices.
