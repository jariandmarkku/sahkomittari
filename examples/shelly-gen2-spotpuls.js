// Spotpuls Shelly Gen2/Gen3 Smart Relay Controller
// Uses ultra-compact Spotpuls IoT endpoint (< 500 bytes): https://spotpuls.app/api/v1/shelly/FI.json
// Change ZONE (e.g. "FI", "SE3", "NO1", "DK2", "DE-LU") and WINDOW_HOURS (1..24) as needed.

let ZONE = "FI";
let WINDOW_HOURS = 3;
let RELAY_ID = 0;
let POLL_MS = 60 * 60 * 1000; // 1 hour (spot prices only change once per hour)
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

updateRelay();
Timer.set(POLL_MS, true, updateRelay);
