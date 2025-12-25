import os
import pandas as pd
import numpy as np
import nolds
import warnings
from stormsInf import STORMS

warnings.filterwarnings("ignore")

ROOT_DIR = "Storms"
WINDOW_HOURS = 24 * 7
WEEKS = 4
HOURS_PER_WEEK = 24 * 7
LAST_HOURS = WEEKS * HOURS_PER_WEEK


def choose_storm():
    print("Available storms:")
    for name in STORMS:
        print(f" - {name.title()}")
    choice = input("Choose storm: ").strip().upper()
    if choice in STORMS:
        return choice
    print("Unknown storm. Defaulting to MALIK.")
    return "MALIK"


def compute_weekly_lle(series):
    series = series.ffill().bfill()
    values = series.values
    lle = []

    for start in range(len(values) - WINDOW_HOURS + 1):
        window = values[start:start + WINDOW_HOURS]
        try:
            le = nolds.lyap_r(window, emb_dim=6)
        except:
            le = np.nan
        lle.append(le)

    return pd.Series(
        [np.nan] * (WINDOW_HOURS - 1) + lle,
        index=series.index
    )


def delta_sigma_for_municipality(csv_path):
    df = pd.read_csv(csv_path)
    df["Datetime"] = pd.to_datetime(df["timestamp"])
    df.set_index("Datetime", inplace=True)

    series = df["mean_wind_speed"].ffill().bfill()
    lle = compute_weekly_lle(series)

    if len(lle) < LAST_HOURS * 2:
        raise ValueError(f"Not enough data in {csv_path}")

    last_lle = lle.iloc[-LAST_HOURS:]
    baseline_lle = lle.iloc[:-LAST_HOURS]

    sigma_last = np.nanstd(last_lle.values)
    sigma_baseline = np.nanstd(baseline_lle.values)

    return sigma_last - sigma_baseline


def print_rows(values, row_len=2):
    for i in range(0, len(values), row_len):
        row = values[i:i + row_len]
        print(",".join(str(v) for v in row))


storm_name = choose_storm()
config = STORMS[storm_name]

base_dir = os.path.join(ROOT_DIR, config["BaseDir"])
affected_folder = config["AffectedFolder"]
not_affected_folder = config["NotAffectedFolder"]

affected_dsigma = []
not_affected_dsigma = []

print("\nComputing Δσ (LLE volatility change) per municipality...\n")

for mun_id, filename in config["AFFECTED"].items():
    path = os.path.join(base_dir, affected_folder, filename)
    ds = delta_sigma_for_municipality(path)
    affected_dsigma.append(ds)

for mun_id, filename in config["NOT_AFFECTED"].items():
    path = os.path.join(base_dir, not_affected_folder, filename)
    ds = delta_sigma_for_municipality(path)
    not_affected_dsigma.append(ds)

print("Affected Δσ values:")
print_rows(affected_dsigma)

print("\nNot affected Δσ values:")
print_rows(not_affected_dsigma)