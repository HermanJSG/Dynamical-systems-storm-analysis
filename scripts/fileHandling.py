from datetime import date
import os
import json
from datetime import timedelta, datetime
from stormsInf import STORMS

USB_PATH = "/Volumes/Herman2TB/KaosTeori"
ROOT_DIR = "Storms"


def choose_storm():
    print("Available storms:")
    for name in STORMS:
        print(f" - {name.title()}")
    choice = input("Choose storm: ").strip().upper()
    if choice in STORMS:
        return choice
    print("Unknown storm. Defaulting to MALIK.")
    return "MALIK"


def to_hour_timestamp(dt_str):
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M")


def process_day(day, writers):
    path = os.path.join(USB_PATH, day.strftime("%Y-%m-%d.txt"))
    if not os.path.exists(path):
        return

    rows = {}
    for mun_id in writers:
        rows[mun_id] = []

    f = open(path, "r", encoding="utf-8")
    for line in f:
        line = line.strip()
        if line == "":
            continue

        try:
            obj = json.loads(line)
        except:
            continue

        props = obj.get("properties", {})
        mun_id = props.get("municipalityId")

        if mun_id not in writers:
            continue
        if props.get("timeResolution") != "hour":
            continue
        if props.get("parameterId") != "mean_wind_speed":
            continue

        ts = props.get("from")
        val = props.get("value")
        if ts is None or val is None:
            continue

        rows[mun_id].append((to_hour_timestamp(ts), val))

    f.close()

    for mun_id in rows:
        rows[mun_id].sort()
        for ts, val in rows[mun_id]:
            writers[mun_id].write(f"{ts},{val}\n")


def main():
    storm_name = choose_storm()
    config = STORMS[storm_name]

    base_dir = os.path.join(ROOT_DIR, config["BaseDir"])
    affected_folder = config["AffectedFolder"]
    not_affected_folder = config["NotAffectedFolder"]
    affected = config["AFFECTED"]
    not_affected = config["NOT_AFFECTED"]
    start = config["StartDate"]
    end = config["EndDate"]

    os.makedirs(os.path.join(base_dir, affected_folder), exist_ok=True)
    os.makedirs(os.path.join(base_dir, not_affected_folder), exist_ok=True)

    writers = {}

    for mun_id in affected:
        out_path = os.path.join(base_dir, affected_folder, affected[mun_id])
        w = open(out_path, "w", encoding="utf-8")
        w.write("timestamp,mean_wind_speed\n")
        writers[mun_id] = w

    for mun_id in not_affected:
        out_path = os.path.join(base_dir, not_affected_folder, not_affected[mun_id])
        w = open(out_path, "w", encoding="utf-8")
        w.write("timestamp,mean_wind_speed\n")
        writers[mun_id] = w

    current = start
    while current <= end:
        process_day(current, writers)
        current += timedelta(days=1)

    for mun_id in writers:
        writers[mun_id].close()

    print("Done:", storm_name.title())


if __name__ == "__main__":
    main()