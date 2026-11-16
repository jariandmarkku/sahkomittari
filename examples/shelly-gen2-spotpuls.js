// Spotpuls Shelly Gen2/Gen3 Smart Relay Controller
// Uses ultra-compact Spotpuls IoT endpoint (< 500 bytes): https://spotpuls.app/api/v1/shelly/FI.json
// Runs once at boot and then right at the top of every hour (:00:05).

let ZONE = "FI";
let WINDOW_HOURS = 3;
let RELAY_ID = 0;
let API_URL = "https://spotpuls.app/api/v1/shelly/" + ZONE + ".json?vat=1&window=" + WINDOW_HOURS;

function updateRelay() {
  Shelly.call("HTTP.GET", { url: API_URL, timeout: 10 }, function (res, errCode, errMsg) {
    if (errCode !== 0 || !res || res.code !== 200) {
      print("Spotpuls HTTP error:", errCode, errMsg);
      return;
    }
    let data = JSON.parse(res.body);
    let turnOn = data.runContig === 1;
    print("Spotpuls", data.z, "now:", data.now, data.u, "| runContig:", data.runContig);
    Shelly.call("Switch.Set", { id: RELAY_ID, on: turnOn });
  });
}

function scheduleTopOfHour() {
  let nowSec = Math.floor(Date.now() / 1000);
  let jitterMs = 5000 + Math.floor(Math.random() * 20000); // 5–25s after :00 to avoid spikes
  let msToNextHour = nowSec > 1700000000
    ? (3600 - (nowSec % 3600)) * 1000 + jitterMs
    : 60 * 1000; // retry in 60s if NTP clock not synced yet
  Timer.set(msToNextHour, false, function () {
    if (Math.floor(Date.now() / 1000) <= 1700000000) {
      scheduleTopOfHour();
      return;
    }
    updateRelay();
    Timer.set(60 * 60 * 1000, true, updateRelay);
  });
}

updateRelay();
scheduleTopOfHour();
