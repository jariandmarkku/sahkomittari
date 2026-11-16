#!/usr/bin/env python3
"""
Spotpuls Python Spot Electricity & 7-Day Forecast Controller Example.
Docs: https://spotpuls.app/api-docs/
"""

import requests


def get_spot_schedule(zone: str = "FI", window_hours: int = 3, vat: int = 1) -> dict:
    url = "https://spotpuls.app/api/v1/prices"
    params = {"zone": zone, "vat": vat, "window": window_hours, "format": "json"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    data = get_spot_schedule(zone="FI", window_hours=3)
    print(data["aiSummary"])
    print("Run load now (cheapest contiguous window):", data["automation"]["cheapestContiguousWindow"]["activeNow"])
    print("Citation:", data["citation"])
