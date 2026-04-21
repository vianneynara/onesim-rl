"""
The list of configurations for the batch runner. Starts from index 0.
"""

LIST_OF_CONFIGS = [
    # [ Q-Learning with Epsilon-Greedy
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.99999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999999,
            "eg_me": 0.1,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "epsilon", "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.9999999999,
            "eg_me": 0.1,
        }
    },

    # [ Q-Learning with UCB ]
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 0.5,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 1.5,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 5.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 7.5,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ucb", "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 10.0,
        }
    },

    # [ Q-Learning with Thompson Sampling ]
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 2.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 5.0,
        }
    },
    {"alg": "ql", "runs": 500, "bp": "ts", "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 10.0,
        }
    }
]