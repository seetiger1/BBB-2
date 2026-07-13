#!/usr/bin/env python3
from __future__ import annotations
"""
Berliner Bäder – Öffnungszeiten Scraper
========================================

Scrapes the overview page at berlinerbaeder.de/oeffnungszeiten-auf-einem-blick/
and extracts opening times for all currently listed pools into data/pools.json.

Additionally scrapes each pool's detail page to get labels like
"eingeschränkte Wasserfläche" (limited water area) or "Schul-/Vereinsbetrieb"
(schools/clubs only).

Usage:
    python scraper/scrape_pools.py
    python scraper/scrape_pools.py --output /custom/path/pools.json
    python scraper/scrape_pools.py --skip-details   # skip detail page scraping
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Install with: pip install -r requirements.txt")
    sys.exit(1)

OVERVIEW_URL = "https://www.berlinerbaeder.de/oeffnungszeiten-auf-einem-blick/"
BASE_URL = "https://www.berlinerbaeder.de"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "data" / "pools.json"

# German day names for mapping detail page weekly schedule to dates
DE_DAY_NAMES = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
    5: "Samstag",
    6: "Sonntag",
}

# Reverse map for date label parsing
DE_SHORT_TO_WEEKDAY = {
    "Mo": 0, "Di": 1, "Mi": 2, "Do": 3, "Fr": 4, "Sa": 5, "So": 6,
}


def fetch_page(url: str) -> str:
    """Fetch a page and return its HTML content."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text


def weekday_from_date_label(date_label: str) -> int | None:
    """Extract weekday index (0=Mon..6=Sun) from a date label like 'Do. 02.07.26'."""
    for prefix, idx in DE_SHORT_TO_WEEKDAY.items():
        if date_label.startswith(prefix):
            return idx
    return None

def parse_date(date_str: str) -> datetime | None:
    try:
        if len(date_str) == 8:
            return datetime.strptime(date_str, '%d.%m.%y')
        return datetime.strptime(date_str, '%d.%m.%Y')
    except:
        return None

def parse_date_from_label(date_label: str) -> datetime | None:
    parts = date_label.split()
    if len(parts) >= 2:
        return parse_date(parts[-1])
    return None


def scrape_detail_page(url: str) -> list[dict]:
    """
    Scrape a pool detail page and extract all weekly schedules.
    """
    try:
        html = fetch_page(url)
    except Exception as e:
        print(f"  ⚠ Could not fetch detail page {url}: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(html, "html.parser")
    schedules = []
    day_names_set = set(DE_DAY_NAMES.values())

    for t in soup.find_all("table"):
        if not t.find("th", class_="day"):
            continue
        
        prev_h = t.find_previous(["h2", "h3", "h4"])
        heading = prev_h.get_text(strip=True) if prev_h else ""
        
        start_date = None
        end_date = None
        match = re.search(r"(\d{2}\.\d{2}\.\d{2,4})\s*-\s*(\d{2}\.\d{2}\.\d{2,4})", heading)
        if match:
            start_date = parse_date(match.group(1))
            end_date = parse_date(match.group(2))
            
        schedule = {}
        current_day = None
        for tag in t.find_all(["th", "td"]):
            if tag.name == "th" and "day" in tag.get("class", []):
                day_text = tag.get_text(strip=True)
                if day_text in day_names_set:
                    current_day = day_text
                    if current_day not in schedule:
                        schedule[current_day] = []
            elif tag.name == "td" and current_day:
                classes = tag.get("class", [])
                title = tag.get("title", "")
                text = tag.get_text(strip=True)
                
                mobileday = tag.find("span", class_="mobileday")
                if mobileday:
                    text = text.replace(mobileday.get_text(strip=True), "", 1).strip()
                
                text = text.replace("Uhr", "").strip()
                text = re.sub(r"\s*-\s*", " - ", text).strip()

                if "closed" in classes or "geschlossen" in text.lower():
                    schedule[current_day].append({"time": "geschlossen", "label": "geschlossen"})
                elif "time" in classes and any(c.startswith("time_") for c in classes):
                    label = title
                    for dn in DE_DAY_NAMES.values():
                        if label.startswith(dn):
                            label = label[len(dn):].strip()
                    schedule[current_day].append({"time": text, "label": label or "öffentl. Schwimmen"})
                elif title or text:
                    if schedule[current_day] and not schedule[current_day][-1]["label"]:
                        schedule[current_day][-1]["label"] = text
        
        schedules.append({
            "heading": heading,
            "start": start_date,
            "end": end_date,
            "schedule": schedule
        })

    return schedules


def enrich_with_detail_labels(pool: dict, detail_schedules: list[dict], dates: list[str]):
    if not detail_schedules:
        return

    for entry in pool["schedule"]:
        date_label = entry["date"]
        dt = parse_date_from_label(date_label)
        
        chosen_sched = None
        # 1. try override schedules
        if dt:
            for s in detail_schedules:
                if s["start"] and s["end"] and s["start"] <= dt <= s["end"]:
                    chosen_sched = s
                    break
        # 2. fallback
        if not chosen_sched:
            for s in detail_schedules:
                if not s["start"]:
                    chosen_sched = s
                    break
                    
        if not chosen_sched:
            continue

        detail_schedule = chosen_sched["schedule"]
        
        weekday_idx = weekday_from_date_label(date_label)
        if weekday_idx is None:
            continue

        day_name = DE_DAY_NAMES.get(weekday_idx)
        if not day_name or day_name not in detail_schedule:
            continue

        detail_slots = detail_schedule[day_name]

        # Match time slots from overview to detail page labels
        if isinstance(entry["times"], list):
            for time_entry in entry["times"]:
                time_str = time_entry["time"]
                for ds in detail_slots:
                    if ds["time"] == time_str:
                        time_entry["label"] = ds["label"]
                        break
        elif isinstance(entry["times"], str) and entry["times"] != "geschlossen" and entry["times"] != "unbekannt":
            for ds in detail_slots:
                if ds["time"] == entry["times"]:
                    entry["label"] = ds.get("label", "")
                    break
        elif entry["times"] == "unbekannt":
            if any(ds["time"] == "geschlossen" for ds in detail_slots):
                entry["times"] = "geschlossen"


def parse_timetable_section(section_div, pool_type: str) -> tuple[list[str], list[dict]]:
    """
    Parse a single timetable section (Sommerbäder or Hallenbäder).

    Returns (dates, pools) where:
      - dates: list of date strings from the header row
      - pools: list of pool dicts with name, type, detail_url, schedule
    """
    dates = []
    pools = []

    # Find the table container
    container = section_div.find("div", class_="table-container")
    if not container:
        print(f"  ⚠ No table-container found in {pool_type} section", file=sys.stderr)
        return dates, pools

    rows = container.find_all("div", class_="table-row")
    if not rows:
        print(f"  ⚠ No table-rows found in {pool_type} section", file=sys.stderr)
        return dates, pools

    # First row is the header with dates
    header_row = rows[0]
    header_cells = header_row.find_all("div", class_="table-cell")
    for cell in header_cells:
        if "sticky-col" in cell.get("class", []):
            continue  # skip the "Bad" label
        text = cell.get_text(strip=True)
        # Normalize "heute" to today's date
        if text.lower() == "heute":
            today = datetime.now().strftime("%a %d.%m.%y")
            # German short day names
            day_map = {
                "Mon": "Mo.", "Tue": "Di.", "Wed": "Mi.",
                "Thu": "Do.", "Fri": "Fr.", "Sat": "Sa.", "Sun": "So."
            }
            eng_day = datetime.now().strftime("%a")
            de_day = day_map.get(eng_day, eng_day)
            text = f"{de_day} {datetime.now().strftime('%d.%m.%y')}"
        dates.append(text)

    # Remaining rows are pool data
    for row in rows[1:]:
        if "header-row" in row.get("class", []):
            continue

        cells = row.find_all("div", class_="table-cell")
        if not cells:
            continue

        # First cell (sticky-col) has the pool name + link
        name_cell = cells[0]
        link = name_cell.find("a")
        if link:
            pool_name = link.get_text(strip=True)
            detail_path = link.get("href", "")
            detail_url = f"{BASE_URL}{detail_path}" if detail_path.startswith("/") else detail_path
        else:
            pool_name = name_cell.get_text(strip=True)
            detail_url = ""

        if not pool_name:
            continue

        # Extract schedule from remaining cells
        schedule = []
        for i, cell in enumerate(cells[1:]):
            date_label = dates[i] if i < len(dates) else f"Tag {i + 1}"

            # Check for closed marker
            closed_span = cell.find("span", class_="timetable-closed")
            if closed_span:
                schedule.append({"date": date_label, "times": "geschlossen"})
                continue

            # Check for ALL period spans (there can be multiple per cell!)
            period_spans = cell.find_all("span", class_="period")
            if period_spans:
                time_slots = []
                for period_span in period_spans:
                    time_inner_spans = period_span.find_all("span")
                    if len(time_inner_spans) >= 2:
                        open_time = time_inner_spans[0].get_text(strip=True)
                        close_time = time_inner_spans[1].get_text(strip=True)
                        time_slots.append({
                            "time": f"{open_time} - {close_time}",
                            "label": "",  # will be enriched from detail page
                        })
                    else:
                        raw = period_span.get_text(strip=True)
                        raw = raw.replace("\xa0", " ").replace("  ", " ").strip()
                        if raw:
                            time_slots.append({"time": raw, "label": ""})

                if time_slots:
                    schedule.append({"date": date_label, "times": time_slots})
                else:
                    schedule.append({"date": date_label, "times": "unbekannt"})
                continue

            # Fallback: raw text
            raw = cell.get_text(strip=True)
            raw = raw.replace("\xa0", " ").replace("  ", " ").strip()
            if raw:
                schedule.append({"date": date_label, "times": raw})
            else:
                # Empty cell = unknown (no data published yet)
                schedule.append({"date": date_label, "times": "unbekannt"})

        pools.append({
            "name": pool_name,
            "type": pool_type,
            "detail_url": detail_url,
            "schedule": schedule,
        })

    return dates, pools


def scrape_pools(skip_details: bool = False) -> dict:
    """Main scrape function. Returns the complete data dict."""
    print(f"🔄 Fetching {OVERVIEW_URL} ...")
    html = fetch_page(OVERVIEW_URL)
    soup = BeautifulSoup(html, "html.parser")

    all_pools = []
    all_dates = []

    # Find all timetable sections — there are typically 3:
    # "Alle Bäder", "Sommerbäder", "Hallenbäder"
    # We use the Sommerbäder + Hallenbäder sections for type classification
    timetable_sections = soup.find_all("div", class_="facility-timetable")

    if not timetable_sections:
        print("⚠ No facility-timetable sections found!", file=sys.stderr)
        return {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "source_url": OVERVIEW_URL,
            "dates": [],
            "pools": [],
        }

    # Classify each section by its intro text
    typed_sections = []  # (pool_type, section)
    generic_sections = []  # sections without a clear type ("Alle Bäder")

    for section in timetable_sections:
        parent_div = section.find_parent("div", class_="tx-bbb-facility")
        intro = ""
        if parent_div:
            intro_div = parent_div.find("div", class_="facility-timetable-introtext")
            if intro_div:
                intro = intro_div.get_text(strip=True).lower()

        if "sommerbäder" in intro or "sommerbad" in intro:
            typed_sections.append(("Sommerbad", section))
        elif "hallenbäder" in intro or "hallenbad" in intro:
            typed_sections.append(("Hallenbad", section))
        else:
            generic_sections.append(section)

    # Process typed sections first (Sommerbäder, Hallenbäder)
    for pool_type, section in typed_sections:
        dates, pools = parse_timetable_section(section, pool_type)
        if dates and not all_dates:
            all_dates = dates
        all_pools.extend(pools)

    # Only use generic ("Alle Bäder") section if no typed sections found
    if not typed_sections:
        for section in generic_sections:
            dates, pools = parse_timetable_section(section, "Sonstiges")
            if dates and not all_dates:
                all_dates = dates
            all_pools.extend(pools)

    # Deduplicate by name
    seen = set()
    unique_pools = []
    for pool in all_pools:
        key = pool["name"]
        if key not in seen:
            seen.add(key)
            unique_pools.append(pool)

    # Infer type from name for any remaining "Sonstiges" pools
    for pool in unique_pools:
        if pool["type"] == "Sonstiges":
            name_lower = pool["name"].lower()
            if "sommerbad" in name_lower or "strandbad" in name_lower or "kinderbad" in name_lower:
                pool["type"] = "Sommerbad"
            elif "schwimmhalle" in name_lower or "hallenbad" in name_lower or "stadtbad" in name_lower or "sportbad" in name_lower:
                pool["type"] = "Hallenbad"

    print(f"✅ Scraped {len(unique_pools)} pools across {len(all_dates)} days from overview page")

    # Enrich with detail page labels (limited area, schools, etc.)
    if not skip_details:
        print(f"🔍 Fetching detail pages for time slot labels ...")
        for i, pool in enumerate(unique_pools):
            if not pool.get("detail_url"):
                continue
            print(f"  [{i+1}/{len(unique_pools)}] {pool['name']}")
            detail_schedule = scrape_detail_page(pool["detail_url"])
            enrich_with_detail_labels(pool, detail_schedule, all_dates)
            # Be polite — small delay between requests
            time.sleep(0.3)
        print(f"✅ Enriched {len(unique_pools)} pools with detail labels")

    return {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_url": OVERVIEW_URL,
        "dates": all_dates,
        "pools": unique_pools,
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape Berliner Bäder opening times")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--skip-details",
        action="store_true",
        help="Skip scraping individual pool detail pages (faster, no labels)",
    )
    args = parser.parse_args()

    data = scrape_pools(skip_details=args.skip_details)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"📁 Written to {args.output}")

    # Summary
    if data["pools"]:
        types = {}
        for p in data["pools"]:
            types[p["type"]] = types.get(p["type"], 0) + 1
        for t, count in sorted(types.items()):
            print(f"   {t}: {count}")
    else:
        print("   ⚠ No pools found – check if the page structure changed")


if __name__ == "__main__":
    main()
