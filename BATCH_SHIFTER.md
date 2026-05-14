# Batch Shifter Documentation

## Overview

`batch_shifter.py` is a utility module that automatically renames `cfg@N` prefixed run-id folders when batch configs in `batch_configs.py` are modified, accounting for both:
- **Downward shifts:** When configs are removed/commented out (e.g., cfg@5 → cfg@3)
- **Upward shifts:** When configs are added in between (e.g., cfg@2 → cfg@3)

### Smart Matching Strategy

The module uses **signature-based grouped matching** to intelligently handle both shift directions:

1. Groups all configs by their **algorithm+runs signature** (e.g., all `ql500` configs together, all `lfe500` together)
2. Within each group, matches existing folders to active configs **by relative position**
3. This preserves order and works regardless of shift direction

**Why this matters:** A greedy first-match strategy would fail on upward shifts. For example:
- If you add a new Thompson Sampling config at index 1
- Old folders exist at indices [31, 32] (both Thompson Sampling)
- Greedy matching would incorrectly map cfg@31 → index 1 (WRONG!)
- Position-based matching correctly maps: cfg@31 → 31, cfg@32 → 32 (RIGHT!)

---

## Installation & Usage

### Basic Usage

```bash
# Single parent_dir_id
python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --dry-run

# Multiple parent_dir_ids (comma-separated)
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1" --dry-run
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0, ql-p-ms@1, lfe-c-ms@0" --dry-run

# Process all parent_dir_ids
python pyrunner/batch_shifter.py --all --dry-run
python pyrunner/batch_shifter.py --all
```

### Command-Line Arguments

#### `-pid, --parent-dir-id <NAMES>`
Process specific parent_dir_id(s). Can be a single ID or multiple IDs separated by commas. Whitespace around commas is automatically trimmed.

Examples:
- Single: `ql-p-ms@0`
- Multiple: `ql-p-ms@0,ql-p-ms@1`
- Multiple with spaces: `ql-p-ms@0, ql-p-ms@1, lfe-c-ms@0` (spaces are trimmed)

```bash
python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1"
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0, ql-p-ms@1, lfe-c-ms@0"
```

#### `-a, --all`
Process all parent_dir_ids found in `reports/skripsi/`.

```bash
python pyrunner/batch_shifter.py --all
```

#### `--indexonly` (store_true)
Match configs by index only (less strict validation). By default, the module validates that the algorithm and number of runs (`alg+runs` signature, e.g., `ql500`) match between existing folders and active configs. Use this flag for index-based matching when configs have changed significantly.

```bash
python pyrunner/batch_shifter.py --all --indexonly
```

#### `--dry-run` (store_true)
Preview all changes without actually moving or renaming any folders. **Highly recommended** as a first step.

```bash
python pyrunner/batch_shifter.py --all --dry-run
```

#### `--no-archive` (store_true)
Rename folders in-place without archiving old folders to `reports/_shifted/`. By default, old folders are moved to `reports/_shifted/` before renaming, allowing you to keep a record of pre-shift state.

```bash
python pyrunner/batch_shifter.py --all --no-archive
```

---

## How It Works

### Matching Strategy

By default, the module uses a **signature-based matching strategy**:

1. Extracts `alg` and `runs` from each existing folder name (e.g., `cfg@31-ql500-...` → `ql500`)
2. Extracts `alg` and `runs` from each active config in `LIST_OF_CONFIGS`
3. Matches existing folders to new indices by finding configs with the same algorithm and runs

**Note:** The `id` field in configs is **not used** for matching, as it's not currently being utilized.

### With `--indexonly` Flag

Matches configs **by index alone**, without validating algorithm or runs. Useful when:
- Configs have been heavily reordered
- Algorithm or runs values have changed
- You want fastest matching without validation

### Archive Structure

When old folders are archived (default behavior):

```
Before:
reports/skripsi/ql-p-ms@0/run-id/cfg@31-ql500-qlm_bp@ts-ts_iv@5.0/
reports/skripsi/ql-p-ms@0/run-id/cfg@32-ql500-qlm_bp@ts-ts_iv@10.0/

After shift (with archiving):
reports/_shifted/ql-p-ms@0/run-id/cfg@31-ql500-qlm_bp@ts-ts_iv@5.0/
reports/_shifted/ql-p-ms@0/run-id/cfg@32-ql500-qlm_bp@ts-ts_iv@10.0/
reports/skripsi/ql-p-ms@0/run-id/cfg@01-ql500-qlm_bp@ts-ts_iv@5.0/
reports/skripsi/ql-p-ms@0/run-id/cfg@02-ql500-qlm_bp@ts-ts_iv@10.0/
```

The `reports/_shifted/` archive preserves the full directory hierarchy and original folder names for reference or recovery.

---

## Example Scenarios

### Scenario 1: Reduce Epsilon Profiles (4 configs removed)

**batch_configs.py before:**
```python
LIST_OF_CONFIGS = [
    # Indices 1-10: Epsilon-Greedy
    {...},
    {...},
    # ... (10 configs)
    
    # Indices 11-22: UCB
    {...},
    # ... (12 configs)
    
    # Indices 23-27: Thompson Sampling
    {...},
    # ... (5 configs)
    
    # Indices 28-35: Lévy Flight (8 configs - about to comment out 4)
    {...},
    # ... (8 configs)
]
```

**Existing folders (from old run):**
```
cfg@31-lfe500-lfe_la@0.5
cfg@32-lfe500-lfe_la@0.75
cfg@33-lfe500-lfe_la@1.0
cfg@34-lfe500-lfe_la@1.25
```

**Comment out cfg indices 28-31 in batch_configs.py:**
```python
# Indices 28-35: Lévy Flight (reduced from 8 to 4)
# {...},  # Commented: index 28
# {...},  # Commented: index 29
# {...},  # Commented: index 30
# {...},  # Commented: index 31
{...},    # Index 28 (was 32)
{...},    # Index 29 (was 33)
{...},    # Index 30 (was 34)
{...},    # Index 31 (was 35)
```

**Run batch_shifter:**
```bash
python pyrunner/batch_shifter.py --parent-dir-id lfe-c-ms@0 --dry-run
```

**Output:**
```
DRY RUN: Index 31 → 28: cfg@31-lfe500-lfe_la@0.5 → cfg@28-lfe500-lfe_la@0.5
DRY RUN: Index 32 → 29: cfg@32-lfe500-lfe_la@0.75 → cfg@29-lfe500-lfe_la@0.75
DRY RUN: Index 33 → 30: cfg@33-lfe500-lfe_la@1.0 → cfg@30-lfe500-lfe_la@1.0
DRY RUN: Index 34 → 31: cfg@34-lfe500-lfe_la@1.25 → cfg@31-lfe500-lfe_la@1.25
```

**Execute:**
```bash
python pyrunner/batch_shifter.py --parent-dir-id lfe-c-ms@0
```

**Result:**
- Old folders moved to `reports/_shifted/lfe-c-ms@0/run-id/`
- New folders renamed in `reports/skripsi/lfe-c-ms@0/run-id/`

---

### Scenario 2: Process Multiple Runs at Once

```bash
# Dry-run multiple parent_dir_ids
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1" --dry-run

# If satisfied, execute
python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1"

# Or process all parent_dir_ids
python pyrunner/batch_shifter.py --all --dry-run
python pyrunner/batch_shifter.py --all
```

---

### Scenario 3: Add New Config in Between (UPWARD SHIFT)

**batch_configs.py before (35 configs total):**
```python
LIST_OF_CONFIGS = [
    # ... 30 configs (various algorithms) ...
    # Indices 31-35: Thompson Sampling
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-1", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-2", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-3", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-4", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-5", ...},
]
```

**Existing folders (from previous run):**
```
cfg@31-ql500-qlm_bp@ts-ts_iv@5.0
cfg@32-ql500-qlm_bp@ts-ts_iv@10.0
cfg@33-ql500-qlm_bp@ts-ts_iv@15.0
cfg@34-ql500-qlm_bp@ts-ts_iv@20.0
cfg@35-ql500-qlm_bp@ts-ts_iv@25.0
```

**Add a new Thompson Sampling at index 1 (now 36 configs total):**
```python
LIST_OF_CONFIGS = [
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-new", ...},  # NEW at index 1
    # ... other 30 configs shift ...
    # Indices 32-36: Thompson Sampling (shifted from 31-35)
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-1", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-2", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-3", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-4", ...},
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ts-config-5", ...},
]
```

**Run batch_shifter:**
```bash
python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --dry-run
```

**Output:**
```
Active signature groups: {'ql500': 6, ...}
Existing signature groups: {'ql500': 5}
Signature group 'ql500': 5 existing, 6 active unmatched
  Matched: cfg@31 → cfg@32 (signature=ql500, position=0)
  Matched: cfg@32 → cfg@33 (signature=ql500, position=1)
  Matched: cfg@33 → cfg@34 (signature=ql500, position=2)
  Matched: cfg@34 → cfg@35 (signature=ql500, position=3)
  Matched: cfg@35 → cfg@36 (signature=ql500, position=4)

DRY RUN: Index 31 → 32: cfg@31-ql500-... → cfg@32-ql500-...
DRY RUN: Index 32 → 33: cfg@32-ql500-... → cfg@33-ql500-...
DRY RUN: Index 33 → 34: cfg@33-ql500-... → cfg@34-ql500-...
DRY RUN: Index 34 → 35: cfg@34-ql500-... → cfg@35-ql500-...
DRY RUN: Index 35 → 36: cfg@35-ql500-... → cfg@36-ql500-...
```

**Result:**
- cfg@31 → cfg@32 (shifted up by 1)
- cfg@32 → cfg@33 (shifted up by 1)
- cfg@33 → cfg@34 (shifted up by 1)
- cfg@34 → cfg@35 (shifted up by 1)
- cfg@35 → cfg@36 (shifted up by 1)
- Old folders moved to `reports/_shifted/ql-p-ms@0/run-id/`

---

### Scenario 4: In-Place Rename Without Archiving

If you want to rename folders without moving them to `_shifted/`:

```bash
python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --no-archive --dry-run
python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --no-archive
```

---

## Typical Workflow

1. **Modify `batch_configs.py`** by commenting out or deleting configs as needed.

2. **Preview changes** using dry-run:
   ```bash
   python pyrunner/batch_shifter.py --all --dry-run
   ```

3. **Review the output** to verify the shifting logic is correct.

4. **Execute the shift** (after confirming):
   ```bash
   python pyrunner/batch_shifter.py --all
   ```

5. **Verify results** by checking `reports/skripsi/` and `reports/_shifted/` directories.

6. **Continue running simulations** as usual:
   ```bash
   python pyrunner/batch_runner.py --all
   ```

---

## Notes

- **No Rollback:** The module doesn't provide automatic rollback. If you need to undo, manually move folders back from `reports/_shifted/` to their original locations.
  
- **Safe Operations:** The `--dry-run` flag should be used before every real execution to verify behavior.

- **Versioned Folders:** The module currently handles base cfg@N folders. Versioned folders (e.g., `cfg@31(2)`) are not processed.

- **Performance:** Scanning and shifting are fast operations; processing 30+ folders takes < 1 second.

---

## Troubleshooting

### "No cfg@N folders found"
- Ensure run-id directory exists at `reports/skripsi/{parent_dir_id}/run-id/`.
- Check that folder names follow the pattern `cfg@NN-...`.

### "No matching active config"
- This warning appears when an existing folder's algorithm/runs don't match any active config.
- Try using `--indexonly` for lenient matching.

### Permission Denied
- Ensure you have write permissions to `reports/` and `reports/_shifted/`.

---

## Technical Details

### Matching Algorithm

The module uses a greedy matching approach:

1. Iterate through existing cfg@N folders (sorted by index)
2. For each folder, extract the alg+runs signature
3. Find the first unmatched active config with the same alg+runs
4. Create a mapping: `old_index → new_index`
5. Apply renames in sorted order

### Signature Format

- **Folder signature:** Extracted from folder name like `cfg@05-ql500-...` → `(ql, 500)`
- **Config signature:** Built from active config: `ql` + `500` → `ql500`
- **Match:** Folder signature's `alg+runs` == Config signature's format

---

## API Reference

### Core Functions

```python
def extract_cfg_index(folder_name: str) -> Optional[int]
    """Extract cfg index from folder name like 'cfg@05-ql500-...'."""

def extract_alg_and_runs(folder_name: str) -> Optional[Tuple[str, int]]
    """Extract algorithm and runs from folder name."""

def get_active_configs_mapping() -> Dict[int, dict]
    """Build a mapping of config index to config dict for all active configs."""

def build_rename_mapping(
    existing_folders: Dict[int, str],
    active_configs: Dict[int, dict],
    index_only: bool = False
) -> Tuple[Dict[int, int], List[str]]
    """Build a mapping from old cfg index to new cfg index."""

def execute_shift(
    parent_dir_id: str,
    index_only: bool = False,
    dry_run: bool = False,
    no_archive: bool = False
) -> Tuple[int, int]
    """Execute the shift operation for a specific parent_dir_id."""
```

---

## Integration with batch_runner.py

Currently, `batch_shifter.py` is a standalone module. If you'd like to integrate it into `batch_runner.py` with an optional flag like `--shift-pids`, that can be added in the future.

For now, run it separately before executing batch simulations:

```bash
# Step 1: Update batch_configs.py (comment/uncomment configs)
# Step 2: Shift run-id folders
python pyrunner/batch_shifter.py --all --dry-run
python pyrunner/batch_shifter.py --all

# Step 3: Continue with batch runner
python pyrunner/batch_runner.py --all
```
