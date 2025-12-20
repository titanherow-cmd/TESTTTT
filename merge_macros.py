#!/usr/bin/env python3
"""merge_macros.py - Robust File Discovery Version"""

from pathlib import Path
import argparse, json, random, sys, os, math
from copy import deepcopy

def load_json_events(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k in ("events", "items", "entries", "records"):
                if k in data and isinstance(data[k], list): return deepcopy(data[k])
            return [data] if "Time" in data else []
        return deepcopy(data) if isinstance(data, list) else []
    except: return []

def get_file_duration_ms(path: Path) -> int:
    events = load_json_events(path)
    if not events: return 0
    try:
        times = [int(e.get("Time", 0)) for e in events]
        return max(times) - min(times)
    except: return 0

def number_to_letters(n: int) -> str:
    res = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        res = chr(65 + rem) + res
    return res or "A"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_root", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--versions", type=int, default=6)
    parser.add_argument("--target-minutes", type=int, default=25)
    parser.add_argument("--delay-before-action-ms", type=int, default=10)
    parser.add_argument("--bundle-id", type=int, required=True)
    args, unknown = parser.parse_known_args()

    rng = random.Random()
    bundle_dir = args.output_root / f"merged_bundle_{args.bundle_id}"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"--- DEBUG: SEARCHING FOR MACROS ---")
    print(f"Scanning root: {args.input_root.resolve()}")

    # Deep scan: Find every directory that contains at least one .json file
    folders_with_json = []
    for p in args.input_root.rglob("*"):
        if p.is_dir():
            # Filter out hidden folders or output folders if they exist inside input
            if p.name.startswith('.') or "output" in p.parts:
                continue
            
            jsons = [f for f in p.glob("*.json") if "click_zones" not in f.name.lower()]
            if jsons:
                folders_with_json.append((p, jsons))
                print(f"Found folder with {len(jsons)} macros: {p.relative_to(args.input_root)}")

    if not folders_with_json:
        print(f"CRITICAL ERROR: No JSON files found in {args.input_root} or any subfolders!")
        sys.exit(1) # Force the GitHub Action to fail so you can see the error

    for folder_path, json_files in folders_with_json:
        rel_path = folder_path.relative_to(args.input_root)
        out_folder = bundle_dir / rel_path
        out_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing Group: {rel_path}")
        
        for v in range(1, args.versions + 1):
            selected = []
            current_ms = 0.0
            target_ms = args.target_minutes * 60000
            
            pool = list(json_files)
            rng.shuffle(pool)
            
            # Simple Round-Robin to fill time
            while current_ms < target_ms and pool:
                pick = pool.pop(0)
                selected.append(pick)
                # Estimate: Duration + 20% + 1s inter-file gap
                current_ms += (get_file_duration_ms(pick) * 1.2) + 1000
                if not pool and current_ms < target_ms:
                    pool = list(json_files)
                    rng.shuffle(pool)
                if len(selected) > 100: break # Safety cap
            
            if not selected: continue
            
            merged_events = []
            timeline_ms = 0
            accumulated_afk = 0
            is_time_sensitive = "time sensitive" in str(folder_path).lower()

            for i, p in enumerate(selected):
                raw = load_json_events(p)
                if not raw: continue
                
                t_vals = [int(e.get("Time", 0)) for e in raw]
                base_t = min(t_vals) if t_vals else 0
                dur = (max(t_vals) - base_t) if t_vals else 0
                
                # Humanization Gap
                gap = rng.randint(500, 2000) if i > 0 else 0
                timeline_ms += gap
                
                # Roll for Human AFK Pool (Ignore for screenshare links)
                if "screensharelink" not in p.name.lower():
                    pct = rng.choice([0, 0, 0.12, 0.20, 0.28]) # High weight on 0 for stability
                    accumulated_afk += int(dur * pct)

                for e in raw:
                    ne = deepcopy(e)
                    ne["Time"] = (int(e.get("Time", 0)) - base_t) + timeline_ms
                    merged_events.append(ne)
                
                timeline_ms = merged_events[-1]["Time"]

            # Apply Accumulated AFK
            if accumulated_afk > 0:
                if is_time_sensitive:
                    merged_events[-1]["Time"] += accumulated_afk
                else:
                    split_idx = rng.randint(1, len(merged_events) - 1)
                    for k in range(split_idx, len(merged_events)):
                        merged_events[k]["Time"] += accumulated_afk

            final_dur = merged_events[-1]["Time"]
            v_code = number_to_letters(v)
            fname = f"{v_code}_{int(final_dur / 60000)}m.json"
            (out_folder / fname).write_text(json.dumps(merged_events, indent=2))

    print(f"--- SUCCESS: All folders processed ---")

if __name__ == "__main__":
    main()
