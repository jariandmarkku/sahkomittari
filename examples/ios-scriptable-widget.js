// Spotpuls iPhone / iOS Home Screen Widget (Scriptable)
// Shows BOTH Current Hour (NYT) and Next Hour (SEURAAVA) spot electricity prices + 24h Min/Max.
// Install free "Scriptable" app from App Store, paste this script, set Widget Parameter (optional) e.g. FI, SE3, DE-LU.

const ZONE = (args.widgetParameter || "FI").trim() || "FI";
const API_URL = `https://spotpuls.app/api/v1/shelly/${encodeURIComponent(ZONE)}.json?vat=1`;

async function createWidget() {
  const w = new ListWidget();
  w.backgroundColor = new Color("#111210");
  w.setPadding(12, 14, 12, 14);
  w.url = `https://spotpuls.app/?zone=${encodeURIComponent(ZONE)}`;

  try {
    const req = new Request(API_URL);
    req.timeoutInterval = 10;
    const d = await req.loadJSON();

    const lvlColor = (l) => (l === "cheap" ? new Color("#2ecc71") : l === "high" ? new Color("#ff5722") : new Color("#6ea8fe"));
    const fmt = (v) => (v === null || v === undefined ? "—" : Number(v).toFixed(2).replace(".", ","));
    const pad2 = (n) => (n === null || n === undefined ? "--" : String(n).padStart(2, "0"));

    const hdr = w.addStack();
    const title = hdr.addText(`SPOTPULS · ${d.z || ZONE}`);
    title.font = Font.boldMonospacedSystemFont(11);
    title.textColor = new Color("#ffd000");
    hdr.addSpacer();
    const minmax = hdr.addText(`${fmt(d.min24)}–${fmt(d.max24)}`);
    minmax.font = Font.monospacedSystemFont(10);
    minmax.textColor = new Color("#a5a89e");

    w.addSpacer(8);

    const row = w.addStack();
    row.layoutHorizontally();

    const left = row.addStack();
    left.layoutVertically();
    const l1 = left.addText(`NYT ${pad2(d.curHr)}:00`);
    l1.font = Font.boldMonospacedSystemFont(10);
    l1.textColor = new Color("#a5a89e");
    const v1 = left.addText(`${fmt(d.now)}`);
    v1.font = Font.boldMonospacedSystemFont(22);
    v1.textColor = lvlColor(d.lvl);
    const u1 = left.addText(d.u || "snt/kWh");
    u1.font = Font.monospacedSystemFont(9);
    u1.textColor = new Color("#a5a89e");

    row.addSpacer();

    const right = row.addStack();
    right.layoutVertically();
    const l2 = right.addText(`SEUR. ${pad2(d.nextHr)}:00`);
    l2.font = Font.boldMonospacedSystemFont(10);
    l2.textColor = new Color("#a5a89e");
    const v2 = right.addText(`${fmt(d.next)}`);
    v2.font = Font.boldMonospacedSystemFont(22);
    v2.textColor = lvlColor(d.nextLvl);
    const delta = d.now !== null && d.next !== null ? Number(d.next - d.now) : null;
    const dStr = delta === null ? (d.u || "snt/kWh") : `${delta > 0 ? "+" : ""}${delta.toFixed(2).replace(".", ",")} ${d.u || ""}`;
    const u2 = right.addText(dStr);
    u2.font = Font.monospacedSystemFont(9);
    u2.textColor = new Color("#f6f7f3");

    w.addSpacer(6);
    const foot = w.addText("spotpuls.app · 24h min/max");
    foot.font = Font.monospacedSystemFont(9);
    foot.textColor = new Color("#7f837a");
  } catch (e) {
    const err = w.addText("Spotpuls: tarkista verkkoyhteys");
    err.font = Font.systemFont(11);
    err.textColor = Color.white();
  }

  // Refresh near top of next hour (or max 30 min)
  w.refreshAfterDate = new Date(Math.floor(Date.now() / 3600000) * 3600000 + 3610000);
  return w;
}

const widget = await createWidget();
if (config.runsInWidget) {
  Script.setWidget(widget);
} else {
  await widget.presentSmall();
}
Script.complete();
