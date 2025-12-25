import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import nolds
import warnings

warnings.filterwarnings("ignore")

BaseDir = "CopenhagenCloudburst2011"

AffectedFiles = ["CCBGentofte.csv", "CCBIshøj.csv", "CCBKøbenhavn.csv"]
NotAffectedFiles = ["CCBHolstebro.csv", "CCBSorø.csv", "CCBVejle.csv"]

WindowHours = 24 * 7

def load_and_average_mean_wind(files, folder):
    dfs = []
    for filename in files:
        path = os.path.join(BaseDir, folder, filename)
        df = pd.read_csv(path)
        df["Datetime"] = pd.to_datetime(df["date"] + " " + df["hour"].astype(str) + ":00")
        df.set_index("Datetime", inplace=True)
        dfs.append(df[["mean_wind_speed"]])
    combined = pd.concat(dfs, axis=1)
    avg_series = combined.mean(axis=1)
    return avg_series

def compute_weekly_lle(series):
    lle = []
    values = series.values
    for start in range(0, len(values) - WindowHours + 1):
        window_values = values[start:start + WindowHours]
        try:
            le = nolds.lyap_r(window_values, emb_dim=6)
        except:
            le = np.nan
        lle.append(le)
    lle = [np.nan] * (WindowHours - 1) + lle
    return np.array(lle)

affected_series = load_and_average_mean_wind(AffectedFiles, "affected")
not_affected_series = load_and_average_mean_wind(NotAffectedFiles, "notAffected")

lle_affected = compute_weekly_lle(affected_series)
lle_not_affected = compute_weekly_lle(not_affected_series)

last_month_hours = 30 * 24
start_idx = -last_month_hours

idx_affected_last = affected_series.index[start_idx:]
idx_not_affected_last = not_affected_series.index[start_idx:]

std_affected = pd.Series(lle_affected[start_idx:]).expanding().std()
std_not_affected = pd.Series(lle_not_affected[start_idx:]).expanding().std()

plt.figure(figsize=(18, 12))

plt.subplot(3, 1, 1)
plt.plot(affected_series.index, lle_affected, label="Påvirket LLE")
plt.plot(not_affected_series.index, lle_not_affected, label="Ikke påvirket LLE")
plt.ylabel("Ukentlig LLE")
plt.title("LLE hele perioden (Copenhagen Cloudburst 2011)")
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(idx_affected_last, lle_affected[start_idx:], label="Påvirket LLE")
plt.plot(idx_not_affected_last, lle_not_affected[start_idx:], label="Ikke påvirket LLE")
plt.ylabel("Ukentlig LLE")
plt.title("LLE siste måned")
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(idx_affected_last, std_affected, label="Påvirket LLE STD")
plt.plot(idx_not_affected_last, std_not_affected, label="Ikke påvirket LLE STD")
plt.ylabel("Standardavvik")
plt.title("Kumulativt standardavvik av LLE siste måned")
plt.legend()

plt.tight_layout()
plt.show()