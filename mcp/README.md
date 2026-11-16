# Spotpuls MCP Server (`spotpuls-mcp`)

Zero-dependency Model Context Protocol (MCP) server for **Spotpuls** (`https://spotpuls.app`). Gives Claude Desktop, Cursor, Antigravity, and other MCP clients direct access to live European day-ahead electricity spot prices, 7-day forecasts, and optimal load-shifting windows across all 40 bidding zones.

## Tools
- `get_spot_prices(zone, vat, window, format)` — Live hourly spot price, today min/avg/max, cheapest contiguous N-hour window, and 7-day forecast.
- `list_bidding_zones()` — Metadata for all 40 supported European bidding zones.

## Usage in Claude Desktop / Cursor / Antigravity
Add to your MCP config (`mcpServers`):

```json
{
  "mcpServers": {
    "spotpuls": {
      "command": "node",
      "args": ["mcp/server.js"]
    }
  }
}
```
