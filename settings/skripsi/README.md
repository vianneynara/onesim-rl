# Scenario Naming Convention

Abbreviations are necessary to keep scenario file names concise while maintaining clarity and consistency. This document
defines the standardized naming format used throughout the simulation configuration system.

## Overview

Scenario names use a templating system with parameter substitution via `%%ParameterKey%%` syntax. These template paths
are replaced at runtime with actual configuration values. To make filenames manageable, we abbreviate the descriptive
prefixes to short, meaningful codes.

## Naming Format

**Full Format (Descriptive):**

```
RandomSearch-Agent_movementModel@%%Group1.movementModel%%-Target_movementModel@%%Group2.movementModel%%-LevyFlight.levyAlpha@%%Group1.levyAlpha%%-behaviorPolicy@%%QLearningMovement.behaviorPolicy%%-Episode@%%EpisodicPersistenceManager.episodeNumber%%
```

**Abbreviated Format (Used in Filenames):**

```
RandomSearch-amm@%%Group1.movementModel%%-tmm@%%Group2.movementModel%%-la@%%Group1.levyAlpha%%-rlbp@%%QLearningMovement.behaviorPolicy%%-episode@%%EpisodicPersistenceManager.episodeNumber%%
```

## Abbreviation Reference

| Abbreviation | Full Name                              | Configuration Parameter                    | Description                                                    |
|--------------|----------------------------------------|--------------------------------------------|----------------------------------------------------------------|
| `amm`        | Agent's Movement Model                 | `Group1.movementModel`                     | The movement model used by the searching agent (Group 1)       |
| `tmm`        | Target's Movement Model                | `Group2.movementModel`                     | The movement model used by target nodes (Group 2)              |
| `la`         | Lévy Alpha                             | `Group1.levyAlpha`                         | The alpha parameter for Lévy Flight distribution               |
| `rlbp`       | Reinforcement Learning Behavior Policy | `QLearningMovement.behaviorPolicy`         | The exploration/exploitation policy used by the learning agent |
| `episode`    | Episode Number                         | `EpisodicPersistenceManager.episodeNumber` | The simulation episode or iteration number                     |

## Template Variable Format

Template variables follow the pattern: `%%ConfigurationPath%%`

- They are replaced with actual values when the scenario runs
- The path corresponds to configuration parameter names in the `.cfg` files
- Multiple parameters can be combined with hyphen separators (`-`)
