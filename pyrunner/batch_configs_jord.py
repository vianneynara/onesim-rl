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
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 2
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 3
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # 4
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
            "mcnm_fv": True,
        }
    },
    # COMMENTED OUT — eg_ed >= 0.999999999 barely decays over 500 episodes,
    # effectively pure random exploration throughout. Not useful to compare.
    # # 5
    # {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
    #     "overrides": {
    #         "eg_ip": 1.0,
    #         "eg_ed": 0.999999999,
    #         "eg_me": 0.1,
    #         "mcnm_fv": True,
    #     }
    # },
    # # 6
    # {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
    #     "overrides": {
    #         "eg_ip": 1.0,
    #         "eg_ed": 0.9999999999,
    #         "eg_me": 0.1,
    #         "mcnm_fv": True,
    #     }
    # },


    # --- UCB | fv=True ---
    # 5
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": True,
        }
    },
    # 6
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "mcnm_fv": True,
        }
    },
    # 7
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": True,
        }
    },
    # 8
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": True,
        }
    },
    # 9
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": True,
        }
    },
    # 10
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": True,
        }
    },
    # 11
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcnm_fv": True,
        }
    },
    # 12
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcnm_fv": True,
        }
    },
    # 13
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": True,
        }
    },
    # COMMENTED OUT — ucb_ec >= 7.5 causes near-permanent exploration,
    # agent never exploits meaningfully over 500 episodes.
    # # 14
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 7.5,
    #         "mcnm_fv": True,
    #     }
    # },
    # # 15
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 10.0,
    #         "mcnm_fv": True,
    #     }
    # },
    # # 16
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 12.5,
    #         "mcnm_fv": True,
    #     }
    # },
    # # 17
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 15.0,
    #         "mcnm_fv": True,
    #     }
    # },
    # # 18
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 20.0,
    #         "mcnm_fv": True,
    #     }
    # },


    # --- Thompson Sampling | fv=True ---
    # 14
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 0.5,
            "mcnm_fv": True,
        }
    },
    # 15
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcnm_fv": True,
        }
    },
    # 16
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcnm_fv": True,
        }
    },
    # COMMENTED OUT — ts_iv >= 5.0 causes near-random sampling for too long
    # relative to the 500-episode budget. Not useful to compare.
    # # 17
    # {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
    #     "overrides": {
    #         "ts_iv": 5.0,
    #         "mcnm_fv": True,
    #     }
    # },
    # # 18
    # {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
    #     "overrides": {
    #         "ts_iv": 10.0,
    #         "mcnm_fv": True,
    #     }
    # },


    # =========================================================================
    # [ Every Visit (mcnm_fv=False) ]
    # =========================================================================

    # --- Epsilon-Greedy | fv=False ---
    # 17
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 18
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 19
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # 20
    {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
            "mcnm_fv": False,
        }
    },
    # COMMENTED OUT — same reason as fv=True: eg_ed >= 0.999999999 is
    # effectively pure random exploration over 500 episodes.
    # # 21
    # {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
    #     "overrides": {
    #         "eg_ip": 1.0,
    #         "eg_ed": 0.999999999,
    #         "eg_me": 0.1,
    #         "mcnm_fv": False,
    #     }
    # },
    # # 22
    # {"alg": "mcn", "runs": 500, "bp": "epsilon", "id": "mcn1-bp=epsilon",
    #     "overrides": {
    #         "eg_ip": 1.0,
    #         "eg_ed": 0.9999999999,
    #         "eg_me": 0.1,
    #         "mcnm_fv": False,
    #     }
    # },


    # --- UCB | fv=False ---
    # 21
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
            "mcnm_fv": False,
        }
    },
    # 22
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 0.75,
            "mcnm_fv": False,
        }
    },
    # 23
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
            "mcnm_fv": False,
        }
    },
    # 24
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
            "mcnm_fv": False,
        }
    },
    # 25
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
            "mcnm_fv": False,
        }
    },
    # 26
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.5,
            "mcnm_fv": False,
        }
    },
    # 27
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 2.75,
            "mcnm_fv": False,
        }
    },
    # 28
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 3.0,
            "mcnm_fv": False,
        }
    },
    # 29
    {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
            "mcnm_fv": False,
        }
    },
    # COMMENTED OUT — same reason as fv=True: ucb_ec >= 7.5 causes
    # near-permanent exploration, agent never exploits meaningfully.
    # # 30
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 7.5,
    #         "mcnm_fv": False,
    #     }
    # },
    # # 31
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 10.0,
    #         "mcnm_fv": False,
    #     }
    # },
    # # 32
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 12.5,
    #         "mcnm_fv": False,
    #     }
    # },
    # # 33
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 15.0,
    #         "mcnm_fv": False,
    #     }
    # },
    # # 34
    # {"alg": "mcn", "runs": 500, "bp": "ucb", "id": "mcn1-bp=ucb",
    #     "overrides": {
    #         "ucb_ec": 20.0,
    #         "mcnm_fv": False,
    #     }
    # },


    # --- Thompson Sampling | fv=False ---
    # 30
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 0.5,
            "mcnm_fv": False,
        }
    },
    # 31
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
            "mcnm_fv": False,
        }
    },
    # 32
    {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
            "mcnm_fv": False,
        }
    },
    # COMMENTED OUT — same reason as fv=True: ts_iv >= 5.0 causes near-random
    # sampling for too long relative to the 500-episode budget.
    # # 33
    # {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
    #     "overrides": {
    #         "ts_iv": 5.0,
    #         "mcnm_fv": False,
    #     }
    # },
    # # 34
    # {"alg": "mcn", "runs": 500, "bp": "ts", "id": "mcn1-bp=ts",
    #     "overrides": {
    #         "ts_iv": 10.0,
    #         "mcnm_fv": False,
    #     }
    # },
]
