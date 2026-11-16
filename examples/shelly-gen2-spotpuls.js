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
  let secPastHour = Math.floor(Date.now() / 1000) % 3600;
  let msToNextHour = (3600 - secPastHour) * 1000 + 5000; // +5s after :00
  Timer.set(msToNextHour, false, function () {
    updateRelay();
    Timer.set(60 * 60 * 1000, true, updateRelay);
  });
}

updateRelay();
scheduleTopOfHour();
