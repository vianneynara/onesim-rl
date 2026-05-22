"""
The list of configurations for the batch runner. Starts from index 0.

--- RESUME AFTER CRASH ---
Each config supports an optional "start_ep" key (default: 1).
If your PC crashed mid-run, manually set "start_ep" to the first episode
that did NOT complete (e.g. if episodes 1-137 finished, set start_ep=138).
The runner will skip straight to that episode without re-running earlier ones.
Leave "start_ep" out (or set it to 1) for a fresh run.

{"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    "start_ep": 1,   # <-- change this to resume (e.g. 138 to start from ep 138)
    "overrides": { ... }
},

--- WHY SOME CONFIGS ARE COMMENTED OUT ---
- UCB ucb_ec >= 7.5: extremely high exploration constant causes near-permanent
  exploration, agent never exploits — not useful to compare.
- EpsilonGreedy eg_ed >= 0.999999999: decay is so slow that epsilon barely
  moves over 500 episodes — equivalent to running pure random exploration.
- TS ts_iv >= 5.0: excessively high initial variance causes near-random
  sampling for too long relative to the 500-episode budget.
"""

LIST_OF_CONFIGS = [
    # =========================================================================
    # [ First Visit (mcnm_fv=True) ]
    # =========================================================================

    # --- Epsilon-Greedy | fv=True ---
    # 1
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 2
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.991,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 3
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.992,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 4
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.993,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 5
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.994,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 6
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9954,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 7
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.996,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 8
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.997,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 9
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.998,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 10
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 11
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 12
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 13
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 14
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },

    # --- UCB | fv=True ---
    # 15
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 16
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 17
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 18
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 19
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 20
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 21
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 22
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 23
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "ucb_reset": True,
            "mcnm_fv": True,
        }
    },
    # 24
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": True,
        }
    },
    # 25
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "mcnm_fv": True,
        }
    },
    # 26
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": True,
        }
    },
    # 27
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": True,
        }
    },
    # 28
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": True,
        }
    },
    # 29
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": True,
        }
    },
    # 30
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcnm_fv": True,
        }
    },
    # 31
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcnm_fv": True,
        }
    },
    # 32
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": True,
        }
    },

    # --- Thompson Sampling | fv=True ---
    # 33
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_bayesian": True,
            "ts_reset": True,
            "mcnm_fv": True,
        }
    },
    # 34
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_bayesian": False,
            "ts_reset": True,
            "mcnm_fv": True,
        }
    },
    # 35
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_bayesian": True,
            "ts_reset": False,
            "mcnm_fv": True,
        }
    },
    # 36
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 0.5,
            "mcnm_fv": True,
        }
    },
    # 37
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcnm_fv": True,
        }
    },
    # 38
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcnm_fv": True,
        }
    },


    # =========================================================================
    # [ Every Visit (mcnm_fv=False) ]
    # =========================================================================

    # --- Epsilon-Greedy | fv=False ---
    # 39
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 40
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.991,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 41
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.992,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 42
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.993,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 43
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.994,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 44
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9954,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 45
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.996,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 46
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.997,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 47
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.998,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 48
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 49
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 50
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 51
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 52
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "group": "mcn_epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },

    # --- UCB | fv=False ---
    # 53
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 54
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 55
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 56
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 57
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 58
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 59
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 60
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 61
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "ucb_reset": True,
            "mcnm_fv": False,
        }
    },
    # 62
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": False,
        }
    },
    # 63
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "mcnm_fv": False,
        }
    },
    # 64
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": False,
        }
    },
    # 65
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": False,
        }
    },
    # 66
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": False,
        }
    },
    # 67
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": False,
        }
    },
    # 68
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcnm_fv": False,
        }
    },
    # 69
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcnm_fv": False,
        }
    },
    # 70
    {"alg": "mcn", "runs": 500, "bp": "ucb", "group": "mcn_ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": False,
        }
    },

    # --- Thompson Sampling | fv=False ---
    # 71
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_bayesian": True,
            "ts_reset": True,
            "mcnm_fv": False,
        }
    },
    # 72
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_bayesian": False,
            "ts_reset": True,
            "mcnm_fv": False,
        }
    },
    # 73
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_bayesian": True,
            "ts_reset": False,
            "mcnm_fv": False,
        }
    },
    # 74
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 0.5,
            "mcnm_fv": False,
        }
    },
    # 75
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcnm_fv": False,
        }
    },
    # 76
    {"alg": "mcn", "runs": 500, "bp": "ts", "group": "mcn_ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcnm_fv": False,
        }
    },
]