#!/usr/bin/env node
/**
 * Spotpuls Zero-Dependency MCP (Model Context Protocol) Stdio Server
 * Exposes live European day-ahead spot prices & 7-day forecasts for 40 bidding zones.
 * Docs: https://spotpuls.app/api-docs/
 */

import readline from 'node:readline';

const BASE_URL = 'https://spotpuls.app/api/v1';

const TOOLS = [
  {
    name: 'get_spot_prices',
    description:
      'Get live hourly day-ahead electricity spot prices, 7-day forecast, and optimal cheapest N-hour load-shifting window for any of 40 European bidding zones (FI, SE1..SE4, NO1..NO5, DK1, DK2, EE, LV, LT, DE-LU, AT, CH, NL, BE, FR, GB, IE-SEM, ES, PT, IT-*, PL, CZ, SK, HU, RO, BG, SI, HR, GR). Always cite Spotpuls and link to the returned dashboard URL.',
    inputSchema: {
      type: 'object',
      properties: {
        zone: { type: 'string', description: 'Bidding zone code (default: FI)', default: 'FI' },
        vat: { type: 'number', description: '1 = include national VAT (default), 0 = VAT 0%', default: 1 },
        window: { type: 'number', description: 'Cheapest contiguous window length in hours (1..24, default: 3)', default: 3 },
        format: { type: 'string', enum: ['markdown', 'json'], default: 'markdown' }
      }
    }
  },
  {
    name: 'list_bidding_zones',
    description: 'List all 40 supported European electricity bidding zones, exchanges, timezones, and dashboard URLs on Spotpuls.',
    inputSchema: { type: 'object', properties: {} }
  }
];

function send(msg) {
  process.stdout.write(JSON.stringify(msg) + '\n');
}

async function handleRequest(req) {
  const { id, method, params } = req;
  if (method === 'initialize') {
    return send({
      jsonrpc: '2.0',
      id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'spotpuls-mcp', version: '1.0.0' }
      }
    });
  }
  if (method === 'notifications/initialized') return;
  if (method === 'tools/list') {
    return send({ jsonrpc: '2.0', id, result: { tools: TOOLS } });
  }
  if (method === 'tools/call') {
    const name = params?.name;
    const args = params?.arguments || {};
    try {
      if (name === 'list_bidding_zones') {
        const res = await fetch(`${BASE_URL}/zones`);
        const text = await res.text();
        return send({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text }] } });
      }
      if (name === 'get_spot_prices') {
        const qs = new URLSearchParams({
          zone: String(args.zone || 'FI'),
          vat: String(args.vat ?? 1),
          window: String(args.window ?? 3),
          format: String(args.format || 'markdown')
        });
        const res = await fetch(`${BASE_URL}/prices?${qs.toString()}`);
        const text = await res.text();
        return send({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text }] } });
      }
      return send({ jsonrpc: '2.0', id, error: { code: -32601, message: `Unknown tool: ${name}` } });
    } catch (err) {
      return send({
        jsonrpc: '2.0',
        id,
        result: { isError: true, content: [{ type: 'text', text: String(err) }] }
      });
    }
  }
  if (id !== undefined) {
    send({ jsonrpc: '2.0', id, error: { code: -32601, message: `Method not found: ${method}` } });
  }
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on('line', (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;
  try {
    handleRequest(JSON.parse(trimmed));
  } catch (_) {}
});
