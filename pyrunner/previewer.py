"""
previewer.py — Sample an episode from an existing run, then (optionally) run it.

Workflow
--------
1. Locate the source run via -pid + -c (cfg@N).
2. Determine the episode to sample:
   - If --ofepisode is given, use that.
   - Otherwise, find the highest episode in ep/ of that run.
3. Call model_extractor logic to copy & normalize the episode to ep/0.
4. Build the output PID name:
   - If --aspid is given, use it as-is as the prefix.
   - Otherwise prefix with "preview".
   - Output PID format: <prefix>-<original_pid>-at-<ofepisode>
5. If --episodesig is not given, default to 1.
6. If --run is given, execute one.bat (without -b) with the config overrides
   built the same way as batch_runner, pointing at the new output directory.

Usage examples
--------------
  # Dry-run: extract only
  python pyrunner/previewer.py -pid ql-c-ms@0 -c 35

  # Extract + run
  python pyrunner/previewer.py -pid ql-c-ms@0 -c 35 --run

  # Custom episode, custom prefix
  python pyrunner/previewer.py -pid ql-c-ms@0 -c 35 --ofepisode 500 --aspid mytest --run

  # Custom episodesig
  python pyrunner/previewer.py -pid ql-c-ms@0 -c 35 --episodesig 5 --run
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Optional

# Allow running as a script while still using absolute package imports (pyrunner.*)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.utils.path import normalize_report_base
from pyrunner.utils.timefmt import format_timedelta
from pyrunner.model_extractor import (
    find_matching_run_dirs,
    find_highest_episode,
    extract_model,
    _parse_config_indices,
)
from pyrunner.batch_runner import (
    expand_algorithm,
    REPORTS_BASE,
)

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------------------------------- #
# HELPERS
# ------------------------------------------------------------------------------------------------------------------- #

def build_output_pid(prefix: Optional[str], original_pid: str, ofepisode: int) -> str:
    """
    Build the output parent directory ID.

    Format: <prefix>-<original_pid>-at-<ofepisode>

    If prefix is None, "preview" is used.
    """
    effective_prefix = prefix if prefix else "preview"
    return f"{effective_prefix}-{original_pid}-at-{ofepisode}"


def run_preview(
        alg: str,
        full_output_dir: str,
        overrides_string: Optional[str],
        custom_cfg: Optional[str] = None,
        alg_override: Optional[str] = None,
) -> bool:
    """
    Run one.bat WITHOUT -b (interactive/GUI mode), passing the config overrides
    exactly like batch_runner.run_script but without the headless flag.
    """
    script = [
        r".\one.bat",
        "1",
    ]

    if overrides_string:
        script.extend(["-d", overrides_string])

    script.append(expand_algorithm(alg, custom_cfg, alg_override))

    start_time = datetime.now()

    try:
        log.info("%s", "-" * LINE_LENGTH)
        log.info("[PREVIEW] Launching simulation from: %s", full_output_dir)
        log.info("[PREVIEW] Command: %s", " ".join(script))
        log.info("%s", "-" * LINE_LENGTH)

        result = subprocess.run(script, shell=True)

        if result.returncode != 0:
            log.error("[PREVIEW] Simulation exited with code: %s", result.returncode)
            return False

        return True

    except Exception as exc:
        log.error("[PREVIEW] Exception during simulation: %s", exc)
        return False

    finally:
        end_time = datetime.now()
        took = format_timedelta(end_time - start_time)
        log.info("%s", "-" * LINE_LENGTH)
        log.info("[PREVIEW] Simulation finished. Took %s.", took)
        log.info("%s", "-" * LINE_LENGTH)


# ------------------------------------------------------------------------------------------------------------------- #
# MAIN
# ------------------------------------------------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Previewer — sample a specific episode from an existing run into a new directory, "
            "then optionally launch the simulation from that snapshot."
        )
    )

    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=True,
        help="Source parent directory ID (e.g. 'ql-c-ms@0').",
    )

    parser.add_argument(
        "-c", "--config", type=str, required=True,
        help=(
            "Config index filter — matches run dirs by cfg@N. "
            "Supports comma-separated values and ranges (e.g. '35', '1,3-5'). "
            "Required."
        ),
    )

    parser.add_argument(
        "-oe", "--ofepisode", type=int, required=False,
        help=(
            "Episode number to sample. "
            "If not given, the highest episode in ep/ is used."
        ),
    )

    parser.add_argument(
        "-ap", "--aspid", type=str, required=False,
        help=(
            "Custom prefix for the output parent directory ID. "
            "If not given, 'preview' is used. "
            "Final output PID: <aspid>-<original_pid>-at-<ofepisode>."
        ),
    )

    parser.add_argument(
        "-es", "--episodesig", type=int, required=False, default=1,
        help=(
            "Episode signature (runs count) written into the extracted model's runner_id "
            "and config_setting.json. Default: 1."
        ),
    )

    parser.add_argument(
        "--run", action="store_true",
        help=(
            "After extraction, execute one.bat (without -b) using config overrides "
            "that point at the new output directory."
        ),
    )

    parser.add_argument(
        "-srp", "--setreportspath", type=str, required=False,
        help=(
            "Override the base report directory path. "
            f"Default: '{REPORTS_BASE}'."
        ),
    )

    parser.add_argument(
        "-alg", "--algorithm", type=str, required=False,
        help="Override algorithm config key (passed to expand_algorithm as alg_override).",
    )

    parser.add_argument(
        "-rcfg", "--runcfg", type=str, required=False,
        help="Custom config file path override (passed to expand_algorithm as custom_cfg).",
    )

    args = parser.parse_args()

    # ── Resolve reports base ──────────────────────────────────────────────
    reports_base = normalize_report_base(args.setreportspath or REPORTS_BASE)

    # ── Parse config indices ──────────────────────────────────────────────
    try:
        config_indices = _parse_config_indices(args.config)
    except ValueError as exc:
        log.error("Invalid -c/--config value: %s", exc)
        sys.exit(1)

    # ── Header ────────────────────────────────────────────────────────────
    log.info("%s", "=" * LINE_LENGTH)
    log.info("PREVIEWER")
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Source parent ID  : %s", args.parent_dir_id)
    log.info("Config filter     : %s", config_indices)
    log.info("Episode to sample : %s", args.ofepisode or "(highest available)")
    log.info("Episode sig       : %d", args.episodesig)
    log.info("Output prefix     : %s", args.aspid or "preview")
    log.info("Run after extract : %s", args.run)
    log.info("Reports base      : %s", reports_base)
    log.info("%s", "=" * LINE_LENGTH)

    # ── Find matching source directories ─────────────────────────────────
    try:
        matched_dirs = find_matching_run_dirs(
            args.parent_dir_id,
            reports_base,
            config_indices=config_indices,
        )
    except ValueError as exc:
        log.error("Resolution error: %s", exc)
        sys.exit(1)

    if not matched_dirs:
        log.error(
            "No matching run directories found for -pid '%s' -c '%s'.",
            args.parent_dir_id, args.config
        )
        sys.exit(1)

    log.info(
        "Found %d matching run director%s:",
        len(matched_dirs), "y" if len(matched_dirs) == 1 else "ies"
    )
    for d in matched_dirs:
        log.info("  %s", d)

    # ── Process each matched directory ────────────────────────────────────
    for source_dir in matched_dirs:
        ep_root = os.path.join(source_dir, "ep")

        # Determine highest available episode first (needed even when --ofepisode given,
        # so we can validate the requested episode doesn't exceed it)
        highest_ep, problems = find_highest_episode(ep_root)

        if problems:
            for p in problems:
                log.warning("[PREVIEWER] %s", p)

        if highest_ep <= 0:
            log.error("[PREVIEWER] No valid episodes found in: %s", source_dir)
            sys.exit(1)

        # Resolve the episode to sample
        episode_to_sample = args.ofepisode if args.ofepisode is not None else highest_ep

        if episode_to_sample > highest_ep:
            log.error(
                "[PREVIEWER] Requested episode %d exceeds highest available (%d) in: %s",
                episode_to_sample, highest_ep, source_dir
            )
            sys.exit(1)

        if episode_to_sample < 1:
            log.error("[PREVIEWER] Episode number must be >= 1, got: %d", episode_to_sample)
            sys.exit(1)

        log.info("[PREVIEWER] Sampling episode %d (highest: %d)", episode_to_sample, highest_ep)

        # ── Build output PID ──────────────────────────────────────────────
        output_pid = build_output_pid(args.aspid, args.parent_dir_id, episode_to_sample)
        log.info("[PREVIEWER] Output PID: %s", output_pid)

        # ── Extract / normalize the episode ──────────────────────────────
        extract_model(
            source_dir=source_dir,
            source_episode=episode_to_sample,
            target_parent_dir_id=output_pid,
            reports_base=reports_base,
            episodesig=args.episodesig,
            prepfor_overrides=None,
        )

        # ── Optionally run the simulation ─────────────────────────────────
        if args.run:
            # The extracted run lives at:
            #   reports_base / output_pid / run-id / <new_runner_id>
            # We need to find it to build the overrides string.
            # extract_model creates exactly one run-id subdir per call,
            # so we grab the first (and only) one.
            run_id_path = os.path.join(reports_base, output_pid, "run-id")
            if not os.path.isdir(run_id_path):
                log.error("[PREVIEWER] Expected run-id directory not found: %s", run_id_path)
                sys.exit(1)

            subdirs = [
                d for d in os.listdir(run_id_path)
                if os.path.isdir(os.path.join(run_id_path, d))
            ]
            if not subdirs:
                log.error("[PREVIEWER] No run directories found under: %s", run_id_path)
                sys.exit(1)

            # There should be exactly one subdir created by extract_model above
            new_runner_id = subdirs[0]
            full_output_dir = os.path.join(run_id_path, new_runner_id)

            # Build overrides: persistence path + episode 1 as the first episode to run
            persistence_path = os.path.join(full_output_dir, "_persistence.json")
            ep1_report_dir = os.path.join(full_output_dir, "ep", "1")

            overrides = [
                f"EpisodicPersistenceManager.persistencePath={persistence_path}",
                f"Report.reportDir={ep1_report_dir}",
                f"EpisodicPersistenceManager.episodeNumber=1",
            ]
            overrides_string = "@@".join(overrides)

            # Determine algorithm from source config_setting.json
            from pyrunner.utils.jsonio import load_json_file
            cfg_file = os.path.join(full_output_dir, "config_setting.json")
            ok, cfg_data, err = load_json_file(cfg_file)
            if not ok:
                log.error("[PREVIEWER] Cannot read config_setting.json from output dir: %s", err)
                sys.exit(1)

            alg = cfg_data.get("runner_algorithm", "")
            if not alg:
                log.error("[PREVIEWER] runner_algorithm missing in config_setting.json")
                sys.exit(1)

            success = run_preview(
                alg=alg,
                full_output_dir=full_output_dir,
                overrides_string=overrides_string,
                custom_cfg=args.runcfg,
                alg_override=args.algorithm,
            )

            if not success:
                log.error("[PREVIEWER] Simulation run failed.")
                sys.exit(1)

    log.info("%s", "=" * LINE_LENGTH)
    log.info(
        "[PREVIEWER] All done. %d director%s processed.",
        len(matched_dirs), "y" if len(matched_dirs) == 1 else "ies"
    )
    log.info("%s", "=" * LINE_LENGTH)


if __name__ == "__main__":
    main()
