import csv
import os
import sys

# Allow running this file as a script (python pyrunner/batch_runner.py) while still
# using absolute package imports (pyrunner.*).
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.batch_configs import LIST_OF_CONFIGS

CSV_PATH = r"pyrunner"

GROUP_TRANSLATOR = {
    "ql_epsilon": "EG",
    "ql_ucb": "UCB",
    "ql_ps": "PS",
    "lf": "LF",
}

KEY_TRANSLATOR = {
    "eg_ip": "Initial Exploration Probability",
    "eg_me": "Minimum Epsilon Threshold",
    "eg_ed": "Epsilon Decay",
    "ucb_ec": "Exploration Constant",
    "ps_lr": "Q-Tracking PS Learning Rate",
    "ps_iv": "Q-Tracking PS Initial Variance",
    "ps_betabinomial": "Using Beta-Binomial Sampling",
    "ps_reset": "Reset Episodes",
    "lfe_la": "Lévy Alpha",
}

# Collect all possible override keys
override_keys = []
seen_keys = set()

for cfg in LIST_OF_CONFIGS:
    overrides = cfg.get("overrides", {})

    for key in overrides.keys():
        if key not in seen_keys:
            seen_keys.add(key)
            override_keys.append(key)

# Create translated column names
translated_override_columns = [
    KEY_TRANSLATOR.get(key, key)
    for key in override_keys
]

# CSV columns
columns = ["No", "Group"] + translated_override_columns

# Ensure directory exists
os.makedirs(CSV_PATH, exist_ok=True)

csv_file = os.path.join(CSV_PATH, "batch_configs.csv")

# Write CSV
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns)

    writer.writeheader()

    for idx, cfg in enumerate(LIST_OF_CONFIGS, start=1):
        row = {
            "No": idx,
            "Group": GROUP_TRANSLATOR.get(cfg.get("group"), cfg.get("group")),
        }

        overrides = cfg.get("overrides", {})

        for key in override_keys:
            translated_key = KEY_TRANSLATOR.get(key, key)
            row[translated_key] = overrides.get(key, "")

        writer.writerow(row)

print(f"CSV saved to: {csv_file}")