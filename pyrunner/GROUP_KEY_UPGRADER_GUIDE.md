# Group Key Upgrader - User Guide

## Overview

The **Group Key Upgrader** (`group_key_upgrader.py`) is a standalone utility that adds the new config group token (`cg@{group}`) to existing run-id directories. It transforms old run-id naming format to the new format that includes group information.

## Format Transformation

### Before Upgrade
```
cfg@01-ql500-eg_ed@0.99
cfg@05-ql500-qlm_bp@ucb-ucb_ec@0.5
cfg@12-lfe500-lfe_la@1.5
```

### After Upgrade
```
cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99
cfg@05-cg@ql_ucb-ql500-qlm_bp@ucb-ucb_ec@0.5
cfg@12-cg@lf-lfe500-lfe_la@1.5
```

The `cg@{group}` token is **always inserted right after `cfg@NN`** and **before algorithm+runs**.

## Features

- **Smart Matching**: Matches old folders to active configs by comparing (algorithm, runs, behavior_policy)
- **Group Extraction**: Automatically extracts the group value from matching config in LIST_OF_CONFIGS
- **Dry-Run Mode**: Preview changes before applying them
- **Batch Processing**: Process single or multiple parent directories
- **Backward Compatibility**: Safely handles already-upgraded folders (skips them)
- **Error Handling**: Detailed logging of failures and issues

## Usage

### Basic Dry-Run (Recommended First Step)

```bash
# Dry-run on a single parent directory
python -m pyrunner.group_key_upgrader --parent-dir-id ql-p-ms@0 --dry-run

# Dry-run on multiple parent directories
python -m pyrunner.group_key_upgrader --parent-dir-id "ql-p-ms@0,ql-p-ms@1,ql-c-ms@0" --dry-run

# Dry-run on all parent directories
python -m pyrunner.group_key_upgrader --all --dry-run
```

### Actual Upgrade (After Verifying Dry-Run Output)

```bash
# Upgrade a single parent directory
python -m pyrunner.group_key_upgrader --parent-dir-id ql-p-ms@0

# Upgrade multiple parent directories
python -m pyrunner.group_key_upgrader --parent-dir-id "ql-p-ms@0,ql-p-ms@1,ql-c-ms@0"

# Upgrade all parent directories
python -m pyrunner.group_key_upgrader --all
```

## Command-Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--all` | Yes (mutually exclusive) | Process all parent directories in reports base |
| `--parent-dir-id` | Yes (mutually exclusive) | Comma-separated list of parent directory IDs to process |
| `--dry-run` | No | Preview changes without applying them (recommended) |
| `--reports-base` | No | Override base reports directory (default: `reports/skripsi`) |
| `-h, --help` | No | Show help message |

## Matching Algorithm

The upgrader matches old folders to active configs using the following hierarchy:

1. **Extract** `algorithm + runs + behavior_policy` from old folder name
2. **Build signature** from extracted values (e.g., `ql+500+ucb`)
3. **Search** for matching signature in active configs
4. **Extract group** from the first matching config
5. **Insert** `cg@{group}` token in the correct position

### Matching Examples

| Old Folder | Extract | Signature | Matched Config | Group | New Folder |
|------------|---------|-----------|-----------------|-------|-----------|
| `cfg@01-ql500-eg_ed@0.99` | `ql`, `500`, `epsilon` | `ql+500+epsilon` | Config index 1 | `ql_epsilon` | `cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99` |
| `cfg@05-ql500-qlm_bp@ucb-ucb_ec@0.5` | `ql`, `500`, `ucb` | `ql+500+ucb` | Config index 11 | `ql_ucb` | `cfg@05-cg@ql_ucb-ql500-qlm_bp@ucb-ucb_ec@0.5` |
| `cfg@12-lfe500-lfe_la@1.5` | `lfe`, `500`, `None` | `lfe+500` | Config index 29 | `lf` | `cfg@12-cg@lf-lfe500-lfe_la@1.5` |

## Behavior Policy Detection

The upgrader automatically detects behavior policy from folder names:

| Pattern | Behavior Policy |
|---------|-----------------|
| `qlm_bp@ucb` | `ucb` (Upper Confidence Bound) |
| `qlm_bp@ps` | `ps` (Thompson Sampling) |
| `qlm_bp@epsilon` | `epsilon` (Epsilon-Greedy) |
| No `qlm_bp@` for Q-Learning | `epsilon` (default) |
| `lfe500` | `None` (Lévy Flight doesn't have BP) |

## Output Example

### Dry-Run Output
```
[15:30:45 INFO batch_shifter]: ====================================================================================================
[15:30:45 INFO batch_shifter]: Processing: ql-p-ms@0
[15:30:45 INFO batch_shifter]: ====================================================================================================
[15:30:45 INFO batch_shifter]: Found 32 existing run-id folders
[15:30:45 INFO batch_shifter]:   cfg@01: 'cfg@01-ql500-eg_ed@0.99' → 'cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99' (sig=ql+500+epsilon, group=ql_epsilon)
[15:30:45 INFO batch_shifter]:   cfg@02: 'cfg@02-ql500-eg_ed@0.991' → 'cfg@02-cg@ql_epsilon-ql500-eg_ed@0.991' (sig=ql+500+epsilon, group=ql_epsilon)
[15:30:45 INFO batch_shifter]:   cfg@05: 'cfg@05-ql500-qlm_bp@ucb-ucb_ec@0.5' → 'cfg@05-cg@ql_ucb-ql500-qlm_bp@ucb-ucb_ec@0.5' (sig=ql+500+ucb, group=ql_ucb)
[15:30:45 INFO batch_shifter]:   ...
[15:30:45 INFO batch_shifter]: Will rename 32 folder(s)
[15:30:45 INFO batch_shifter]: [DRY-RUN] Would rename: cfg@01-ql500-eg_ed@0.99 → cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99
[15:30:45 INFO batch_shifter]:   ...
[15:30:45 INFO batch_shifter]: Result: 32 total, 32 successful, 0 failed
[15:30:45 INFO batch_shifter]: ====================================================================================================
[15:30:45 INFO batch_shifter]: [SUMMARY] Upgrade completed in 0:00:02.123456
[15:30:45 INFO batch_shifter]: Total: 32 renames, 32 successful, 0 failed
[15:30:45 INFO batch_shifter]: This was a DRY-RUN. To actually rename, remove --dry-run flag.
[15:30:45 INFO batch_shifter]: ====================================================================================================
```

## Special Cases Handled

### Already Upgraded Folders
If a folder already contains `cg@` token, it's skipped:
```
cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99 (Already has cg@ token, skipping)
```

### Unmatched Folders
If a folder cannot be matched to an active config:
```
cfg@15 (sig=ql+500+custom_bp): No matching active config found
```

### Missing Group in Config
If the matching config doesn't have a group key:
```
cfg@20 (sig=lfe+500): Matching config has no group key
```

## Workflow

### Recommended Upgrade Workflow

1. **Review Active Configs**
   - Ensure all configs in `batch_configs.py` have `group` keys set
   - Verify the groups match your naming scheme

2. **Dry-Run on Representative Parent Dir**
   ```bash
   python -m pyrunner.group_key_upgrader --parent-dir-id ql-p-ms@0 --dry-run
   ```

3. **Review Output**
   - Check that all renames look correct
   - Verify no folders are being skipped unexpectedly

4. **Dry-Run on All Parents** (if happy with sample)
   ```bash
   python -m pyrunner.group_key_upgrader --all --dry-run
   ```

5. **Execute Actual Upgrade**
   ```bash
   python -m pyrunner.group_key_upgrader --all
   ```

6. **Verify Results**
   - Spot-check a few renamed directories
   - Run plotters to ensure they still work

## Troubleshooting

### Issue: "No run-id directory found"
- The parent directory ID doesn't exist in reports base
- Verify correct parent directory name
- Check reports base path with `--reports-base`

### Issue: "No matching active config found"
- The old folder's signature doesn't match any active config
- This can happen if configs were significantly reorganized
- Check if the algorithm, runs, or behavior policy changed

### Issue: Renames failed after dry-run success
- Likely due to filesystem permissions
- Try running with elevated privileges
- Check if sufficient disk space available

## Integration with Batch Runner

After upgrading existing run-ids, they will work seamlessly with:
- **bestof_plotter.py**: Group token automatically filtered from legends
- **persistence_plotter.py**: Group token automatically filtered
- **batch_shifter.py**: Still works (only looks at cfg@N and alg+runs)

## Rollback (If Needed)

If something goes wrong, you can manually revert by removing the `cg@{group}-` token:

```bash
# Manual revert example
mv "reports/skripsi/ql-p-ms@0/run-id/cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99" \
   "reports/skripsi/ql-p-ms@0/run-id/cfg@01-ql500-eg_ed@0.99"
```

Or, create the reverse with a duplicate of this script that removes the token.

## Performance

- Scanning: ~50-100 folders/second (depends on filesystem)
- Renaming: Nearly instant
- Total time for ~1000 folders: 10-30 seconds

## Limitations

- Does not rename runs in `_shifted` or `_orphaned` directories
- Requires exact match on (alg, runs, bp) - won't infer close matches
- Group must be present in matching active config

---

**Last Updated**: 2026-05-13  
**Version**: 1.0  
**Status**: Tested and Ready for Production

