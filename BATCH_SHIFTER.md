# BATCH SHIFTER

## Overview

`batch_shifter.py` automatically renames `cfg@N` folders when batch configs in `batch_configs.py` are modified. Handles
both downward shifts (configs removed) and upward shifts (configs added), using signature-based matching to
intelligently preserve config groups.

## Basic Usage

```sh
# Single parent_dir_id
python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --dry-run

# Multiple parent_dir_ids
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1" --dry-run

# All parent_dir_ids
python pyrunner/batch_shifter.py --all --dry-run
python pyrunner/batch_shifter.py --all

```

## Arguments

| Argument                | Type | Description                                                                                                          |
|-------------------------|------|----------------------------------------------------------------------------------------------------------------------|
| `-pid, --parent-dir-id` | str  | Process specific parent_dir_id(s), comma-separated (e.g., `ql-p-ms@0` or `ql-p-ms@0,ql-p-ms@1`). Whitespace trimmed. |
| `-a, --all`             | flag | Process all parent_dir_ids found in `reports/skripsi/`                                                               |
| `--dry-run`             | flag | Preview changes without moving/renaming folders. **Recommended before execution.**                                   |
| `--no-archive`          | flag | Rename in-place without archiving to `reports/_shifted/`. By default, old folders are archived first.                |
| `--indexonly`           | flag | Match configs by index only (skip algorithm+runs validation). Use when configs have changed significantly.           |

## How It Works

**Default Matching (Signature-Based):**

- Extracts `alg+runs` signature from existing folders (e.g., `cfg@31-ql500-...` → `ql500`)
- Extracts `alg+runs` from active configs in `LIST_OF_CONFIGS`
- Matches by signature and relative position within each group (preserves order, handles both shifts)

**Archive Structure:**

- Old folders moved to `reports/_shifted/{parent_dir_id}/run-id/` (with original names preserved)
- New folders renamed in `reports/skripsi/{parent_dir_id}/run-id/`

## Typical Workflow

1. Modify `batch_configs.py` (comment out/add configs)
2. Preview: `python pyrunner/batch_shifter.py --all --dry-run`
3. Review output to verify shifting logic
4. Execute: `python pyrunner/batch_shifter.py --all`
5. Continue running simulations: `python pyrunner/batch_runner.py --all`

## Notes

- Use `--dry-run` before every real execution
- No automatic rollback: manually restore from `reports/_shifted/` if needed
- Versioned folders (e.g., `cfg@31(2)`) are not processed
- Fast operation: 30+ folders shift in < 1 second
